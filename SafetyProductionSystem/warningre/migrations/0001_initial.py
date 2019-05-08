# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.db import migrations, models
import django.db.models.deletion
import warning.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('warning', '0001_initial'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarningReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('state', models.CharField(default='新建', max_length=10, verbose_name='状态')),
                ('number', models.CharField(max_length=30, verbose_name='告警回执单编码')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_updated_at', models.DateTimeField(auto_now_add=True, verbose_name='最后更新时间')),
                ('work_type', models.CharField(default='告警回执', max_length=10, verbose_name='工单类型')),
                ('enclosure', models.FileField(null=True, upload_to='Warning/', verbose_name='附件')),
                ('content', models.CharField(max_length=200, null=True, verbose_name='回执内容')),
                ('result', models.CharField(max_length=200, verbose_name='回执结果')),
                ('is_activate', models.SmallIntegerField(default=1, null=True, verbose_name='是否激活')),
                ('created_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='告警回执单创建人', to='systemsettings.MyUser', verbose_name='回执人')),
                ('last_updated_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), to='systemsettings.MyUser', verbose_name='告警回执单最后更新人')),
                ('pinstance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='warningreceipt', to='lbworkflow.ProcessInstance', verbose_name='Process instance')),
                ('place', models.ForeignKey(on_delete=models.SET('systemsettings.Company'), to='systemsettings.Company', verbose_name='公司名称')),
                ('warning_notice', models.ForeignKey(on_delete=models.SET(warning.models.WarningNotice), to='warning.WarningNotice', verbose_name='关联告警通知单')),
            ],
            options={
                'verbose_name': '告警回执单',
            },
        ),
    ]
