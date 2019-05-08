from django.db import models
from systemsettings.models import SupervisionType
# Create your models here.
# ------------------------指标管理--------------陈桂林--------------
# 指标定义列表
class StandardList(models.Model):
    number = models.CharField(max_length=40, verbose_name='指标定义编号', null=True)
    describe = models.CharField(max_length=50, verbose_name='指标定义描述', null=True)
    Supervision_type = models.ForeignKey(SupervisionType, verbose_name='监督类型',
                                         on_delete=models.SET(SupervisionType),related_name='指标定义监督类型')
    cycle = models.CharField(max_length=10, verbose_name='指标填报周期', null=True)
    state = models.CharField(max_length=20, verbose_name='状态', default='拟定')
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    def __str__(self):
        return self.describe

    class Meta:
        verbose_name='指标定义列表'

# 指标定义详情
class StandardDetails(models.Model):
    definition = models.ForeignKey(StandardList, on_delete=models.SET(StandardList), verbose_name='指标类型',related_name='指标类型')
    standard_name = models.CharField(max_length=40, verbose_name='指标名称', null=True)
    sis_text = models.CharField(max_length=50, verbose_name='sis测点', null=True)
    maintenance_staff = models.ForeignKey('systemsettings.MyUser', verbose_name='维护人员',related_name='指标维护人员',
                                          on_delete=models.SET('systemsettings.MyUser'))
    standard_value = models.CharField(max_length=20, verbose_name='标准值', null=True)
    upper_limit_value = models.CharField(max_length=20, verbose_name='上限值', null=True)
    lower_limit_value = models.CharField(max_length=20, verbose_name='下限值', null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    def __str__(self):
        return self.standard_name

    class Meta:
        verbose_name='指标定义详情'

# 指标填报列表
class StandardFill(models.Model):
    number = models.CharField(max_length=40, verbose_name='指标填报编号', null=True)
    describe = models.CharField(max_length=50, verbose_name='指标填报描述', null=True)
    Supervision_type = models.ForeignKey(SupervisionType, verbose_name='监督类型', on_delete=models.SET(SupervisionType),related_name='指标填报监督类型')
    state = models.CharField(max_length=20, verbose_name='状态', default='拟定')
    definition = models.ForeignKey(StandardList, on_delete=models.SET(StandardList), verbose_name='指标定义编号',related_name='指标定义编号')
    fill_time = models.DateTimeField(verbose_name='填报日期', auto_now_add=True)
    place = models.CharField(max_length=20, verbose_name='地点', null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    def __str__(self):
        return self.describe

    class Meta:
        verbose_name='指标填报列表'

# 指标填报详情
class StandardEntry(models.Model):
    standard_fill = models.ForeignKey(StandardFill, on_delete=models.SET(StandardFill), verbose_name='指标填报列表',related_name='指标填报列表')
    name = models.CharField(max_length=20, verbose_name='指标名称', null=True)
    sis_text = models.CharField(max_length=10, verbose_name='sis测点', null=True)
    maintenance_staff = models.ForeignKey('systemsettings.MyUser', verbose_name='维护人员',related_name='维护人员',
                                          on_delete=models.SET('systemsettings.MyUser'))
    last_updated_by = models.ForeignKey('systemsettings.MyUser', verbose_name='指标最后修改人', related_name='指标最后修改人',
                                        on_delete=models.SET('systemsettings.MyUser'))
    measured_value = models.CharField(max_length=20, verbose_name='测量值', null=True)
    sis_modify = models.CharField(max_length=20, verbose_name='sis修改值', null=True)
    standard_value = models.CharField(max_length=20, verbose_name='标准值', null=True)
    upper_limit_value = models.CharField(max_length=20, verbose_name='上限值', null=True)
    lower_limit_value = models.CharField(max_length=20, verbose_name='下限值', null=True)
    is_activate = models.SmallIntegerField(verbose_name='是否激活', default=1, null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name='指标填报详情'

