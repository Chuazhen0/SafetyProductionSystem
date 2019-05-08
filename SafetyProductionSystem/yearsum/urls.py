from django.conf.urls import url
from . import myviews

app_name = 'yearsum'

urlpatterns = [
    # 4.总结汇总
    # 展示列表
    url(r'list/$', myviews.year_sum, name='year_sum'),
    # 新增年度总结汇总
    url(r'add/$', myviews.year_sum_add, name='year_sum_add'),
    # 编辑年度总结汇总
    url(r'(?P<y_id>\d+)/edit/$', myviews.year_sum_edit, name='year_sum_edit'),
    # 详情
    url(r'(?P<y_id>\d+)/detail/$', myviews.year_sum_detail, name='year_sum_detail'),
    # 删除年度总结汇总
    url(r'(?P<y_id>\d+)/delete/$', myviews.year_sum_delete, name='year_sum_delete'),
    # form表单搜索
    url(r'search/$', myviews.year_sum_search, name='year_sum_search'),
    # 下载附件
    url(r'down_file/$', myviews.down_file, name='down_file'),
    ]