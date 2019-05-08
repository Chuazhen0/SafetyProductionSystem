from django.db import models
from lbworkflow.models  import BaseWFObj
from systemsettings.models import Company,KKS,MyUser,EquipmentMajor,Stard

# 问题记录表
class Problemlog(BaseWFObj):
    place = models.ForeignKey(Company,verbose_name='公司名称',on_delete=models.SET(Company))
    name = models.CharField(max_length=30,verbose_name='问题名称')
    number = models.CharField(max_length=30,verbose_name='问题编码')
    source = models.CharField(max_length=30,verbose_name='问题来源')
    desc = models.CharField(max_length=30,verbose_name='问题描述',null=True)
    dis_time = models.DateTimeField(auto_now_add=True,verbose_name='发现时间')
    rect_time = models.DateTimeField(auto_now_add=True,verbose_name='整改时间')
    KKS_code = models.ForeignKey(KKS, verbose_name='KKS编码', on_delete=models.SET(KKS))
    cause = models.CharField(max_length=30, verbose_name='问题原因',null=True)
    advise = models.CharField(max_length=30, verbose_name='整改建议',null=True)
    hand_info = models.CharField(max_length=30, verbose_name='处理情况',null=True)
    state = models.CharField(max_length=30,default='拟定', verbose_name='状态')
    level = models.SmallIntegerField(verbose_name='问题等级',null=True)
    # refer_pro = models.CharField(max_length=10,verbose_name='问题涉及指标)
    dis_user = models.ForeignKey(MyUser,verbose_name='发现人',related_name="问题发现人",on_delete=models.SET(MyUser))
    abard_user = models.ForeignKey(MyUser,verbose_name='整改人',related_name="问题整改人",on_delete=models.SET(MyUser))
    tar_pro = models.ForeignKey(EquipmentMajor,verbose_name='问题涉及专业',on_delete=models.SET(EquipmentMajor),null=True)
    stard = models.ForeignKey(Stard,verbose_name='相关标准号',on_delete=models.SET(Stard),null=True)
    accessory = models.FileField(upload_to='pro/',null=True,verbose_name='附件')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='问题记录表'