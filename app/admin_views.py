from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect

from django.contrib import admin
from .models import *
from .admin import *


#获取全部活动数据
@login_required
def activity(request):
   if request.GET['id'] !=0 :
       id=request.GET['id']
       int_activity = Activity.objects.filter(id=id).values()[0]

   return JsonResponse(int_activity)
#获取全部客户数据（用于数据筛选）
@login_required
def consumer(request):
    p = {p.id: p.name for p in Consumer.objects.all()}
    return JsonResponse(p)


@login_required
def sku(request):
    #p = {p.id: p.name for p in Activity.objects.all()}
   skulist= Sku.objects.all().values()

   id2product_name={p.id: p.name for p in Product.objects.all()}
   for p in skulist:
       
       p['sku_name'] = id2product_name.get(p['product_id'],'')+p['name']
   return JsonResponse(list(skulist), safe=False)

@login_required
def save(request):

    data = dict(request.POST.items())
    if len(data['id'])>0:
        active=Activity(**data)
        active.save()

    return HttpResponseRedirect('/ka/admin/app/activity/')

@login_required
def dels(request):
    data=request.POST
    return HttpResponseRedirect('/ka/admin/app/activity/'+request.POST.get('id')+'/delete/')
