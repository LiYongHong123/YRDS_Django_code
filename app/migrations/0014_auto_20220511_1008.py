# Generated by Django 3.2.12 on 2022-05-11 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20220509_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumer',
            name='password',
            field=models.TextField(default=None, null=True, verbose_name='客户密码'),
        ),
        migrations.AlterField(
            model_name='product',
            name='remark',
            field=models.TextField(blank=True, default='', verbose_name='兑换说明'),
        ),
    ]
