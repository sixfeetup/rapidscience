from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache

from actstream import action
from taggit.models import Tag

from rlp.discussions.models import ThreadedComment
from . import choices
from .forms import SearchForm, BookForm, BookSectionForm, JournalArticleForm, ProjectReferenceForm, ReferenceShareForm
from .models import Reference, ProjectReference
from rlp.core.email import send_transactional_mail


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
    return render(request, template_name, context)


@never_cache
@login_required
def add_book(request, reference_pk=None, template_name='bibliography/add_book.html'):
    if reference_pk:
        instance = get_object_or_404(Reference, pk=reference_pk)
        project_reference = ProjectReference.objects.get(
            reference=instance,
            owner=request.user
        )
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tag_ids = POST.pop('tags', [])
        form = BookForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    project_reference = ProjectReference.objects.create(
                        reference=reference, owner=request.user)
                    action.send(request.user, verb='added', action_object=project_reference)
                    messages.success(request, "Reference added successfully!")
                # Set the tags
                if tag_ids:
                    try:
                        tags = Tag.objects.filter(id__in=tag_ids)
                    except:
                        tags = []
                    project_reference.tags.set(*tags)
                    # Trigger any post-save signals (e.g. Haystack's real-time indexing)
                    project_reference.save()
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            data['tags'] = project_reference.tags.all()
            form = BookForm(initial=data)
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
        project_reference = ProjectReference.objects.get(
            reference=instance,
            owner=request.user
        )
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tag_ids = POST.pop('tags', [])
        form = BookSectionForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    project_reference = ProjectReference.objects.create(
                        reference=reference, owner=request.user)
                    action.send(request.user, verb='added', action_object=project_reference)
                    messages.success(request, "Reference added successfully!")
                # Set the tags
                if tag_ids:
                    try:
                        tags = Tag.objects.filter(id__in=tag_ids)
                    except:
                        tags = []
                    project_reference.tags.set(*tags)
                    # Trigger any post-save signals (e.g. Haystack's real-time indexing)
                    project_reference.save()
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            data['tags'] = project_reference.tags.all()
            form = BookSectionForm(initial=data)
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
        project_reference = ProjectReference.objects.get(
            reference=instance,
            owner=request.user
        )
    else:
        instance = None
    if request.method == 'POST':
        # Make a copy so we can manipulate
        POST = request.POST.copy()
        # Remove tags, if present
        tag_ids = POST.pop('tags', [])
        form = JournalArticleForm(POST, request.FILES, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                reference = form.save()
                if reference_pk:
                    messages.success(request, "Reference updated successfully!")
                else:
                    project_reference = ProjectReference.objects.create(
                        reference=reference, owner=request.user)
                    action.send(request.user, verb='added', action_object=project_reference)
                    messages.success(request, "Reference added successfully!")
                # Set the tags
                if tag_ids:
                    try:
                        tags = Tag.objects.filter(id__in=tag_ids)
                    except:
                        tags = []
                    project_reference.tags.set(*tags)
                    # Trigger any post-save signals (e.g. Haystack's real-time indexing)
                    project_reference.save()
            # TODO redirect to ?
            return redirect('/')
    else:
        if instance:
            data = instance.raw_data.copy()
            if instance.upload:
                data['upload'] = instance.upload
            data['tags'] = project_reference.tags.all()
            data['publication_date'] = datetime.strptime(data['publication_date'], '%d %b %Y')
            form = JournalArticleForm(initial=data)
        else:
            form = JournalArticleForm()
    context = {
        'form': form,
        'instance': instance,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@never_cache
@login_required
def reference_add(request, reference_pk, edit=False):
    reference = get_object_or_404(Reference, pk=reference_pk)
    with transaction.atomic():
        project_reference, created = ProjectReference.objects.get_or_create(
            reference=reference, defaults={'owner': request.user}
        )
        if created:
            action.send(request.user, verb='added', action_object=project_reference)
            messages.success(request, 'Reference added successfully!')
        else:
            messages.info(request, "The reference you selected was already added to this project by {}.".format(
                project_reference.owner.get_full_name()))
        if request.is_ajax():
            context = {
                'messages': render_to_string('bootstrap3/messages.html', {}, request=request),
            }
            return JsonResponse(context)
    # TODO redirect to ?
    return redirect('/')


@never_cache
@login_required
def reference_edit(request, reference_pk, template_name='bibliography/edit_reference.html'):
    reference = get_object_or_404(Reference, pk=reference_pk)
    # For manually added references, show the custom forms for each type
    if 'reference_type' in reference.raw_data:
        if reference.raw_data['reference_type'] == choices.JOURNAL_ARTICLE:
            return add_article(request, reference_pk)
        elif reference.raw_data['reference_type'] == choices.BOOK:
            return add_book(request, reference_pk)
        elif reference.raw_data['reference_type'] == choices.BOOK_SECTION:
            return add_book_chapter(request, reference_pk)
    # The rest of this view is for adding tags to references coming from Pubmed or Crossref
    project_reference = ProjectReference.objects.get(reference=reference)
    # Need to edit the 'project reference', that's what should get the tags right?
    if request.method == 'POST':
        form = ProjectReferenceForm(request.POST, instance=project_reference)
        if form.is_valid():
            tags = form.cleaned_data.get('tags') or []
            project_reference.tags.set(*tags)
            # Trigger any post-save signals (e.g. Haystack's real-time indexing)
            project_reference.save()
            messages.success(request, "Reference updated successfully!")
            # TODO redirect to ?
            return redirect('/')
    else:
        form = ProjectReferenceForm(instance=project_reference, initial={'tags': project_reference.tags.all()})
    # It shouldn't be possible to land on the edit page if there aren't any tags, but just in case, remove the form
    if not Tag.objects.count():
        form = None
    context = {
        'form': form,
        'instance': project_reference,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@login_required
def reference_share(request, reference_pk):
    project_reference = get_object_or_404(ProjectReference, pk=reference_pk)
    if request.method == 'POST':
        form = ReferenceShareForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.user = request.user
            share.reference = project_reference.reference
            share.save()
            form.save_m2m()
            # Collect the recipients using a set() so we don't send duplicate messages (as a share.recipient and as a
            # project member).
            recipients = set(share.recipients.all())
            if share.group:
                # put it in the project's timeline
                action.send(request.user, verb='shared', action_object=share, target=share.group)
            # Only email individuals who were specifically selected
            for user in recipients:
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
def reference_delete(request, reference_pk, template_name='bibliography/reference_delete.html'):
    project_reference = get_object_or_404(
        ProjectReference, reference__id=reference_pk, owner=request.user)
    if request.POST:
        title = project_reference.reference.title
        ctype = ContentType.objects.get_for_model(project_reference.__class__)
        comment_ctype = ContentType.objects.get_for_model(ThreadedComment)
        with transaction.atomic():
            # Recursively find all comments and replies for this project_reference and delete them.
            # TODO: turn this into a model manager method
            qs_to_delete = ThreadedComment.objects.filter(object_pk=project_reference.id, content_type=ctype)
            comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
            qs_to_delete.delete()
            while comment_children_ids:
                qs_to_delete = ThreadedComment.objects.filter(
                    content_type=comment_ctype, parent_id__in=comment_children_ids)
                comment_children_ids = list(qs_to_delete.values_list('id', flat=True))
                qs_to_delete.delete()
            project_reference.delete()
        messages.success(request, "Successfully deleted '{}'".format(title))
        # TODO redirect to ?
        return redirect('/')
    context = {
        'obj': project_reference,
        'tab': 'bibliography',
    }
    return render(request, template_name, context)


@never_cache
@login_required
def reference_detail(request, reference_pk, template_name='bibliography/reference_detail.html'):
    project_reference = get_object_or_404(ProjectReference, reference__id=reference_pk)
    context = {
        'obj': project_reference,
        'tab': 'bibliography',
        'comment_list': project_reference.discussions.all(),
    }
    return render(request, template_name, context)
