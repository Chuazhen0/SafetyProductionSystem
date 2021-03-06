# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.db import migrations, models
import django.db.models.deletion
import weekworkplan.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('weekworkplan', '0001_initial'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeekWorkTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('created_at', models.DateTimeField(verbose_name='创建时间')),
                ('last_updated_at', models.DateTimeField(verbose_name='最后更新时间')),
                ('enclosure', models.FileField(null=True, upload_to='Plan/', verbose_name='附件')),
                ('is_activate', models.SmallIntegerField(default=1, null=True, verbose_name='是否激活')),
                ('number', models.CharField(max_length=30, verbose_name='周期检测任务编码')),
                ('task_start_time', models.DateField(verbose_name='计划开始时间')),
                ('time_limit', models.CharField(max_length=10, verbose_name='完成时限')),
                ('created_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='周期检测任务创建人', to='systemsettings.MyUser', verbose_name='创建人')),
                ('last_updated_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='周期检测任务最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人')),
                ('pinstance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='weekworktask', to='lbworkflow.ProcessInstance', verbose_name='Process instance')),
                ('place', models.ForeignKey(on_delete=models.SET('systemsettings.Company'), to='systemsettings.Company', verbose_name='公司名称')),
                ('plan', models.ForeignKey(on_delete=models.SET(weekworkplan.models.WeekWorkPlan), related_name='周期检测计划名称', to='weekworkplan.WeekWorkPlan', verbose_name='周期检测计划名称')),
            ],
            options={
                'verbose_name': '周期检测任务',
            },
        ),
    ]
