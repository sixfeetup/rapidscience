from django import template

from rlp.bibliography.forms import ReferenceShareForm


register = template.Library()


@register.assignment_tag
def get_share_form():
    """
    Get a (new) form object to share a reference.

    Syntax::

        {% get_share_form as form %}
    """
    return ReferenceShareForm()
