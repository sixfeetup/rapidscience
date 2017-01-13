from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.core.exceptions import ObjectDoesNotExist

from actstream.models import Action

from .forms import BookmarkForm, BookmarkFolderForm, UpdateBookmarkForm
from .models import Bookmark, Folder


@login_required
def add_bookmark(request, action_pk):
    context = dict()
    bookmarks = request.user.bookmark_set.filter(folder__isnull=True)
    bookmarks_folders = request.user.folder_set.all()

    action = Action.objects.get(pk=action_pk)
    if request.method == 'POST':
        form = BookmarkForm(request.POST)
        context['form'] = render_to_string(
            'bookmarks/_add_bookmark_form.html',
            {
                'action': action,
                'form': form,
                'bookmarks_folders': bookmarks_folders,
                'bookmarks': bookmarks,
            },
            request=request)
        if form.is_valid():
            # Now save the bookmark
            bookmark, created = Bookmark.objects.get_or_create(
                object_pk=action.action_object.pk,
                content_type=action.action_object_content_type,
                owner=request.user
            )
            bookmark.name = form.cleaned_data['name']
            bookmark.folder = form.cleaned_data['folder']
            bookmark.save()
            # TODO: change messaging if object already bookmarked?
            messages.success(request, 'Your bookmark was saved!')
            # Now return a success message
            context['messages'] = render_to_string('bootstrap3/messages.html', {}, request=request)
    else:
        form = BookmarkForm(initial={
            'object_pk': action.action_object.pk,
            'content_type': action.action_object_content_type,
        })
        context['form'] = render_to_string(
            'bookmarks/_add_bookmark_form.html',
            {
                'form': form,
                'bookmarks_folders': bookmarks_folders,
                'bookmarks': bookmarks,
            },
            request=request
        )
    return JsonResponse(context)


@login_required
def update_bookmark(request, bookmark_pk):
    context = dict()
    if request.method == 'POST':
        form = UpdateBookmarkForm(request.POST)
        if form.is_valid():
            try:
                bookmark = Bookmark.objects.get(pk=bookmark_pk)
                bookmark.name = form.cleaned_data['name']
                bookmark.folder = form.cleaned_data['folder']
                bookmark.save()
                context['error'] = False
                messages.success(request, 'Your bookmark was saved!')
            except ObjectDoesNotExist:
                context['error'] = True
                messages.error(request, 'Bookmark does not exists')
        else:
            context['error'] = True
            messages.error(request, 'Error occured.')

    context['messages'] = render_to_string('bootstrap3/messages.html', {}, request=request)
    return JsonResponse(context)


@login_required
def delete_bookmark(request, bookmark_pk):
    if request.method == 'POST':
        context = {}
        Bookmark.objects.filter(pk=bookmark_pk).delete()
        context['error'] = False
        messages.success(request, 'Bookmark deleted.')

        context['messages'] = render_to_string('bootstrap3/messages.html', {}, request=request)
        return JsonResponse(context)


@login_required
def add_bookmark_folder(request):
    if request.method == 'POST':
        form = BookmarkFolderForm(request.POST)
        context = {}
        if form.is_valid():
            folder_name = form.cleaned_data['name']
            folder = Folder(name=folder_name, user=request.user)
            try:
                folder.save()
                context['error'] = False
                context['folder_id'] = folder.pk
                context['folder_name'] = folder.name
                messages.success(request, 'Folder added.')
            except IntegrityError:
                context['error'] = True
                messages.error(request, 'Folder with the name {0} already exists'.format(folder_name))
        else:
            context['error'] = True
            messages.error(request, 'Error occured.')

        context['messages'] = render_to_string('bootstrap3/messages.html', {}, request=request)
        return JsonResponse(context)


@login_required
def delete_bookmark_folder(request, folder_pk):
    if request.method == 'POST':
        context = {}
        try:
            Folder.objects.filter(pk=folder_pk).delete()
            context['error'] = False
            messages.success(request, 'Bookmarks folder deleted.')
        except ProtectedError:
            context['error'] = True
            messages.error(request, 'The folder contains bookmarks.')

        context['messages'] = render_to_string('bootstrap3/messages.html', {}, request=request)
        return JsonResponse(context)
