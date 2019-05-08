from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import WeekWorkTaskForm

from .models import WeekWorkTask


class WeekWorkTaskCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': WeekWorkTaskForm,
        
    }


new = WeekWorkTaskCreateView.as_view()


class WeekWorkTaskUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': WeekWorkTaskForm,
        
    }


edit = WeekWorkTaskUpdateView.as_view()


class WeekWorkTaskListView(WFListView):
    wf_code = 'weekworktask'
    model = WeekWorkTask
    excel_file_name = 'weekworktask'
    excel_titles = [
        'Created on', 'Created by',
        '创建时间', '最后更新人', '最后更新时间', '附件', '组织', '地点', '是否激活', '状态', '任务编号', '任务名称', '计划编号', '计划开始时间', '完成时限', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.created_at, o.last_updated_by, o.last_updated_at, o.enclosure, o.orgid, o.place, o.is_activate, o.state, o.number, o.task_name, o.plan_number, o.task_start_time, o.time_limit, 
            o.pinstance.cur_node.name,
        ]


show_list = WeekWorkTaskListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}