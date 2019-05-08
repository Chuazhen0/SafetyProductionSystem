from django.conf.urls import url
from . import myviews
from .views import flowchart
from .views import processinstance
from .views.list import ListWF,ListWF_inverted
from .views.list import MyWF
from .views.list import Todo,Todo_inverted
from .views.transition import BatchExecuteAgreeTransitionView
from .views.transition import BatchExecuteGiveUpTransitionView
from .views.transition import BatchExecuteRejectTransitionView
from .views.transition import ExecuteAgreeTransitionView
from .views.transition import ExecuteBackToTransitionView
from .views.transition import ExecuteGiveUpTransitionView
from .views.transition import ExecuteRejectTransitionView
from .views.transition import ExecuteTransitionView
from .views.transition import execute_transitions

urlpatterns = [
    url(r'^t/$', ExecuteTransitionView.as_view(), name="wf_execute_transition"),
    url(r'^t/agree/$', ExecuteAgreeTransitionView.as_view(), name="wf_agree"),
    url(r'^t/back_to/$', ExecuteBackToTransitionView.as_view(), name="wf_back_to"),
    url(r'^t/reject/$', ExecuteRejectTransitionView.as_view(), name="wf_reject"),
    url(r'^t/give_up/$', ExecuteGiveUpTransitionView.as_view(), name="wf_give_up"),
    url(r'^t/batch/agree/$', BatchExecuteAgreeTransitionView.as_view(), name="wf_batch_agree"),
    url(r'^t/batch/reject/$', BatchExecuteRejectTransitionView.as_view(), name="wf_batch_reject"),
    url(r'^t/batch/give_up/$', BatchExecuteGiveUpTransitionView.as_view(), name="wf_batch_give_up"),
    url(
        r'^t/e/(?P<wf_code>\w+)/(?P<trans_func>\w+)/$', execute_transitions,
        name='wf_execute_transition'),
    url(r'^start_wf/$', processinstance.start_wf, name='wf_start_wf'),
    url(r'^report_list/$', processinstance.report_list, name='wf_report_list'),
    url(r'^new/(?P<wf_code>\w+)/$', processinstance.new, name='wf_new'),
    url(r'^delete/$', processinstance.delete, name='wf_delete'),
    url(r'^list/(?P<wf_code>\w+)/$', processinstance.show_list, name='wf_list'),
    url(r'^edit/(?P<pk>\d+)/$', processinstance.edit, name='wf_edit'),
    url(r'^(?P<pk>\d+)/$', processinstance.detail, name='wf_detail'),
    url(r'^(?P<pk>\d+)/print/$', processinstance.detail,
        {
            'ext_ctx': {'is_print': True}
        },
        name='wf_print_detail'),

    url(r'^todo/$', Todo.as_view(), name='wf_todo'),
    url(r'^todo_inverted/$',Todo_inverted.as_view(),name='wf_todo_inverted'),
    url(r'^todo_search/$',myviews.todo_search,name='todo_search'),
    url(r'^list/$', ListWF.as_view(), name='wf_list_wf'),
    url(r'^list_inverted/$', ListWF_inverted.as_view(), name='wf_list_wf'),
    url(r'^wf_search/$',myviews.wf_search,name='wf_search'),
    url(r'^my/$', MyWF.as_view(), name='wf_my_wf'),
    url(r'^flowchart/process/(?P<wf_code>\w+)/$',
        flowchart.process_flowchart, name='wf_process_flowchart'),
    url(r'^mywf_list/$', myviews.mywf_list, name='mywf_list'),
    url(r'^mywf_search/$',myviews.mywf_search,name='mywf_search'),
    url(r'^mywf_add/$', myviews.mywf_add, name='mywf_add'),
    url(r'^(?P<p_id>\d+)/mywf_detail/$', myviews.mywf_detail, name='mywf_detail'),
    # url(r'^(?P<p_id>\d+)/mywf_detail2/$', myviews.mywf_detail2, name='mywf_detail2'),
    url(r'^(?P<p_id>\d+)/mywf_delete/$', myviews.mywf_delete, name='mywf_delete'),
    # url(r'^check_app_object/$', myviews.check_app_object, name='check_app_object'),
    url(r'^(?P<pp_id>\d+)/node_add/$', myviews.node_add, name='node_add'),
    url(r'^(?P<node_id>\d+)/node_delete/$', myviews.node_delete, name='node_delete'),
    url(r'^(?P<node_id>\d+)/node_edit/$', myviews.node_edit, name='node_edit'),
    url(r'^mywf_checkjob/$', myviews.mywf_checkjob, name='mywf_checkjob'),
    url(r'^mywf_get_user_list/$', myviews.mywf_get_user_list, name='mywf_get_user_list'),   # 根据岗位/部门查询对应用户列表返回

    # 迷糊查询
    url(r'^ajax/search/$', myviews.ajax_search, name='ajax_search'),

    url(r'^(?P<process_id>\d+)/wf_history/$', myviews.wf_history, name='wf_history'),   # 工作流程历史记录
    url(r'^(?P<process_id>\d+)/todo_history/$', myviews.todo_history, name='todo_history'),  # 工作流程历史记录
    url(r'get_complete_desc/$', myviews.get_complete_desc, name='get_complete_desc'),   # 根据流程id查询对应的任务完成情况描述信息
    url(r'get_username/$', myviews.get_username, name='get_username'),   # 根据用户帐号查询用户名
    url(r'^(?P<task_id>\d+)/(?P<pro_ins_id>\d+)/wf_approval/$', myviews.wf_approval, name='wf_approval'),   # 进入审批详情页，查看工作内容，进行通过或驳回操作
]
