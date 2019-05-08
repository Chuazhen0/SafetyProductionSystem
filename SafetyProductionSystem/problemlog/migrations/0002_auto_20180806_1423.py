# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import systemsettings.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systemsettings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problemlog', '0001_initial'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemlog',
            name='KKS_code',
            field=models.ForeignKey(on_delete=models.SET(systemsettings.models.KKS), to='systemsettings.KKS', verbose_name='KKS编码'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='abard_user',
            field=models.ForeignKey(on_delete=models.SET(systemsettings.models.MyUser), related_name='问题整改人', to='systemsettings.MyUser', verbose_name='整改人'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='dis_user',
            field=models.ForeignKey(on_delete=models.SET(systemsettings.models.MyUser), related_name='问题发现人', to='systemsettings.MyUser', verbose_name='发现人'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='pinstance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problemlog', to='lbworkflow.ProcessInstance', verbose_name='Process instance'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='place',
            field=models.ForeignKey(on_delete=models.SET(systemsettings.models.Company), to='systemsettings.Company', verbose_name='公司名称'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='stard',
            field=models.ForeignKey(null=True, on_delete=models.SET(systemsettings.models.Stard), to='systemsettings.Stard', verbose_name='相关标准号'),
        ),
        migrations.AddField(
            model_name='problemlog',
            name='tar_pro',
            field=models.ForeignKey(null=True, on_delete=models.SET(systemsettings.models.EquipmentMajor), to='systemsettings.EquipmentMajor', verbose_name='问题涉及专业'),
        ),
    ]
