from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import NetStaffQuaForm

from .models import NetStaffQua


class NetStaffQuaCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': NetStaffQuaForm,
        
    }


new = NetStaffQuaCreateView.as_view()


class NetStaffQuaUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': NetStaffQuaForm,
        
    }


edit = NetStaffQuaUpdateView.as_view()


class NetStaffQuaListView(WFListView):
    wf_code = 'staff_qua'
    model = NetStaffQua
    excel_file_name = 'staff_qua'
    excel_titles = [
        'Created on', 'Created by',
        '组织', '地点', '资质类型', '发证单位', '证件编号', '有效日期', '人员资质', '是否激活', '关联人员', '创建时间', '监督网络人员资质信息表最后更新人', '最后更新时间', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.orgid, o.place, o.qua_type, o.publish_organ, o.number, o.effect_time, o.qua, o.is_activate, o.staff, o.created_at, o.last_updated_by, o.last_updated_at, o.work_type, 
            o.pinstance.cur_node.name,
        ]


show_list = NetStaffQuaListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}