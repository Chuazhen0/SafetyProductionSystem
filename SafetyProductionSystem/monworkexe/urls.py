from django.conf.urls import url
from . import myviews

app_name = 'monworkexe'

urlpatterns = [
    # 2.月度工作执行
    # 展示列表
    url(r'list/$', myviews.mon_work, name='mon_work'),
    # 添加月度工作执行
    url(r'add/$', myviews.mon_work_add, name='mon_work_add'),
    # 编辑月度工作执行
    url(r'(?P<m_id>\d+)/edit/$', myviews.mon_work_edit, name='mon_work_edit'),
    # 删除月度工作执行
    url(r'(?P<m_id>\d+)/delete/$', myviews.mon_work_delete, name='mon_work_delete'),
    # 查看详情
    url(r'(?P<m_id>\d+)/detail/$', myviews.mon_work_detail, name='mon_work_detail'),
    # ajax 获取选中员工number
    url(r'check/$', myviews.check, name='check'),
    # form表单搜索
    url(r'search/$', myviews.mon_work_search, name='mon_work_search'),

    ]