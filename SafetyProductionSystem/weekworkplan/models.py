from django.db import models
from lbworkflow.models import BaseWFObj
from weekworktask.models import WeekWorkTask
from systemsettings.models import SupervisionType
# Create your models here.
# 周期检测计划编码表
class WeekWorkPlan(BaseWFObj):
    id = models.AutoField(verbose_name='主键', primary_key=True)
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'),related_name='周期检测计划公司名称')
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='检测计划创建人', on_delete=models.SET('systemsettings.MyUser'))
    created_at = models.DateTimeField(verbose_name='创建时间')
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='检测计划最后更新人',on_delete=models.SET('systemsettings.MyUser'))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间')
    enclosure = models.FileField(upload_to='Plan/', null=True, verbose_name='附件')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    number = models.CharField(verbose_name='周期检测计划编码', max_length=30)
    plan = models.CharField(verbose_name='周期检测计划名称', max_length=20)
    third_org = models.CharField(verbose_name='第三方机构', max_length=20)
    rate_desc = models.CharField(verbose_name='频率', max_length=50)
    rate_code= models.CharField(verbose_name='频率代码', max_length=50)
    time_limit = models.CharField(verbose_name='完成时限', max_length=10)
    state = models.CharField(max_length=5, default='新建', verbose_name='状态')
    planner = models.ForeignKey('systemsettings.MyUser', verbose_name='策划人', related_name='检测计划策划人', on_delete=models.SET('systemsettings.MyUser'))
    plan_time = models.DateField(verbose_name='策划时间')
    execute_user = models.ForeignKey('systemsettings.MyUser', verbose_name='执行人', related_name='检测计划执行人', on_delete=models.SET('systemsettings.MyUser'))
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督专业', on_delete=models.SET(SupervisionType),null=True,default=1)

    class Meta:
        verbose_name='周期检测计划'

    def create_task(self):  # 生成空的周期工作任务记录
        weekwork_plan = WeekWorkPlan.objects.filter(id=self.id).first()
        weekwork_task = WeekWorkTask.objects.create(place=self.place, is_activate=1, plan=weekwork_plan)
        weekwork_task.save()