from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import WarningNotice



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class WarningNoticeForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(WarningNoticeForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['place', 'state'],
            
            ['number', 'resource'],
            
            ['enclosure', 'title'],
            
            ['supervise_major', 'equipment'],
            
            ['problem', 'exetuct_user'],
            
            ['abnormal', 'result'],
            
            ['suggest', 'time_require'],
            
            ['is_activate', 'last_updated_at'],
            
            ['work_type', ''],
            
        ])

    class Meta:
        model = WarningNotice
        fields = [
            'place', 'state', 'number', 'resource', 'enclosure', 'title', 'supervise_major', 'equipment', 'problem', 'exetuct_user', 'abnormal', 'result', 'suggest', 'time_require', 'is_activate', 'last_updated_at', 'work_type'
        ]
