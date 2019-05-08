from django.conf.urls import url,include
from . import myviews

app_name = 'netstaff'

urlpatterns = [
    # 2. 网络人员维护
    # 展示网络结构
    url(r'list/$', myviews.show_structure, name="show_structure"),
    # 网路机构人员信息
    url(r'(?P<u_id>\d+)/detail/$', myviews.net_staff, name="net_staff"),
    # 增加网络机构人员
    url(r'add/$', myviews.add_staff, name="add_staff"),
    # 删除网络机构人员
    url(r'(?P<u_id>\d+)/delete/$', myviews.delete_staff, name="delete_staff"),
    # 编辑网络机构人员
    url(r'(?P<u_id>\d+)/edit/$', myviews.edit_net_staff, name="edit_net_staff"),
    # 查询网络结构
    url(r'search/$', myviews.structure_search, name="structure"),
    ]