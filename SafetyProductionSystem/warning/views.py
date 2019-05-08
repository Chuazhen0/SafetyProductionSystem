from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import WarningNoticeForm

from .models import WarningNotice


class WarningNoticeCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': WarningNoticeForm,
        
    }


new = WarningNoticeCreateView.as_view()


class WarningNoticeUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': WarningNoticeForm,
        
    }


edit = WarningNoticeUpdateView.as_view()


class WarningNoticeListView(WFListView):
    wf_code = 'warning'
    model = WarningNotice
    excel_file_name = 'warning'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '状态', '告警通知单编码', '来源', '附件', '告警通知单名称', '监督类型', '关联设备', '关联问题', '责任人', '异常情况', '可能或已经造成的后果', '整改建议', '整改时间要求', '是否激活', '最后更新时间', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.state, o.number, o.resource, o.enclosure, o.title, o.supervise_major, o.equipment, o.problem, o.exetuct_user, o.abnormal, o.result, o.suggest, o.time_require, o.is_activate, o.last_updated_at, o.work_type, 
            o.pinstance.cur_activity.name,
        ]


show_list = WarningNoticeListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}