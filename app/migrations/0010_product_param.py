# Generated by Django 3.2.12 on 2022-03-17 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_dongorder_exchangecode'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='param',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='参数'),
        ),
    ]