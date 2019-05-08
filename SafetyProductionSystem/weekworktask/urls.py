from django.conf.urls import url
from . import myviews

app_name = "weekworktask"

urlpatterns = [
    # 查询周期检测任务
    url(r'search/$', myviews.periodic_task_search, name='periodic_task_search'),
    # 周期检测任务列表展示
    url(r'^list/$', myviews.show_periodic_task_list, name='show_periodic_task_list'),
    # 周期检测任务添加
    url(r'^add/$', myviews.add_periodic_task, name='add_periodic_task'),
    # 周期检测任务详情
    url(r'(?P<wid>\d+)/detail/$', myviews.show_one_task, name='show_one_task'),
    # 周期检测任务修改
    url(r'(?P<wid>\d+)/edit/$', myviews.edit_periodic_task, name='edit_periodic_task'),
    # 周期检测任务删除
    url(r'(?P<wid>\d+)/delete/$', myviews.del_task, name='del_task'),
    url(r'^my_week_list/$', myviews.my_week_list, name='my_week_list'),   # 查看我的周期工作任务
    url(r'^(?P<w_id>\d+)/myweek_add/$', myviews.myweek_add, name='myweek_add'),   # 提交我的周期工作任务
    ]