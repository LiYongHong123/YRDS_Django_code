import json, requests
import hashlib
import time
from datetime import datetime
from collections import defaultdict
from io import BytesIO

from Crypto.Cipher import DES3
import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count

from .img_util import create_validate_code, do_post
from .models import *
from env import appid, KEYS

def index(request):
    res = {}
    if request.POST:
        res = json.loads(json.dumps(request.POST))
        session_code = request.session.get('valid_code', '').upper()
        request.session['valid_code'] = 'no'
        qs = Code.objects.filter(name=request.POST['name'].strip())
        '''
        if session_code != 'OK' and request.POST.get('code','').upper() != session_code:
            res['msg'] = '验证码不正确'
        el
        '''
        if request.POST['name'].count('-') or qs.count() != 1:
            res['msg'] = '卡密不正确'
        elif qs.filter(status=6).count() == 1:
            #staus 为6的时候代表着 该卡券已经过期
            res['msg'] = '卡券过期'
        elif qs.filter(status=0).count() != 1:
            title = {2: '已经到账', 3: '兑换失败', 4: '兑换失败'}.get(qs[0].status, '已经兑换')
            return __code_use(qs[0], title)
        else:
            request.session['valid_code'] = 'ok'
            return __code_show(qs[0])
    return render(request, 'index.html', res)


def __code_use(code, head):
    if code.status == 5: # 外部卡密
        is_link = code.account.startswith('http://') or code.account.startswith('https://')
        return render(None, 'info.html', {'activity': code.activity.name, 'account': code.account, 'remark': code.sku.product.remark, 'is_link': is_link})
    param = '手机号' if code.sku.product.param.count('phone') else '账号'
    retry = 0
    if head.count('失败') and code.sku.product.param.count('msgCode'):
        retry = code.id
    return render(None, 'succ.html', {'head': head, 'account': code.account,  'remark': code.sku.product.remark, 'param': param, 'retry': retry})

def __code_show(code, msg=None):
    sku = list({'id': i.id, 'name': i, 'param': i.product.param, 'enable': i.enable, 'remark': i.product.remark} for i in Sku.objects.filter(id__in=code.activity.skus.split(',')))
    return render(None, 'code.html', {'activity': code.activity.name, 'sku': sku, 'name': code.name, 'msg': msg})

def use(request):
    if not request.POST:
        return redirect('.')
    code = Code.objects.get(name=request.POST['name'])
    sku = request.POST['sku']
    if code.status == 0 and code.activity.skus.split(',').count(sku) == 1:
        ext = {}
        if request.POST.get('msgCode'):
            ext['verifyCode'] = request.POST['msgCode']
        # 如果有jdsign这个值说明是广吉的京东 广吉只需要短信签名不需要验证吗
        if request.POST.get('jdsign'):
            ext['extmsg'] = request.POST['jdsign']
            del ext['verifyCode']
        msg = code.post_order(sku, request.POST.get('account'), ext)
        if msg == None:
            if Channel.objects.filter(sku_id=sku).count()!=0:
                param = json.loads(Channel.objects.filter(sku_id=sku)[0].param)
                #将通道的sku数据中的商品编号进行传递
                i = 0
                for sku in param.get('sku', []):
                    i += 1
                    code_name = f'{code.name}-{i}'
                    if Code.objects.filter(name=code_name).count() != 0:
                        continue
                    code = Code(None, code_name, code.activity_id)
                    code.save()
                    msg = code.post_order(sku, request.POST.get('account'))
            return __code_use(code, '兑换成功')
    else:
        msg = '权益券已兑换'
    return __code_show(code, msg)


def retry(request):
    qs = Code.objects.filter(id=request.GET.get('id'))
    if qs.count() == 1:
        code = qs[0]
        if code.status == 3 and code.sku.product.param.count('msgCode'):
            code.status = 0
            code.retry += 1
            code.save()
    return redirect('.')


def code(request):
    """
    获取验证码
    :param request:
    :return:
    """
    stream = BytesIO()
    # 生成图片 img、数字代码 code，保存在内存中，而不是 Django 项目中
    img, code = create_validate_code()
    img.save(stream, 'PNG')

    # 写入 session
    request.session['valid_code'] = code
    return HttpResponse(stream.getvalue())


def msgCode(request):
    verifyCode = request.POST.get('msgCode')
    sku = request.POST.get('sku')
    r = {}  # 存放返回结果
    param = {}  # 存放参数
    # 需要根据面额id获取到该面额要走的通道id
    channel_id = Channel.objects.filter(sku_id=sku).values_list('source_id')[0][0];
    account = request.POST['account']
    if (channel_id == 10):
        url = 'http://api.gjxnet.com/'
        param['timestamp'] = int(time.time())
        param['mobile'] = account
        param['userid'] = 'P493'
        if verifyCode:
            data = 'userid+mobile+timestamp'
            param['verifyCode'] = verifyCode
            param['jdsign'] = request.POST.get('jdsign')
            data = [str(param[i]) for i in data.split('+')] + [KEYS.get(10)]
            param['key'] = hashlib.md5(''.join(data).encode()).hexdigest()
            print(f'req to {url}checkjShortMessage,param:',param )
            rue = requests.get(f'{url}checkjShortMessage', param)
            print('res',rue, rue.text)
            rue = rue.json()
            # print(1, r, f'>{verifyCode}<')
            if (rue['resultCode'] == 'T00001'):
                r['code'] = 0
                r['msg'] = rue['resultMsg']
            else:
                r['code'] = 1
                r['msg'] = rue['resultMsg']
        else:
            data = 'userid+mobile+timestamp'
            data = [str(param[i]) for i in data.split('+')] + [KEYS.get(10)]
            param['key'] = hashlib.md5(''.join(data).encode()).hexdigest()
            print(f'req to {url}jdSendShortMessage,param:',param )
            rue = requests.get(f'{url}jdSendShortMessage', param)
            print('res',rue, rue.text)
            rue = rue.json()
            if (rue['resultCode'] == 'T00001'):
                r['code'] = 0
                r['jdsign'] = rue['resultMsg']
            else:
                r['code'] = 1
                r['msg'] = rue['resultMsg']
            # print(2, r)
        return JsonResponse(r, safe=False)
    else:
        url = 'http://api.yaajie.com:8080/'
        if verifyCode:
            r = requests.get(f'{url}jingDong/checkCode', {'phone': account, 'code': verifyCode}).json()
            # print(1, r, f'>{verifyCode}<')
        else:
            r = requests.get(f'{url}jingDong/getVerifyCode', {'phone': account}).json()
            # print(2, r)
        return JsonResponse(r)


def callback(request):
    print('GET:', request.GET, 'body:', request.body)
    print('POST:', request.POST, 'body:', request.body)
    ex_order = ''
    if request.body:
        channel = int(request.GET.get('channel', 0))
        body = request.body.decode()
        if body[0] not in ('{','['): # pushang
            if channel == 3:
                order_no = body.split('extOrderId=')[1].split('&')[0]
                ex_order = body.split('orderId=')[1].split('&')[0]
            elif channel == 6:#软客
                order_no = body.split('id=')[1].split('&')[0]
                if body.count('operatorid='):#operatorid 官方流水号
                    #设置上游单号
                    ex_order = body.split('operatorid=')[1].split('&')[0]
                else:
                    ex_order = ''
            elif channel == 9:
                order_no = body.split('serialno=')[1].split('&')[0]
                ex_order = body.split('ejId=')[1].split('&')[0]
            elif channel == 10:#广吉、本康堂
                order_no = body.split('bizid=')[1].split('&')[0]
                ex_order = body.split('orderid=')[1].split('&')[0]
            elif channel == 11:
                print(body)
                order_no = body.split('outOrderId=')[1].split('&')[0]
                ex_order = body.split('orderId=')[1].split('&')[0]
            elif channel == 15:
                print(body)
                order_no = body.split('outTradeNo=')[1].split('&')[0]
                ex_order = body.split('outTradeNo=')[1].split('&')[0]
        else:
            req = json.loads(request.body)
            if req.get('order_no'): # taiping
                ex_order = req['serial_no']
                order_no = req['order_no']
                channel = 1
            else: #xinmei
                ex_order = req['orderNo']
                order_no = req['thirdOrderNo']
                channel = 2
    elif 'sellerid' in request.GET['channel']:
        channel = int(request.GET['channel'].split('?sellerid=')[0])
        order_no = request.GET['channel'].split('sellerid=')[1]
        #上游单号修改为本地单号_重试次数
        ex_order = request.GET['channel'].split('sellerid=')[1]
    else:
        order_no = request.GET.get('order_no', '')
        channel = int(request.GET.get('channel', 1))
    qs = Code.objects.filter(id=order_no.split('_')[0], status=1)
    if qs.count():
        code = qs[0]
        if ex_order:
            code.ex_order = ex_order
            code.save()
        if channel == 2 and req.get('orderStatus') == '1':
            code.update_status(2)
            return HttpResponse('SUCCESS')
        r = do_post('query', {'no': order_no}, code.activity.consumer.appid or appid, channel)
        if r in (2, 3): # (2, '已到账'), (3, '充值失败')
            code = Code.objects.get(id=code.id)
            code.update_status(r)
        elif channel == 10:
            return HttpResponse(0)
    return {
            1: JsonResponse({'status': '0', 'message': '成功'}),
            2: HttpResponse('SUCCESS'),
            3: HttpResponse('OK'),
            6: HttpResponse('OK'),
            7: HttpResponse('OK'),
            9: HttpResponse('success'),
            10: HttpResponse(1),
            11:HttpResponse('ok'),
            12:HttpResponse('ok'),
            13: HttpResponse('ok'),
            14: HttpResponse('ok'),
            15: HttpResponse('success'),
    }.get(channel)


'''
 　　* @param string $key 加密使用的密钥
 　　* @param string $vi 加密使用的向量
 　　* @des 3DES加密
     * 填充方式：PKCS5Padding
        PKCS#5填充是将数据填充到8的倍数，
        填充后数据长度的计算公式是 定于元数据长度为x，
        填充后的长度是 x + (8 - (x % 8)),
        填充的数据是 8 - (x % 8)，块大小固定为8字节
 　　*/
     输出: base64
     编码: UTF-8
 '''
def decode(card_code):
    key = KEYS[3][:16]  # 初始化密钥
    iv = key[:8].encode()  # 偏移量
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]  # 用来去除补位
    '''
    解密：先base64解密，然后是DES3解密，然后取消补位
    '''
    #base64反编译（base64解密） decodebytes：解密函数
    res = base64.decodebytes(card_code.encode("utf8"))
    #声明解密函数
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    #DES3解密
    msg = des3.decrypt(res)
    #取消补位  unpad：取消补位方法
    res = unpad(msg).decode("utf8")
    return res


def stock_check(request):
    force = datetime.now().hour in (8, 18)
    for i in Sku.objects.filter(stock__gt=0):
        i.check_stock(force)
    activity2count = {i['activity_id']: i['id__count'] for i in 
        Code.objects.filter(status__in=(1,7)).values('activity_id').annotate(Count('id'))}
    consumer2count = defaultdict(int)
    for i in Activity.objects.filter(id__in=activity2count.keys()):
        consumer2count[i.consumer_id] += activity2count[i.id]
    for i in Consumer.objects.filter(id__in=consumer2count.keys()):
        send_msg(f'客户{i.name}有{consumer2count[i.id]}单待处理', i.token, i.at)
    return HttpResponse()
