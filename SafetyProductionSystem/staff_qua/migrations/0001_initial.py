# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.db import migrations, models
import lbworkflow.models.runtime
import qua25.models
import systemsettings.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('qua25', '0003_qua_qua_type'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffQua',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('number', models.CharField(max_length=30, verbose_name='人员资质对应编码')),
                ('state', models.CharField(default='新建', max_length=5, verbose_name='状态')),
                ('created_at', models.DateTimeField(verbose_name='创建时间')),
                ('last_updated_at', models.DateTimeField(verbose_name='最后更新时间')),
                ('is_activate', models.SmallIntegerField(default=1, null=True, verbose_name='是否激活')),
                ('effect_time', models.DateField(verbose_name='有效日期')),
                ('qua_enclosure', models.FileField(null=True, upload_to='', verbose_name='资质扫描件')),
                ('created_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='技术监督资质创建人', to='systemsettings.MyUser', verbose_name='创建人')),
                ('last_updated_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='资质维护明细最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人')),
                ('pinstance', models.ForeignKey(null=True, on_delete=models.SET(lbworkflow.models.runtime.ProcessInstance), related_name='技术监督人员资质对应流程', to='lbworkflow.ProcessInstance', verbose_name='流程编号')),
                ('place', models.ForeignKey(on_delete=models.SET('systemsettings.Company'), related_name='技术监督人员资质公司名称', to='systemsettings.Company', verbose_name='公司名称')),
                ('publisher', models.ForeignKey(on_delete=models.SET('systemsettings.Department'), related_name='技术监督资质发证单位', to='systemsettings.Department', verbose_name='发证单位')),
                ('qua', models.ForeignKey(on_delete=models.SET(qua25.models.Qua), related_name='技术监督资质', to='qua25.Qua', verbose_name='资质')),
                ('supervision_major', models.ForeignKey(on_delete=models.SET(systemsettings.models.SupervisionType), related_name='技术监督资质监督专业', to='systemsettings.SupervisionType', verbose_name='监督专业')),
                ('user', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='技术监督资质对应人员', to='systemsettings.MyUser', verbose_name='人员')),
            ],
            options={
                'verbose_name': '人员资质对应表',
            },
        ),
    ]
