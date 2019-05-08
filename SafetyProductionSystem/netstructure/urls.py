
from django.conf.urls import url
from . import myviews

app_name = 'netstructure'

urlpatterns = [
    # 展示网络结构列表
    url(r'^list/$', myviews.show_structure_list, name="show_structure_list"),
    # 查看网络结构详情
    url(r'^(?P<u_id>\d+)/detail/$', myviews.structure_detail, name="structure_detail"),
    # 新建网络结构
    url(r'add/$', myviews.new_structure, name="new_structure"),
    # 编辑网络结构
    url(r'^(?P<u_id>\d+)/edit/$', myviews.edit_structure, name="edit_structure"),
    # 删除网络结构
    url(r'^(?P<u_id>\d+)/(?P<m_id>\d+)/delete/$', myviews.delete_structure, name="delete_structure"),
    # 搜索网络结构
    url(r'^search/$', myviews.netstructure_search, name="netstructure_search"),
    # 网络结构导入excel文件
    url(r'^structure_import_excel/$', myviews.structure_import_excel, name="structure_import_excel"),
    # 网络结构导入模板excel
    url(r'download_net_mould/$', myviews.download_net_mould, name="download_net_mould")
    ]