from django.db import models
from lbworkflow.models import BaseWFObj
# Create your models here.
# 网络结构信息表
class NetStructure(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='监督网络公司名称')  # 地点，一般默认为分公司
    number = models.CharField(max_length=30,verbose_name='网络结构编号',unique=True) # 唯一
    parent = models.ForeignKey('self', null=True, verbose_name='上级监督网络',on_delete=models.SET('self'))
    desc = models.CharField(max_length=50, null=True, verbose_name='描述')
    classify = models.CharField(max_length=10, verbose_name='类别')  # 可供选择：九大监督/五大管理
    state = models.CharField(max_length=10, verbose_name='状态', default='新建')  # 可供选择： 新建/审批/已批准
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='网络结构创建人',on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间' ,auto_now_add=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='网络结构最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    work_type = models.CharField(verbose_name='工单类型',default="网络结构信息",max_length=10)
    level = models.SmallIntegerField(verbose_name='监督网络级别', null=True)
    def __str__(self):
        return self.desc

    class Meta:
        verbose_name='网络结构信息'