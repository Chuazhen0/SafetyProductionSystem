from django.conf.urls import url
from . import myviews

app_name = "quatype"

urlpatterns = [
    # ----------------  资质类别维护 ------------- 朱洪立
    # 查看所有资质类型
    url(r'^list/', myviews.qua_type_list, name='qua_type_list'),
    # 添加资质类型
    url(r'^add/', myviews.qua_type_add, name='qua_type_add'),
    # 编辑资质类型
    url(r'^(?P<u_id>\d+)/edit/', myviews.qua_type_edit, name='qua_type_edit'),
    # 删除资质类型
    url(r'^(?P<u_id>\d+)/delete/', myviews.qua_type_delete, name='qua_type_delete'),
    # 展示详情
    url(r"^(?P<u_id>\d+)/detail/", myviews.qua_type_detail, name='qua_type_detail'),
    # 搜索资质类型
    url(r'^search/', myviews.quatype_search, name='quatype_search'),
    ]