# Generated by Django 3.2.10 on 2021-12-26 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': '活动', 'verbose_name_plural': '活动'},
        ),
        migrations.AlterModelOptions(
            name='code',
            options={'verbose_name': '卡密', 'verbose_name_plural': '卡密'},
        ),
        migrations.AlterModelOptions(
            name='consumer',
            options={'verbose_name': '客户', 'verbose_name_plural': '客户'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': '商品', 'verbose_name_plural': '商品'},
        ),
        migrations.AlterModelOptions(
            name='sku',
            options={'verbose_name': '面额', 'verbose_name_plural': '面额'},
        ),
        migrations.AddField(
            model_name='code',
            name='sku',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.sku', verbose_name='所属活动'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.consumer', verbose_name='客户'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(max_length=50, verbose_name='活动名称'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='skus',
            field=models.CharField(max_length=1024, verbose_name='活动商品'),
        ),
        migrations.AlterField(
            model_name='code',
            name='account',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='使用账号'),
        ),
        migrations.AlterField(
            model_name='code',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.activity', verbose_name='所属活动'),
        ),
        migrations.AlterField(
            model_name='code',
            name='name',
            field=models.CharField(max_length=50, verbose_name='卡密'),
        ),
        migrations.AlterField(
            model_name='code',
            name='status',
            field=models.IntegerField(choices=[(0, '正常'), (1, '停用')], default=0, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='name',
            field=models.CharField(max_length=50, verbose_name='客户名称'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=50, verbose_name='商品名'),
        ),
        migrations.AlterField(
            model_name='sku',
            name='name',
            field=models.CharField(max_length=50, verbose_name='面额名称'),
        ),
        migrations.AlterField(
            model_name='sku',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product', verbose_name='所属商品'),
        ),
    ]
