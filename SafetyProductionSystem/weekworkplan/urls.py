from django.conf.urls import url
from . import myviews

app_name = "weekworkplan"

urlpatterns = [

    # 查询周期检测计划
    url(r'search/$', myviews.periodic_search, name='periodic_search'),
    # 展示周期检测计划
    url(r'list/$', myviews.show_periodic_list, name='show_periodic_list'),
    # 展示一个周期检测计划
    url(r'(?P<wid>\d+)/detail/$', myviews.show_one_periodic, name='show_one_periodic'),
    # 新建周期检测计划
    url(r'add/$', myviews.add_periodic_plan, name='add_periodic_plan'),
    # 修改周期检测计划
    url(r'(?P<wid>\d+)/edit/$', myviews.edit_periodic_plan, name='edit_periodic_plan'),
    # 删除周期检测计划
    url(r'(?P<wid>\d+)/delete/$', myviews.del_periodic, name='del_periodic'),
    url(r'down_file/$', myviews.down_file, name='down_file'),
]