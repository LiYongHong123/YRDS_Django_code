# Generated by Django 3.2.12 on 2022-07-27 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20220727_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='ex_phone',
            field=models.CharField(blank=True, default=None, max_length=500, null=True, verbose_name='联系方式'),
        ),
        migrations.AddField(
            model_name='sku',
            name='param',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
    ]