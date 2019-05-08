from django import forms
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout

from lbutils import BootstrapFormHelperMixin
from lbworkflow.forms import WorkflowFormMixin
from lbworkflow.forms import BSQuickSearchForm

from .models import NetStaff



class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class NetStaffForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(NetStaffForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            
            ['orgid', 'place'],
            
            ['staff', 'number'],
            
            ['netstructure', 'desc'],
            
            ['phone', 'net_name'],
            
            ['department', 'created_at'],
            
            ['last_updated_by', 'last_updated_at'],
            
            ['is_activate', 'work_type'],
            
        ])

    class Meta:
        model = NetStaff
        fields = [
            'orgid', 'place', 'staff', 'number', 'netstructure', 'desc', 'phone', 'net_name', 'department', 'created_at', 'last_updated_by', 'last_updated_at', 'is_activate', 'work_type'
        ]
