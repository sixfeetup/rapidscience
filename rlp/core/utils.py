from django.conf import settings
from django.http import HttpResponseForbidden


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
        if settings.DEBUG:
            print("inspecting classbasedview ", cls, "for:", fname)
        if hasattr(cls, fname):
            view_func = getattr(cls, fname)

            # we wrap the wrapper so that fname and view_func are shared between interations.
            def make_wrapper(fn, vf, oc, id_name):
                def wrapper(self, request, *args, **kwargs):
                    if settings.DEBUG:
                        print("wrapper:", fn, args, kwargs)
                    if oc.objects.get(id=kwargs[id_name]).is_shared_with_user(request.user):
                        if settings.DEBUG:
                            print("permisssion granted", vf)
                        return vf(self, request, *args, **kwargs)
                    # ideally, we'd redirect to the appropriate project join using reverse('projects:projects_join', args=[proj.id] )
                    # but we dont have a good way to select the appropriate project
                    if settings.DEBUG:
                        print('sorry, denied')
                    return HttpResponseForbidden()

                return wrapper

            if settings.DEBUG:
                print("wrapping ", fname, "on", cls)
            setattr(cls, fname, make_wrapper(fname, view_func, obj_class, id_name))
    return cls
