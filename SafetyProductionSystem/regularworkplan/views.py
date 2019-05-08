from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import RegularWorkForm

from .models import RegularWork


class RegularWorkCreateView( CreateView):
    form_classes = {
        'form': RegularWorkForm,

    }


new = RegularWorkCreateView.as_view()


class RegularWorkUpdateView( UpdateView):
    form_classes = {
        'form': RegularWorkForm,

    }


edit = RegularWorkUpdateView.as_view()


class RegularWorkListView(WFListView):
    wf_code = 'regularworkplan'
    model = RegularWork
    excel_file_name = 'regularworkplan'
    excel_titles = [
        'Created on', 'Created by',
        '组织', '地点', '状态', '编号', '来源', '附件', '告警通知单名称', '监督类型', '执行人', '异常情况', '可能或已经造成的后果', '整改建议', '整改时间要求', '是否激活',
        '创建时间', '告警通知单最后更新人', '最后更新时间', '工单类型',
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.orgid, o.place, o.state, o.number, o.resource, o.enclosure, o.title, o.upervise_major, o.exetuct_enployee,
            o.abnormal, o.result, o.suggest, o.time_require, o.is_activate, o.created_at, o.last_updated_by,
            o.last_updated_at, o.work_type,
            o.pinstance.cur_node.name,
        ]


show_list = RegularWorkListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}