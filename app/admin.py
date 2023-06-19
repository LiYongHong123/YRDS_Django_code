import csv, codecs

from apscheduler.schedulers.background import BackgroundScheduler
from django import forms
from django.contrib import admin, messages
from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django import *
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

class autoFilter(admin.SimpleListFilter):
    # 右侧栏人为可读的标题
    title = '所属活动'
    template = 'autofilter.html'
    parameter_name = 'query_id'
    activities_id = []
    activities_lists = list();
    def lookups(self, request, model_admin):
        activity_skus_id = []
        activity_consumer_id = []
        activity_ids = []
        data_list = []
        activity_skus_id_data = [] # 这个变量用来存放有逗号的值。

        # ('参数值',‘前端页面可见文字’)
        # 每个元素中的第一个元素 Tuple是将要执行的选项的编码值 出现在URL查询中。
        # 第二个元素是 将出现的选项的用户可读的名称 在右侧栏中。
        # 查询客户表内所有数据
        qs = Consumer.objects.all()
        # activities_id 数组用来存放要输出到页面右侧的选项的数据
        activities_id = []
        activities_lists = list();
        #必须有一个数组的清空，否者的话list的数据累加
        self.activities_lists.clear();

        # 循环客户表
        for i in qs:
            # format 格式化字符串的函数 将x.id的格式从数值型转换为字符串类型
            # addpend函数 将括号内的内容添加到id_shu数组中
            # join 将括号内的数组用  ,  进行分割转换为字符串
            # 将特殊的用户id后添加一个逗号  用于区分用户id和活动id
            str1 = format(i.id)+","
            #首先需要将客户数据放入到activities_id数组中
            activities_id+=[[str1,i.name]]
            activities_list = {};
            #一维输入完成（一维：客户信息）
            activities_list['value']=str1;
            activities_list['name']=i.name;
            #一维输入完成
            #二位输入完成（二维：商品信息）
            # 根据客户表获取到活动数据
            # activities = Activity.objects.filter(consumer_id=i.id)
            #skus_ids 存放客户活动涉及到的所有的商品面值id
            skus_ids=Activity.objects.filter(consumer_id=i.id).values_list('skus');
            num = [];                                                                   # 声明 num列表用来存放处理后的值
            for a in skus_ids :                                                         # 把 skus_ids 查询集进行遍历
                for b in a :
                    if b.find(',') != -1 :                                              # 如果 当前元组中有,
                        temNum = b.split(',');                                          # 对当前元组进行,分割
                        for x in temNum :
                            num += [(x,)]                                               # 把拼接后的元组拼接倒num列表中
            num += list(skus_ids)                                                       # 把 skus_ids 查询集拼接到num列表中
            for a in num :                                                              # 遍历 num 列表
                for b in a :
                    if b.find(',') != -1:                                               # 如果num列表中的元组是多个值的，就删除当前元组
                        num.remove(a)
            #product_ids  在sku数据表中根据活动涉及到的面值id获得到了 面值所属的商品 存放到变量
            prouduct_ids = Sku.objects.filter(id__in=[a for b in num for a in b]).values_list('product_id');
            #product_num 根据sku数据表的商品id 获取到product商品表的数据信息 id 和商品名称
            product_num = Product.objects.filter(id__in=prouduct_ids).values_list('id', 'name');
            qs = Activity.objects.all()                                                 # 获取Activity表中的所有数据，赋值给qs变量
            for a in qs:                                                                # 遍历 qs变量
                if(a.skus.find(',') > -1 ):                                             # 如果遍历时该元素的skus的值有,
                    activity_skus_id.append(a.skus.split(','))                          # 把该元素追加到activity_skus_id变量
                    activity_skus_id_data.append(a)                                     # 把该元素追加到activity_skus_id_data变量

            #二维循环（商品信息循环）
            er_lists=list();
            for p in product_num:                                                       #遍历用户id和用户名称信息
                er_list={};
                er_list['p_id']=format(p[0])+"-"+format(i.id);                          # 商品id-客户id
                er_list['name']=p[1];
                # 获取该商品下所有的面值信息
                product_suk_ids = [a for b in Sku.objects.filter(product_id = p[0]).values_list('id') for a in b]
                                                                                        # 根据product表的id 获取Sku表的id 以数组的形式赋值给product_suk_ids
                for c in product_suk_ids:                                               # 遍历 product_suk_ids
                    if Activity.objects.filter(skus=c, consumer_id=i.id):               # 如果 Activity表的skus的值是当前当前遍历的product_suk_ids的值，并且Activity表的consumer_id的值和i.id相同
                        product_active = Activity.objects.filter(skus__in=product_suk_ids,consumer_id=i.id).all();  #获取 根据面值信息和客户id进行筛选信息
                        data_list = product_active;                                     # 把product_active赋值给data_list
                    else :
                        for a in activity_skus_id:                                      # 遍历activity_skus_id序列
                            for k in range(0,len(activity_skus_id)):                    # 遍历activity_skus_id的长度
                                if int(activity_skus_id_data[k].consumer_id) == int(i.id):
                                    for g in a :
                                        if(int(g) == int(c)):
                                            data_list = [];                             # 清空data_list数组
                                            data_list.append(activity_skus_id_data[k])  # activity_skus_id_data[k]追加到data_list数组中

                #三维输入完成 （三维：活动信息）
                er_list['list']=data_list;
                er_lists.append(er_list);
            activities_list['list']=er_lists;
            #二维输入完成（二维：商品信息）
            self.activities_lists.append(activities_list)
        return   activities_id

    def queryset(self, request, queryset):
        # 判断传递过来的参数是否有 , 有逗号的就说明是根据客户下所有的活动id进行筛选的，没有的话说明根据活动id进行筛选
        jiego=None
        actComId = []                                                                   # 声明 所有一对多的商品
        actConsumerId = []                                                              # 声明 所有一对多的客户id
        activityId = []                                                                 # 声音 所有一对多的活动id
        if self.value():
             p_hand = self.value().find("_")
             flag = self.value().find(",")
             p_flag = self.value().find("-")

             if p_hand != -1:                                                           # 判断是否选中多个元素
                handList = self.value().split('_')                                      # 声明 存放url传入的query_id的值的列表
                hand_one = []                                                           # 声明 筛选出的一级 id
                hand_two = []                                                           # 声明 筛选出的二级 id
                hand_three = []                                                         # 声明 筛选出的三级 id
                data_list = []                                                          # 声明 该数组用于最终拉取数据

                for i in handList:                                                      # 对url传入的参数进行遍历
                    if i.find(',') == -1 & i.find('-') == -1:                           # 对筛选出的三维数组进行数据拉去
                        hand_three.append(i)                                            # 筛选出三级的id并且拉取数据
                        data_list += hand_three                                         # 把晒筛选出的三级数组拼接到最终要拉取数据的列表里
                    elif i.find(',') != -1:                                             # 对筛选出的一维列表进行拉取数据
                        hand_one.append(int(i.split(',')[0]))                           # 对url传入的一维列表按,进行分割
                        hand_one_list = [a for b in Activity.objects.filter(consumer_id__in=hand_one).values_list('id') for a in b]
                        data_list += hand_one_list                                      # 把晒筛选出的一级数组拼接到最终要拉取数据的列表里
                    elif i.find('-') != -1:                                             # 对筛选出的三维数组进行拉取数据
                        hand_two.append(i)                                              # 把url里传过来的参数保存到hand_two列表里
                        hand_two_kehu = []                                              # 存放url里传入的三维数组的，二维数组
                        cus_id = []                                                     # 客户id
                        com_id = []                                                     # 商品id
                        for j in hand_two:                                              # 遍历url传入的数据，以-符分割为二维数组
                            hand_two_kehu.append(j.split('-'))                          # hand_two_kehu的值是：[['4', '1'], ['11', '1']]
                        for k in hand_two_kehu:                                         # 遍历hand_two_kehu这个二维数组，分别获取客户id和商品id
                            for x in range(0,len(k),2):                                 # 获取客户id
                                com_id.append(k[x])
                            for p in range(1,len(k)):                                   # 获取商品id
                                cus_id.append(k[p])
                        product_suk_ids = [a for b in Sku.objects.filter(product_id__in = com_id).values_list('id')
                                           for a in b]                                  # 获取该商品下所有的面值信息

                        qs = Activity.objects.all();                                    # 获取所有的活动信息
                        for a in qs:
                            if(a.skus.find(',') > -1):                                  # 如果当前的活动是一对多
                                actComId.append(a.skus.split(','))                      # 获取当前轰动的所有商品id 并根据,进行分割
                                actConsumerId.append(a.consumer_id)                     # 拿到当前元素的客户id
                                activityId.append(a.id)                                 # 拿到当前活动的id
                        for c in product_suk_ids :                                      # 遍历客户表的skus的id值，判断是一对一的，还是一对多的。
                            if Activity.objects.filter(skus = c,skus__in=product_suk_ids):
                                product_active = [a for b in Activity.objects.filter(skus__in=product_suk_ids, consumer_id__in=cus_id).values_list('id') for a in b]
                                data_list += product_active;                            # 把要查询的数据添加到最终要提交的列表data_list中
                            else :
                                for i in actComId :
                                    for k in range(0, len(actComId)):
                                        for j in range(0, len(cus_id)):                 # 遍历商品id
                                            if int(actConsumerId[k] == int(cus_id[j])): # 如果是指定的一对多客户
                                                for g in i:
                                                    if(int(g) == int(c)):               # 如果是指定的skus
                                                        data_list.append(activityId[k]);# 把当前活动添加到最终要查询的列表中
                jiego = Code.objects.filter(activity_id__in=data_list);                 # 数据拉取

# -----------

             elif flag == -1 & p_flag== -1 :
                 #flag等于-1 说明传入的字符串没有逗号 为活动id数据  需要根据活动的id查询权益
                 jiego= Code.objects.filter(activity_id=self.value())

             elif flag != -1 :#点击的客户
                  #flag不等于-1 说明传入的字符串中有逗号 为用户id数据 需要根据用户的id查询权益
                  #将字符串根据 逗号 进行分割 得到用户的id 并且转换数据类型为int
                  active_id= int(self.value().split(',')[0])
                  #根据用户id得到该用户下的活动id
                  activitie_id = Activity.objects.filter(consumer_id=active_id).values_list('id')
                  #根据活动id得到所属该活动下的权益
                  jiego=Code.objects.filter(activity_id__in=activitie_id)
             elif p_flag != -1:#点击的商品
                 # flag不等于-1 说明传入的字符串中有逗号 为用户id数据 需要根据用户的id查询权益
                 # 将字符串根据 逗号 进行分割 得到用户的id 并且转换数据类型为int
                 p_id = int(self.value().split('-')[0]);#商品id   5
                 c_id =  int(self.value().split('-')[1]);#客户id  4
                 # 获取该商品下所有的面值信息
                 product_suk_ids = Sku.objects.filter(product_id=p_id).values_list('id');
                 # 获取 根据面值信息和客户id进行筛选信息
                 product_active = Activity.objects.filter(skus__contains=product_suk_ids,
                                                          consumer_id=c_id).values_list('id')  # 只有这种方式才弄够让前端获取到
                 jiego = Code.objects.filter(activity_id__in=product_active)
                 # if Activity.objects.filter(skus__in=product_suk_ids):
                 #     product_active = Activity.objects.filter(skus__contains=product_suk_ids,
                 #                                              consumer_id=c_id).values_list('id')
                 #     jiego = Code.objects.filter(activity_id__in=product_active)
                 # else:
                 #     product_active = Activity.objects.filter(skus__in=product_suk_ids,
                 #                                              consumer_id=c_id).values_list('id')
                 #     jiego = Code.objects.filter(activity_id__in=product_active)

            # 有其他的过滤器
             if request.GET.get('ex_id') is not None:
                 jiego =jiego & Code.objects.filter(ex_id__in=request.GET.get('ex_id').split(','))
             if request.GET.get('status__exact') is not None:
                 jiego = jiego & Code.objects.filter(status__exact=request.GET.get('status__exact'))
             if request.GET.get('use_time__gte') is not None:
                 jiego = jiego & Code.objects.filter(use_time__gte=request.GET.get('use_time__gte'))
             if request.GET.get('use_time__lt') is not None:
                    jiego = jiego & Code.objects.filter(use_time__lt=request.GET.get('use_time__lt'))
             if request.GET.get('create_time__gte') is not None:
                 jiego = jiego & Code.objects.filter(create_time__gte=request.GET.get('create_time__gte'))
             if request.GET.get('create_time__lt') is not None:
                 jiego = jiego & Code.objects.filter(create_time__lt=request.GET.get('create_time__lt'))
             if request.GET.get('finish_time__gte') is not None:
                 jiego = jiego & Code.objects.filter(finish_time__gte=request.GET.get('finish_time__gte'))
             if request.GET.get('finish_time__lt') is not None:
                 jiego = jiego & Code.objects.filter(finish_time__lt=request.GET.get('finish_time__lt'))
             if request.GET.get('use_time__isnull') is not None:
                 if request.GET.get('use_time__isnull')== 'False':
                    #有日期
                     jiego = jiego & Code.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull'))
                     for s in Code.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull')):
                       s.use_time
                 # 没有日期
                 elif request.GET.get('use_time__isnull') == 'True':
                     jiego = jiego & Code.objects.filter(use_time__isnull=request.GET.get('use_time__isnull'))
                     for s in Code.objects.filter(use_time__isnull=request.GET.get('use_time__isnull')):
                         s.use_time
        return jiego

    def choices(self, cl):
        all_choice = {
            'selected': self.value(),
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        cl.params=self.activities_lists;
        return ({
            'get_query': cl.params,
            'current_value': self.value(),
            'all_choice': all_choice,
            'parameter_name': self.parameter_name
        }, )

class autoSku(admin.SimpleListFilter):
    # 右侧栏人为可读的标题
    title = '所属商品'
    template = 'autoSku.html'
    parameter_name = 'sku_id'
    activities_id = []
    activities_lists = list();

    # 外部卡密右侧过滤器
    def lookups(self, request, model_admin):
        # ('参数值',‘前端页面可见文字’)
        # 每个元素中的第一个元素 Tuple是将要执行的选项的编码值 出现在URL查询中。
        # 第二个元素是 将出现的选项的用户可读的名称 在右侧栏中。
        # 查询客户表内所有数据
        qs = Product.objects.all()
        # activities_id 数组用来存放要输出到页面右侧的选项的数据
        activities_id = []
        activities_lists = list();
        #必须有一个数组的清空，否者的话list的数据累加
        self.activities_lists.clear();

        # 循环客户表
        for i in qs:
            # 声明一个变量用于存储兑换码的数量
            total = []
            # format 格式化字符串的函数 将x.id的格式从数值型转换为字符串类型
            # addpend函数 将括号内的内容添加到id_shu数组中
            # join 将括号内的数组用  ,  进行分割转换为字符串
            # 将特殊的用户id后添加一个逗号  用于区分用户id和活动id
            str1 = format(i.id)+","
            #首先需要将客户数据放入到activities_id数组中
            activities_id+=[[str1,i.name]]
            activities_list = {};
            #一维输入完成（一维：客户信息）
            activities_list['value']=str1;
            activities_list['name']=i.name;
            #一维输入完成
            #  找sku 表  Sku.objects.filter
            product_num=Sku.objects.filter(product_id=i.id).values_list('id','name','stock');

            #过滤内部卡密
            if i.param == "":

                # 二维循环（商品信息循环）
                er_lists = list();
                for p in product_num:

                    # 把外部卡密的id,用户名和是否兑换的状态赋值给outcard变量
                    outcard = OutCard.objects.filter(sku_id=p[0]).values_list('id','name','status');
                    er_list = {};

                    er_list['p_id'] = format(p[0]);  # 商品id-客户id
                    er_list['name'] = i.name + p[1];

                    totalII = []
                    for out in outcard:
                        if out[2] == 0:
                            total.append(out);
                            totalII.append(out[0]);

                    er_list['name'] = i.name + p[1];
                    er_list['showII'] = len(totalII);
                    er_lists.append(er_list);
                    activities_list['list'] = er_lists;
                # 二维输入完成（二维：商品信息）
                self.activities_lists.append(activities_list)

            activities_list['show'] = len(total);
        return   activities_id


    def queryset(self, request, queryset):

        # 判断传递过来的参数是否有 , 有逗号的就说明是根据客户下所有的活动id进行筛选的，没有的话说明根据活动id进行筛选
        jiego=None
        if self.value():
             flag = self.value().find(",")
             p_flag = self.value().find("-")
             if flag == -1 & p_flag== -1 :
                 #flag等于-1 说明传入的字符串没有逗号 为活动id数据  需要根据活动的id查询权益
                 jiego= OutCard.objects.filter(sku_id=self.value())
             elif  flag != -1 :#点击的客户
                  #flag不等于-1 说明传入的字符串中有逗号 为用户id数据 需要根据用户的id查询权益
                  #将字符串根据 逗号 进行分割 得到用户的id 并且转换数据类型为int
                  active_id= int(self.value().split(',')[0])
                  #根据用户id得到该用户下的活动id
                  activitie_id = Sku.objects.filter(product_id=active_id).values_list('id')
                  #根据活动id得到所属该活动下的权益
                  jiego=OutCard.objects.filter(sku_id__in=activitie_id)
            # 有其他的过滤器
             if request.GET.get('status__exact') is not None:
                 jiego = jiego & OutCard.objects.filter(status__exact=request.GET.get('status__exact'))
             if request.GET.get('use_time__gte') is not None:
                 jiego = jiego & OutCard.objects.filter(use_time__gte=request.GET.get('use_time__gte'))
             if request.GET.get('use_time__lt') is not None:
                    jiego = jiego & OutCard.objects.filter(use_time__lt=request.GET.get('use_time__lt'))
             if request.GET.get('create_time__gte') is not None:
                 jiego = jiego & OutCard.objects.filter(create_time__gte=request.GET.get('create_time__gte'))
             if request.GET.get('create_time__lt') is not None:
                 jiego = jiego & OutCard.objects.filter(create_time__lt=request.GET.get('create_time__lt'))
             if request.GET.get('finish_time__gte') is not None:
                 jiego = jiego & OutCard.objects.filter(finish_time__gte=request.GET.get('finish_time__gte'))
             if request.GET.get('finish_time__lt') is not None:
                 jiego = jiego & OutCard.objects.filter(finish_time__lt=request.GET.get('finish_time__lt'))
             if request.GET.get('use_time__isnull') is not None:
                 if request.OutCard.get('use_time__isnull')== 'False':
                    #有日期
                     jiego = jiego & Code.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull'))
                     for s in OutCard.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull')):
                         s.use_time
                 # 没有日期
                 elif request.GET.get('use_time__isnull') == 'True':
                     jiego = jiego & Code.objects.filter(use_time__isnull=request.GET.get('use_time__isnull'))
                     for s in OutCard.objects.filter(use_time__isnull=request.GET.get('use_time__isnull')):
                         s.use_time
        return jiego

    def choices(self, cl):
        all_choice = {
            'selected': self.value(),
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        cl.params=self.activities_lists;
        return ({
            'get_query': cl.params,
            'current_value': self.value(),
            'all_choice': all_choice,
            'parameter_name': self.parameter_name
        }, )

class autoexid(admin.SimpleListFilter):
    # 右侧栏人为可读的标题
    title = '上游通道'
    parameter_name = 'ex_id'

    def lookups(self, request, model_admin):
        #自定义上游通道列表
        list = ((0, '南京立方'), (1, '北京太平永顺'), (2, '新美科技'), ('3,4,5,8', '浦上'), (6, '软客'), (9, '渡渡鸟'),(10,'广吉'),(11,'美嘉（未税）'),(12,'本康堂（未税）'),(13,'乐充-德森'),(14,'乐充-永好'))
        return list

    def queryset(self, request, queryset):
        # 判断传递过来的参数是否有 , 有逗号的就说明是根据客户下所有的活动id进行筛选的，没有的话说明根据活动id进行筛选
        jiego = None
        #赛选
        if self.value():
            jiego = Code.objects.filter(ex_id__in=self.value().split(','))
            # 有其他的过滤器
            if request.GET.get('query_id') is not None:
                flag = request.GET.get('query_id').find(",")
                p_flag = request.GET.get('query_id').find("-")
                if flag == -1 & p_flag == -1:
                    # flag等于-1 说明传入的字符串没有逗号 为活动id数据  需要根据活动的id查询权益
                    jiego = Code.objects.filter(activity_id=request.GET.get('query_id'))
                elif flag != -1:  # 点击的客户
                    # flag不等于-1 说明传入的字符串中有逗号 为用户id数据 需要根据用户的id查询权益
                    # 将字符串根据 逗号 进行分割 得到用户的id 并且转换数据类型为int
                    active_id = int(request.GET.get('query_id').split(',')[0])
                    # 根据用户id得到该用户下的活动id
                    activitie_id = Activity.objects.filter(consumer_id=active_id).values_list('id')
                    # 根据活动id得到所属该活动下的权益
                    jiego = Code.objects.filter(activity_id__in=activitie_id)
                elif p_flag != -1:  # 点击的商品
                    # flag不等于-1 说明传入的字符串中有逗号 为用户id数据 需要根据用户的id查询权益
                    # 将字符串根据 逗号 进行分割 得到用户的id 并且转换数据类型为int
                    p_id = int(request.GET.get('query_id').split('-')[0]);  # 商品id
                    c_id = int(request.GET.get('query_id').split('-')[1]);  # 客户id
                    # 获取该商品下所有的面值信息
                    product_suk_ids = Sku.objects.filter(product_id=p_id).values_list('id');
                    # 获取 根据面值信息和客户id进行筛选信息
                    product_active = Activity.objects.filter(skus__in=product_suk_ids,
                                                             consumer_id=c_id).values_list('id')  # 只有这种方式才弄够让前端获取到
                    jiego = Code.objects.filter(activity_id__in=product_active)
            if request.GET.get('status__exact') is not None:
                jiego = jiego & Code.objects.filter(status__exact=request.GET.get('status__exact'))
            if request.GET.get('use_time__gte') is not None:
                jiego = jiego & Code.objects.filter(use_time__gte=request.GET.get('use_time__gte'))
            if request.GET.get('use_time__lt') is not None:
                jiego = jiego & Code.objects.filter(use_time__lt=request.GET.get('use_time__lt'))
            if request.GET.get('create_time__gte') is not None:
                jiego = jiego & Code.objects.filter(create_time__gte=request.GET.get('create_time__gte'))
            if request.GET.get('create_time__lt') is not None:
                jiego = jiego & Code.objects.filter(create_time__lt=request.GET.get('create_time__lt'))
            if request.GET.get('finish_time__gte') is not None:
                jiego = jiego & Code.objects.filter(finish_time__gte=request.GET.get('finish_time__gte'))
            if request.GET.get('finish_time__lt') is not None:
                jiego = jiego & Code.objects.filter(finish_time__lt=request.GET.get('finish_time__lt'))
            if request.GET.get('use_time__isnull') is not None:
                if request.GET.get('use_time__isnull') == 'False':
                    # 有日期
                    jiego = jiego & Code.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull'))
                    for s in Code.objects.exclude(use_time__isnull=request.GET.get('use_time__isnull')):
                        s.use_time
                # 没有日期
                elif request.GET.get('use_time__isnull') == 'True':
                    jiego = jiego & Code.objects.filter(use_time__isnull=request.GET.get('use_time__isnull'))
                    for s in Code.objects.filter(use_time__isnull=request.GET.get('use_time__isnull')):
                        s.use_time
        return jiego

class DateRangeFilterss(admin.DateFieldListFilter):
    template = 'autoDatetime.html';
    def expected_parameters(self):
        params = [self.lookup_kwarg_since, self.lookup_kwarg_until]
        if self.field.null:
            params.append(self.lookup_kwarg_isnull)
        return params

    def choices(self, changelist):
        for title, param_dict in self.links:
            yield {
                # 初步判定  selected变量为 a标签的文字内容
                'selected': self.date_params == param_dict,
                #初步判定  query_string变量为 a标签的url阐述变量
                'query_string': changelist.get_query_string(param_dict, [self.field_generic]),
                #确认  title为标题
                'display': title,
                'field_generic':self.field_generic,
                'field_path':self.field_path,
            }




@admin.register(Product)
class Admin(admin.ModelAdmin):
    list_display = ('name', 'param', 'remark')


class ImportCodeForm(forms.Form):
    code = forms.CharField(label='导入卡密', widget=forms.Textarea, initial='每行1条，格式：卡密 有效期（2022-05-20）')
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)  # 这个字段是必需的，表示选择了多少项


@admin.register(Sku)
class Admin(admin.ModelAdmin):
    list_display = ('id', 'product', 'name', 'enable', 'stock', 'at', 'token')
    actions = ('import_code',)

    @admin.action(description='导入外部卡密')
    def import_code(self, request, queryset):
        if request.POST.get('post'):
            form = ImportCodeForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code'].split('\n')
                for i in code:
                    tmp = i.replace('\r', '').split('\t')
                    # print('import code', tmp)
                    for j in '日':
                        tmp[1] = tmp[1].replace(j, '')
                    for j in '/年月':
                        tmp[1] = tmp[1].replace(j, '-')
                    OutCard(name=tmp[0], expire_time=tmp[1], sku=queryset[0]).save()
                self.message_user(request, f'成功导入{len(code)}张外部卡密', messages.SUCCESS)
            else:
                self.message_user(request, '输入错误', messages.ERROR)
        else:
            return render(request, 'import_code.html',
                          {'form': ImportCodeForm(initial={
                              '_selected_action': request.POST.getlist('_selected_action')
                          }), 'object': queryset[0]})


@admin.register(Channel)
class Admin(admin.ModelAdmin):
    list_display = ('source_id', 'sku', 'status', 'param')


@admin.register(Consumer)
class Admin(admin.ModelAdmin):
    list_display = ('name',)


class SetTypeForm(forms.Form):
    type = forms.IntegerField(label='生成卡券数量')
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)  # 这个字段是必需的，表示选择了多少项


@admin.register(Activity)
class Admins(admin.ModelAdmin):
    list_display = ('consumer', 'name', 'skus','status','due_time','down_price')
    actions = ('create_code', 'export_code')
    #添加/编辑字段
    fields=('consumer', 'name', 'skus','due_time','down_price')
    list_filter = ('consumer',)
    def timedTask(num=12):
        #获取当前时间戳
        now = datetime.now()  # 获取现在的时间
        #获取所有的活动信息（与当前时间戳进行对比 将过去的进行筛选出来）
        over_activity=Activity.objects.filter(due_time__lte=now);

        #获取所有的活动信息（与当前时间戳进行对比 将未来的进行筛选出来）
        future_activity=Activity.objects.filter(due_time__gt=now);
        #循环修改过期的活动的状体（变为活动停止）
        for i in over_activity:
            #判断已过期的活动的活动状态
            if i.status==1:
                #活动状态为1 代表该活动的活动状态为过期---》活动状态：过期，到期时间：过期 ----》不进行修改
                test=1
            elif i.status==0:
                # 活动状态为0 代表该活动的活动状态为进行中---》活动状态：进行中，到期时间：过期 ----》进行修改--》卡：未过期=>过期，活动：进行=>过期
                #修改过期的活动的状态
                i.status=1;
                #循环修改国企的活动所属的卡券状态（变为已过期）
                #根据过期活动的id 筛选出所属的卡券
                over_code=Code.objects.filter(activity_id=i.id)
                for s in over_code:
                    #判断当前的权益券的状态是否为未使用
                    if s.status ==0:
                        #如果当前权益券的状态是未使用的话  将卡券状态转换为过期状态
                        s.status = 6
                #批量修改过期的卡券的状态
                Code.objects.bulk_update(over_code,['status',])
        #批量修改过期活动状态
        Activity.objects.bulk_update(over_activity, ['status', ])
        for i in future_activity:
            #判断未过期的活动的活动状态
            if i.status==1:
                #活动状态为1 代表该活动的活动状态为过期---》活动状态：过期，到期时间：未过期 ----》进行修改
                # 修改过期的活动的状态-》过期改为进行
                i.status = 0;
                # 循环修改未过期的活动所属的卡券状态（变为未使用）
                # 根据过期活动的id 筛选出所属的卡券
                future_code = Code.objects.filter(activity_id=i.id)
                for s in future_code:
                    # 判断当前的权益券的状态是否为过期
                    if s.status == 6:
                        # 如果当前权益券的状态是过期的话  将卡券状态转换为未使用状态
                        s.status = 0
                # 批量修改过期的卡券的状态
                Code.objects.bulk_update(future_code, ['status', ])
            elif i.status==0:
                # 活动状态为0 代表该活动的活动状态为进行中---》活动状态：进行中，到期时间：未过期 ----》不进行修改
               test=1
        #批量修改过期活动状态
        Activity.objects.bulk_update(future_activity, ['status', ])

    scheduler = BackgroundScheduler()
    #定时时间 设置 interval 为定时时间段（多长时间执行一次）   cron为定时时间（每日几点执行一次）
    #scheduler.add_job(timedTask, 'interval',  minutes= 1)
    scheduler.add_job(timedTask, 'cron', hour = 0, minute = 00)
    scheduler.start()

    #在修改活动数据之后会进行一次活动状态的筛选修改 编辑
    def save_model(self, request, obj, form, change):

        """
        Given a model instance save it to the database.
        """
        obj.save()
        #调用 修改编辑的函数
        self.timedTask()
    @admin.action(description='生成权益券')
    def create_code(self, request, queryset):
        if request.POST.get('post'):
            form = SetTypeForm(request.POST)
            if form.is_valid():
                type = form.cleaned_data['type']
            for qs in queryset:
                for i in range(type):
                    gen_code(qs.id)
            self.message_user(request, '成功生成%d张权益券' % (len(queryset) * type), messages.SUCCESS)
        else:
            return render(request, 'set_type.html',
                          {'form': SetTypeForm(initial={
                              '_selected_action': request.POST.getlist('_selected_action')
                          }), 'objects': queryset})

    @admin.action(description='导出权益券')
    def export_code(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=a.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow(['活动','卡密','创建时间','状态','兑换商品','使用账号','使用时间','到账时间','本地订单号','上游单号'])
        qs = Code.objects.filter(activity_id__in=request.POST.getlist('_selected_action'))
        for i in qs:
            writer.writerow(
                [i.activity,i.name,i.create_time.strftime(FMT),  i.status, i.sku, i.account, i.use_time.strftime(FMT) if i.use_time else '',
            i.finish_time.strftime(FMT) if i.finish_time else '', f'{i.id}_{i.retry}' if i.retry else i.id, i.ex_order])
        return response



@admin.register(Code)
class Admin(admin.ModelAdmin):
    # list_display:用于设置列表页要显示的不同字段
    # search_fields：用于设置搜索栏中要搜索的不同字段
    # list_fileter：边框筛选工具，比如可以设置为按作者进行筛选，常用的有选择的字段筛选、时间的过滤
    list_display = ('id','activity', 'name', 'sku', 'status', 'account','ex_id', 'ex_order', 'create_time', 'use_time', 'finish_time')
    search_fields = ('name', 'account','ex_order')
    list_filter = ('status','ex_id' ,('use_time', DateRangeFilterss), ('create_time', DateRangeFilterss), ('finish_time', DateRangeFilterss),autoFilter )
    actions = ('retry_order','bulk_editing','export_code','order_recharge')
    list_per_page = 20
    fields = ('activity', 'name', 'sku', 'status', 'account','ex_id', 'ex_order',  'use_time', 'finish_time','retry')

    #获取list_display数据
    def get_list_display(self, request):
        if request.user.has_perm('app.service') and not request.user.has_perm('app.change_code'):  # an example
            # 将元组修改为list列表（元组不容许修改元素内容 会报错）
            lists = list(self.list_display)
            # 修改列表内容 name_self 将卡券字段的中间部分加密
            lists[2] = 'name_self'
            # 将list列表转换会元组
            self.list_display = tuple(lists)
        else:
            self.list_display = (
            'id','activity', 'name', 'sku', 'status', 'account', 'ex_id', 'ex_order', 'create_time', 'use_time',
            'finish_time')

        return self.list_display

    def get_list_filter(self, request):
        if request.user.has_perm('app.service') and not request.user.has_perm('app.change_code'):  # an example
            self.list_filter = (('use_time', DateRangeFilterss), ('create_time', DateRangeFilterss), ('finish_time', DateRangeFilterss) )
        else:
            self.list_filter = ('status', autoexid, ('use_time', DateRangeFilterss), ('create_time', DateRangeFilterss),
                           ('finish_time', DateRangeFilterss), autoFilter)
        return self.list_filter
    # 获取当前用户信息（权限、是否为超级用户）
    #如果是超级管理员显示完整的权益券
    #如果不是超级管理员显示不完整的权益券码
    def name_self(self,obj):
        # 将权益券码部分用*代替 权益券码
        a = obj.name.replace(obj.name[5:-5], '*' * len(obj.name[5:-5]))
        return a;
    #待修改 权限语句

    #change_view 权益券修改的时候调用的函数
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # 判断语句 如果用户有app.service权限并且没有change_code权限的时候（表明该用户为客服用户）
        if request.user.has_perm('app.service') and  not request.user.has_perm('app.change_code'):  # an example
            #将元组修改为list列表（元组不容许修改元素内容 会报错）
            lists=list(self.fields)
            #修改列表内容 name_self 将卡券字段的中间部分加密
            lists[1]='name_self'
            #将list列表转换会元组
            self.fields=tuple(lists)
        else:
            self.fields=('activity', 'name', 'sku', 'status', 'account','ex_id', 'ex_order',  'use_time', 'finish_time','retry')
        return self.changeform_view(request, object_id, form_url, extra_context)

    @admin.action(description='充值重试')
    def retry_order(self, request, queryset):
        for i in queryset:
            i.retry += 1
            i.post_order()
    retry_order.has_service_permission=('service')

    @admin.action(description='订单重置')
    def order_recharge(self, request, queryset):
        for i in queryset:
            if i.status == 3 or i.status == 7 or i.status == 8:
                i.post_order_recharge()
    order_recharge.has_service_permission = ('service')


    @admin.action(description='批量修改-待充值')
    def bulk_editing(self, request, queryset):
        for i in queryset:
            i.change_style()

    bulk_editing.allowed_permissions = ('change',)
    def datetostring(self):
        return self.aa.strftime('%Y-%m-%d %H:%M:%S')

    @admin.action(description='导出权益券')
    def export_code(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=a.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow(
            ['所属活动', '权益券码', '兑换商品', '状态', '使用账号', '上游通道', '上游单号', '创建时间', '兑换时间',
             '到账时间','下游价格','换购订单号'])
        #修复导出功能的 全部导出
        qs = queryset
        begin = end = qs[0].create_time
        for i in qs:
            #便利整个导出数组找到 起止时间
            begin = min(begin, i.create_time)
            end = max(end, i.create_time)
        delta = timedelta(0,1)
        orderlist=DongOrder.objects.filter(create_time__range=(begin-delta, end+delta))
        order_dic={}
        for p in orderlist:
            for g in p.exchangeCode.split(';'):
                order_dic[g]=p.orderId
        mya = {p.id:(p.name,p.down_price) for p in Activity.objects.all()}
        for i in qs:
            if (order_dic.get(i.name,'')!=''):  # 如果在东莞订单信息表中找到数据
                # 换购订单号
                i.exchangeCode = order_dic.get(i.name,'')
            else:  # 在订单表中没有找到数据
                i.exchangeCode = '无'

            # 数据库字段如果为空会默认为-1
            if i.ex_id == -1:
                ex_name = "未知通道"
            elif i.ex_id != -1 and i.ex_id:
                ex_name = SOURCE[i.ex_id][1]
            else:
                ex_name = "未知通道"

            # 判断日期是否为空之后调用日期转字符串
            if i.create_time == None:
                create_time = i.create_time
            else:
                self.aa = i.create_time
                create_time = self.datetostring()
            if i.use_time == None:
                use_time = i.use_time
            else:
                self.aa = i.use_time
                use_time = self.datetostring()
            if i.finish_time == None:
                finish_time = i.finish_time
            else:
                self.aa = i.finish_time
                finish_time = self.datetostring()


            #关于兑换商品的信息处理
            sku=Sku.objects.filter(id=i.sku_id).values('product_id','name')
            if sku.count()>0:
                for g in sku:
                    g['product_id']
                mypro={i.id:i.name for i in Product.objects.filter(id=g['product_id'])}
                for g in sku:
                    i.sku_name=mypro.get(g['product_id'],'')+g['name']
            else:
                i.sku_name=mya.get(i.activity_id,('',0))[0]
            writer.writerow(
                [i.activity, i.name, i.sku_name, CODE_STATUS[i.status][1], i.account, ex_name, i.ex_order, create_time,
                 use_time, finish_time,mya.get(i.activity_id,(0,''))[1],i.exchangeCode]
                )

        return response
    export_code.allowed_permissions = ('change',)

@admin.register(OutCard)
class Admin(admin.ModelAdmin):
        list_display = ('sku', 'code', 'create_time', 'use_time', 'expire_time', 'status', 'name',)
        search_fields = ('name', 'code__name')
        list_filter = ('status',  ('use_time', DateRangeFilterss),('create_time', DateRangeFilterss),autoSku)
        actions = ['export_outcode']

        def datetostring(self):
            return self.aa.strftime('%Y-%m-%d %H:%M:%S')

        @admin.action(description='导出外部卡密')
        def export_outcode(self, request, queryset):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment;filename=a.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow(
                [ '兑换商品','内部卡密', '创建时间', '兑换时间', '过期时间', '状态', '卡密,分割'
                 ])
            # 修复导出功能的 全部导出
            qs = queryset

            for i in qs:
                # 判断日期是否为空之后调用日期转字符串
                if i.create_time == None:
                    create_time = i.create_time
                else:
                    self.aa = i.create_time
                    create_time = self.datetostring()
                if i.use_time == None:
                    use_time = i.use_time
                else:
                    self.aa = i.use_time
                    use_time = self.datetostring()
                if i.expire_time == None:
                    expire_time = i.expire_time
                else:
                    self.aa = i.expire_time
                    expire_time = self.datetostring()
                writer.writerow(
                    [i.sku, i.code, create_time,use_time, expire_time,CODE_STATUS[i.status][1], i.name]
                )
            return response


@admin.register(DongCard)
class Admin(admin.ModelAdmin):
        list_display = ('activity', 'consumer', 'cardCode', 'cardName', 'synchro', 'style', 'autoOut', 'faceAmt', 'productPrice')
        search_fields = ('cardCode', 'cardName')
        list_filter = ('style', 'autoOut')


@admin.register(DongOrder)
class Admin(admin.ModelAdmin):
    list_display = ('consumer', 'card', 'orderId', 'orderQuantity', 'orderTime', 'create_time')
    search_fields = ('orderId', 'exchangeCode')
