# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.db import migrations, models
import django.db.models.deletion
import mon_plan_sum.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        ('monworkexe', '0001_initial'),
        ('mon_plan_sum', '0002_auto_20180806_1423'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='monworkexe',
            name='created_by',
            field=models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='月度工作执行创建人', to='systemsettings.MyUser', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='execute_user',
            field=models.ForeignKey(null=True, on_delete=models.SET('systemsettings.MyUser'), related_name='月度工作执行人', to='systemsettings.MyUser', verbose_name='执行人'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='last_updated_by',
            field=models.ForeignKey(on_delete=models.SET('systemsettings.MyUser'), related_name='月度工作执行最后更新人', to='systemsettings.MyUser', verbose_name='最后更新人'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='pinstance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monworkexe', to='lbworkflow.ProcessInstance', verbose_name='Process instance'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='place',
            field=models.ForeignKey(on_delete=models.SET('systemsettings.Company'), related_name='月度工作执行公司名称', to='systemsettings.Company', verbose_name='公司名称'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='plan_number',
            field=models.ForeignKey(on_delete=models.SET(mon_plan_sum.models.MonPlanSum), related_name='月度计划编码', to='mon_plan_sum.MonPlanSum', verbose_name='月度计划编码'),
        ),
        migrations.AddField(
            model_name='monworkexe',
            name='plan_smallnumber',
            field=models.ForeignKey(on_delete=models.SET(mon_plan_sum.models.SmallDatas), related_name='月度计划记录号', to='mon_plan_sum.SmallDatas', verbose_name='月度计划记录号'),
        ),
    ]
