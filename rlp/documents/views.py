from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render, Http404
from django.views.decorators.cache import never_cache
from django.views.generic.edit import FormView

from actstream import action
from PIL import Image
from taggit.models import Tag

from rlp.accounts.models import User
from rlp.core.email import activity_mail
from rlp.core.forms import group_choices
from rlp.core.utils import bookmark_and_notify, add_tags, fill_tags
from rlp.discussions.models import ThreadedComment
from rlp.projects.models import Project
from .forms import AddMediaForm, FileForm, ImageForm, LinkForm, VideoForm
from .models import Document


class AddMedia(LoginRequiredMixin, FormView):
    form_class = AddMediaForm
    template_name = 'documents/add_media.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(AddMedia, self).get_context_data(**kwargs)
        initial_proj = self.request.session.get('last_viewed_project')
        if initial_proj and initial_proj != -1:
            context['origin'] = Project.objects.get(pk=initial_proj)
        else:
            context['origin'] = self.request.user
        return context


    def get_form(self, form_class):
        form = super(AddMedia, self).get_form(form_class)
        try:
            group = Project.objects.get(id=self.request.session.get('last_viewed_project'))
        except Project.DoesNotExist:
            group = []
        user = self.request.user
        all_members = ((member.id, member.get_full_name()) for member in User.objects.all())
        if group and group.approval_required:
            form.fields['members'].hide_field = True
            form.fields['members'].choices = [(user.id, user.get_full_name())]
            form.fields['members'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['groups'].widget.attrs['class'] = 'select2 hiddenField'
        elif group:
            form.fields['members'].choices = all_members
            form.fields['groups'].choices = group_choices(user, exclude=[group])
        else:
            form.fields['members'].choices = all_members
            form.fields['groups'].choices = group_choices(user)
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        data = request.POST.copy()
        filetype = data.get('filetype')
        if filetype == 'file':
            if 'upload' not in self.request.FILES.keys():
                messages.error(request, "Please upload a file")
                return self.form_invalid(form)
        elif filetype == 'link':
            if not data['url']:
                messages.error(request, "Please add a link")
                return self.form_invalid(form)
        elif filetype == 'video':
            if not data['share_link']:
                messages.error(request, "Please add a video link")
                return self.form_invalid(form)
        if form.is_valid():
            return self.form_valid(request, filetype)
        else:
            messages.error(request, "Please correct the errors below")
            return self.form_invalid(form)

    def form_valid(self, request, filetype):
        form = self.get_form()
        if filetype == 'file':
            return add_document(request, form)
        elif filetype == 'link':
            return add_link(request, form)
        elif filetype == 'video':
            return add_video(request, form)
        return render(request, 'documents/add_media.html')


@never_cache
@login_required
def add_document(request, add_form=None, doc_pk=None, template_name='documents/add_document.html', ):
    """ accept a new file upload """
    if doc_pk:
        document = get_object_or_404(Document, pk=doc_pk)
    else:
        document = None

    form_class = FileForm
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        if 'upload' in request.FILES:
            try:
                Image.open(request.FILES['upload'])
                request.FILES['upload'].seek(0)
                form_class = ImageForm
            except IOError:
                pass
        if request.FILES:
            form = form_class(POST, request.FILES, instance=document)
        else:
            form = form_class(POST, instance=document)
        if form.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                document.owner = request.user
                initial_proj = request.session.get('last_viewed_project')
                if not doc_pk:
                    if initial_proj and initial_proj != -1:
                        document.origin = Project.objects.get(pk=initial_proj)
                    else:
                        document.origin = request.user
                document.save()
                add_tags(document, tags)
                if doc_pk:
                    message = "Updated successfully!"
                else:
                    new_action = action.send(
                        request.user,
                        verb='uploaded',
                        action_object=document,
                    )
                    message = "Your upload was successful!"
                    # Send email notification
                    if initial_proj and initial_proj != -1:
                        target = Project.objects.get(pk=initial_proj)
                        # activity_mail(request.user, document, target, request)
                        if target.approval_required:
                            document.shareable = False
                            document.save()
                messages.success(request, message)
                if add_form:
                    bookmark_and_notify(
                        document, add_form, request,
                        'documents', 'document',
                    )
            return redirect(document.get_absolute_url())
        else:
            messages.error(request, "Check the errors below.")

    else:
        initial = {}
        form = form_class(instance=document, initial=initial)
        fill_tags( document, form)
    context = {
        'form': form,
        'document': document,
        'tab': 'documents',
    }
    if doc_pk:
        context['origin'] = document.origin
    else:
        initial_proj = request.session.get('last_viewed_project')
        if initial_proj and initial_proj != -1:
            context['origin'] = Project.objects.get(pk=initial_proj)
        else:
            context['origin'] = request.user
    return render(request, template_name, context)


@never_cache
@login_required
def add_link(request, add_form=None, doc_pk=None, template_name='documents/add_link.html'):
    if doc_pk:
        document = get_object_or_404(Document, pk=doc_pk)
    else:
        document = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        form = LinkForm(POST, instance=document)
        if form.is_valid():
            with transaction.atomic():
                link = form.save(commit=False)
                link.owner = request.user
                initial_proj = request.session.get('last_viewed_project')
                if not doc_pk:
                    if initial_proj and initial_proj != -1:
                        link.origin = Project.objects.get(pk=initial_proj)
                    else:
                        link.origin = request.user
                link.save()
                add_tags(link, tags)
                if doc_pk:
                    message = "Updated successfully!"
                else:
                    new_action = action.send(
                        request.user,
                        verb='added',
                        action_object=link,
                    )
                    message = "Your link was successfully added!"
                    # Send email notification
                    if initial_proj and initial_proj != -1:
                        target = Project.objects.get(pk=initial_proj)
                        # this email goes to everyone in the group, which
                        # is also done when bookmark_and_notify is called
                        # below
                        # activity_mail(request.user, link, target, request)
                        if target.approval_required:
                            link.shareable = False
                            link.save()
                messages.success(request, message)
                if add_form:
                    bookmark_and_notify(
                        link, add_form, request,
                        'documents', 'link',
                    )
            return redirect(link.get_absolute_url())
        else:
            messages.error(request, "Check the errors below.")
    else:
        initial = {}
        form = LinkForm(instance=document, initial=initial)
        fill_tags(document, form)
    context = {
        'form': form,
        'document': document,
        'tab': 'documents',
    }
    if doc_pk:
        context['origin'] = document.origin
    else:
        initial_proj = request.session.get('last_viewed_project')
        if initial_proj and initial_proj != -1:
            context['origin'] = Project.objects.get(pk=initial_proj)
        else:
            context['origin'] = request.user
    return render(request, template_name, context)


@never_cache
@login_required
def add_video(request, add_form=None, doc_pk=None, template_name='documents/add_video.html'):
    if doc_pk:
        document = get_object_or_404(Document, pk=doc_pk)
    else:
        document = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        form = VideoForm(POST, instance=document)
        if form.is_valid():
            with transaction.atomic():
                video = form.save(commit=False)
                video.owner = request.user
                initial_proj = request.session.get('last_viewed_project')
                if not doc_pk:
                    if initial_proj and initial_proj != -1:
                        video.origin = Project.objects.get(pk=initial_proj)
                    else:
                        video.origin = request.user
                video.save()
                add_tags(video, tags)
                if doc_pk:
                    message = "Updated successfully!"
                else:
                    new_action = action.send(
                        request.user,
                        verb='added',
                        action_object=video,
                    )
                    message = "Your video was successfully added!"
                    # Send email notification
                    if initial_proj and initial_proj != -1:
                        target = Project.objects.get(pk=initial_proj)
                        #activity_mail(request.user, video, target, request)
                        if target.approval_required:
                            video.shareable = False
                            video.save()
                messages.success(request, message)
                if add_form:
                    bookmark_and_notify(
                        video, add_form, request,
                        'documents', 'video',
                    )
            return redirect(video.get_absolute_url())
        else:
            messages.error(request, "Check the errors below.")
    else:
        initial = {}
        form = VideoForm(instance=document, initial=initial)
        fill_tags(document, form)
    context = {
        'form': form,
        'document': document,
        'tab': 'documents',
    }
    if doc_pk:
        context['origin'] = document.origin
    else:
        initial_proj = request.session.get('last_viewed_project')
        if initial_proj and initial_proj != -1:
            context['origin'] = Project.objects.get(pk=initial_proj)
        else:
            context['origin'] = request.user
    return render(request, template_name, context)


@never_cache
@login_required
def document_detail(request, doc_pk, template_name='documents/document_detail.html'):
    document = get_object_or_404(Document, pk=doc_pk)
    last_viewed_path = request.session.get('last_viewed_path')
    user_can_comment = document.is_shared_with_user(request.user) or request.user == document.owner
    context = {
        'document': document,
        'tab': 'documents',
        'comment_list': document.discussions.all(),
        'last_viewed_path': last_viewed_path,
        'user_interaction': user_can_comment,
        'expand_comments': True,
    }
    return render(request, template_name, context)


@never_cache
@login_required
def document_edit(request, doc_pk):
    document = get_object_or_404(Document, pk=doc_pk)
    display_type = document.display_type.lower()
    if 'link' in display_type:
        return add_link(request, doc_pk=doc_pk)
    elif 'video' in display_type:
        return add_video(request, doc_pk=doc_pk)
    else:
        return add_document(request, doc_pk=doc_pk)


@never_cache
@login_required
def document_delete(request, doc_pk, template_name='documents/delete.html'):
    document = get_object_or_404(Document, pk=doc_pk)
    if request.user != document.owner:
        messages.error(request, "You do not have permission to delete this.")
        return redirect(document.get_absolute_url())
    if request.method == 'POST':
        title = document.title
        ctype = ContentType.objects.get_for_model(document.__class__)
        comment_ctype = ContentType.objects.get_for_model(ThreadedComment)
        with transaction.atomic():
            # Recursively find all comments and replies for this document and delete them.
            # TODO: turn this into a model manager method
            qs_to_delete = ThreadedComment.objects.filter(object_pk=document.id, content_type=ctype)
            comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
            qs_to_delete.delete()
            while comment_children_ids:
                qs_to_delete = ThreadedComment.objects.filter(
                    content_type=comment_ctype, parent_id__in=comment_children_ids)
                comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
                qs_to_delete.delete()
            document.delete()
        messages.success(request, "Successfully deleted '{}'".format(title))
        return redirect(reverse('dashboard'))
    context = {
        'document': document,
        'tab': 'documents',
    }
    return render(request, template_name, context)
