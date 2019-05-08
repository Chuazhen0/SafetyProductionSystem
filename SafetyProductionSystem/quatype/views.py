from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import QuaTypeForm

from .models import QuaType


class QuaTypeCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': QuaTypeForm,
        
    }


new = QuaTypeCreateView.as_view()


class QuaTypeUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': QuaTypeForm,
        
    }


edit = QuaTypeUpdateView.as_view()


class QuaTypeListView(WFListView):
    wf_code = 'quatype'
    model = QuaType
    excel_file_name = 'quatype'
    excel_titles = [
        'Created on', 'Created by',
        '创建时间', '最后更新人', '最后更新时间', '组织', '地点', '是否激活', '描述', '专业', '编号', '备注', '状态', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.created_at, o.last_updated_by, o.last_updated_at, o.orgid, o.place, o.is_activate, o.desc, o.supervision, o.number, o.remark, o.state, 
            o.pinstance.cur_node.name,
        ]


show_list = QuaTypeListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}