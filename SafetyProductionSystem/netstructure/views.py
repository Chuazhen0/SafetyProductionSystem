from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import NetStructureForm

from .models import NetStructure


class NetStructureCreateView( CreateView):
    form_classes = {
        'form': NetStructureForm,
        
    }


new = NetStructureCreateView.as_view()


class NetStructureUpdateView(UpdateView):
    form_classes = {
        'form': NetStructureForm,
        
    }


edit = NetStructureUpdateView.as_view()


class NetStructureListView(WFListView):
    wf_code = 'netstructure'
    model = NetStructure
    excel_file_name = 'netstructure'
    excel_titles = [
        'Created on', 'Created by',
        '组织', '地点', '网络结构编号', '上级监督网络', '描述', '类别', '状态', '创建时间', '是否激活', '最后更新人', '最后更新时间', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.orgid, o.place, o.number, o.parent, o.desc, o.classify, o.state, o.created_at, o.is_activate, o.last_updated_by, o.last_updated_at, o.work_type, 
            o.pinstance.cur_node.name,
        ]


show_list = NetStructureListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}