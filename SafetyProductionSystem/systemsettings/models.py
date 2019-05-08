from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from qua25.models import Qua
# 菜单表
class Menu(models.Model):
    title = models.CharField(max_length=15, verbose_name='菜单名称')
    order = models.SmallIntegerField(blank=True, default=1, verbose_name='排序')
    is_active = models.SmallIntegerField(default=1, verbose_name='是否激活')
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name='父级菜单', on_delete=models.SET('self'))
    level = models.SmallIntegerField(verbose_name='菜单级别',null=True)
    url = models.URLField(verbose_name='菜单路由')
    font_class = models.CharField(max_length=100, verbose_name='字体图标类型', null=True)
    number = models.CharField(max_length=3,verbose_name='菜单编号',default='')

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '>'.join(title_list)
    # join()中的sequence元素必须都为字符串，将其按照一定的连接符连接起来

# 操作表
class Operation(models.Model):
    title = models.CharField(max_length=15, verbose_name='操作名称')
    url = models.URLField(blank=True, null=True, verbose_name='排序')
    is_active = models.SmallIntegerField(default=1, verbose_name='是否激活')
    menu = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.SET(Menu))
    key = models.CharField(max_length=10, verbose_name='关键词')

    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.title)

# 角色表
class Role(models.Model):
    name = models.CharField(max_length=30, verbose_name='角色名称')
    is_activate = models.SmallIntegerField(default=1, verbose_name='是否被选用')
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='最后更新时间', auto_now_add=True)
    operations = models.ManyToManyField(Operation, verbose_name='操作')
    # 定义角色和权限的多对多关系
    def __str__(self):
        return self.name

# 电厂编码表
class PowerPlants(models.Model):
    pownumber=models.CharField(max_length=30,verbose_name='电厂编码')
    powname=models.CharField(max_length=30,verbose_name='电厂名称')
    powsimplename = models.CharField(max_length=15,verbose_name='简称')

    def __str__(self):
        return self.powname

# 公司编码表
class Company(models.Model):
    comnumber = models.CharField(max_length=30, verbose_name='公司编码')
    comname = models.CharField(max_length=30, verbose_name='公司名称')
    comsimplename = models.CharField(max_length=15, verbose_name="公司简称")

    def __str__(self):
        return self.comname

# 部门编码表
class Department(models.Model):
    departnumber = models.CharField(max_length=30, verbose_name='部门编码')
    departname = models.CharField(max_length=30, verbose_name='部门名称')
    simple_name = models.CharField(max_length=30, verbose_name='部门简称', null=True)
    company = models.ForeignKey(Company,verbose_name='所属公司',on_delete=models.SET(Company))
    def __str__(self):
        return self.departname
# 班组表
class Team(models.Model):
    teamnumber = models.CharField(max_length=30, verbose_name='班组编码')
    teamname = models.CharField(max_length=30, verbose_name='班组名称')
    simple_name = models.CharField(max_length=30, verbose_name='班组简称', null=True)
    department = models.ForeignKey(Department,verbose_name='所属部门',on_delete=models.SET(Department))
    def __str__(self):
        return self.teamname
# 岗位编码表
class Job(models.Model):
    jobnumber = models.CharField(max_length=30, verbose_name='岗位编码')
    jobname = models.CharField(max_length=30, verbose_name='岗位名称')
    simple_name = models.CharField(max_length=30, verbose_name='岗位简称', null=True)
    company = models.ForeignKey(Company,verbose_name='所属公司',on_delete=models.SET(Company))
    def __str__(self):
        return self.jobname

# 设备专业编码表  5种
class EquipmentMajor(models.Model):
    number = models.CharField(verbose_name='设备专业编码',max_length=30)
    name = models.CharField(verbose_name='设备专业名称', max_length=10)
    def __str__(self):
        return self.name

# 监督专业编码表  12种
class SupervisionType(models.Model):
    number = models.CharField(max_length=30, verbose_name='监督专业编码')
    name = models.CharField(max_length=10, verbose_name='监督专业名称')
    form_use = models.CharField(max_length=10, verbose_name='报表使用', null=True)
    def __str__(self):
        return self.name
# 设备台账编码表
class EquipmentCount(models.Model):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    number = models.CharField(max_length=30, verbose_name='台账编号')
    name = models.CharField(max_length=30, verbose_name='台账名称')
    equipment_major = models.ForeignKey(EquipmentMajor, verbose_name='设备专业', null=True,
                                        on_delete=models.SET(EquipmentMajor))
    status = models.SmallIntegerField(default=1, verbose_name='状态')  # 1:在用
    created_on = models.DateTimeField(verbose_name='创建时间', null=True, auto_now_add=True)
    last_updated_on = models.DateTimeField(verbose_name='最后更新时间', null=True, auto_now_add=True)

# KKS编码表
class KKS(models.Model):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    KKs_organid = models.CharField(max_length=30,blank=True, null=True,verbose_name='KKS电厂接口id',default='')
    KKS_code = models.CharField(max_length=30, blank=True, null=True,verbose_name='KKS编码',default='')
    KKS_codename = models.TextField(blank=True, null=True, verbose_name='KKS编码名称',default='')
    def __str__(self):
        return self.KKS_code

 # 工作区域编码表
class WorkArea(models.Model):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称', on_delete=models.SET('systemsettings.Company'))
    number = models.CharField(max_length=30, verbose_name='工作区域编码')
    name= models.CharField(verbose_name='工作区域名称', max_length=10)
    def __str__(self):
        return self.name

# 标准编码表
class Stard(models.Model):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',on_delete=models.SET('systemsettings.Company'))
    number = models.CharField(max_length=30, verbose_name='标准编码')
    name = models.CharField(max_length=30, verbose_name='标准名称')
    smallnumber = models.CharField(max_length=30, verbose_name='标准号')
    publisher = models.ForeignKey(Department,verbose_name='标准发布单位',on_delete=models.SET(Department))
    type = models.CharField(max_length=10,verbose_name='标准类型')
    V_number = models.CharField(max_length=10,verbose_name='标准版本')
    updated_time = models.DateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name


# 责任组
class MyGroup(models.Model):
    place = models.ForeignKey(Company, verbose_name='公司名称',on_delete=models.SET(Company))
    number = models.CharField(max_length=10, unique=True, verbose_name='责任组编号',null=True,blank=True)
    name = models.CharField(max_length=30, verbose_name='责任组名称',null=True,blank=True)
    duty_user = models.ManyToManyField('systemsettings.MyUser', verbose_name='对应人员',null=True,blank=True)
    spare1 = models.CharField(max_length=30, verbose_name='备用字段1', null=True, blank=True)
    spare2 = models.CharField(max_length=30, verbose_name='备用字段2', null=True, blank=True)
    def __str__(self):
        return self.name

# 人员编码表
class MyUser(models.Model):
    name = models.CharField(max_length=5, verbose_name='姓名')
    number = models.CharField(max_length=10, unique=True,verbose_name='工号')
    user = models.OneToOneField(User, on_delete=models.SET(User),verbose_name='内置用户')
    department = models.ForeignKey(Department, blank=True, null=True, verbose_name='部门名称',on_delete=models.SET(Department))
    jobname = models.ForeignKey(Job, blank=True, null=True, verbose_name='岗位名称',on_delete=models.SET(Job))
    company = models.ForeignKey(Company, blank=True, null=True, verbose_name='公司名称',on_delete=models.SET(Company))
    equipment_major = models.ForeignKey(EquipmentMajor, verbose_name='设备专业编码', null=True,on_delete=models.SET(EquipmentMajor))
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督专业编码', null=True,on_delete=models.SET(SupervisionType))
    group = models.ForeignKey(MyGroup, verbose_name='人员所属责任组', null=True,on_delete=models.SET(MyGroup))
    roles = models.ManyToManyField(Role, verbose_name='绑定角色')
    quas = models.ManyToManyField(Qua,verbose_name='人员资质',related_name='基本人员资质')

    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='电话')
    state = models.SmallIntegerField(default=1, verbose_name='状态')
    headimage = models.ImageField(upload_to='image/', blank=True, null=True, verbose_name='头像')
    startdate = models.DateField(blank=True, null=True, verbose_name='聘用日期')
    enddate = models.DateField(blank=True, null=True, verbose_name='终止日期')
    is_activate = models.SmallIntegerField(default=1, verbose_name='是否激活')


    def __str__(self):
        return self.name


#  python json数据转dict
class TreeNode():
    def __init__(self):
        self.id = 0
        self.text = "Node 1"
        self.href = None
        self.selectable = True
        self.backColor = "#2894FF"
        self.color = "#ffffff"
        self.state = {
                             'checked': True,
                             'disabled': True,
                             'expanded': True,
                             'selected': True,
                         },
        self.tags = ['available'],
        self.nodes = []
        # self.enableLinks = None

    def to_dict(self):
        icon = (len(self.nodes) > 0) and 'glyphicon glyphicon-list-alt' or 'glyphicon glyphicon-user'
        return {
                'id': self.id,
                'text': self.text,
                'icon': icon,
                'href': self.href,
                'tags': ['点击操作'],
                'nodes': self.nodes,
                'backColor': self.backColor,
                'color': self.color,
                # 'enableLinks': self.enableLinks,
            }




