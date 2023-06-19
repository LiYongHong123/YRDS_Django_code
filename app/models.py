import json, requests, random, string
from datetime import datetime, timedelta
from django.db import models
from env import DING_TOKEN, appid
from .img_util import do_post, init_chars
from ckeditor.fields import RichTextField

FMT = '%Y-%m-%d %H:%M:%S'


class Product(models.Model):
    name = models.CharField('商品名', max_length=50)
    param = models.CharField('参数', default='', blank=True, max_length=50)
    # remark = models.TextField('兑换说明', blank=True, default='')
    remark = RichTextField('兑换说明', blank=True, default='')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

    def __str__(self):
        return self.name


class Sku(models.Model):
    name = models.CharField('面额名称', max_length=50)
    product = models.ForeignKey(Product, models.CASCADE, verbose_name='所属商品')
    enable = models.BooleanField('可用', default=True)
    stock = models.IntegerField('最小库存', default=0)
    token = models.CharField('消息推送Token', null=True, blank=True, default=None, max_length=250)
    at = models.CharField('At手机号', null=True, blank=True, default=None, max_length=500)
    param = models.CharField(max_length=250, null=True, blank=True, default=None)

    class Meta:
        verbose_name = '面额'
        verbose_name_plural = '面额'

    def check_stock(self, force=False):
        if self.stock > 0:
            cnt = OutCard.objects.filter(sku_id=self.id, status=0).count()
            if cnt < self.stock:
                send_msg(f'{self}库存{cnt}不足{self.stock}', self.token, self.at)
            elif force:
                send_msg(f'{self}库存{cnt}最小库存{self.stock}', self.token, self.at)
            

    def __str__(self):
        return f'{self.product}-{self.name}'

#修改、添加的时候记得修改  admin.py 的导出的数据 切记！！！！！！
SOURCE = ((0, '南京立方'), (1, '北京太平永顺'), (2, '新美科技'), (3, '浦上京东直充,接口21'), (4, '浦上淘宝直充,接口11'), (5,'浦上加油卡,接口4'), (6,'软客直冲,接口2.2'), (7, '未知通道'), (8, '浦上京东直充,接口22' ), (9, '渡渡鸟,直充接口1.2' ),(10, '广吉' ),(11,'美佳（未税）'),(12,'本康堂（未税）'),(13,'乐充时代-德森'),(14,'乐充时代-永好'),(15,'xxxx-xx'),(16,"好利来-好利来"))
STATUS = ((0, '自动'), (1, '手工'))
class Channel(models.Model):
    sku = models.ForeignKey(Sku, models.CASCADE)
    source_id = models.IntegerField(default=0, choices=SOURCE)
    param = models.CharField(max_length=250)
    status = models.IntegerField(default=0, choices=STATUS)


class Consumer(models.Model):
    name = models.CharField('客户名称', max_length=50)
    password = models.TextField('客户密码', null=True, default=None)
    appid = models.CharField('业务id', null=True, blank=True, default=None, max_length=250)
    token = models.CharField('消息推送Token', null=True, blank=True, default=None, max_length=250)
    at = models.CharField('At手机号', null=True, blank=True, default=None, max_length=500)

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        return self.name

Activity_STATUS = ((0, '进行中'), (1, '活动停止'))
class Activity(models.Model):
    name = models.CharField('活动名称', max_length=50)
    consumer = models.ForeignKey(Consumer, models.CASCADE, verbose_name='客户')
    skus = models.CharField('活动商品', max_length=1024)
    due_time = models.DateTimeField('到期时间', default=None, null=True, blank=True)
    status = models.IntegerField('活动状态', default=0, choices=Activity_STATUS)
    down_price = models.FloatField('下游价格', default=None, null=True, blank=True)

    class Meta:
        verbose_name = '活动'
        verbose_name_plural = '活动'

    def __str__(self):
         return f'{self.consumer}--{self.name}'


CODE_STATUS = ((0, '未使用'), (1, '已兑换'), (2, '已到账'), (3, '充值失败'), (4, '未配置规格'), (5, '兑换卡密'), (6, '过期'), (7, '待手工充值'),(8, '待充值'))
class Code(models.Model):
    name = models.CharField('权益券码', max_length=50, unique=True)
    activity = models.ForeignKey(Activity, models.CASCADE, verbose_name='所属活动')
    status = models.IntegerField('状态', default=0, choices=CODE_STATUS)
    sku = models.ForeignKey(Sku, models.SET_NULL, default=None, null=True, blank=True, verbose_name='兑换商品')
    account = models.CharField('使用账号', max_length=500, null=True, blank=True)
    ex_id = models.IntegerField('上游通道', default=None, null=True, blank=True, choices=SOURCE)
    ex_order = models.CharField('上游单号', max_length=500, default='', null=True, blank=True)
    use_time = models.DateTimeField('兑换时间', default=None, null=True, blank=True)
    finish_time = models.DateTimeField('到账时间', default=None, null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    retry = models.IntegerField('重试次数', default=0)
    ex_phone = models.CharField('联系方式', max_length=500, default=None, null=True, blank=True)

    class Meta:
        verbose_name = '权益券'
        verbose_name_plural = '权益券'
        permissions = (
            ("service", u"客服权限"),
        )
    def post_order(self, sku=None, account=None, ext={}):
        if self.sku_id == None and self.account == None:
            self.sku_id = sku
            self.account = account
            self.use_time = datetime.now()
        if self.status in (1, 2) or self.sku_id == None:
            return
        consumer = self.activity.consumer
        app_id = consumer.appid or appid
        qs = Channel.objects.filter(sku_id=self.sku_id)
        channel = None
        if qs.count() == 1:
            channel = qs[0]
            for i in range(self.retry):
                r = do_post('query', {'no': f'{self.id}_{i}' if i else self.id}, app_id, channel.source_id)
                if r in (1, 2):  # (1, '已兑换'), (2, '已到账')
                    self.update_status(r)
                    return
        self.status = 1
        self.save()
        if channel:
            if channel.status != 0 and self.retry == 0: # 手工充值
                self.status = 7
                self.save()
                return
            param = json.loads(channel.param)
            param.update(ext)
            no = f'{self.id}_{self.retry}' if self.retry else self.id
            # send_msg(f'手机号:[{self.account}],订单号:[{no}]开始充值')
            param.update({'no': no, 'mobile': self.account})
            r = do_post('order', param, app_id, channel.source_id)
            # 更改上游通道
            self.ex_id = channel.source_id;
            self.save()
            if r == 4: # (4, '未配置规格')
                self.status = r
                self.save()
                send_msg(f'手机号:[{self.account}],订单号:[{no}]充值请求失败.响应:{json.dumps(r)}', consumer.token, consumer.at)
        else:
            qs = OutCard.objects.filter(sku_id=self.sku_id, status=0)
            if qs.count():
                out = qs[0]
                out.use(self)
                self.status = 5
                self.account = out.name
                self.save()
            else:
                Sku.objects.filter(id=self.sku_id).update(enable=False)
                self.sku_id = self.account = None
                self.status = 0
                self.save()
                print(self.sku_id, sku)
                return '库存不足'
            
    def change_style(self):
        #修改订单状态-》待充值
        self.status=8;#修改状态 8为待充值状态
        self.save();#保存到数据库中

    def post_order_recharge(self):
        self.account = None
        self.sku = None
        self.retry += 1
        self.use_time = None
        self.status = 0
        self.ex_id = None
        self.finish_time = None
        self.save();  # 保存到数据库中
        print('id：' + self.id + '到账时间：' + self.finish_time + '兑换时间' + self.use_time + '上游通道：' + self.ex_id)


    def update_status(self, status):
        self.status = status
        if status == 2:
            self.finish_time = datetime.now()
            # send_msg(f'手机号:[{self.account}]充值成功')
        else:
            consumer = self.activity.consumer
            send_msg(f'手机号:[{self.account}]充值失败', consumer.token, consumer.at)
        self.save()


class OutCard(models.Model):
    name = models.CharField('卡密,分割', max_length=250, unique=True)
    sku = models.ForeignKey(Sku, models.SET_NULL, null=True, verbose_name='兑换商品')
    code = models.ForeignKey(Code, models.SET_NULL, default=None, null=True, blank=True, verbose_name='内部卡密')
    use_time = models.DateTimeField('兑换时间', default=None, null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    status = models.IntegerField('状态', default=0, choices=CODE_STATUS)
    expire_time = models.DateTimeField('过期时间', default=datetime(2022,8,19))

    class Meta:
        verbose_name = '外部卡密'
        verbose_name_plural = '外部卡密'

    def use(self, code):
        self.code = code
        self.use_time = datetime.now()
        self.status = 1
        self.save()
        if self.sku_id:
            try:
                self.sku.check_stock()
            except:
                pass


class DongCard(models.Model):
    activity = models.ForeignKey(Activity, models.CASCADE, verbose_name='所属活动')
    consumer = models.ForeignKey(Consumer, models.CASCADE, verbose_name='客户')
    cardCode = models.CharField('卡券产品编号', max_length=50, primary_key=True)
    cardName = models.CharField('卡券名称', max_length=50)
    synchro = models.IntegerField('券商出码方式', default=1, choices=((1,'实时出码'),(2,'延时出码')))
    style = models.BooleanField('卡券状态', default=True, choices=((True, '可用'), (False, '停用')))
    autoOut = models.BooleanField('直接外部卡密', default=False)
    faceAmt = models.IntegerField('卡券面值(元)', null=True, blank=True)
    productPrice = models.IntegerField('券商协议价格(元)')
    listImg = models.CharField('列表图', max_length=150)
    detailImg = models.CharField('详情图', max_length=150)
    baseMapImg = models.CharField('底图', max_length=150, null=True, blank=True)
    cardDesc = models.TextField('产品介绍')
    codeValidity = models.CharField('有效期yyyy-MM-dd HH:mm:ss', max_length=50, null=True, blank=True)
    remark = models.CharField('附加内容', max_length=150, null=True, blank=True)

    class Meta:
        verbose_name = '东莞卡券基本信息'
        verbose_name_plural = '东莞卡券基本信息'

    def to_dict(self):
        return {'cardCode': self.cardCode, 'cardName': self.cardName, 'synchro': self.synchro,'style': self.style, 'faceAmt': self.faceAmt, 'productPrice': self.productPrice, 'listImg': self.listImg, 'detailImg': self.detailImg, 'baseMapImg': self.baseMapImg, 'cardDesc': self.cardDesc}


class DongOrder(models.Model):
    submitTimestamp = models.CharField('请求时间戳', max_length=50)
    consumer = models.ForeignKey(Consumer, models.CASCADE, verbose_name='客户')
    card = models.ForeignKey(DongCard, models.CASCADE, verbose_name='卡券批次号')
    orderId = models.CharField('换购订单号', max_length=50)
    orderQuantity = models.IntegerField('换购数量')
    orderTime = models.CharField('换购时间', max_length=50)
    orderPrice = models.IntegerField('换购总金额')
    orderPoints = models.IntegerField('换购积分数')
    ext = models.TextField('扩展域')
    exchangeCode = models.TextField('兑换编码', null=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '东莞订单信息'
        verbose_name_plural = '东莞订单信息'

    def to_dict(self):
        return {'orderId': self.orderId, 'wnOrderId': self.id, 'retResult': '0000', 'exchangeCode': self.exchangeCode, 'codeValidity': self.card.codeValidity, 'remark': self.card.remark, 'exchangeLink': ''} 


def send_msg(msg, token=None, at=None):
    if token == None: token=DING_TOKEN
    at = [] if at == None else at.split(',')
    try:
        r = requests.post(f'https://oapi.dingtalk.com/robot/send?access_token={token}', json={'msgtype': 'text','text': {'content':msg}, 'at': {'atMobiles': at}})
        print('send_msg:', msg, r, r.text)
    except:
        print('send_msg error')


def gen_code(activity, length=16):
    s = random.sample(init_chars, length)
    try:
        code = Code(None, ''.join(s), activity)
        code.save()
        return code
    except:
        return gen_code(activity)






