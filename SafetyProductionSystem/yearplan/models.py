from django.db import models
from lbworkflow.models import BaseWFObj
# Create your models here.
class YearPlan(BaseWFObj):  # 监督年度计划汇总表
    desc = models.CharField(max_length=50, null=True, verbose_name='计划描述')
    number = models.CharField(max_length=30, verbose_name='年度计划编码')
    year = models.CharField(verbose_name='年份', max_length=10)
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    # created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人',related_name='年度计划创建人',on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人',related_name='年度计划最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    enclosure = models.FileField(upload_to='Plan/', null=True, verbose_name='附件')
    state = models.CharField(max_length=10, verbose_name='状态', default='新建')
    work_type = models.CharField(verbose_name='工单类型', default="年度计划",max_length=10)
    def __str__(self):
        return self.desc

    class Meta:
        verbose_name='年度计划汇总'