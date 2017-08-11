# middleware for getting the current user for the permissions checks
# which should work with the web, admin, management commands, etc


# user will come from the request, the os, or the first staff user.
# TODO: just make this a django-cms compatible util
import os
import pwd

from threading import local
_threadlocals = local()

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

# this should not be 'user' so as to avoid conflicts with django-cms user
THREADLOCAL_USER_KEY = 'casereport_user'

class CurrentUserMiddleware(MiddlewareMixin):
    # django-cms basically does this, but we dont want to depend upon it

    def process_request(self, request):
        self.set_user(request.user)


    @staticmethod
    def set_user(user):
        setattr(_threadlocals, THREADLOCAL_USER_KEY, user)

    @staticmethod
    def get_user():
        user = getattr(_threadlocals, THREADLOCAL_USER_KEY, None)

        if not user:
            # we must not be in a web serving context, see if we have
            # a matching django user for the process user
            username = pwd.getpwuid(os.getuid()).pw_name
            from django.contrib.auth import get_user_model
            User = get_user_model()
            query_args = {
                User.USERNAME_FIELD: username
            }
            user = User.objects.filter(**query_args).first()

            if not user:
                user = User.objects.filter(is_superuser=True).first()

        CurrentUserMiddleware.set_user( user )
        return user
