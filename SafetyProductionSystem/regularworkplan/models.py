from django.db import models
from systemsettings.models import KKS,Company,EquipmentMajor,MyUser,SupervisionType,Stard,MyGroup
from lbworkflow.models import BaseWFObj
from regularworktask.models import RegularWorkTask
from SafetyProductionSystem.settings import CRONJOBS
from django.db.models.signals import post_save
import logging


# Create your models here.


# 定期工作编码表
class RegularWorkPlan(models.Model):
    id = models.AutoField(verbose_name='主键',primary_key=True)
    place = models.ForeignKey(Company, verbose_name='公司名称',on_delete=models.SET(Company))
    number = models.CharField(max_length=30,verbose_name='定期工作编码')
    KKS_code = models.ForeignKey( KKS,verbose_name='KKS编码', on_delete=models.SET(KKS),null=True)
    KKS_codename = models.CharField(max_length=1000, verbose_name='KKS编码名称', null=True)
    exe_user = models.ForeignKey(MyUser, verbose_name='责任人', on_delete=models.SET(MyUser),null=True)
    exe_group = models.ForeignKey(MyGroup, verbose_name='责任组', on_delete=models.SET(MyGroup),null=True)
    equipment_major = models.ForeignKey(EquipmentMajor, verbose_name='设备专业', on_delete=models.SET(EquipmentMajor))
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督专业', on_delete=models.SET(SupervisionType),null=True)
    nature = models.CharField(max_length=10,verbose_name='性质',null=True) # 运行/检修/管理
    type = models.CharField(max_length=10,verbose_name='定期工作类型') # 技术监督设备类/技术监督管理类/25项反措设备类/25项反措管理类
    score = models.IntegerField(verbose_name='标准分值',null=True,default=0)
    work_content = models.TextField(verbose_name='工作项目',max_length=200)
    weekend_desc = models.CharField(verbose_name='周期描述',max_length=30) # 小时 ，天 ，周 ，月 ，年 ，一次性
    num1 = models.CharField(verbose_name='周期描述1',max_length=50,default='0',null=True)
    num2 = models.CharField(verbose_name='周期描述2',max_length=50,default='0',null=True)
    warinig_time = models.SmallIntegerField(verbose_name='提前提醒时间')
    state = models.CharField(max_length=10,verbose_name='状态',null=True,default='拟定')
    overdue_1 = models.SmallIntegerField(verbose_name='超期一级预警',null=True)
    overdue_2= models.SmallIntegerField(verbose_name='超期二级预警',null=True)
    overdue_3 = models.SmallIntegerField(verbose_name='超期三级预警',null=True)
    resource = models.CharField(max_length=50,verbose_name='业务来源',null=True)
    start_time = models.DateTimeField(verbose_name='开始时间',null=True)
    end_time = models.DateTimeField(verbose_name='结束时间',null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1,)
    stard = models.ForeignKey(Stard,verbose_name ='标准编码',on_delete=models.SET(Stard),null=True)
    stard_smallnumber = models.CharField(verbose_name ='标准号',null=True,max_length=30)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name ='创建时间')
    last_edit_time = models.DateTimeField(auto_now=True,verbose_name="最后更新时间")
    def __str__(self):
        return self.work_content

    class Meta:
        verbose_name='定期工作策划主信息表'

    def create_task(self):  # 生成空的定期工作任务记录
        regular_plan = RegularWorkPlan.objects.filter(id=self.id).first()
        new_task = RegularWorkTask.objects.create(place=self.place, result='', is_activate=1, regularwork=regular_plan)
        new_task.save()


# 工作内容表
class WorkContent(models.Model):
    # KKS = models.ForeignKey(KKS,verbose_name='KKS编码',on_delete=models.SET(KKS))
    regular_work = models.ForeignKey(RegularWorkPlan,verbose_name='定期工作策划',on_delete=models.SET(RegularWorkPlan))
    number = models.IntegerField(verbose_name='工作内容序号')
    content = models.TextField(verbose_name='工作内容')
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='工作内容创建人',
                                   on_delete=models.SET('systemsettings.MyUser'), null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', null=True, auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='工作内容最后更新人',
                                        on_delete=models.SET('systemsettings.MyUser'), null=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间', null=True, auto_now_add=True)

# 工作准备表
class PreWork(models.Model):
    # KKS = models.ForeignKey(KKS,verbose_name='KKS编码',on_delete=models.SET(KKS))
    regular_work = models.ForeignKey(RegularWorkPlan,verbose_name='定期工作策划',on_delete=models.SET(RegularWorkPlan))
    number = models.IntegerField(verbose_name='工作准备序号')
    content = models.TextField(verbose_name='工作准备内容')
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='工作准备创建人',
                                   on_delete=models.SET('systemsettings.MyUser'), null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', null=True, auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='工作准备最后更新人',
                                        on_delete=models.SET('systemsettings.MyUser'), null=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间', null=True, auto_now_add=True)


# 注意事项表
class WorkCare(models.Model):
    # KKS = models.ForeignKey(KKS,verbose_name='KKS编码',on_delete=models.SET(KKS))
    regular_work = models.ForeignKey(RegularWorkPlan,verbose_name='定期工作策划',on_delete=models.SET(RegularWorkPlan))
    number = models.IntegerField(verbose_name='注意事项序号')
    content = models.TextField(verbose_name='注意事项内容')
    created_by = models.ForeignKey('systemsettings.MyUser', verbose_name='创建人', related_name='注意事项创建人',
                                   on_delete=models.SET('systemsettings.MyUser'), null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', null=True, auto_now_add=True)
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='最后更新人', related_name='注意事项最后更新人',
                                        on_delete=models.SET('systemsettings.MyUser'), null=True)
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间', null=True, auto_now_add=True)


# 工作数据表
class WorkData(models.Model):
    number = models.IntegerField(verbose_name='工作数据序号')
    regular_work = models.ForeignKey(RegularWorkPlan, verbose_name='定期工作策划', on_delete=models.SET(RegularWorkPlan))
    data_name = models.CharField(verbose_name='数据名称', max_length=50, null=True)
    data_value = models.CharField(verbose_name='数据标准值', max_length=50, null=True)
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称', null=True,
                              on_delete=models.SET('systemsettings.Company'), related_name='工作数据公司单位名称')

# 定时工作任务
class crontab_task(models.Model):
    weekdesc = models.CharField(max_length=10,verbose_name='定期描述')
    num1 = models.CharField(verbose_name='周期描述11', max_length=50, default='0', null=True)
    num2 = models.CharField(verbose_name='周期描述22', max_length=50, default='0', null=True)
    myid = models.IntegerField(verbose_name='定期工作策划id')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, )


