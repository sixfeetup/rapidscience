from django.contrib import admin

from .models import Topic, Project, ProjectMembership, Role


class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('title',)}


class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'contact', 'order']
    list_editable = ['order']


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


admin.site.register(Topic, TopicAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Role, RoleAdmin)
