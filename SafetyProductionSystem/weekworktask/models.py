from django.db import models
from lbworkflow.models import BaseWFObj
from django.contrib.auth.models import User
# Create your models here.
class WeekWorkTask(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',
                              on_delete=models.SET('systemsettings.Company'))
    created_by = models.ForeignKey(User, verbose_name='创建人', related_name='周期检测任务创建人',
                                   on_delete=models.SET(User), null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', null=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='周期检测任务最后更新人',
                                        on_delete=models.SET('systemsettings.MyUser'), null=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间', null=True)
    enclosure = models.FileField(upload_to='week_task_enclosure_files', null=True, verbose_name='附件')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    number = models.CharField(verbose_name='周期检测任务编码', max_length=30, null=True)
    # plan = models.ForeignKey(WeekWorkPlan,verbose_name='周期检测计划名称',on_delete=models.SET(WeekWorkPlan),related_name='周期检测计划名称')
    plan = models.ForeignKey('weekworkplan.WeekWorkPlan',on_delete=models.SET('./weekworkplan.WeekWorkPlan'), verbose_name='周期检测计划名称')
    task_start_time = models.DateField(verbose_name='计划开始时间', null=True)
    time_limit = models.CharField(verbose_name='完成时限', max_length=10, null=True)
    result = models.CharField(max_length=200, verbose_name='周期工作任务完成情况', null=True)

    class Meta:
        verbose_name = '周期检测任务'

    def __str__(self):
        return self.plan.plan