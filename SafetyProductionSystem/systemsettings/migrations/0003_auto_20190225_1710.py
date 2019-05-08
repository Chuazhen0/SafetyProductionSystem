# Generated by Django 2.0.5 on 2019-02-25 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemsettings', '0002_supervisiontype_form_use'),
    ]

    operations = [
        migrations.AddField(
            model_name='mygroup',
            name='duty_user',
            field=models.ManyToManyField(blank=True, null=True, to='systemsettings.MyUser', verbose_name='对应人员'),
        ),
        migrations.AlterField(
            model_name='mygroup',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='责任组名称'),
        ),
        migrations.AlterField(
            model_name='mygroup',
            name='number',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='责任组编号'),
        ),
    ]
