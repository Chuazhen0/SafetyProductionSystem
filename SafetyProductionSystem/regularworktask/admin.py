from django.contrib import admin

from .models import RegularWorkTask


class RegularWorkTaskAdmin(admin.ModelAdmin):
    list_display = ('place', 'regularwork', 'result', 'is_activate', 'tanchuang', 'has_readed', 'enclosure_file')


admin.site.register(RegularWorkTask, RegularWorkTaskAdmin)
