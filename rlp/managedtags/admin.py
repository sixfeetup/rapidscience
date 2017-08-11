from django.contrib import admin
from .models import ManagedTag

# Register your models here.
class ManagedTagAdmin(admin.ModelAdmin):
    model = ManagedTag
    list_display = ( 'name', 'approved', 'create_date', 'update_date')
    list_filter = ( 'approved', )
    #date_hierarchy = 'create_date'  # ignored by djangocms,
    # but djangoadmin handles this nicely

admin.site.register(ManagedTag, ManagedTagAdmin)
