from django.http import JsonResponse

from .models import *

def check(request):
    res = {}
    session_code = request.session.get('valid_code', '').upper()
    request.session['valid_code'] = 'no'
    qs = Code.objects.filter(name=request.POST['name'].strip())
    # if session_code != 'OK' and request.POST.get('code','').upper() != session_code:
    #     print(session_code, request.POST.get('code',''))
    #     res['msg'] = '验证码不正确'
    # el
    if request.POST['name'].count('-') or qs.count() != 1:
        res['msg'] = '卡密不正确'
    elif qs.filter(status=0).count() == 1:
        res['step'] = 1
        code = qs[0]
        request.session['valid_code'] = 'ok'
        res = __api_code_show(code, res)
    else:
        res['step'] = 2
        code = qs[0]
        res = __api_code_used(code, res)
    return JsonResponse(res)

def __api_code_used(code, res={}):
    res['account'] = code.account
    res['status']=code.status
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
