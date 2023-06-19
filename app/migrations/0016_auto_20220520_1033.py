# Generated by Django 3.2.12 on 2022-05-20 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20220519_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcard',
            name='expire_time',
            field=models.DateTimeField(default='2022-08-19', verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='sku',
            name='stock',
            field=models.IntegerField(default=0, verbose_name='最小库存'),
        ),
        migrations.AddField(
            model_name='sku',
            name='token',
            field=models.CharField(default=None, max_length=50, null=True, verbose_name='消息推送'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='source_id',
            field=models.IntegerField(choices=[(0, '南京立方'), (1, '北京太平永顺'), (2, '新美科技')], default=0),
        ),
        migrations.AlterField(
            model_name='code',
            name='status',
            field=models.IntegerField(choices=[(0, '未使用'), (1, '已兑换'), (2, '已到账'), (3, '充值失败'), (4, '未配置规格'), (5, '兑换卡密'), (6, '过期')], default=0, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='outcard',
            name='status',
            field=models.IntegerField(choices=[(0, '未使用'), (1, '已兑换'), (2, '已到账'), (3, '充值失败'), (4, '未配置规格'), (5, '兑换卡密'), (6, '过期')], default=0, verbose_name='状态'),
        ),
    ]