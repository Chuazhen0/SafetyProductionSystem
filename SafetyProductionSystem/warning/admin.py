from django.contrib import admin

from .models import WarningNotice


class WarningNoticeAdmin(admin.ModelAdmin):
    list_display = ('place', 'state', 'number', 'resource', 'enclosure', 'title', 'supervise_major', 'equipment', 'problem', 'exetuct_user', 'abnormal', 'result', 'suggest', 'time_require', 'is_activate', 'last_updated_at', 'work_type')


admin.site.register(WarningNotice, WarningNoticeAdmin)
