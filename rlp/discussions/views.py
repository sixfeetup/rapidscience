from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django import http
from django.shortcuts import get_object_or_404, redirect, render

from rlp.projects.models import Project
from .forms import ThreadedCommentEditForm, ThreadedCommentWithTitleEditForm
from .models import ThreadedComment
from .shortcuts import get_url_for_comment, get_comments_for_instance


@login_required
def post_redirect(request, content_type_id, object_id):
    """
    Redirect to an object's page based on a content-type ID and an object ID.
    """
    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        if not content_type.model_class():
            raise http.Http404("Content type %(ct_id)s object has no associated model".format(content_type_id))
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ObjectDoesNotExist, ValueError):
        raise http.Http404("Content type {} object {} doesn't exist".format(content_type_id, object_id))
    return redirect(get_url_for_comment(obj))


@login_required
def comment_detail(request, pk, slug, comment_pk, template_name='discussions/comment_detail.html'):
    project = get_object_or_404(Project, pk=pk, slug=slug)
    comment = get_object_or_404(ThreadedComment, pk=comment_pk)
    context = {
        'comment': comment,
        'comment_list': get_comments_for_instance(comment),
        'project': project,
        'tab': 'discussions',
    }
    return render(request, template_name, context)


@login_required
def comment_edit(request, pk, slug, comment_pk, template_name='discussions/comment_edit.html'):
    project = get_object_or_404(Project, pk=pk, slug=slug)
    comment = get_object_or_404(ThreadedComment, pk=comment_pk)
    if request.user != comment.user:
        messages.error(request, "You do not have permission to edit this.")
        return redirect(comment.get_absolute_url())
    # Allow editing of the title if this is a top-level 'topic' thread.
    if comment.content_type.model_class() == Project:
        form_class = ThreadedCommentWithTitleEditForm
    else:
        form_class = ThreadedCommentEditForm
    if request.method == 'POST':
        form = form_class(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment successfully updated!")
            return redirect(comment.get_absolute_url())
    else:
        form = form_class(instance=comment)
    context = {
        'comment': comment,
        'form': form,
        'project': project,
        'tab': 'discussions',
    }
    return render(request, template_name, context)


@login_required
def comment_delete(request, pk, slug, comment_pk, template_name='discussions/comment_delete.html'):
    project = get_object_or_404(Project, pk=pk, slug=slug)
    comment = get_object_or_404(ThreadedComment, pk=comment_pk)
    if request.user != comment.user:
        messages.error(request, "You do not have permission to delete this.")
        return redirect(comment.get_absolute_url())
    if request.method == 'POST':
        qs_to_delete = ThreadedComment.objects.filter(parent_id=comment.id)
        comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
        # This deletes the comment too, since parent_id == comment.id
        qs_to_delete.delete()
        while comment_children_ids:
            qs_to_delete = ThreadedComment.objects.filter(parent_id__in=comment_children_ids)
            comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
            qs_to_delete.delete()
        messages.success(request, "Comment successfully deleted!")
        return redirect(project.get_absolute_url())
    context = {
        'comment': comment,
        'project': project,
        'tab': 'discussions'
    }
    return render(request, template_name, context)
