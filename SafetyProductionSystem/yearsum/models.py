from django.db import models
from lbworkflow.models import BaseWFObj
# Create your models here.
class YearSum(BaseWFObj):  # 监督年度总结汇总表
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    sum_desc = models.CharField(max_length=200, verbose_name='总结描述')
    sum_type = models.CharField(max_length=5, verbose_name='总结类型', default='年度总结')
    year = models.CharField(verbose_name='年份', max_length=10)
    state = models.CharField(max_length=10, verbose_name='状态', default='新建')
    # created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人',related_name='年度总结创建人',on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人',related_name='年度总结最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    enclosure = models.FileField(upload_to='Plan/', null=True, verbose_name='附件')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    work_type = models.CharField(verbose_name='工单类型', default="年度总结",max_length=10)
    def __str__(self):
        return  self.sum_desc
    class Meta:
        verbose_name='年度总结'