# Generated by Django 3.2.10 on 2022-01-15 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_code_update_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='finish_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='到账时间'),
        ),
        migrations.AlterField(
            model_name='code',
            name='use_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='兑换时间'),
        ),
    ]
