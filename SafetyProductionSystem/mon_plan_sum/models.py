from django.db import models
from  lbworkflow.models import BaseWFObj
from systemsettings.models import SupervisionType

class MonPlanSum(BaseWFObj):  # 月度计划与总结表
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='月度工作计划公司名称')
    desc = models.CharField(max_length=50, null=True, verbose_name='计划描述')
    number = models.CharField(max_length=30, verbose_name='计划编码')
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督类型',on_delete=models.SET(SupervisionType))
    year = models.CharField(verbose_name='年份',max_length=5)
    month = models.CharField(verbose_name='月份',max_length=5)
    state = models.CharField(max_length=10, default='拟定', verbose_name='状态')  # 可选操作：新建/审批中/已批准
    # created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='月度计划与总结创建人',on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='月度计划与总结最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间', auto_now_add=True)
    enclosure = models.FileField(upload_to='Plan/', null=True, verbose_name='附件')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    work_type = models.CharField(verbose_name='工单类型', default="月度计划与总结",max_length=10)
    def __str__(self):
        return self.desc
    class Meta:
        verbose_name='月度计划与总结'
class SmallDatas(models.Model):
    smallnumber = models.CharField(max_length=30, verbose_name='月度计划记录号')
    content = models.CharField(max_length=200, verbose_name='月度计划内容')
    exe_user = models.ForeignKey('systemsettings.MyUser', verbose_name='责任人', related_name='责任人',
                                 on_delete=models.SET('systemsettings.MyUser'))
    finish_time = models.DateTimeField(verbose_name='完成时间')
    monplansum = models.ForeignKey(MonPlanSum,verbose_name='月度计划编码',on_delete=models.SET(MonPlanSum))
    is_activate = models.SmallIntegerField(verbose_name='是否活动',default=1)
    def __str__(self):
        return self.smallnumber