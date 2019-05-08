from django.conf.urls import url
from . import myviews

app_name = 'warningre'

urlpatterns = [
    # 查询告警回执单
    url(r'search/$', myviews.warning_rece_search, name='warning_rece_search'),
    # 添加告警回执单
    url(r'add/$', myviews.add_warningreceipt, name='add_warningreceipt'),
    # 告警通知回执
    url(r'list/$', myviews.show_warningreceipt, name='show_warningreceipt'),
    # 展示一个告警回执详情
    url(r'(?P<wid>\d+)/detail/$', myviews.show_one_warningreceipt, name='show_one_warningreceipt'),
    # 编辑告警回执单
    url(r'(?P<wid>\d+)/edit/$', myviews.one_warningreceipt, name='one_warningreceipt'),
    # 删除告警回执单
    url(r'(?P<wid>\d+)/delete/$', myviews.del_warningreceipt, name='del_warningreceipt'),
    # 下载附件
    url(r'down_file/$', myviews.down_file, name='down_file'),
]