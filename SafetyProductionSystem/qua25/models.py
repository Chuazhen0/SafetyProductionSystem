from django.db import models
from quatype.models import QuaType
from lbworkflow.models import BaseWFObj
from lbworkflow.models import ProcessInstance
# Create your models here.
# 资质编码表
class Qua(models.Model):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='技术监督资质公司名称')
    number = models.CharField(max_length=30, verbose_name='资质编码')
    name = models.CharField(max_length=30, verbose_name='资质名称')
    qua_type = models.ForeignKey(QuaType, verbose_name='资质类型', on_delete=models.SET(QuaType),related_name='技术监督资质资质类型')
    warining_time = models.IntegerField(verbose_name="提前提醒天数", default=0, null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    class Meta:
        verbose_name = '资质编码表'


