from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from actstream.models import Action

from .models import Bookmark


@require_POST
@login_required
def add_bookmark(request, action_pk):
    action = Action.objects.get(pk=action_pk)
    # Now save the bookmark
    bookmark, created = Bookmark.objects.get_or_create(
        object_pk=action.action_object.pk,
        content_type=action.action_object_content_type,
        owner=request.user
    )
    # TODO: change messaging if object already bookmarked?
    messages.success(request, 'Your bookmark was saved!')
    # Now return a success message
    context = {
        'messages': render_to_string('bootstrap3/messages.html', {}, request=request),
        'form': render_to_string('bookmarks/_form.html', {'action': action}, request=request)
    }
    return JsonResponse(context)
