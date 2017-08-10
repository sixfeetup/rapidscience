import sys
from collections import Iterable, namedtuple

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.utils.functional import SimpleLazyObject

from taggit.models import Tag

from rlp.managedtags.models import ManagedTag


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
    from rlp.core.views import SendToView
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


# these are the verbs related to the creation of public content
# which is why 'created' is not listed -- its a private workflow state
# and 'published' is listed.
CREATION_VERBS = (
    'replied',
    'added',
    'published',
    'started',
    'uploaded',
)

# the order of these matter.    That further down the list, the more important
# the verb is considered by the score_action function.
# This is mostly so that 'shared' can be beaten by just about anything else
COMBINABLE_VERBS = ('created', 'shared',) + CREATION_VERBS


def rollup(input, rollup_name, rollup_attr='target'):
    """ Rolls similar items in a list up under an array on the first i
        similar item.
        Adjacent, equivalent items are dropped entirely.

        similar_action() looks at only the second and third column,
        and same_action looks at the second, third and fourth,
        similar_action() tests for similar objects ( can be consolidated )
        and same_action() tests for equivalent ( which can be dropped ).

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
    def score_action(action):
        try:
            return COMBINABLE_VERBS.index(action.verb)
        except ValueError:
            return -1

    def similar_action(action):
        return str(
            (
                action.actor_object_id,
                'combined' if action.verb in COMBINABLE_VERBS else action.verb,
                action.action_object_content_type,
                action.action_object_object_id
            )
        )

    def same_action(action):
        return str(
            (
                action.actor_object_id,
                action.action_object_content_type,
                action.action_object_object_id,
                action.target_content_type,
                action.target_object_id
            )
        )

    input_iter = iter(input)
    i = next(input_iter)
    i_sim = similar_action(i)
    equivalent_ids = set()

    for n in input_iter:
        n_sim = similar_action(n)
        n_same = same_action(n)

        # if similar but not the same, roll it up
        # this swaps them, then rolls n up into the new i
        if n_sim == i_sim:
            if n_same not in equivalent_ids:
                equivalent_ids.add(n_same)
                #if n score higher, or isnt in out ranked list, swap to the top
                if score_action(n) > score_action(i) or score_action(n) == -1:
                    (i, n) = (n, i)
                if not hasattr(i, rollup_name):
                    setattr(i, rollup_name, [])
                    if hasattr(i, rollup_attr) and getattr(i, rollup_attr):
                        getattr(i, rollup_name).append( getattr(i, rollup_attr) )
                #getattr(i, rollup_name).append(n)
                val = getattr(n, rollup_attr)
                if val and val not in getattr(i, rollup_name):
                    getattr(i, rollup_name).append(val)
                # and move any previous rollups into the new ia
                if hasattr(n, rollup_name):
                    getattr(i, rollup_name).extend(getattr(n, rollup_name))
        else:
            yield i
            equivalent_ids = {same_action(i)}
            i = n
            i_sim = similar_action(i)

    yield i


def fill_tags(tagged_obj, form):
    """ populate the tags and new_tags fields of the form with the tags
        and the UNAPPROVED managed_tags of the tagged instance
    """
    if tagged_obj.tags.count():
        form.fields['tags'].initial = tagged_obj.tags.all()
    if tagged_obj.mtags.count():
        form.fields['new_tags'].initial = ", ".join(
            [mt.name for mt in tagged_obj.mtags.all() if not mt.approved])


def add_tags(obj, tags):
    """ Passing an object and tags, add the tags to the object and save.
        Tags should be a dictionary with 'ids' of existing tags,
        and 'new' with a list of new tags to be added
    """
    if tags['ids']:
        try:
            set_tags = Tag.objects.filter(id__in=tags['ids'])
            obj.tags.set(*set_tags)
        except:
            obj.tags.add(*tags['ids'][0].split(","))
    else:
        obj.tags.clear()
    if tags['new']:
        obj.mtags.clear()
        new_tagwords = [tw for tw in map(str.strip, tags['new'][0].split(","))
                        if tw]
        for ntw in new_tagwords:
            new_slug = slugify(ntw)
            managed_tag, is_new = ManagedTag.objects.get_or_create(slug=new_slug,
                                                                   defaults={
                                                                       'name':ntw,
                                                                   })
            # potentially upgrade to an existing Tag
            if managed_tag.approved:
                t = Tag.objects.get(slug=new_slug)
                obj.tags.add(t)
            else:
                obj.mtags.add(managed_tag)

    # Trigger any post-save signals (e.g. Haystack's real-time indexing)
    obj.save()


FORMAT_NAMED = 'NAMED'
FORMAT_SIMPLE = 'SIMPLE'

def resolve_email_targets(target, exclude=None, fmt=FORMAT_NAMED, debug=False):
    """ Take a target comprised of users, projects, strings and return a set
        of email addresses in either x@domain.tld or Name <x@domain.tld> format
        with duplicates removed and known opt-out's honored.
    """
    if exclude:
        print("exclude:", exclude)
        if isinstance(exclude, str):
            excludables = resolve_email_targets({exclude}, fmt=FORMAT_SIMPLE)
        elif isinstance(exclude, SimpleLazyObject):
            # wrapped user
            excludables = resolve_email_targets({exclude}, fmt=FORMAT_SIMPLE)
        else:
            excludables = resolve_email_targets(exclude, fmt=FORMAT_SIMPLE)
    else:
        excludables = {}

    if debug:
        print("will exclude:", excludables)

    if isinstance(target, str):
        return set(target)
    else:
        # start with a set of items to resolve
        if isinstance( target, Iterable):
            starting_set = set(target)
        else:
            starting_set = {target}

        # expand any Projects into Users
        users_and_strings = set()
        for item in starting_set:
            if hasattr(item, 'users'):
                for m in item.active_members():
                    users_and_strings.add(m)
            else:
                users_and_strings.add(item)

        # email_addresses
        naas = set()
        emails = set()
        NameAndAddress = namedtuple('NameAndAddress', "name address")
        for recipient in users_and_strings:
            if hasattr(recipient, "opt_out_of_email"):
                if recipient.opt_out_of_email:
                    pass # skip the opted-out target
                else:
                    naa = NameAndAddress(recipient.get_full_name(),
                                         recipient.email)
                    naas.add(naa)
            else:
                naa = NameAndAddress( None, recipient)
                # that assumes it was a plain email addr
                naas.add(naa)
        # now we can result it down to a list of strings
        for naa in naas:
            if naa.address in excludables:
                if debug:
                    print("excluding", naa.address)
                continue
            if naa.name:
                if fmt == FORMAT_NAMED:
                    emails.add('"{name}" <{email}>'.format(name=naa.name,
                                                           email=naa.address))
                else:
                    emails.add(naa.address)
            else:
                emails.add(naa.address)
        return emails



def test_resolve_email_targets():
    from rlp.accounts.models import User
    from rlp.projects.models import Project

    from pprint import pprint

    u1 = User.objects.first()
    u2 = User.objects.last()
    p1 = Project.objects.first()
    p2 = Project.objects.last()
    s1 = "glenn@gmail.com"
    s2 = "glenn franxman <glenn@sixfeetup.com>"
    resolve_email_targets(u1)
    #Out[11]: {'Sixies Up <email>'}

    resolve_email_targets(u2)
    #Out[12]: {'Glenn OtherUser <email>'}

    resolve_email_targets(p1)
    #Out[13]: {'Christine Veenstra-VanderSháw <email>',
    #          'Glenn Superuser <email>'}

    resolve_email_targets(p2)
    #Out[14]: {'Sarah Greene <email>'}

    resolve_email_targets([u2])
    resolve_email_targets([p2])
    resolve_email_targets([s2])

    pprint(resolve_email_targets((u1, u2, p1, p2, s1, s2)))
    pprint(resolve_email_targets((u1, u1, p1, p1, s1, s1)))
    print(u1, "opting out")
    u1.opt_out_of_email = True
    res = resolve_email_targets((u1, u1, p1, p1, s1, s1), exclude=["christine@sixfeetup.com", 'glenn@sixfeetup.com'], debug=True)
    pprint(res)
    assert u1 not in res, "opt-out failed"
    assert s1 in res

    res = resolve_email_targets((u1, u2, p1, p1, s1, s1), exclude="christine@sixfeetup.com", debug=True)
    pprint(res)
    assert "christine@sixfeetup.com" not in res, "exclude string failed"

    res = resolve_email_targets((u1, u2, p1, p1, s1, s1), exclude=u2, debug=True)
    pprint(res)
    assert u2 not in res, "exclude failed"

    res = resolve_email_targets((u1, u2, p1, p1, s1, s1), exclude=[p1,p2], debug=True)
    pprint(res)
    for u in p1.active_members():
        assert u not in res, "exclude by group failed"
    for u in p2.active_members():
        assert u not in res, "exclude by group failed"

    lazy_user = SimpleLazyObject( lambda: u2)
    print( "\nExclude lazy_user(", u2.email, ") from ",(u1.email,u2.email) )
    res = resolve_email_targets((u1, u2,), exclude=lazy_user, debug=True)
    pprint(res)
    assert u2 not in res
