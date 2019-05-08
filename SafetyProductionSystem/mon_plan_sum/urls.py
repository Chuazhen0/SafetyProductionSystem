from django.conf.urls import url
from . import myviews

app_name = 'mon_plan_sum'

urlpatterns = [
# 展示列表
url(r'list/$', myviews.mon_plan_sum, name='mon_plan_sum_list'),
# 添加月度计划
url(r'add/$', myviews.mon_plan_sum_add, name='mon_plan_sum_add'),
# 编辑月度计划
url(r'(?P<m_id>\d+)/edit/$', myviews.mon_plan_sum_edit, name='mon_plan_sum_edit'),
# 删除月度计划
url(r'(?P<m_id>\d+)/delete/$', myviews.mon_plan_sum_delete, name='mon_plan_sum_delete'),
# 查看详情
url(r'(?P<m_id>\d+)/detail/$', myviews.mon_plan_sum_detail, name='mon_plan_sum_detail'),
# form表单搜索
url(r'search/$', myviews.mon_plan_sum_search, name='mon_plan_sum_search'),
url(r'down_file/$', myviews.down_file, name='down_file'),
]