from django.contrib import admin

from .models import WarningReceipt


class WarningReceiptAdmin(admin.ModelAdmin):
    list_display = ('place', 'state', 'number', 'warning_notice', 'created_at', 'last_updated_at', 'work_type', 'enclosure', 'content', 'result', 'is_activate')


admin.site.register(WarningReceipt, WarningReceiptAdmin)
