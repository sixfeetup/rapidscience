from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User, UserLogin, Institution, InstitutionDomain
from rlp.projects.models import ProjectMembership


class ProjectMembershipAdmin(admin.TabularInline):
    model = ProjectMembership
    extra = 1


class CustomUserAdmin(UserAdmin):
    actions = None
    fieldsets = (
        (None, {
            'fields': (
                'first_name', 'last_name', 'email', 'password'
            )
        }),
        (_('Profile'), {
            'fields': (
                'title', 'degrees', 'bio', 'research_interests', 'website', 'orcid', 'photo', 'institution',
                'linkedin', 'twitter',),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions'),
                            'classes': ('collapse',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined'),
                                'classes': ('collapse',)}),
    )
    inlines = [
        ProjectMembershipAdmin
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'institution', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ['date_joined', 'last_login']
    search_fields = (
        'email', 'first_name', 'last_name',
    )
    ordering = ('email',)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        if not request.user.is_superuser:
            exclude_fields = ['is_superuser', 'groups', 'user_permissions']
            restricted_fieldsets = []
            for field, config_dict in fieldsets:
                config_dict = config_dict.copy()
                config_dict['fields'] = [f for f in config_dict['fields'] if f not in exclude_fields]
                restricted_fieldsets.append([field, config_dict])
            return restricted_fieldsets
        return fieldsets


class UserLoginAdmin(admin.ModelAdmin):
    actions = None
    list_display = [
        'full_name',
        'email',
        'date_created',
    ]
    readonly_fields = ['user', 'date_created']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    def full_name(self, obj):
        return obj.user.get_full_name()

    def email(self, obj):
        return obj.user.email

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class InstitutionDomainAdmin(admin.ModelAdmin):
    list_display = ['institution', 'domain']
    search_fields = ['domain']


class InstitutionDomainInline(admin.StackedInline):
    model = InstitutionDomain


class InstitutionAdmin(admin.ModelAdmin):
    inlines = [InstitutionDomainInline]
    list_display = ['name', 'website']
    search_fields = ['name']


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserLogin, UserLoginAdmin)
admin.site.login_form = AuthenticationForm
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(InstitutionDomain, InstitutionDomainAdmin)
