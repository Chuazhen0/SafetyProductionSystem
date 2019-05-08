from django.conf.urls import url
from . import myviews

app_name = 'regularworkplan'

urlpatterns = [
    url(r'list/$', myviews.regularwork, name='regularworkplan'),
    url(r'add/$', myviews.regularwork_add, name='regularwork_add'),
    url(r'(?P<e_id>\d+)/detail/$', myviews.regularwork_detail, name='regularwork_detail'),
    url(r'(?P<e_id>\d+)/edit/$', myviews.regularwork_edit, name='regularwork_edit'),
    url(r'(?P<e_id>\d+)/delete/$', myviews.regularwork_delete, name='regularwork_delete'),
    url(r'search/$', myviews.regularwork_search, name='regularwork_search'),
    # 定期工作工作准备
    url(r'ready_add/(?P<pid>\d+)/$', myviews.add_work_ready, name='add_work_ready'),
    url(r'ready_detail/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.show_one_ready, name='show_one_ready'),
    url(r'(?P<pid>\d+)/ready_list/$', myviews.show_work_ready, name='show_work_ready'),
    url(r'ready_delete/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.del_work_ready, name='del_work_ready'),
    # 定期工作注意事项
    url(r'matter_add/(?P<pid>\d+)/$', myviews.add_matter, name='add_work_matter'),
    url(r'matter_detail/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.show_one_matter, name='show_one_matter'),
    url(r'(?P<pid>\d+)/matter_list/$', myviews.show_work_ready, name='show_work_matter'),
    url(r'matter_delete/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.del_work_matter, name='del_work_matter'),
    # 定期工作工作内容
    url(r'work_content_add/(?P<pid>\d+)/$', myviews.add_work_content, name='add_work_content'),
    url(r'work_content_detail/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.show_one_content, name='show_one_content'),
    url(r'(?P<pid>\d+)/work_content_list/$', myviews.show_work_ready, name='show_work_ready'),
    url(r'work_content_delete/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.del_work_content, name='del_work_content'),
    # 定期工作工作数据
    url(r'work_data_add/(?P<pid>\d+)/$', myviews.add_work_data, name='add_work_data'),
    url(r'work_data_detail/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.show_one_data, name='show_one_data'),
    url(r'(?P<pid>\d+)/work_data_list/$', myviews.show_work_ready, name='show_work_ready'),
    url(r'work_data_delete/(?P<pid>\d+)/(?P<zid>\d+)/$', myviews.del_work_data, name='del_work_data'),
    # 定期工作导入模板下载
    url(r'download_regularworkplan_mould/$',myviews.download_regularworkplan_mould,name='download_regularworkplan_mould'),
    url(r'search_kks/$',myviews.search_kks,name='search_kks'),

]