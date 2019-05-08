from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import WeekWorkTask



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class WeekWorkTaskForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(WeekWorkTaskForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['created_at', 'last_updated_by'],
            
            ['last_updated_at', 'enclosure'],
            
            ['orgid', 'place'],
            
            ['is_activate', 'state'],
            
            ['number', 'task_name'],
            
            ['plan_number', 'task_start_time'],
            
            ['time_limit', ''],
            
        ])

    class Meta:
        model = WeekWorkTask
        fields = [
            'created_at', 'last_updated_by', 'last_updated_at', 'enclosure', 'orgid', 'place', 'is_activate', 'state', 'number', 'task_name', 'plan_number', 'task_start_time', 'time_limit'
        ]
