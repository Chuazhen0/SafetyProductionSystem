# Generated by Django 2.0.5 on 2018-10-08 09:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myform', '0028_auto_20181006_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myform',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2018, 10, 8, 9, 13, 9, 647661), verbose_name='创建时间'),
        ),
    ]
