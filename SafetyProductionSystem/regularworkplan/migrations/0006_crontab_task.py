# Generated by Django 2.0.5 on 2018-08-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regularworkplan', '0005_auto_20180816_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='crontab_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekdesc', models.CharField(max_length=10, verbose_name='定期描述')),
                ('num1', models.CharField(default='0', max_length=50, null=True, verbose_name='周期描述11')),
                ('num2', models.CharField(default='0', max_length=50, null=True, verbose_name='周期描述22')),
                ('myid', models.IntegerField(verbose_name='定期工作策划id')),
                ('is_activate', models.SmallIntegerField(default=1, verbose_name='是否激活')),
            ],
        ),
    ]
