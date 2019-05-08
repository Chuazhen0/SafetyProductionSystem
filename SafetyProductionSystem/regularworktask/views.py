from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import RegularWorkTaskForm

from .models import RegularWorkTask


class RegularWorkTaskCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': RegularWorkTaskForm,
        
    }


new = RegularWorkTaskCreateView.as_view()


class RegularWorkTaskUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': RegularWorkTaskForm,
        
    }


edit = RegularWorkTaskUpdateView.as_view()


class RegularWorkTaskListView(WFListView):
    wf_code = 'regularworktask'
    model = RegularWorkTask
    excel_file_name = 'regularworktask'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '定期工作任务', '定期工作任务完成情况', '是否激活', '是否已弹窗', '是否已读', '附件', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.regularwork, o.result, o.is_activate, o.tanchuang, o.has_readed, o.enclosure_file, 
            o.pinstance.cur_activity.name,
        ]


show_list = RegularWorkTaskListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}