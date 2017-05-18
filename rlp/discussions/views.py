from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import never_cache
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django import http
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import FormView

from rlp.accounts.models import User
from rlp.core.forms import member_choices, group_choices
from rlp.core.utils import bookmark_and_notify
from rlp.projects.models import Project
from .forms import (
    ThreadedCommentEditForm,
    ThreadedCommentWithTitleEditForm,
    NewDiscussionForm
)
from .models import ThreadedComment
from .shortcuts import get_url_for_comment


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
@never_cache   # hamfisted.
def comment_detail(request, comment_pk, template_name='discussions/comment_detail.html'):
    """ Comment detail page.
        If the comment can be traced back to a project, then the user must be an active member of the group
        in order to turn on the ability to comment.
    """
    comment = get_object_or_404(ThreadedComment, pk=comment_pk)

    user_can_comment = comment.is_shared_with_user(request.user)

    last_viewed_path = request.session.get('last_viewed_path')
    context = {
        'comment': comment,
        'comment_list': comment.children(),
        'tab': 'discussions',
        'user_interaction': user_can_comment,
        'expand_comments': True,
        'last_viewed_path': last_viewed_path,
    }
    return render(request, template_name, context)


@login_required
def comment_edit(request, comment_pk, template_name='discussions/comment_edit.html'):
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
        'tab': 'discussions',
    }
    return render(request, template_name, context)


@login_required
def comment_delete(request, comment_pk, template_name='discussions/comment_delete.html'):
    comment = get_object_or_404(ThreadedComment, pk=comment_pk)
    if request.user != comment.user:
        messages.error(request, "You do not have permission to delete this.")
        return redirect(comment.get_absolute_url())
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment successfully deleted!")
        # TODO: invalidate the cache on the comment_detail page
        return redirect(reverse('dashboard'))
    context = {
        'comment': comment,
        'tab': 'discussions'
    }
    return render(request, template_name, context)


def comment_done(request, *args, **kwargs):
    comment_pk = request.GET.get('c')
    comment = ThreadedComment.objects.get(id=comment_pk)
    top_comment = comment.discussion_root
    if top_comment.is_discussion:
        # redirect to the top-level of this thread
        url = reverse(
            'comments-detail',
            kwargs={'comment_pk': top_comment.id},
        )
    else:
        url = top_comment.content_object.get_absolute_url()
    return redirect(url)


class CreateDiscussion(LoginRequiredMixin, FormView):
    form_class = NewDiscussionForm
    success_url = '/'
    template_name = 'discussions/discussion_create.html'

    def get_form(self, form_class):
        form = super(CreateDiscussion, self).get_form(form_class)
        try:
            group = Project.objects.get(id=self.request.GET.get('id'))
        except Project.DoesNotExist:
            group = []
        user = self.request.user
        members = ((member.id, member.get_full_name()) for member in User.objects.all())
        if group and group.approval_required:
            form.fields['members'].hide_field = True
            form.fields['members'].choices = [(user.id, user.get_full_name())]
            form.fields['groups'].choices = [(group.id, group.title)]
            form.fields['groups'].initial = [group.id]
            form.fields['members'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['groups'].widget.attrs['class'] = 'select2 hiddenField'
        else:
            form.fields['members'].choices = members
            form.fields['groups'].choices = group_choices(user)
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, "Please correct the errors below")
            return self.form_invalid(form)

    def form_valid(self, form):
        data = form.cleaned_data
        user = self.request.user
        ct = ContentType.objects.get_for_model(Site)
        site = Site.objects.get_current()
        new_discussion = ThreadedComment(
            title=data['discussion_title'],
            user=user,
            user_name=user.get_full_name(),
            user_email=user.email,
            comment=data['discussion_body'],
            content_type=ct,
            site_id=site.id,
            object_pk=site.id,
        )
        new_discussion.save()

        discussion_url = new_discussion.get_absolute_url()
        bookmark_and_notify(
            new_discussion, self, self.request,
            'discussions', 'threadedcomment',
        )
        return redirect(discussion_url)