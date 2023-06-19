# Generated by Django 3.2.12 on 2022-05-20 13:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20220520_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='sku',
            name='at',
            field=models.CharField(default=None, max_length=500, null=True, verbose_name='At手机号'),
        ),
        migrations.AlterField(
            model_name='outcard',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 19, 0, 0), verbose_name='创建时间'),
        ),
    ]