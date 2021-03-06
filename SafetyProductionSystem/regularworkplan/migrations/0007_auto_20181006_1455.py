# Generated by Django 2.0.5 on 2018-10-06 14:55

from django.db import migrations, models
import regularworkplan.models


class Migration(migrations.Migration):

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('regularworkplan', '0006_crontab_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='工作数据序号')),
                ('data_name', models.CharField(max_length=50, null=True, verbose_name='数据名称')),
                ('data_value', models.CharField(max_length=50, null=True, verbose_name='数据标准值')),
                ('place', models.ForeignKey(null=True, on_delete=models.SET('systemsettings.Company'), related_name='工作数据公司单位名称', to='systemsettings.Company', verbose_name='公司名称')),
                ('regular_work', models.ForeignKey(on_delete=models.SET(regularworkplan.models.RegularWorkPlan), to='regularworkplan.RegularWorkPlan', verbose_name='定期工作策划')),
            ],
        ),
        migrations.RemoveField(
            model_name='prework',
            name='KKS',
        ),
        migrations.RemoveField(
            model_name='workcare',
            name='KKS',
        ),
        migrations.RemoveField(
            model_name='workcontent',
            name='KKS',
        ),
        migrations.AddField(
            model_name='prework',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='prework',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='工作准备创建人', to='systemsettings.MyUser', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='prework',
            name='last_updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='最后更新时间'),
        ),
        migrations.AddField(
            model_name='prework',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='工作准备最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人'),
        ),
        migrations.AddField(
            model_name='workcare',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='workcare',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='注意事项创建人', to='systemsettings.MyUser', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='workcare',
            name='last_updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='最后更新时间'),
        ),
        migrations.AddField(
            model_name='workcare',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='注意事项最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人'),
        ),
        migrations.AddField(
            model_name='workcontent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='workcontent',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='工作内容创建人', to='systemsettings.MyUser', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='workcontent',
            name='last_updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='最后更新时间'),
        ),
        migrations.AddField(
            model_name='workcontent',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='工作内容最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人'),
        ),
    ]
