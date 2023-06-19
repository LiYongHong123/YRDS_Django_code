import hashlib
from urllib.parse import quote

from django.http import JsonResponse

from .models import *
def check(arr, map, password='094759'):
    c = ''
    print(map)
    #判断是否有该客户
    if Consumer.objects.filter(id=map['pid']).count()>0:
        con = Consumer.objects.get(id=map['pid'])
    else:
        #没有该客户提示错误提示
        return JsonResponse({'retMsg': f'商户不存在', 'retCode': '1001', 'retResult': '1001'})
    password = con.password
    for i in arr:
        if i == 'password':
            c = f'{c}&{i}={password}'
        elif map.get(i) != None:
            # print(i, map[i])
            c = f'{c}&{i}={map[i] if type(map[i]) != str else quote(map[i])}'
    m = hashlib.md5()
    m.update(c[1:].encode('utf8'))
    if m.hexdigest() != map.get('signMsg'):
        print(c[1:], m.hexdigest(), map.get('signMsg'))
        return JsonResponse({'retMsg': f'签名错误', 'retCode': '1004', 'retResult': '1004'})


def card(request):
    ts = request.GET.get('submitTimestamp')
    pid = request.GET.get('pid', '100001')
    aid = request.GET.get('cardBatchNo')
    if not ts or not pid or not aid:
        return JsonResponse({'retMsg': f'no param pid:{pid} or cardBatchNo:{aid} or submitTimestamp:{ts}', 'retCode': '1003'})
    qs = DongCard.objects.filter(consumer_id=pid, style=True)
    res = check(('submitTimestamp', 'pid', 'cardBatchNo', 'password'), request.GET)
    if res: return res
    if aid:
        qs = qs.filter(cardCode=aid)
        if qs.count() != 1:
            return JsonResponse({'retMsg': f'error pid:{pid} or cardBatchNo:{aid}', 'retCode': '2001'})
        data = qs[0].to_dict()
    else:
        data = list(i.to_dict() for i in qs)
    return JsonResponse({'retMsg': 'ok', 'retCode': '0000', 'data': data})



def order(request):
    req=request.POST
    orderId = req.get('orderId')
    aid = req.get('aid')
    pid = req.get('pid', '100001')
    if not aid or not aid.isdigit():
        return JsonResponse({'retMsg': f'产品编码为空！', 'retResult': '1003'})
    if not orderId :
        return JsonResponse({'retMsg': f'流水号为空 ', 'retResult': '1002'})
    res = check(('submitTimestamp', 'pid', 'cardBatchNo', 'password', 'orderId', 'orderQuantity',
                 'orderTime'), req)
    if res: return res
    qs = DongCard.objects.filter(cardCode=aid, consumer_id=pid, style=True)
    if qs.count() != 1:
        return JsonResponse({'retMsg': f'error pid:{pid} or cardBatchNo:{aid}', 'retResult': '2001'})
    qs2 = DongOrder.objects.filter(consumer_id=pid,orderId=req['orderId'])
    card = qs[0]
    if qs2.count() > 0:
        #本次请求的订单号已又充值记录 返回信息
        code = Code.objects.filter(name=qs2[0].exchangeCode)[0]
        res = {'wnOrderId': code.id, 'orderId': qs2[0].orderId}
        res['code'] = {2: '01', 3: '02', 4: '02'}.get(code.status, '00')
        return JsonResponse(res)
    if card.autoOut and Sku.objects.filter(id=card.activity.skus, enable=False).exists():
        return JsonResponse({'retMsg': '库存不足', 'retResult': '2002'})
    orderTime=datetime.now().strftime("%Y%m%d%H%M%S%f")
    order = DongOrder(None, req['submitTimestamp'], pid, aid, req['orderId'], req['orderQuantity'], orderTime,
                      0, 0, '', '')
    order.save()
    res = []
    for i in range(int(req['orderQuantity'])):
        if card.autoOut:
            code = Code(None, f'{order.id}-{i}', card.activity.id)
            code.save()
            code.post_order(card.activity.skus, '')
            res.append(code.account)
        else:
            #生成卡密
            res.append(gen_code(card.activity_id).name)
    order.exchangeCode = ';'.join(res)
    order.save()
    type=2
    if type==1:
        #type为1时直接返回我平台卡密
        return JsonResponse(order.to_dict())
    elif type==2:
        re={'name':order.exchangeCode,'account': req.get('account'),'sku':card.activity.skus}
        jieguo=direct_use(re)
        backdef(req.get('callback_url'),{'name':order.exchangeCode,'orderId':orderId})
        return JsonResponse({'retMsg': f'请求成功 ', 'retResult': '0000','time':datetime.now().strftime("%Y%m%d%H%M%S%f")})

#回调函数
def backdef(url,param):
    code=Code.objects.filter(name=param['name'])[0]
    res={'wnOrderId':code.id,'orderId':param['orderId']}
    res['code'] = {2: '01', 3: '02', 4: '02'}.get(code.status, '00')
    print(f'req to {url},param:',res )
    rue = requests.post(url, res)
    print('res', rue, rue.text)

def __api_code_used(code, res={}):
    res['account'] = code.account
    if code.status == 5:
        res['activity'] = code.activity.name
        res['remark'] = code.sku.product.remark
    else:
        res['head'] = {2: '已经到账', 3: '兑换失败', 4: '兑换失败'}.get(code.status, '兑换成功')
        res['param'] = param = '手机号' if code.sku.product.param.count('phone') else '账号'
        res['retry'] = code.id if res['head'].count('失败') and code.sku.product.param.count('msgCode') else 0    
    return res


def __api_code_show(code, res):
    res['activity'] = code.activity.name
    res['sku'] = list({'id': i.id, 'name': str(i), 'param': i.product.param, 'remark': i.product.remark} for i in Sku.objects.filter(id__in=code.activity.skus.split(','), enable=True))
    res['name'] = code.name
    return res

#生成卡密之后直冲
def direct_use(request):
    print(request['name'])
    res = {}
    code = Code.objects.get(name=request['name'])
    sku = request['sku']
    if code.status == 0 and code.activity.skus.split(',').count(sku) == 1:
        ext = {}
        res['msg'] = code.post_order(sku, request['account'], ext)
        if res['msg'] == None:
            res = __api_code_used(code, res)
    else:
        res['msg'] = '权益券错误'
    if res['msg']:
        res = __api_code_show(code, res)
    return res


def use(request):
    res = {}
    code = Code.objects.get(name=request.POST['name'])
    sku = request.POST['sku']
    if code.status == 0 and code.activity.skus.split(',').count(sku) == 1:
        ext = {}
        if request.POST.get('msgCode'):
            ext['verifyCode'] = request.POST['msgCode']
        res['msg'] = code.post_order(sku, request.POST.get('account'), ext)
        if res['msg'] == None:
            res = __api_code_used(code, res)
    else:
        res['msg'] = '权益券错误'
    if res['msg']:
        res = __api_code_show(code, res)
    return JsonResponse(res)

#订单查询接口
def queryorder(request):
    req = request.POST
    orderId = req.get('orderId')
    pid = req.get('pid', '100001')
    if DongOrder.objects.filter(orderId=orderId,consumer_id=pid).count()>0:
        #表示又该订单的存在
        #根据权益码获取订单的信息
        order=DongOrder.objects.filter(orderId=orderId,consumer_id=pid)[0]
        codes=Code.objects.filter(name=order.exchangeCode)[0]
        res = {'wnOrderId': codes.id, 'orderId': order.orderId,'use_time':codes.use_time,'finish_time':codes.finish_time}
        res['code'] = {2: '01', 3: '02', 4: '02'}.get(codes.status, '00')
        return JsonResponse(res)
    else:
        return JsonResponse({'retMsg': f'无此订单 ', 'retResult': '3001'})
