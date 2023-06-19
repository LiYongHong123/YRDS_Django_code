import json, hashlib
from urllib.parse import quote
from django.http import JsonResponse
from .models import *

def check(arr, map, password='094759'):
    c = ''
    con = Consumer.objects.get(id=map['pid'])
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
        return JsonResponse({'retMsg': f'check signMsg error', 'retCode': '1002', 'retResult': '1002'})


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


def buy(request):
    try:
        req = json.loads(request.body)
        print(req)
    except:
        print(request.body)
        return JsonResponse({'retMsg': 'no json request', 'retResult': '1003'})
    quantity = req.get('orderQuantity')
    aid = req.get('cardBatchNo')
    pid = req.get('pid', '100001')
    if not aid or not aid.isdigit():
        return JsonResponse({'retMsg': f'error cardBatchNo {aid}', 'retResult': '1003'})
    if not quantity or type(quantity) != int:
        return JsonResponse({'retMsg': f'error orderQuantity {quantity}', 'retResult': '1003'})
    res = check(('submitTimestamp', 'pid', 'cardBatchNo', 'password', 'orderId', 'customerNo', 'orderQuantity', 'orderTime', 'orderPoints', 'orderPrice', 'provUser', 'provUse', 'ext'), req)
    if res: return res
    qs = DongCard.objects.filter(cardCode=aid, consumer_id=pid, style=True)
    if qs.count() != 1:
        return JsonResponse({'retMsg': f'error pid:{pid} or cardBatchNo:{aid}', 'retResult': '2001'})
    card = qs[0]
    qs2 = DongOrder.objects.filter(consumer_id=pid, card_id=card.cardCode, orderId=req['orderId'])
    if qs2.count() > 0:
        return JsonResponse(qs2[0].to_dict())
    if card.autoOut and (Sku.objects.filter(id=card.activity.skus, enable=False).exists() or OutCard.objects.filter(sku_id=card.activity.skus, status=0).count() < quantity):
        return JsonResponse({'retMsg': '库存不足', 'retResult': '2002'})
    order = DongOrder(None, req['submitTimestamp'], pid, aid, req['orderId'], quantity, req['orderTime'], req.get('orderPrice'), req.get('orderPoints'), req.get('ext'), '')
    order.save()
    res = []
    for i in range(quantity):
        if card.autoOut:
            code = Code(None, f'{order.id}-{i}', card.activity.id)
            code.save()
            code.post_order(card.activity.skus, '')
            res.append(code.account)
        else:
            res.append(gen_code(card.activity_id).name)
    order.exchangeCode = ';'.join(res)
    order.save()
    return JsonResponse(order.to_dict())

