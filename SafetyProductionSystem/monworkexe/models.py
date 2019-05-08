from django.db import models
from lbworkflow.models import BaseWFObj
from mon_plan_sum.models import MonPlanSum,SmallDatas
# Create your models here.
class MonWorkExe(BaseWFObj):  # 月度工作执行
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='月度工作执行公司名称')
    number = models.CharField(max_length=30, verbose_name='月度工作执行编码')
    # created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人',related_name='月度工作执行创建人',on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
   # last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人',related_name='月度工作执行最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    plan_number = models.ForeignKey(MonPlanSum,verbose_name='月度计划编码',on_delete=models.SET(MonPlanSum),related_name='月度计划编码')
    plan_smallnumber = models.ForeignKey(SmallDatas,verbose_name='月度计划记录号',on_delete=models.SET(SmallDatas),related_name='月度计划记录号')
    plan_content = models.CharField(max_length=200, verbose_name='计划工作内容')
    finish_time = models.DateTimeField(verbose_name='计划完成时间', null=True)
    execute_user = models.ForeignKey('systemsettings.MyUser', null=True, verbose_name='执行人',related_name='月度工作执行人',on_delete=models.SET('systemsettings.MyUser'))
    execute_desc = models.CharField(max_length=200, null=True, verbose_name='执行情况')
    problem_desc = models.CharField(max_length=200, null=True, verbose_name='存在问题')
    remarks = models.CharField(max_length=200, null=True, verbose_name='备注')
    # 关联问题管理
    # problem = models.ForeignKey()
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    state = models.CharField(max_length=10, default='新建', verbose_name='状态')  # 可选操作：新建/审批中/已批准
    work_type = models.CharField(verbose_name='工单类型', default="月度工作执行",max_length=10)

    def __str__(self):
        return self.plan_content
    class Meta:
        verbose_name='月度工作执行'