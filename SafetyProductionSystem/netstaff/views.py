from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import NetStaffForm

from .models import NetStaff


class NetStaffCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': NetStaffForm,
        
    }


new = NetStaffCreateView.as_view()


class NetStaffUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': NetStaffForm,
        
    }


edit = NetStaffUpdateView.as_view()


class NetStaffListView(WFListView):
    wf_code = 'netstaff'
    model = NetStaff
    excel_file_name = 'netstaff'
    excel_titles = [
        'Created on', 'Created by',
        '组织', '地点', '监督网络人员', '工号', '所属监督网络', '职责说明', '联系方式', '监督网络岗位', '所在部门', '创建时间', '最后更新人', '最后更新时间', '是否激活', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.orgid, o.place, o.staff, o.number, o.netstructure, o.desc, o.phone, o.net_name, o.department, o.created_at, o.last_updated_by, o.last_updated_at, o.is_activate, o.work_type, 
            o.pinstance.cur_node.name,
        ]


show_list = NetStaffListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}