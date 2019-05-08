from django.conf.urls import url
from . import myviews

app_name = 'regularworktask'

urlpatterns = [
    url(r'my_list/$', myviews.my_list, name='my_list'),  # 展示待我完成的定期工作任务列表
    url(r'^my_search/$',myviews.my_search,name='my_search'), # 我的定期工作任务搜索
    url(r'(?P<e_id>\d+)/my_add/$', myviews.my_add, name='my_add'),  # 填写完成情况
    url(r'list/$', myviews.regularwork, name='regularworktask'),
    url(r'add/$', myviews.regularwork_add, name='regularwork_add'),
    url(r'(?P<e_id>\d+)/detail/$', myviews.regularwork_detail, name='regularwork_detail'),
    url(r'(?P<e_id>\d+)/edit/$', myviews.regularwork_edit, name='regularwork_edit'),
    url(r'(?P<e_id>\d+)/delete/$', myviews.regularwork_delete, name='regularwork_delete'),
    url(r'search/$', myviews.regularwork_search, name='regularwork_search'),
    url(r'regularwork_import_excel/$', myviews.regularwork_import_excel, name='regularwork_import_excel'),


    # url(r'search/$', myviews.regularwork_search, name='regularwork_search'),
]