from access_tokens import tokens
from django.http import Http404
from django.conf import settings


def validate_token(function):
    def wrap(request, *args, **kwargs):
        token = kwargs.get('token')
        case_id = kwargs.get('case_id')
        validate = tokens.validate(
            token, scope=(), key=case_id,
            salt=settings.TOKEN_SALT, max_age=None
        )
        if validate:
            return function(request, *args, **kwargs)
        else:
            raise Http404
    return wrap
