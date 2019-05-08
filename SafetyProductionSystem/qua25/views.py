from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import QuaForm

from .models import Qua


class QuaCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': QuaForm,
        
    }


new = QuaCreateView.as_view()


class QuaUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': QuaForm,
        
    }


edit = QuaUpdateView.as_view()


class QuaListView(WFListView):
    wf_code = 'qua25'
    model = Qua
    excel_file_name = 'qua25'
    excel_titles = [
        'Created on', 'Created by',
        '状态', '创建时间', '最后更新人', '最后更新时间', '组织', '地点', '是否激活', '资质类型', '监督专业', '发证单位', '证件编号', '有效日期', '资质证书', '关联人员', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.state, o.created_at, o.last_updated_by, o.last_updated_at, o.orgid, o.place, o.is_activate, o.qua_type, o.supervision_major, o.publish_organ, o.number, o.effect_time, o.qua_enclosure, o.staff, 
            o.pinstance.cur_node.name,
        ]


show_list = QuaListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}