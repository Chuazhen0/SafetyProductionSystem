# Generated by Django 2.0.5 on 2018-10-06 14:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myform', '0026_auto_20180907_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myform',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2018, 10, 6, 14, 55, 18, 660119), verbose_name='创建时间'),
        ),
    ]
