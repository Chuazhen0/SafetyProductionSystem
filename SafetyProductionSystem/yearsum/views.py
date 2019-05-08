from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import YearSumForm

from .models import YearSum


class YearSumCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': YearSumForm,
        
    }


new = YearSumCreateView.as_view()


class YearSumUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': YearSumForm,
        
    }


edit = YearSumUpdateView.as_view()


class YearSumListView(WFListView):
    wf_code = 'yearsum'
    model = YearSum
    excel_file_name = 'yearsum'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '总结描述', '总结类型', '年份', '状态', '创建时间', '最后更新人', '最后更新时间', '附件', '是否激活', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.sum_desc, o.sum_type, o.year, o.state, o.created_at, o.last_updated_by, o.last_updated_at, o.enclosure, o.is_activate, o.work_type, 
            o.pinstance.cur_activity.name,
        ]


show_list = YearSumListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}