# Generated by Django 2.0.5 on 2018-08-15 09:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myform', '0010_auto_20180811_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myform',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2018, 8, 15, 9, 26, 53, 74491), verbose_name='创建时间'),
        ),
    ]
