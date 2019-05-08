from django.conf.urls import url,include
from . import myviews
from django.views.generic import RedirectView

app_name = 'myform'

urlpatterns = [
    # 展示填报报表
    url(r'^show_all_form/$', myviews.show_user_data, name='show_user_data'),
    # 填报的table页面
    url(r'^show_add_form/$', myviews.show_add_target, name='show_add_target'),
    # 展示所有分专业报表
    url(r'^watch_form/$', myviews.show_all_form, name='show_all_form'),
    # 展示一个专业报表的详情
    url(r'^watch_one_form/$', myviews.show_one_form, name='show_one_form'),
    # 添加一个新的报表头
    url(r'^form_attribute_add/$', myviews.add_myform_head, name='form_attribute_add'),
    # 汇总表展示
    url(r'^all_remittance_show/$', myviews.show_all_time, name='show_all_time'),
    # 点击单个详情汇总表
    url(r'^one_remittance_show/$', myviews.remittance_show, name='remittance_show'),
    url(r'form_search/$', myviews.form_search, name="form_search"),  # 查询报表
    url(r'form_search_show/$', myviews.form_search_show, name="form_search_show"),  # 查看列表查询报表
    url(r'state_change/$', myviews.state_change, name="state_change"),  # 查询报表
    url(r'^delete_form/(?P<form_id>\d+)/$', myviews.delete_form, name='delete_form'),  # 删除报表头
]
