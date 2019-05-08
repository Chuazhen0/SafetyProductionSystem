from django.db import models
from lbworkflow.models import BaseWFObj
# Create your models here.
# 资质类型编码表
class QuaType(BaseWFObj):
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='资质类别维护创建人',on_delete=models.SET('systemsettings.MyUser'), default='')
    created_at = models.DateTimeField(verbose_name='创建时间')
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='资质类别维护最后更新人',on_delete=models.SET('systemsettings.MyUser'), default='')
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间')
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    number = models.CharField(verbose_name='资质类型编码', max_length=30)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    desc = models.CharField(verbose_name='名称', max_length=20,null=True)
    supervision = models.ForeignKey('systemsettings.SupervisionType', verbose_name='专业',on_delete=models.SET('systemsettings.SupervisionType'),null=True)
    remark = models.CharField(verbose_name='备注', max_length=200,null=True)
    state = models.CharField(max_length=5, default='新建', verbose_name='状态')
    class Meta:
        verbose_name='资质类别维护'