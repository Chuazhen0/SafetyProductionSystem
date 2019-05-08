# Generated by Django 2.0.5 on 2019-02-28 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemsettings', '0005_merge_20190227_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='mygroup',
            name='spare1',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='备用字段1'),
        ),
        migrations.AddField(
            model_name='mygroup',
            name='spare2',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='备用字段2'),
        ),
        migrations.AddField(
            model_name='supervisiontype',
            name='form_use',
            field=models.CharField(max_length=10, null=True, verbose_name='报表使用'),
        ),
    ]
