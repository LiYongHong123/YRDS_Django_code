# Generated by Django 3.2.12 on 2022-03-17 23:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_product_param'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='remark',
            field=models.TextField(default='', verbose_name='兑换说明'),
        ),
        migrations.CreateModel(
            name='OutCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='卡密,分割')),
                ('use_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='兑换时间')),
                ('status', models.IntegerField(choices=[(0, '未使用'), (1, '已兑换'), (2, '已到账'), (3, '充值失败'), (4, '未配置规格')], default=0, verbose_name='状态')),
                ('code', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.code', verbose_name='内部卡密')),
                ('sku', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.sku', verbose_name='兑换商品')),
            ],
            options={
                'verbose_name': '外部卡密',
                'verbose_name_plural': '外部卡密',
            },
        ),
    ]