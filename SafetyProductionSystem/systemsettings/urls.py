from django.conf.urls import url,include
from . import views
from django.views.generic import RedirectView

app_name = 'systemsettings'

urlpatterns = [
    url(r'^login/$', views.mylogin, name='login'),  # 用户登陆
    url(r'^check_info/$', views.check_info, name='check_info'),  # ajax弹窗
    url(r'^login_out/$', views.login_out, name="login_out"),  # 用户退出
    url(r'^starter/$',views.starter,name='starter'),
    url(r'^user_list/$', views.user_list, name="user_list"),  # 点击用户进入用户界面
    url(r'^search_user/',views.search_user,name='search_user'), # 根据条件搜索用户
    url(r'^(?P<u_id>\d+)/detail/$', views.user_details, name="user_details"),  # 展示用户详情页面
    url(r'^(?P<u_id>\d+)/self_detail/$', views.self_detail, name="self_detail"),  # 展示用户详情页面
    url(r'^add/$', views.add_user, name='add_user'),  # 新增用户
    url(r'^check_department/$', views.check_department, name='check_department'),  # 新增用户
    url(r'^(?P<u_id>\w+)/edit/$', views.edit_user, name='edit_user'),  # 修改用户
    url(r'^delete/(?P<u_id>\d+)/$', views.delete, name='delete'),  # 删除用户
    url(r'^role_list/$', views.role_list, name='role_list'),  # 显示所有操作项和角色
    url(r'^search_role/$', views.search_role,name='search_role'), # 根据条件搜索角色
    url(r'^role_add/$', views.new_role, name='new_role'),  # 新建角色
    url(r'^role_edit/(?P<rid>\d+)/$', views.edit_role, name='edit_role'),  # 编辑角色
    url(r'^role_delete/(?P<rid>\d+)/$', views.del_role, name='del_role'),  # 删除(停用)角色
    url(r'^show_opeartion/$' , views.show_opeartion , name = "show_opeartion"),
    url(r'^show_role/$' , views.show_role , name = "show_role"),
    url(r'^check_password/$' , views.check_password , name = "check_password"),
    url(r'^update_info2/$' , views.update_info2 , name = "update_info2"),
    url(r'^update_info1/$' , views.update_info1 , name = "update_info1"),
    url(r'^user_import_excel/$' , views.user_import_excel , name = "user_import_excel"),  # excel导入用户
    url(r'^show_og/' , views.show , name = "show_og"),  # 组织机构#  树状结构数据的获取
    url(r'^all_organiza/$', views.all_organiza , name = 'all_organiza'),
    url(r'tree/$', views.tree, name='dept_tree'),
    url(r'(?P<mid>\d+)/(?P<tid>\d+)/org_detail/$', views.show_one_organization, name='show_one_organization'),   # 展示一个组织机构信息
    url(r'(?P<mid>\d+)/(?P<tid>\d+)/add_organization/$', views.add_organization, name='add_organization'),   # 添加组织机构
    url(r'(?P<mid>\d+)/(?P<tid>\d+)/edit_organization/$', views.edit_organization, name='edit_organization'),   # 修改组织机构
    url(r'(?P<mid>\d+)/(?P<tid>\d+)/delete_origaniza/$',  views.delete_origaniza, name="delete_origaniza"),  #  删除组织机构
    url(r'download_user_mould/$', views.download_user_mould, name="download_user_mould"),  # 用户导入模板excel
    url(r'^duty_group_list/$', views.duty_group_list, name="duty_group_list"),  # 责任组列表页
    url(r'^duty_group_search/$',views.duty_group_search,name='duty_group_search'), #责任组搜索
    url(r'^duty_group_add/$', views.duty_group_add, name="duty_group_add"),  # 责任组新建
    url(r'^duty_group_detail/(?P<group_id>\d+)/$', views.duty_group_detail, name="duty_group_detail"),  # 责任组详情
    url(r'^duty_group_delete/(?P<group_id>\d+)/$', views.duty_group_delete, name="duty_group_delete"),  # 责任组删除
    url(r'^duty_group_edit/(?P<group_id>\d+)/$', views.duty_group_edit, name="duty_group_edit"),  # 责任组编辑
    url('page', views.update_page, name="update_page"),  # 责任组编辑

]
