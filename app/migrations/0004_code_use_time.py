# Generated by Django 3.2.10 on 2021-12-26 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20211226_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='use_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='使用时间'),
        ),
    ]
