from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import RegularWork



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class RegularWorkForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(RegularWorkForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'number'],
            
            ['KKS_code', 'KKS_codename'],
            
            ['count_number', 'count_name'],
            
            ['work_area', 'exe_user'],
            
            ['equipment_major', 'supervision_major'],
            
            ['nature', 'type'],
            
            ['score', 'work_content'],
            
            ['weekend_desc', 'warinig_time'],
            
            ['state', 'overdue_1'],
            
            ['overdue_2', 'overdue_3'],
            
            ['resource', 'start_time'],
            
            ['end_time', 'is_activate'],
            
            ['stard', 'stard_smallnumber'],
            
        ])

    class Meta:
        model = RegularWork
        fields = [
            'place', 'number', 'KKS_code', 'KKS_codename', 'count_number', 'count_name', 'work_area', 'exe_user', 'equipment_major', 'supervision_major', 'nature', 'type', 'score', 'work_content', 'weekend_desc', 'warinig_time', 'state', 'overdue_1', 'overdue_2', 'overdue_3', 'resource', 'start_time', 'end_time', 'is_activate', 'stard', 'stard_smallnumber'
        ]
