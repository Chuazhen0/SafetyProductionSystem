from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import MonPlanSumForm

from .models import MonPlanSum


class MonPlanSumCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': MonPlanSumForm,
        
    }


new = MonPlanSumCreateView.as_view()


class MonPlanSumUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': MonPlanSumForm,
        
    }


edit = MonPlanSumUpdateView.as_view()


class MonPlanSumListView(WFListView):
    wf_code = 'mon_plan_sum'
    model = MonPlanSum
    excel_file_name = 'mon_plan_sum'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '计划描述', '计划编码', '监督类型', '年份', '月份', '状态', '创建时间', '最后更新人', '最后更新时间', '附件', '是否激活', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.desc, o.number, o.supervision_major, o.year, o.month, o.state, o.created_at, o.last_updated_by, o.last_updated_at, o.enclosure, o.is_activate, o.work_type, 
            o.pinstance.cur_activity.name,
        ]


show_list = MonPlanSumListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}