from django.contrib import admin

from .models import Topic, Project, ProjectMembership


class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('title',)}


class ProjectMembershipAdmin(admin.TabularInline):
    model = ProjectMembership
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMembershipAdmin]
    list_display = ['title', 'order', 'topic', 'institution']
    list_editable = ['order']
    list_filter = ['topic', 'institution']
    search_fields = ['title', 'topic__title', 'institution__name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ ProjectMembershipAdmin, ]


admin.site.register(Topic, TopicAdmin)
admin.site.register(Project, ProjectAdmin)
