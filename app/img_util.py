import random
import sys
import time
import datetime
import xmltodict

from PIL import Image, ImageDraw, ImageFont, ImageFilter

_letter_cases = "abcdefghjkmnpqrstuvwxy"  # 小写字母，去除可能干扰的i，l，o，z
_upper_cases = _letter_cases.upper()  # 大写字母
_numbers = ''.join(map(str, range(3, 10)))  # 数字
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))


# PIL

def create_validate_code(size=(120, 30),
                         chars=init_chars,
                         img_type="GIF",
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(0, 0, 255),
                         font_size=18,
                         length=4,
                         draw_lines=True,
                         n_line=(1, 2),
                         draw_points=True, point_chance=2,
                         font_type="static/font/Monaco.ttf"):
    """
    @todo: 生成验证码图片
    @param size: 图片的大小，格式（宽，高），默认为(120, 30)
    @param chars: 允许的字符集合，格式字符串
    @param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    @param mode: 图片模式，默认为RGB
    @param bg_color: 背景颜色，默认为白色
    @param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
    @param font_size: 验证码字体大小
    @param font_type: 验证码字体，默认为 ae_AlArabiya.ttf
    @param length: 验证码字符个数
    @param draw_lines: 是否划干扰线
    @param n_lines: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    @param draw_points: 是否画干扰点
    @param point_chance: 干扰点出现的概率，大小范围[0, 100]
    @return: [0]: PIL Image实例
    @return: [1]: 验证码图片中的字符串
    """

    width, height = size  # 宽高
    # 创建图形
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)  # 创建画笔

    def get_chars():
        """生成给定长度的字符串，返回列表格式"""
        return random.sample(chars, length)

    def create_lines():
        """绘制干扰线"""
        line_num = random.randint(*n_line)  # 干扰线条数

        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            # 结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        """绘制干扰点"""
        chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        """绘制验证码字符"""
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

        font = ImageFont.truetype('DejaVuSans.ttf', font_size)
        font_width, font_height = font.getsize(strs)

        draw.text(((width - font_width) / 3, (height - font_height) / 3),
                  strs, font=font, fill=fg_color)

        return ''.join(c_chars)

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）

    return img, strs


from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5, SHA1, SHA256
import base64, urllib, requests, json, hashlib
from datetime import datetime
from env import KEYS, is_prod, HOST

config = {
    1: {'query': 'open.ds.phone.query',
        'order': 'open.ds.phone.order',
        'no': 'thrid_order_no',
        'param': {'callback_url': f'{HOST}callback?channel=1'},
        },
    2: {'query': 'order.query',
        'order': 'order.recharge',
        'no': 'thirdOrderNo',
        'param': {'orderNum': '1', 'userIp': '61.24.2.3'},
        'mobile': 'rechargeAccount',
        },
    3: {'query': 'queryOrder',
        'order': 'jingdongzc/makeOrder',
        'no': 'extOrderId',
        'param': {'merchantId': 'M14795', 'notifyUrl': f'{HOST}callback?channel=3'},
        'mobile': 'account',
        },
    4: {'query': 'queryOrder',
        'order': 'tianMao/makeOrder',
        'no': 'extOrderId',
        'param': {'merchantId': 'M14795', 'notifyUrl': f'{HOST}callback?channel=3'},
        'mobile': 'buyerNick',
        },
    5: {'query': 'queryOrder',
        'order': 'jyk/makeOrder',
        'no': 'extOrderId',
        'param': {'merchantId': 'M14795', 'notifyUrl': f'{HOST}callback?channel=3', 'number': '1'},
        'mobile': 'account',
        },
    6: {'query': 'query',  # 订单查询接口
        'order': 'submit',
        'no': 'orderid',
        'param': {'cpid': '9232', 'returnurl': f'{HOST}callback?channel=6', 'buynum': '1', 'buyerIp': '47.92.212.102'},
        'mobile': 'account',
        'req_method': 'form',
        },
    7: {'query': 'queryOrder',
        'order': 'extractCard/makeOrder',
        'no': 'extOrderId',
        'param': {'merchantId': 'M14795', 'notifyUrl': f'{HOST}callback?channel=3', 'buyNumber': '1'},
        },
    8: {'query': 'queryOrder',
        'order': 'woerma/makeOrder',
        'no': 'extOrderId',
        'param': {'merchantId': 'M14795', 'notifyUrl': f'{HOST}callback?channel=3', 'entityTp': '01'},
        'mobile': 'account',
        },
    9: {'query': 'open/queryOrder',
        'order': 'Open/buy',
        'no': 'serialno',
        'param': {'appId': '8002', 'notifyUrl': f'{HOST}callback?channel=9'},
        'mobile': 'uAccount',
        'req_method': 'form',
        },
    10: {'query': 'queryOrderStatusAPI',
         'order': 'sendOrderAPI',
         'no': 'bizid',
         'param': {'userid': 'P493', 'notifyurl': f'{HOST}callback?channel=10'},
         },
    11: {'query': 'api/order/query',
         'order': 'api/order/submit',
         'no': 'outOrderId',
         'param': {'appId': '6kXXaFafyO', 'callbackUrl': f'{HOST}callback?channel=11'},
         'mobile': 'uuid',
         },
    12: {'query': 'queryOrderStatusAPI',
         'order': 'sendOrderAPI',
         'no': 'bizid',
         'param': {'userid': 'P496', 'notifyurl': f'{HOST}callback?channel=10'},
         },
    13: {'query': 'queryorder',
         'order': 'submitorder',
         'no': 'sellerid',
         'param': {'agentcode': '202211111021', 'notifyurl': f'{HOST}callback?channel=13'},
         'mobile': 'account',
         },
    14: {'query': 'queryorder',
         'order': 'submitorder',
         'no': 'sellerid',
         'param': {'agentcode': '202211111148', 'notifyurl': f'{HOST}callback?channel=14'},
         'mobile': 'account',
         },
    15: {'query': 'query',
         'order': 'order',
         'no': 'outTradeNo',
         # 'param': {'merchantId': '23329', 'notifyurl': f'{HOST}callback?channel=15'},
         'param': {'merchantId': '23329', 'notifyUrl': f'{HOST}callback?channel=15'},
         'mobile': 'rechargeAccount',
         },
    16: {'query': 'Query', # 查询
         'order': 'Send',  # 下单
         'no': 'billno',   # 流水号 100000
         'param': {'userid': '100000', 'notifyUrl': f'{HOST}callback?channel=16'}, # userid 用户编号
         'mobile': 'account', # 手机号
         },#
}


class HttpBase(object):
    def __init__(self, method, param, source_id):
        self.conf = config[source_id]
        self.method = conf[method]  # query
        param[conf['no']] = param['no']  # submit
        del param['no']
        param.update(conf['param'])
        if param.get('mobile') and conf.get('mobile'):
            param[conf['mobile']] = param['mobile']
            del param['mobile']
        self.param = param

    def sign(self):
        data = [str(param[i]) for i in self.conf['sign_data'].split('+')] + [KEYS.get(3)]
        self.param['sign'] = hashlib.md5(''.join(data).encode()).hexdigest()


def do_post(method, param, appid, source_id):
    conf = config[source_id]
    method = conf[method]  # query
    param[conf['no']] = param['no']  # submit
    del param['no']
    param.update(conf['param'])
    if param.get('mobile') and conf.get('mobile'):
        param[conf['mobile']] = param['mobile']
        del param['mobile']
    if source_id in (13, 14):  # 乐充时代
        conf["req_method"] = 'form'
        # MD5.digest(userid + mobile + productid + sign)，加密方式为MD5 (32位，小写)
        if method.count('submitorder'):
            data = 'agentcode+sellerid+account+code+num+value+notifyurl+remark+time'
            param['account'] = base64.b64encode(param['account'].encode('utf-8')).decode('utf-8')
        else:
            data = 'agentcode+sellerid+time'

        param['time'] = datetime.now().strftime("%Y%m%d%H%M%S%f")
        data = [str(param[i]) for i in data.split('+')] + [KEYS.get(source_id)]
        param['sign'] = hashlib.md5(''.join(data).encode()).hexdigest()
        url = f'http://121.196.177.34:1012/api/md5/{method}'
    elif source_id == 11:  # 美嘉
        conf["req_method"] = 'form'
        # MD5.digest(userid + mobile + productid + sign)，加密方式为MD5 (32位，小写)
        if method.count('submit'):
            # appId appSecret callbackUrl itemId outOrderId timestamp uuid
            data = 'appId+appSecret+callbackUrl+itemId+outOrderId+timestamp+uuid'
        else:
            # appId orderId outOrderId timestamp
            data = 'appId+appSecret+outOrderId+timestamp'
        param['appSecret'] = KEYS.get(11)
        param['timestamp'] = datetime.now().strftime("%Y%m%d%H%M%S%f")
        postall = ''
        for i in data.split('+'):
            value = str(param[i])
            postall += i + '=' + value + '&'
        b = list(postall)
        b.pop()
        print(''.join(b))
        param['sign'] = hashlib.md5(''.join(b).encode()).hexdigest()
        url = f'http://120.79.190.232:8911/{method}'
    # 自己添加的接口 15
    elif source_id == 15:  # 自己添加的接口
        print('15-----')
        conf["req_method"] = 'form' #post 请求
        if method.count('order'):
            # appId appSecret callbackUrl itemId outOrderId timestamp uuid
            data = 'accountType+merchantId+notifyUrl+number+outTradeNo+productId+rechargeAccount+timeStamp'
        else:
            data = 'merchantId+outTradeNo+timeStamp'
        print(param)
        param['timeStamp'] = int(time.time())
        postall = ''
        for i in data.split('+'):
            print(param[i])
            value = str(param[i])
            postall += i + '=' + value + '&'
        b = list(postall)
        b.pop()
        data_str = ''.join(b) + '&key=' + KEYS.get(15)
        print(''.join(b))
        param['sign'] = hashlib.md5(data_str.encode()).hexdigest().upper()
        url = f'http://test.openapi.1688sup.cn/recharge/{method}'

    # 自己添加的接口 16
    elif source_id == 16:  # 自己添加的接口
        print('16-----')
        conf["req_method"] = 'form' #post 请求
        if method.count('Send'):
            data = 'account+billno+number+billno+productid+time+userid'
        else:
            data = 'billno+time+userid'
        param['time'] = int(time.time())
        postall = ''
        for i in data.split('+'):
            print(param[i])
            value = str(param[i])
            postall += i + '=' + value + '&'
        b = list(postall)
        b.pop()
        data_str = ''.join(b) + '&userkey=' + KEYS.get(16)
        print(''.join(b))
        param['sign'] = hashlib.md5(data_str.encode()).hexdigest().upper()
        url = f'https://api.qinameng.com:9001/GameOrder/{method}'


    # 自己添加的接口 END

    elif source_id == 10:  # 广吉、德本堂
        conf["req_method"] = 'form'
        # MD5.digest(userid + mobile + productid + sign)，加密方式为MD5 (32位，小写)
        if method.count('queryOrderStatusAPI'):
            data = 'userid+bizid'
        else:
            data = 'userid+mobile+productid'
        data = [str(param[i]) for i in data.split('+')] + [KEYS.get(10)]
        param['key'] = hashlib.md5(''.join(data).encode()).hexdigest()
        url = f'http://api.gjxnet.com/{method}'
    elif source_id == 12:  # 广吉、德本堂
        conf["req_method"] = 'form'
        # MD5.digest(userid + mobile + productid + sign)，加密方式为MD5 (32位，小写)
        if method.count('queryOrderStatusAPI'):
            data = 'userid+bizid'
        else:
            data = 'userid+mobile+productid'
        data = [str(param[i]) for i in data.split('+')] + [KEYS.get(12)]
        param['key'] = hashlib.md5(''.join(data).encode()).hexdigest()
        url = f'http://api.gjxnet.com/{method}'
    elif source_id == 9:
        param['timestamp'] = int(time.time())
        if method.count('buy'):
            data = 'appId+itemFacePrice+itemId+notifyUrl+serialno+timestamp+uAccount'
        else:
            data = 'appId+notifyUrl+serialno+timestamp'
        data = [str(param[i]) for i in data.split('+')] + [KEYS.get(9)]
        # print(data)
        param['sign'] = hashlib.md5(''.join(data).encode()).hexdigest()
        url = f'http://test.d8h.info/api/{method}'
    elif source_id in (3, 4, 5, 7, 8):  # pushang
        conf["req_method"] = 'get'
        if method.count('woerma'):
            data = 'extOrderId+account+merchantId+productId+notifyUrl'
        elif method.count('tianMao'):
            data = 'buyerNick+extOrderId+merchantId+notifyUrl+productId'
        elif method.count('jyk'):
            data = 'account+amt+extOrderId+merchantId+notifyUrl+number+type'
        elif method.count('jingdongzc'):
            data = 'extOrderId+account+merchantId+productId+verifyCode+notifyUrl'
        elif method.count('extractCard'):  # 提卡密
            data = 'buyNumber+extOrderId+merchantId+notifyUrl+productId'
        else:
            data = 'extOrderId+merchantId'
        data = [str(param[i]) for i in data.split('+')] + [KEYS.get(3)]
        # print(data)
        param['sign'] = hashlib.md5(''.join(data).encode()).hexdigest()
        if method.count('jyk'):
            param['md5'] = param['sign']
            del param['sign']
        url = f'http://api.yaajie.com:8080/api/{method}'
    elif source_id == 6:  # 软客
        # 获取当前时间戳(时间戳的数据需要转换为字符串类型的否则没办法进行md5的转换)
        if method.count('submit'):  # 直充接口
            param["createtime"] = datetime.now().strftime('%Y%m%d%H%M%S')
            data = f'cpid={param["cpid"]}&gamegoodid={param["gamegoodid"]}&createtime={param["createtime"]}&account={param["account"]}'
            data += f'&orderid={param["orderid"]}&buynum={param["buynum"]}'
        else:  # 订单查询接口
            data = f'{param["cpid"]}{param["orderid"]}'
            param['OrderID'] = param['orderid']
        data = f'{data}{KEYS.get(6)}'
        # 添加KEY值
        param['sign'] = hashlib.md5(data.encode()).hexdigest()
        url = f'https://openapi.xunyin.com/openapi/{method}'
        # 请求接口地址（后期修改为接口请求的地址 {method}：为接口的具体方法）
    elif source_id == 2:  # xinmei
        data = f'{json.dumps(param)}{KEYS.get(source_id)}'
        sign = hashlib.md5(data.encode()).hexdigest()
        url = f'https://open.doxm.net/apiRoute?appId=xm0gfe3qp571ag&appType=RECHARGE_API&charset=&format=json&method={method}&sign={sign}&signType=MD5&tmStamp={int(datetime.now().timestamp() * 1000)}&version=1.0'
    elif source_id == 1:  # taipingyongshun
        data = f'app_id={appid}&method={method}&timestamp={datetime.now().strftime("%Y%m%d%H%M%S")}&version=3.0&'
        hash_obj = SHA256.new(f'{data}{json.dumps(param)}'.encode('utf-8'))
        private_keyBytes = base64.b64decode(KEYS.get(source_id))
        priKey = RSA.importKey(private_keyBytes)
        signer = PKCS1_v1_5.new(priKey, )

        sign = urllib.parse.quote(base64.b64encode(signer.sign(hash_obj)).decode())
        url = f'http://8.140.131.56/api/rest?{data}sign={sign}'
    print('do post req:', url, param)
    try:
        return process_req(url, param, conf, source_id, method)
    except Exception as e:
        print('do post err', e)
        return 4


def process_req(url, param, conf, source_id, method):
    if not is_prod:
        return 2
    # 发起接口请求  默认为form
    if conf.get('req_method') == 'get':
        r = requests.get(url, param)
    elif conf.get('req_method') == 'form':
        r = requests.post(url, param)
    else:
        r = requests.post(url, json=param)

    # r 为接口调用后返回的结果
    print('do post res:', r, r.text)
    if r.text[0] in ('{', '['):
        r = r.json()
    else:
        r = xmltodict.parse(r.text.lower())
    if source_id == 1:
        if r['data'].get('order_status'):
            r = r['data']['order_status']
        elif r['status'] == '1':
            r = 4
    elif source_id == 2:
        if r.get('status') == '1':
            r = 2
        else:
            r = 3
        r = {'1': 2}.get(r['status'], 4)
    elif source_id in (3, 4, 5):
        if r.get('data'):
            r = {4: 2, 5: 3, 3: 1}.get(r['data'], 4)
        else:
            r = {0: 1}.get(r['code'])
    elif source_id == 6:  # 软客直充接口返回数据处理
        # 在处理返回数据的时候要注意查看返回数据的类型格式
        code = r['order'].get('code')
        # 如果为code为空的话 说明没有code这个返回值也就是说他调用的事订单查询接口，所以会有state订单状态返回值
        # 如果没有变量code的话就执行code = r['order'].get('state')
        if not code: code = r['order'].get('state')
        # {'0000': 1, '8888': 2}.get(code, 3) 从{}花括号内的对象中获得于变量code相同的
        # 即 如果code为0000 那么r为1；code为8888 r为2 若果code的数值不在对象组中的话 r默认为3
        if method.count('query'):
            from .models import Code
            Code.objects.filter(id=str(param['orderid']).split('_')[0]).update(ex_order=r['order']['orderid'])
        r = {'0000': 1, '8888': 2}.get(code, 3)
    elif source_id == 7:  # 浦上卡密接口返回数据处理
        if r.get('data'):  # 订单查询返回数据处理
            r = {4: 2, 5: 3, 3: 1}.get(r['data'], 3)
        else:  # 卡密接口返回数据处理
            r = {0: 1}.get(r['code'])
    elif source_id == 9:  # 浦上卡密接口返回数据处理
        if r.get('data'):
            r = {3: 2, -1: 3, 1: 1, 2: 1}.get(r['data'].get('status'), 4)
        else:
            r = 4
    elif source_id in (10, 12):  # 广吉
        if r['resultCode'] == 'T00002':
            r = {'2': 2, '3': 3}.get(r['resultMsg'], 1)
        else:
            r = {'T00001': 1, 'T00007': 1}.get(r['resultCode'], 3)
    elif source_id == 11:  # 美佳
        if r.get('orderStatus'):
            # ，2-充值成功，3-充值失败，1-处理中，4-未查询到订单
            r = {'2': 2, '3': 3, '1': 1, '4': 4}.get(r['orderStatus'])
        else:
            r = {'00': 1}.get(r['code'], 3)
    elif source_id in (13, 14):  # 乐充
        if r.get('state'):
            # ，2-充值成功，3-充值失败，1-处理中，4-未查询到订单
            r = {'2': 2, '-11': 3, '4': 3}.get(r['state'], 1)
        else:
            r = {'s100': 1}.get(r['recode'], 3)
    elif source_id in 15:  # 自己写的15接口
        if r.get('state'):
            # ，2-充值成功，3-充值失败，1-处理中，4-未查询到订单
            r = {'1': 1, '3': 3}.get(r['state'])
    elif source_id in 16:  # 自己写的16接口
        if r.get('orderStatus'):
            # ，0-充值成功，1-充值失败，2-处理中
            r = {'0': 0, '1': 1,'2' : 2}.get(r['orderStatus'])
    return r

# CODE_STATUS = ((0, '未使用'), (1, '已兑换'), (2, '已到账'), (3, '充值失败'), (4, '未配置规格'), (5, '兑换卡密'), (6, '过期'), (7, '待手工充值'))
