from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import RegularWorkTask



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class RegularWorkTaskForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(RegularWorkTaskForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'regularwork'],
            
            ['result', 'is_activate'],
            
            ['tanchuang', 'has_readed'],
            
            ['enclosure_file', ''],
            
        ])

    class Meta:
        model = RegularWorkTask
        fields = [
            'place', 'regularwork', 'result', 'is_activate', 'tanchuang', 'has_readed', 'enclosure_file'
        ]
