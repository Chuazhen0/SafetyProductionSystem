from django.conf.urls import url
from . import myviews

app_name = 'yearplan'

urlpatterns = [
    # 展示列表
    url(r'list/$', myviews.year_plan, name='year_plan'),
    # 新增年度计划汇总
    url(r'add/$', myviews.year_plan_add, name='year_plan_add'),
    # 编辑年度计划汇总
    url(r'(?P<y_id>\d+)/edit/$', myviews.year_plan_edit, name='year_plan_edit'),
    # 详情
    url(r'(?P<y_id>\d+)/detail/$', myviews.year_plan_detail, name='year_plan_detail'),
    # 删除
    url(r'(?P<y_id>\d+)/delete/$', myviews.year_plan_delete, name='year_plan_delete'),
    # ajax 搜索
    url(r'search/$', myviews.year_plan_search, name='year_plan_search'),
    # 下载附件
    url(r'down_file/$', myviews.down_file, name='down_file'),
    ]