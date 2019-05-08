from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import MonWorkExeForm

from .models import MonWorkExe


class MonWorkExeCreateView(BSFormSetMixin, CreateView):
    form_classes = {
        'form': MonWorkExeForm,
        
    }


new = MonWorkExeCreateView.as_view()


class MonWorkExeUpdateView(BSFormSetMixin, UpdateView):
    form_classes = {
        'form': MonWorkExeForm,
        
    }


edit = MonWorkExeUpdateView.as_view()


class MonWorkExeListView(WFListView):
    wf_code = 'monworkexe'
    model = MonWorkExe
    excel_file_name = 'monworkexe'
    excel_titles = [
        'Created on', 'Created by',
        '公司名称', '月度工作执行编码', '创建时间', '最后更新时间', '月度计划编码', '月度计划记录号', '计划工作内容', '计划完成时间', '执行人', '执行情况', '存在问题', '备注', '是否激活', '状态', '工单类型', 
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.place, o.number, o.created_at, o.last_updated_at, o.plan_number, o.plan_smallnumber, o.plan_content, o.finish_time, o.execute_user, o.execute_desc, o.problem_desc, o.remarks, o.is_activate, o.state, o.work_type, 
            o.pinstance.cur_activity.name,
        ]


show_list = MonWorkExeListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {}