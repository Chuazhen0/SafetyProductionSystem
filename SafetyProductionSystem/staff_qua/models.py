from django.db import models
from lbworkflow.models import BaseWFObj,ProcessInstance
from qua25.models import Qua
from systemsettings.models import SupervisionType
# Create your models here.


# 人员资质对应表
class StaffQua(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='技术监督人员资质公司名称')
    number = models.CharField(max_length=30, verbose_name='人员资质对应编码')
    state = models.CharField(max_length=5, default='新建', verbose_name='状态')
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='技术监督资质创建人',
                                   on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间')
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='资质维护明细最后更新人',
                                        on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    qua = models.ForeignKey(Qua, verbose_name='资质', on_delete=models.SET(Qua),related_name='技术监督资质')
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督专业', on_delete=models.SET(SupervisionType),related_name='技术监督资质监督专业')
    publisher = models.ForeignKey('systemsettings.Department', verbose_name='发证单位',on_delete=models.SET('systemsettings.Department'),related_name='技术监督资质发证单位')
    effect_time = models.DateField(verbose_name='有效日期')
    qua_enclosure = models.FileField(verbose_name='资质扫描件', null=True)
    user = models.ForeignKey('systemsettings.MyUser', verbose_name='人员', on_delete=models.SET('systemsettings.MyUser'),related_name='技术监督资质对应人员')
    pinstance = models.ForeignKey(ProcessInstance, verbose_name='流程编号', on_delete=models.SET(ProcessInstance),
                                  related_name='技术监督人员资质对应流程',null=True)
    company_id = models.SmallIntegerField(verbose_name="对应公司id", default=7, null=True)
    # 增加company_id作为接收前端公司列表返回值的字段
    class Meta:
        verbose_name = '人员资质对应表'