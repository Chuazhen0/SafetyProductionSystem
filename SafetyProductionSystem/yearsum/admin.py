from django.contrib import admin

from .models import YearSum


class YearSumAdmin(admin.ModelAdmin):
    list_display = ('place', 'sum_desc', 'sum_type', 'year', 'state', 'created_at', 'last_updated_by', 'last_updated_at', 'enclosure', 'is_activate', 'work_type')


admin.site.register(YearSum, YearSumAdmin)
