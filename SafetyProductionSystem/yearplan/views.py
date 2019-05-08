from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import YearPlanForm

from .models import YearPlan


class YearPlanCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': YearPlanForm,
        
    }


new = YearPlanCreateView.as_view()


class YearPlanUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': YearPlanForm,
        
    }


edit = YearPlanUpdateView.as_view()


class YearPlanListView(WFListView):
    wf_code = 'yearplan'
    model = YearPlan
    excel_file_name = 'yearplan'
    excel_titles = [
        'Created on', 'Created by',
        '计划描述', '年度计划编码', '年份', '公司名称', '创建时间', '最后更新人', '最后更新时间', '是否激活', '附件', '状态', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.desc, o.number, o.year, o.place, o.created_at, o.last_updated_by, o.last_updated_at, o.is_activate, o.enclosure, o.state, o.work_type, 
            o.pinstance.cur_activity.name,
        ]


show_list = YearPlanListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}