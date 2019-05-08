from django.contrib import admin

from .models import MonWorkExe


class MonWorkExeAdmin(admin.ModelAdmin):
    list_display = ('place', 'number', 'created_at', 'last_updated_at', 'plan_number', 'plan_smallnumber', 'plan_content', 'finish_time', 'execute_user', 'execute_desc', 'problem_desc', 'remarks', 'is_activate', 'state', 'work_type')


admin.site.register(MonWorkExe, MonWorkExeAdmin)
