from django.contrib import admin

from actstream import action
from embed_video.admin import AdminVideoMixin

from .models import File, Image, Link, Video


class FileAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            action.send(obj.owner, verb='uploaded', action_object=obj, target=obj.project)


class ImageAdmin(admin.ModelAdmin):
    exclude = ['height', 'width']

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            action.send(obj.owner, verb='uploaded', action_object=obj, target=obj.project)


class LinkAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            action.send(obj.owner, verb='added', action_object=obj, target=obj.project)


class VideoAdmin(AdminVideoMixin, admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            action.send(obj.owner, verb='added', action_object=obj, target=obj.project)


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Video, VideoAdmin)
