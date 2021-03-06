# Generated by Django 2.0.5 on 2018-08-06 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import regularworkplan.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('regularworkplan', '0001_initial'),
        ('lbworkflow', '0002_auto_20171019_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegularWorkTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('result', models.CharField(max_length=200, null=True, verbose_name='定期工作任务完成情况')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('pinstance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='regularworktask', to='lbworkflow.ProcessInstance', verbose_name='Process instance')),
                ('regularwork', models.ForeignKey(on_delete=models.SET(regularworkplan.models.RegularWorkPlan), to='regularworkplan.RegularWorkPlan', verbose_name='定期工作任务')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
