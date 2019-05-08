from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import YearSum



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class YearSumForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(YearSumForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'sum_desc'],
            
            ['sum_type', 'year'],
            
            ['state', 'created_at'],
            
            ['last_updated_by', 'last_updated_at'],
            
            ['enclosure', 'is_activate'],
            
            ['work_type', ''],
            
        ])

    class Meta:
        model = YearSum
        fields = [
            'place', 'sum_desc', 'sum_type', 'year', 'state', 'created_at', 'last_updated_by', 'last_updated_at', 'enclosure', 'is_activate', 'work_type'
        ]
