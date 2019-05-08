from django.contrib import admin

from .models import MonPlanSum


class MonPlanSumAdmin(admin.ModelAdmin):
    list_display = ('place', 'desc', 'number', 'supervision_major', 'year', 'month', 'state', 'created_at', 'last_updated_by', 'last_updated_at', 'enclosure', 'is_activate', 'work_type')


admin.site.register(MonPlanSum, MonPlanSumAdmin)
