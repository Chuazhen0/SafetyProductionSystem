from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import WarningReceipt



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class WarningReceiptForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(WarningReceiptForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'state'],
            
            ['number', 'warning_notice'],
            
            ['created_at', 'last_updated_at'],
            
            ['work_type', 'enclosure'],
            
            ['content', 'result'],
            
            ['is_activate', ''],
            
        ])

    class Meta:
        model = WarningReceipt
        fields = [
            'place', 'state', 'number', 'warning_notice', 'created_at', 'last_updated_at', 'work_type', 'enclosure', 'content', 'result', 'is_activate'
        ]
