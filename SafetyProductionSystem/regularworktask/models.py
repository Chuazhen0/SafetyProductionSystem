from django.db import models

from lbworkflow.models import BaseWFObj
# Create your models here.


class RegularWorkTask(BaseWFObj):
    place = models.ForeignKey('systemsettings.Company', verbose_name='公司名称',default='',
                              on_delete=models.SET('systemsettings.Company'))
    regularwork = models.ForeignKey('regularworkplan.RegularWorkPlan',on_delete=models.SET('regularworkplan.RegularWorkPlan'),verbose_name='定期工作任务')
    result = models.CharField(max_length=200,verbose_name='定期工作任务完成情况',null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    tanchuang = models.SmallIntegerField(verbose_name='是否已弹窗', default=0,null=True)
    has_readed = models.SmallIntegerField(verbose_name='是否已读', default=0,null=True)
    enclosure_file = models.FileField(verbose_name='附件', null=True, upload_to='./task_enclosure_files')

    class Meta:
        verbose_name='定期工作任务'

    def __str__(self):
        return self.regularwork.work_content

