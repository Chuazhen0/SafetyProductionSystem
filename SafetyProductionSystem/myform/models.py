from django.db import models
from lbworkflow.models import BaseWFObj
from systemsettings.models import PowerPlants,Job,SupervisionType,MyUser,Company
from datetime import datetime
# Create your models here.
# 测点编码表
class Point(models.Model):
    powerplants = models.ForeignKey(PowerPlants, verbose_name='电厂名称',on_delete=models.SET(PowerPlants),related_name='测点编码名称')
    number = models.CharField(max_length=30, verbose_name='测点编码',)
    name = models.CharField( max_length=30,verbose_name='测点名称')
    ptype = models.ForeignKey(SupervisionType,verbose_name='监督专业',related_name='测点监督专业',on_delete= models.SET(SupervisionType))
    crewnumber = models.CharField(max_length=20, verbose_name='机组号',default='')
# 测点数据表
class PointData(models.Model):
    number = models.ForeignKey(Point,related_name='测点编码',verbose_name='测点编码',on_delete=models.SET(Point))
    write_time = models.DateField(auto_now_add=True,verbose_name='填报时间')
    pvalue = models.DecimalField(max_digits=11,decimal_places=2,verbose_name='测点值')

# 指标编码表
class Target(models.Model):
    powerplants = models.ForeignKey(PowerPlants, verbose_name='电厂名称', on_delete=models.SET(PowerPlants),related_name='指标电厂名称')
    number = models.CharField(max_length=30, verbose_name='指标编码')
    name = models.CharField(max_length=30, verbose_name='指标名称')
    unit = models.CharField(max_length=30, verbose_name='指标单位')
    calculat_formula = models.CharField(max_length=50,verbose_name='指标计算公式',null=True)
    stard_value = models.DecimalField(max_digits=11,decimal_places=2,verbose_name='指标标准值')
    stat_type = models.CharField(max_length=30,verbose_name='指标统计类型',null=True)
    exe_depart = models.ForeignKey(Job,verbose_name='指标责任岗位',on_delete=models.SET(Job),null=True)
    ptype = models.ForeignKey(SupervisionType, verbose_name='监督专业', related_name='指标监督专业',on_delete=models.SET(SupervisionType))
    crewnumber = models.CharField(max_length=20, verbose_name='机组号',default='')
# 指标数据表
class TargetData(models.Model):
    number = models.ForeignKey(Target, related_name='指标数据', verbose_name='指标数据', on_delete=models.SET(Point))
    write_time = models.DateField(auto_now_add=True, verbose_name='填报时间')
    pvalue = models.CharField(max_length=20, verbose_name='指标值', null=True)
# 报表文本项编码表
class FormText(models.Model):
    number = models.CharField(max_length=30, verbose_name='报表文本项编码')
    name = models.CharField(max_length=30, verbose_name='报表文本项名称')
    power_plan = models.ForeignKey(PowerPlants, verbose_name='电厂编码',related_name='报表电厂',default='',on_delete=models.SET(PowerPlants))
    type = models.ForeignKey(SupervisionType, verbose_name='监督专业',related_name='报表专业',default='',on_delete=models.SET(SupervisionType))
# 报表文本项数据表
class FormTextData(models.Model):
    number = models.ForeignKey(FormText,verbose_name='报表文本项编码',on_delete=models.SET(FormText))
    write_time = models.DateField(auto_now_add=True, verbose_name='填报时间')
    content = models.TextField(verbose_name='报表文本项内容')

# 报表状态表
class Form_state(models.Model):
    # state_num: 0-电厂未报送  1-电厂报送  2-退回
    state_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='报表状态号')
    state_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='报表状态名称')
    edit_person = models.ForeignKey(MyUser, verbose_name='报表状态最后更新人',on_delete=models.SET(MyUser), null=True,blank=True)
    spare1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='备用字段1')
    spare2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='备用字段2')

# 报表编码表
class MyForm(BaseWFObj):
    powerplants = models.ForeignKey(PowerPlants, verbose_name='电厂名称', on_delete=models.SET(PowerPlants),related_name='报表电厂名称',null=True,blank=True)
    company = models.ForeignKey(Company, verbose_name='公司名称', on_delete=models.SET(Company),related_name='报表公司名称',null=True,blank=True)
    number = models.CharField(max_length=30, verbose_name='报表编码') # 集团名称
    formname = models.CharField(max_length=30,verbose_name='报表名称') # 状态
    exe_job = models.ForeignKey(Job,verbose_name='报表填报责任岗位',on_delete=models.SET(Job),null=True)
    ptype = models.ForeignKey(SupervisionType, verbose_name='监督专业', related_name='报表监督专业',on_delete=models.SET(SupervisionType))
    created_at = models.DateField(default=datetime.now(),verbose_name='创建时间')
    create_person = models.ForeignKey(MyUser,related_name='create_person', verbose_name='报表填报人',on_delete=models.SET(MyUser), null=True,blank=True)
    form_date = models.CharField(max_length=50, null=True, blank=True, verbose_name='填报月份')
    # state = models.ForeignKey(Form_state, verbose_name='报表状态', null=True, blank=True,on_delete=models.SET(Form_state)) #
    # state_num: 0-电厂未报送  1-电厂已报送  2-已审核 3-已退回
    state_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='报表状态号')
    state_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='报表状态名称')
    edit_person = models.ForeignKey(MyUser,related_name='edit_person', verbose_name='报表状态最后更新人', on_delete=models.SET(MyUser), null=True,blank=True)




# 监督类型对应url表
class PtypeUrl(models.Model):
    url_name = models.CharField(max_length=100, verbose_name='url名称')
    p_type = models.ForeignKey(SupervisionType, verbose_name='监督专业', related_name='报表类型监督专业',on_delete=models.SET(SupervisionType))
    url_data = models.CharField(max_length=100, verbose_name='监督类型对应url')

