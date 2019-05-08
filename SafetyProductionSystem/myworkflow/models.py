from django.db import models
from systemsettings.models import Company,SupervisionType
from lbworkflow.models import Process,Node



class MyProcess(models.Model):
    company = models.ForeignKey(Company, blank=True, null=True, verbose_name='公司名称', on_delete=models.SET(Company))
    supervision_major = models.ForeignKey(SupervisionType, verbose_name='监督专业编码', null=True,on_delete=models.SET(SupervisionType))
    myprocess_name = models.CharField(max_length=30, verbose_name='流程名称')
    app_name = models.CharField(max_length=30,verbose_name='对应表单')
    process = models.OneToOneField(Process,on_delete=models.SET(Process),verbose_name='关联lb工作流程')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, )
    app_object_id = models.CharField(verbose_name='具体表单记录',default='',null=True,max_length=100)
    def __str__(self):
        return self.myprocess_name



class MyNode(models.Model):
    node_name = models.CharField(verbose_name='节点名称',max_length=10)
    resource = models.CharField(verbose_name='岗位流转类型',max_length=10) # 监督网络/行政
    operators_job = models.TextField(verbose_name='操作者岗位',blank=True)
    myprocess = models.ForeignKey(MyProcess,verbose_name='所属流程',on_delete=models.SET(MyProcess))
    node = models.OneToOneField(Node,verbose_name='关联lb流程节点',on_delete=models.SET(Node))
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, )

    def __str__(self):
        return self.node_name


# 工作流历史记录表
class TaskHistory(models.Model):
    node_name = models.CharField(verbose_name='审批节点名称',null=True,blank=True, max_length=100)
    approve_name = models.CharField(verbose_name='审批人',null=True,blank=True, max_length=100)
    created_name = models.CharField(verbose_name='创建人', null=True,blank=True,max_length=100)
    approve_type = models.CharField(verbose_name='审批状态',null=True,blank=True, max_length=100)
    content = models.TextField(verbose_name='描述',null=True,blank=True)
    process_id = models.IntegerField(verbose_name='流程编号', default=1 )
    created_time = models.DateTimeField(verbose_name='创建时间', null=True, blank=True)

    def __str__(self):
        return self.node_name



