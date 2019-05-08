from django.contrib import admin

# Register your models here.
from systemsettings import models
admin.site.register(models.Menu)
admin.site.register(models.EquipmentCount)
admin.site.register(models.Role)
admin.site.register(models.EquipmentMajor)
admin.site.register(models.Operation)
admin.site.register(models.MyUser)

