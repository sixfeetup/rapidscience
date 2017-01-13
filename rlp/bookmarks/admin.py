from django.contrib import admin
from .models import Folder, Bookmark


class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner',  'folder', 'content_type', 'object_pk')


class BookmarkInline(admin.TabularInline):
    model = Bookmark
    fk_name = "folder"


class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    inlines = [BookmarkInline, ]


admin.site.register(Folder, FolderAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
