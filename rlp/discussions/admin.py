from django.contrib import admin
from .models import ThreadedComment

class ThreadedCommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user_name')
    list_filter = ('user_name',)

# Register your models here.
admin.site.register(ThreadedComment, ThreadedCommentAdmin)
