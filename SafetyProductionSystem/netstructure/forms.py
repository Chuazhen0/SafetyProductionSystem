from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import NetStructure



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class NetStructureForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(NetStructureForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['orgid', 'place'],
            
            ['number', 'parent'],
            
            ['desc', 'classify'],
            
            ['state', 'created_at'],
            
            ['is_activate', 'last_updated_by'],
            
            ['last_updated_at', 'work_type'],
            
        ])

    class Meta:
        model = NetStructure
        fields = [
            'orgid', 'place', 'number', 'parent', 'desc', 'classify', 'state', 'created_at', 'is_activate', 'last_updated_by', 'last_updated_at', 'work_type'
        ]
