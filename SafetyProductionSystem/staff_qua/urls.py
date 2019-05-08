from django.conf.urls import url
from . import myviews

app_name = 'staff_qua'

urlpatterns = [
    # 展示所有人员
    url(r'list/$', myviews.show_employee, name="show_employee"),
    # 查看某个人员的资质
    url(r'(?P<u_id>\d+)/bug_bug/$', myviews.show_staff_qua_datail, name="show_staff_qua_datail"),
    # 编辑人员资质
    url(r'(?P<u_id>\d+)/edit/$', myviews.edit_staff_qua, name="edit_staff_qua"),
    # 增加人员资质
    url(r'(?P<u_id>\d+)/add/$', myviews.add_staff_qua, name="add_staff_qua"),
    # 删除人员资质
    url(r'(?P<u_id>\d+)/delete/$', myviews.delete_staff_qua, name='delete_staff_qua'),
    # 查询人员资质
    url(r'search/$', myviews.staff_qua_search, name='staff_qua_search'),
    ]