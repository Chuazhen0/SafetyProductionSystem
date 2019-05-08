from django.db import models
from lbworkflow.models import BaseWFObj
from systemsettings.models import SupervisionType,KKS
from problemlog.models import Problemlog
# Create your models here.
class WarningResource(models.Model):
    name = models.CharField(max_length=15,verbose_name='告警来源类',default='')
class WarningNotice(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    state = models.CharField(default="新建", verbose_name='状态',max_length=10)
    number = models.CharField(max_length=30, verbose_name='告警通知单编码')
    resource = models.ForeignKey(WarningResource, verbose_name='来源',on_delete=models.SET(WarningResource),default='')
    enclosure = models.FileField(upload_to='Warning/', null=True, verbose_name='附件')
    title = models.CharField(max_length=20, verbose_name='告警通知单名称')
    supervise_major = models.ForeignKey(SupervisionType, verbose_name='监督类型',on_delete=models.SET(SupervisionType))
    equipment = models.ForeignKey(KKS,verbose_name='关联设备',null=True,on_delete=models.SET(KKS))
    problem	= models.ForeignKey(Problemlog,verbose_name='关联问题',null=True,on_delete=models.SET(Problemlog))
    exetuct_user = models.ForeignKey('systemsettings.MyUser', verbose_name='责任人',related_name='告警责任人',on_delete=models.SET('systemsettings.MyUser'))
    abnormal = models.CharField(max_length=200, verbose_name='异常情况')
    result = models.CharField(max_length=200, verbose_name='可能或已经造成的后果')
    suggest = models.CharField(max_length=200, verbose_name='整改建议')
    time_require = models.CharField(max_length=200, verbose_name='整改时间要求')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    work_type = models.CharField(verbose_name='工单类型', default="告警通知单",max_length=10)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name='告警通知单'