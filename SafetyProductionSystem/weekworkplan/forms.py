from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import WeekWorkPlan



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class WeekWorkPlanForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(WeekWorkPlanForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['created_at', 'last_updated_by'],
            
            ['last_updated_at', 'enclosure'],
            
            ['orgid', 'place'],
            
            ['is_activate', 'number'],
            
            ['plan', 'third_org'],
            
            ['rate_desc', 'time_limit'],
            
            ['state', 'planner'],
            
            ['plan_time', 'executor'],
            
        ])

    class Meta:
        model = WeekWorkPlan
        fields = [
            'created_at', 'last_updated_by', 'last_updated_at', 'enclosure', 'orgid', 'place', 'is_activate', 'number', 'plan', 'third_org', 'rate_desc', 'time_limit', 'state', 'planner', 'plan_time', 'executor'
        ]
