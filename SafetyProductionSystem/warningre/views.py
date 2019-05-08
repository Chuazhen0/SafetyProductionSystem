from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import WarningReceiptForm

from .models import WarningReceipt


class WarningReceiptCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': WarningReceiptForm,
        
    }


new = WarningReceiptCreateView.as_view()


class WarningReceiptUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': WarningReceiptForm,
        
    }


edit = WarningReceiptUpdateView.as_view()


class WarningReceiptListView(WFListView):
    wf_code = 'warningre'
    model = WarningReceipt
    excel_file_name = 'warningre'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '状态', '告警回执单编码', '关联告警通知单', '创建时间', '最后更新时间', '工单类型', '附件', '回执内容', '回执结果', '是否激活', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.state, o.number, o.warning_notice, o.created_at, o.last_updated_at, o.work_type, o.enclosure, o.content, o.result, o.is_activate, 
            o.pinstance.cur_activity.name,
        ]


show_list = WarningReceiptListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}