from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
import sys

from rlp.core.views import SendToView

def enforce_sharedobject_permissions(cls, obj_class, id_name, methods=None):
    """ Class decorator intended for subclasses of ClassBasedViews that serve rlp.core.models.SharedObjectMixin subclasses.
        This decorator will inspect your view for the standard http methods
        and wrap those individual methods in a check that the user has access to the resource.
        On failure it returns a 403 Forbidden.
        The SharedContent should use the SharedObjectMixin which supplies the required is_shared_with_user method.
        You can restrict the wrapping behavior to only certain methods by passing an array of method names.

        use like:
            from functools import partial
            @partial(wrap_requests_with_permissions_check, obj_class=CaseReport, id_name='case_id')
            class MyView(TemplateView):a
                ...

        Presently, python3 class decorators cannot take additional arguments beyond the class,
        so we use functools' partial to create a wrapper for our wrapper that encloses the obj_class and parameter name.
    """
    # wrap get, post, put, delete, etc
    for fname in methods or cls.http_method_names:
        if fname == 'options':
            continue
        #if settings.DEBUG:
        #    print("inspecting classbasedview ", cls, "for:", fname, file=sys.stderr)
        if hasattr(cls, fname):
            view_func = getattr(cls, fname)

            # we wrap the wrapper so that fname and view_func are shared between interations.
            def make_wrapper(fn, vf, oc, id_name):
                def wrapper(self, request, *args, **kwargs):
                    if settings.DEBUG:
                        print("wrapper:", fn, args, kwargs, file=sys.stderr)
                    obj = oc.objects.get(id=kwargs[id_name])
                    if hasattr(obj, 'can_view'):
                        if obj.can_view(user=request.user):
                            return vf(self, request, *args, **kwargs)
                    if obj.is_shared_with_user(request.user):
                        if settings.DEBUG:
                            print("permisssion granted", vf, file=sys.stderr)
                        return vf(self, request, *args, **kwargs)
                    # ideally, we'd redirect to the appropriate project join using reverse('projects:projects_join', args=[proj.id] )
                    # but we dont have a good way to select the appropriate project
                    if settings.DEBUG:
                        print('sorry, denied', file=sys.stderr)
                    messages.warning(request, "Permission to access {dt}:{i} denied.".format(dt=oc.__name__,i=kwargs[id_name]))
                    return HttpResponseRedirect(redirect_to="/")

                return wrapper

            if settings.DEBUG:
                print("wrapping ", fname, "on", cls, "for shared object permissions", file=sys.stderr)
            setattr(cls, fname, make_wrapper(fname, view_func, obj_class, id_name))
    return cls


def bookmark_and_notify(
    obj, view, request, app_label,
    model_name, comment=None,
):
    '''When using the "send to" form:
        * bookmark content for the user creating the content
        * bookmark for the group last viewed (if any)
    '''
    initial_proj = request.session.get('last_viewed_project')
    if initial_proj:
        project_type = ContentType.objects.get_by_natural_key(
            'projects', 'project',
        )
        Project = project_type.model_class()
        group = Project.objects.get(id=initial_proj)
        group.bookmark(obj)
        obj.share_with([group], request.user, comment)
    else:
        group = None
    SendToView.post(
        view,
        request,
        app_label,
        model_name,
        obj.id,
    )
    return group


# the order of these matter.    That further down the list, the more important
# the verb is considered by the score_verb function.
# This is mostly so that 'shared' can be beaten by just about anything else
COMBINABLE_VERBS = (
    'shared',
    'added',
    'created',
    'started',
    'uploaded',
)

def score_verb( x ):
    try:
        return COMBINABLE_VERBS.index(x)
    except ValueError as not_in_list:
        return -1

def rollup(input, simfunc, samefunc, scorefunc, rollup_name):
    """ Rolls similar items in a list up under an array on the first i
        similar item.
        Adjacent, equivalent items are dropped entirely.

        Given a simfunc that looks at only the second and third column,
        and a samefunc that looks at the second, third and fourth,
        The simfunc tests for similar objects ( can be consolidated )
        and the samefunc tests for equivalent ( which can be dropped ).

        Turns this:
             1 | a | b | c
             2 | d | e | f
             3 | d | e | g
             4 | d | e | f
             5 | d | h | i
        into
             1 | a | b | c | []
             3 | d | e | f | [2]
             5 | d | h | i | []

        Item 2 rolled up into 3 because its key fields(d,e) were the same, and
        and it is assumed the sequence is reverse chronological.
        Item 4 is dropped because it is equivalent to item 2.
    """
    input_iter = iter(input)

    i = next( input_iter )
    i_sim = simfunc(i)
    equivalent_ids = set([samefunc(i),])

    for n in input_iter:
        n_sim = simfunc(n)
        n_same = samefunc(n)

        # if similar but not the same, roll it up
        # this swaps them, then rolls n up into the new i
        if n_sim == i_sim:
            if n_same not in equivalent_ids:
                equivalent_ids.add( n_same )
                if scorefunc(n) > scorefunc(i):
                    (i, n) = (n, i)
                if not hasattr( i, rollup_name ):
                    setattr( i, rollup_name, [] )
                getattr(i, rollup_name).append( n )
                # and move any previous rollups into the new ia
                if hasattr(n, rollup_name):
                    getattr(i, rollup_name).extend( getattr(n,rollup_name))
        else:
            yield i
            i = n
            i_sim = simfunc(i)
            equivalent_ids = set([samefunc(i),])

    yield i

