from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.generic.edit import FormView

from actstream import action

from rlp.core.forms import member_choices, group_choices
from rlp.core.utils import bookmark_and_notify, add_tags, fill_tags, resolve_email_targets
from rlp.discussions.models import ThreadedComment
from rlp.projects.models import Project
from . import choices
from .forms import (
    AttachReferenceForm,
    BookForm,
    BookSectionForm,
    JournalArticleForm,
    ReferenceShareForm,
    SearchForm,
)
from .models import Reference, UserReference
from rlp.core.email import send_transactional_mail, activity_mail


@never_cache
@login_required
def reference_search(request, template_name='bibliography/reference_search.html'):
    results = None
    query = request.GET.get('q', '')
    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            results = form.results
        if not results:
            messages.warning(request, "No results found for {}".format(query))
    else:
        form = SearchForm()

    context = {
        'form': form,
        'tab': 'bibliography',
        'results': results,
        'query': query
    }
    initial_proj = request.session.get('last_viewed_project')
    if initial_proj and initial_proj != -1:
        context['origin'] = Project.objects.get(pk=initial_proj)
    else:
        context['origin'] = request.user
    return render(request, template_name, context)


@never_cache
@login_required
def add_book(request, reference_pk=None, template_name='bibliography/add_book.html'):
    if reference_pk:
        instance = get_object_or_404(Reference, pk=reference_pk)
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        form = BookForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    action.send(request.user, verb='added', action_object=reference)
                    messages.success(request, "Reference added successfully!")
                add_tags(reference, tags)
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            form = BookForm(initial=data)
            fill_tags(instance, form)
        else:
            form = BookForm()
    context = {
        'form': form,
        'instance': instance,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@never_cache
@login_required
def add_book_chapter(request, reference_pk=None, template_name='bibliography/add_book_chapter.html'):
    if reference_pk:
        instance = get_object_or_404(Reference, pk=reference_pk)
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        form = BookSectionForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    action.send(request.user, verb='added', action_object=reference)
                    messages.success(request, "Reference added successfully!")
                # Set the tags
                add_tags(reference, tags)
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            form = BookSectionForm(initial=data)
            fill_tags(instance, form)
        else:
            form = BookSectionForm()
    context = {
        'form': form,
        'instance': instance,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@never_cache
@login_required
def add_article(request, reference_pk=None, template_name='bibliography/add_article.html'):
    if reference_pk:
        instance = get_object_or_404(Reference, pk=reference_pk)
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tags = {}
        tags['ids'] = POST.pop('tags', [])
        tags['new'] = POST.pop('new_tags', [])
        form = JournalArticleForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    action.send(request.user, verb='added', action_object=reference)
                    messages.success(request, "Reference added successfully!")
                add_tags(reference, tags)
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            data['publication_date'] = datetime.strptime(data['publication_date'], '%d %b %Y')
            form = JournalArticleForm(initial=data)
            fill_tags(instance, form)
        else:
            form = JournalArticleForm()
    context = {
        'form': form,
        'instance': instance,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


class ReferenceAttachView(LoginRequiredMixin, FormView):
    template_name = 'bibliography/edit_reference.html'
    form_class = AttachReferenceForm

    def get_context_data(self, **kwargs):
        context = super(ReferenceAttachView, self).get_context_data(**kwargs)
        user = self.request.user
        uref_id = self.kwargs.get('uref_id',None)
        reference_id = self.kwargs['reference_pk']

        ref = Reference.objects.get(pk=reference_id)

        if uref_id:
            uref = UserReference.objects.get(id=uref_id)
            context['origin'] = uref.origin
        else:
            uref = UserReference(reference=ref, user=user)
            uref.id = -1 # fake, so that the tag lookup in the templates doesnt fail.


        context['reference'] = ref
        context['user_reference'] = uref
        if self.request.method == 'GET':
            try:
                group = Project.objects.get(id=self.request.session.get('last_viewed_project'))
            except Project.DoesNotExist:
                group = []
            # populate initial data
            form = AttachReferenceForm()
            form.fields['description'].initial = uref.description
            if group and group.approval_required:
                form.fields['members'].hide_field = True
                form.fields['members'].choices = [(user.id, user.get_full_name())]
                form.fields['members'].widget.attrs['class'] = 'select2 hiddenField'
                form.fields['groups'].widget.attrs['class'] = 'select2 hiddenField'
            elif group:
                form.fields['members'].choices = member_choices()
                form.fields['groups'].choices = group_choices(self.request.user, exclude=[group])
            else:
                form.fields['members'].choices = member_choices()
                form.fields['groups'].choices = group_choices(self.request.user)
            fill_tags(uref, form)
            context['form'] = form
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        user = self.request.user
        ref = Reference.objects.get(pk=self.kwargs['reference_pk'])
        uref_id = self.kwargs.get('uref_id',None)

        initial_proj = self.request.session.get('last_viewed_project')
        if initial_proj and initial_proj != -1:
            target = Project.objects.get(pk=initial_proj)

        if uref_id:
            uref = UserReference.objects.get(id=uref_id, reference=ref, user=user)
        else:
            uref = UserReference(reference=ref, user=user)
            uref.id = None
            if initial_proj and initial_proj != -1:
                uref.origin = target
            else:
                uref.origin = user

        uref.description = data.get('description')
        if initial_proj and initial_proj != -1 and target.approval_required:
            uref.shareable = False
        uref.save()

        tags = {}
        tags['ids'] = data.pop('tags', [])
        tags['new'] = [data.pop('new_tags')] if data['new_tags'] else []
        add_tags(uref, tags)
        target = bookmark_and_notify(
            uref, self, self.request, 'bibliography', 'userreference',
        )
        if not target:
            target = user
        action.send(
            user,
            verb='added',
            action_object=uref,
            target=target,
        )
        activity_mail(user, uref, target, self.request)
        last_viewed_path = self.request.session.get('last_viewed_path', '/')
        return redirect(last_viewed_path)


# @never_cache
# @login_required
# def reference_edit(request, reference_pk, template_name='bibliography/edit_reference.html'):
#     reference = get_object_or_404(Reference, pk=reference_pk)
#     # For manually added references, show the custom forms for each type
#     if 'reference_type' in reference.raw_data:
#         if reference.raw_data['reference_type'] == choices.JOURNAL_ARTICLE:
#             return add_article(request, reference_pk)
#         elif reference.raw_data['reference_type'] == choices.BOOK:
#             return add_book(request, reference_pk)
#         elif reference.raw_data['reference_type'] == choices.BOOK_SECTION:
#             return add_book_chapter(request, reference_pk)
#     # The rest of this view is for adding tags to references coming from Pubmed or Crossref
#     if request.method == 'POST':
#         form = AttachReferenceForm(request.POST)
#         if form.is_valid():
#             tags = {}
#             tags['ids'] = form.cleaned_data.getlist('tags', [])
#             tags['new'] = form.cleaned_data.getlist('new_tags', [])
#             add_tags(reference, tags)
#             messages.success(request, "Reference updated successfully!")
#             # TODO redirect to ?
#             # should go to accounts/dashboard/bibliography/
#             # or /groups/<group slug>/bibliography/
#             return redirect('/')
#     else:
#         form = AttachReferenceForm()
#         form.fields['description'].initial = reference.description
#         form.fields['members'].choices = member_choices()
#         form.fields['groups'].choices = group_choices(request.user)
#         fill_tags(reference, form)
#     context = {
#         'form': form,
#         'instance': reference,
#         'tab': 'bibliography',
#     }
#     return render(request, template_name, context)
#

@login_required
def reference_share(request, reference_pk):
    reference = get_object_or_404(Reference, pk=reference_pk)
    if request.method == 'POST':
        form = ReferenceShareForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.user = request.user
            share.reference = reference
            share.save()
            form.save_m2m()
            # Collect the recipients using a set() so we don't send duplicate messages (as a share.recipient and as a
            # project member).
            recipients = set(share.recipients.all())
            if share.group:
                # put it in the project's timeline
                action.send(request.user, verb='shared', action_object=share, target=share.group)
            # Only email individuals who were specifically selected
            for user in resolve_email_targets(recipients, reason='share'):
                if user.notify_immediately:
                    send_transactional_mail(
                        user.email,
                        'A reference has been shared with you',
                        'emails/shared_reference_notification', {
                            'share': share,
                        }
                    )

            messages.success(request, 'This reference was successfully shared!')
            context = {
                'messages': render_to_string('bootstrap3/messages.html', {}, request=request),
                'form': render_to_string(
                    'bibliography/_share_reference_form.html',
                    {'form': ReferenceShareForm()},
                    request=request
                ),
            }
        else:
            context = {
                'form': render_to_string('bibliography/_share_reference_form.html', {'form': form}, request=request),
            }
    else:
        context = {
            'form': render_to_string(
                'bibliography/_share_reference_form.html',
                {'form': ReferenceShareForm()},
                request=request
            ),
        }
    return JsonResponse(context)


@never_cache
@login_required
def reference_delete(request, reference_pk, uref_id, template_name='bibliography/reference_delete.html'):
    reference = get_object_or_404(Reference, pk=reference_pk)
    user = request.user
    user_reference = UserReference.objects.get(id=uref_id, user=user, reference=reference)

    if request.POST:
        title = reference.title
        ctype = ContentType.objects.get_for_model(Reference)
        comment_ctype = ContentType.objects.get_for_model(ThreadedComment)
        with transaction.atomic():
            # Recursively find all comments and replies for this reference and delete them.
            # TODO: turn this into a model manager method
            qs_to_delete = ThreadedComment.objects.filter(object_pk=user_reference.id, content_type=ctype)
            comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
            qs_to_delete.delete()
            while comment_children_ids:
                qs_to_delete = ThreadedComment.objects.filter(
                    content_type=comment_ctype, parent_id__in=comment_children_ids)
                comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
                qs_to_delete.delete()
            user_reference.delete()
        messages.success(request, "Successfully deleted '{}'".format(title))
        # TODO redirect to ?
        return redirect('/')
    context = {
        'obj': reference,
        'user_reference': user_reference,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@never_cache
@login_required
def reference_detail(request, reference_pk, uref_id, template_name='bibliography/reference_detail.html'):
    reference = get_object_or_404(Reference, pk=reference_pk)
    try:
        user_reference = UserReference.objects.get(id=uref_id, reference_id=reference_pk)
    except UserReference.DoesNotExist as dne:
        user_reference = UserReference()
        user_reference.id = 0
    user_can_comment = user_reference.is_shared_with_user(request.user) or request.user == UserReference.user
    context = {
        'obj': reference,
        'user_reference': user_reference,
        'tab': 'bibliography',
        'comment_list': user_reference.discussions.all(),
        'user_interaction': user_can_comment,
        'expand_comments': True,
    }
    return render(request, template_name, context)
