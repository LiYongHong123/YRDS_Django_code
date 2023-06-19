from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views, admin_views,api_out
from . import do_views
from . import api_views
urlpatterns = [
    url('api/out/order', api_out.order),
    url('api/out/queryorder', api_out.queryorder),
    url('admin_api/save', admin_views.save),
    url('admin_api/sku', admin_views.sku),
    url('admin_api/consumer', admin_views.consumer),
    url('admin_api/activity', admin_views.activity),
    url('api/check', api_views.check),
    url('api/use', api_views.use),
    url('d/card', do_views.card),
    url('d/buy', do_views.buy),
    url('use', views.use),
    url('code', views.code),
    url('retry', views.retry),
    # url('info', views.info),
    url('callback', views.callback),
    url('msgCode', views.msgCode),
    url('stock_check', views.stock_check),

    url(r'', views.index),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
