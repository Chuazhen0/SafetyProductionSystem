from django.conf.urls import url
from . import myviews

app_name = 'standard'

urlpatterns = [
    # ------------------------指标定义管理------------------------
    # 展示所有指标定义
    url(r'standard/$', myviews.show_all_standard, name='show_all_standard'),
    # 新增指标定义
    url(r'standard_add/$', myviews.add_standard, name='add_standard'),
    # 编辑指标定义
    url(r'(?P<sid>\d+)/standard_edit/$', myviews.edit_standard, name='edit_standard'),
    # 删除指标定义
    url(r'(?P<sid>\d+)/standard_delete/$', myviews.del_standard, name='del_standard'),
    # 展示指标定义详情
    url(r'(?P<sid>\d+)/standard_one_detail/$', myviews.show_standard_details, name='show_standard_details'),
    # 新建指标定义详情
    url(r'(?P<sid>\d+)/standard_detail_add/$', myviews.add_stand_details, name='add_stand_details'),
    # 展示一个指标定义详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_detail/$', myviews.show_one_stand_details, name='show_one_stand_details'),
    # 编辑一个指标定义详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_edit/$', myviews.edit_stand_details, name='edit_stand_details'),
    # 删除一个指标定义详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_delete/$', myviews.del_stand_details, name='del_stand_details'),
    # 查询指表填报
    url(r'standard_search/$', myviews.standard_search, name='standard_search'),

    # ------------------------指标填报管理------------------------
    # 查询测点填报
    url(r'standard_fill_search/$', myviews.standardfill_search, name='standardfill_search'),
    # 展示所有指标填报
    url(r'standard_fill/$', myviews.show_all_standardfill, name='show_all_standardfill'),
    # 添加一个指标填报信息
    url(r'standard_fill_add/$', myviews.add_standardfill, name='add_standardfill'),
    # ajax动态根据监督类型改变指标类型
    url(r'change_station/$',myviews.change_station,name='change_station'),
    # 编辑一个指标填报
    url(r'(?P<sid>\d+)/standard_fill_edit/$', myviews.edit_standardfill, name='edit_standardfill'),
    # 删除指标填报
    url(r'(?P<sid>\d+)/standard_fill_delete/$', myviews.del_standardfill, name='del_standardfill'),
    # 展示指标填报详情内容
    url(r'(?P<sid>\d+)/standard_detail_fill/$', myviews.show_all_standardfill_details, name='show_all_standardfill_details'),
    # 新增指标填报详情内容
    url(r'(?P<sid>\d+)/standard_detail_fill_add/$', myviews.add_standardfill_details, name='add_standardfill_details'),
    # 展示一个指标填报详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_fill_detail/$', myviews.show_one_standardfill_details, name='show_one_standardfill_details'),
    # 编辑一个指标填报详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_fill_edit/$', myviews.edit_standardfill_details, name='edit_standardfill_details'),
    # 删除一个指标填报详情
    url(r'(?P<did>\d+)/(?P<sid>\d+)/standard_detail_fill_delete/$', myviews.del_standardfill_details, name='del_standardfill_details'),


]
