from django.contrib import admin

from .models import EmailLog


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['to_email', 'date_sent', 'subject']
    list_filter = ['subject']
    search_fields = ['to_email']
    date_hierarchy = 'date_sent'
    readonly_fields = ['to_email', 'date_sent', 'subject', 'message_text']
    exclude = ['message_html', ]


admin.site.register(EmailLog, EmailLogAdmin)
