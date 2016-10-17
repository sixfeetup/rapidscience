# Largely borrowed from http://github.com/danirus/django-comments-xtd/ but with customizations.
# Removed unnecessary features and backward's incompatibility shims.
default_app_config = 'rlp.discussions.apps.DiscussionsConfig'


def get_model():
    from rlp.discussions.models import ThreadedComment
    return ThreadedComment


def get_form():
    from rlp.discussions.forms import ThreadedCommentForm
    return ThreadedCommentForm
