from django.db import models
from lbworkflow.models import BaseWFObj
from warning.models import WarningNotice

# 告警回执单.
class WarningReceipt(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    state = models.CharField(default="新建", verbose_name='状态',max_length=10)
    number = models.CharField(max_length=30, verbose_name='告警回执单编码')
    warning_notice = models.ForeignKey(WarningNotice, verbose_name='关联告警通知单',on_delete=models.SET(WarningNotice))
    created_at = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    work_type = models.CharField(verbose_name='工单类型', default="告警回执",max_length=10)
    enclosure = models.FileField(upload_to='Warning/', null=True, verbose_name='附件')
    content = models.CharField(max_length=200, verbose_name='回执内容',null=True)
    result = models.CharField(max_length=200, verbose_name='回执结果')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)

    def __str__(self):
        return '告警回执单'

    class Meta:
        verbose_name='告警回执单'
