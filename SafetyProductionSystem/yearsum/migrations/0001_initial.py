# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='YearSum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('sum_desc', models.CharField(max_length=200, verbose_name='总结描述')),
                ('sum_type', models.CharField(default='年度总结', max_length=5, verbose_name='总结类型')),
                ('year', models.CharField(max_length=10, verbose_name='年份')),
                ('state', models.CharField(default='新建', max_length=10, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_updated_at', models.DateTimeField(auto_now_add=True, verbose_name='最后更新时间')),
                ('enclosure', models.FileField(null=True, upload_to='Plan/', verbose_name='附件')),
                ('is_activate', models.SmallIntegerField(default=1, null=True, verbose_name='是否激活')),
                ('work_type', models.CharField(default='年度总结', max_length=10, verbose_name='工单类型')),
                ('created_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='年度总结创建人', to='systemsettings.MyUser', verbose_name='创建人')),
                ('last_updated_by', models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='年度总结最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人')),
                ('pinstance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='yearsum', to='lbworkflow.ProcessInstance', verbose_name='Process instance')),
                ('place', models.ForeignKey(on_delete=models.SET('systemsettings.Company'), to='systemsettings.Company', verbose_name='公司名称')),
            ],
            options={
                'verbose_name': '年度总结',
            },
        ),
    ]
