from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import WeekWorkPlanForm

from .models import WeekWorkPlan


class WeekWorkPlanCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': WeekWorkPlanForm,
        
    }


new = WeekWorkPlanCreateView.as_view()


class WeekWorkPlanUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': WeekWorkPlanForm,
        
    }


edit = WeekWorkPlanUpdateView.as_view()


class WeekWorkPlanListView(WFListView):
    wf_code = 'weekworkplan'
    model = WeekWorkPlan
    excel_file_name = 'weekworkplan'
    excel_titles = [
        'Created on', 'Created by',
        '创建时间', '最后更新人', '最后更新时间', '附件', '组织', '地点', '是否激活', '计划编号', '计划名称', '第三方机构', '频率', '完成时限', '状态', '策划人', '策划时间', '执行人', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.created_at, o.last_updated_by, o.last_updated_at, o.enclosure, o.orgid, o.place, o.is_activate, o.number, o.plan, o.third_org, o.rate_desc, o.time_limit, o.state, o.planner, o.plan_time, o.executor, 
            o.pinstance.cur_node.name,
        ]


show_list = WeekWorkPlanListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}