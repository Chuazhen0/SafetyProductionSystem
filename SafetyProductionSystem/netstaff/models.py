from django.db import models
from lbworkflow.models import BaseWFObj
from netstructure.models import NetStructure
from systemsettings.models import MyUser,Company,Department
# Create your models here.
class NetStaff(BaseWFObj):
    place = models.ForeignKey(Company, verbose_name='公司名称',on_delete=models.SET(Company),related_name='网络人员公司名称')
    netstructure = models.ForeignKey(NetStructure, verbose_name='所属监督网络',on_delete=models.SET(NetStructure))
    phone = models.CharField(max_length=11, null=True, verbose_name='联系方式') # 11位以内数字
    net_name = models.SmallIntegerField(verbose_name='监督网络岗位')# 1为生技部主任  2.监督专责  3.执行人
    user = models.ManyToManyField(MyUser, verbose_name='对应人员')
    department = models.ForeignKey(Department, verbose_name='所在部门', null=True,on_delete=models.SET(Department))
    created_by = models.ForeignKey(MyUser, verbose_name='创建人', related_name='监督网络人员信息表创建人',on_delete=models.SET(MyUser))
    created_at = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    last_updated_by = models.ForeignKey(MyUser, verbose_name='最后更新人', related_name='监督网络人员信息表最后更新人',on_delete=models.SET(MyUser))
    last_updated_at = models.DateTimeField(verbose_name='最后更新时间',auto_now_add=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    work_type = models.CharField(verbose_name='工单类型', default="网络人员信息",max_length=10)

    # def __str__(self):
    #     return self.net_name

    class Meta:
        verbose_name = '网络人员维护'