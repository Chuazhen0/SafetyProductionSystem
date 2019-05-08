from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import MonWorkExe



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class MonWorkExeForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(MonWorkExeForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'number'],
            
            ['created_at', 'last_updated_at'],
            
            ['plan_number', 'plan_smallnumber'],
            
            ['plan_content', 'finish_time'],
            
            ['execute_user', 'execute_desc'],
            
            ['problem_desc', 'remarks'],
            
            ['is_activate', 'state'],
            
            ['work_type', ''],
            
        ])

    class Meta:
        model = MonWorkExe
        fields = [
            'place', 'number', 'created_at', 'last_updated_at', 'plan_number', 'plan_smallnumber', 'plan_content', 'finish_time', 'execute_user', 'execute_desc', 'problem_desc', 'remarks', 'is_activate', 'state', 'work_type'
        ]
