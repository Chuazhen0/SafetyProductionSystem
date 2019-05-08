from django.conf.urls import url
from . import myviews

app_name = "qua25"

urlpatterns = [
    # --------------- 人员资质维护 --------------  朱洪立
    # 查看所有资质类型
    url(r'^list/', myviews.qua_list, name="qua_list"),
    # 增加
    url(r'^add/', myviews.add_qua_info, name="add_qua_info"),
    # 查看详情
    url(r'^(?P<u_id>\d+)/detail/', myviews.qua_detail, name="qua_detail"),
    # 编辑
    url(r'^(?P<u_id>\d+)/edit/', myviews.edit_staff, name="edit_staff"),
    # 删除
    url(r'^(?P<u_id>\d+)/delete/', myviews.delete_staff, name="delete_staff"),
    # 查找资质类型
    url(r'^search/$', myviews.qua_search, name="qua_search"),
    # 查看所有资质编码
    #url(r'^show_staff_encrypt/', myviews.show_staff_encrypt, name='show_staff_encrypt'),
    # 新增资质编码
    #url(r'^add_staff_encrypt/', myviews.add_staff_encrypt, name='add_staff_encrypt'),
]