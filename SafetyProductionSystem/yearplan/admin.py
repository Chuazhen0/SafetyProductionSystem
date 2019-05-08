from django.contrib import admin

from .models import YearPlan


class YearPlanAdmin(admin.ModelAdmin):
    list_display = ('desc', 'number', 'year', 'place', 'created_at', 'last_updated_by', 'last_updated_at', 'is_activate', 'enclosure', 'state', 'work_type')


admin.site.register(YearPlan, YearPlanAdmin)
