from django.db.models import Q
from django.utils import timezone
from lbutils import as_callable

from lbworkflow.models import ProcessInstance
from lbworkflow.models import Task
from lbworkflow.settings import PROCESS_INSTANCE_GET_PERMIT_QUERY_PARAM_FUNC
from lbworkflow.views.generics import ListView
from systemsettings.models import Company,MyUser
from .helper import get_base_wf_permit_query_param







class ListWF(ListView):
    ordering = '-created_on'
    template_name = 'myworkflow/list_wf.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'no',
        'summary',
        'created_by__username',
        'cur_node__name',
    ]
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_obj = self.request.user.username
        # print('11111111111111',user_obj)
        # place = MyUser.objects.filter(number=user_obj).first().company_id
        # print('111112222222',place)
        # place = user_obj.myuser.company
        # # place = user_obj.myuser.company
        # context['company_list'] = MyUser.objects.filter(is_activate=1,company_id=place)
        # context['company_list'] = Company.objects.all()
        context['sort'] = True
        return context

    def get_permit_query_param(self, user, q_param):
        # override this function to add addition permit
        get_permit_query_param = as_callable(PROCESS_INSTANCE_GET_PERMIT_QUERY_PARAM_FUNC)
        return get_permit_query_param(user, q_param)

    def get_base_queryset(self):
        user = self.request.user
        # company_list = Company.objects.all()

        # qs = ProcessInstance.objects.exclude(cur_node__status__in=['draft', 'given up'])
        qs = ProcessInstance.objects.filter(created_by=self.request.user)

        if not user.is_superuser:
            q_param = get_base_wf_permit_query_param(user, '')
            q_param = self.get_permit_query_param(user, q_param)
            qs = qs.filter(q_param)
        qs = qs.select_related(
            'process',
            'created_by',
            'cur_node'
        ).distinct()
        return qs

class ListWF_inverted(ListView):
    ordering = 'created_on'
    template_name = 'myworkflow/list_wf.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'no',
        'summary',
        'created_by__username',
        'cur_node__name',
    ]
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_obj = self.request.user.username
        # print('11111111111111',user_obj)
        # place = MyUser.objects.filter(number=user_obj).first().company_id
        # print('111112222222',place)
        # place = user_obj.myuser.company
        # # place = user_obj.myuser.company
        # context['company_list'] = MyUser.objects.filter(is_activate=1,company_id=place)
        # context['company_list'] = Company.objects.all()
        context['sort'] = False
        return context

    def get_permit_query_param(self, user, q_param):
        # override this function to add addition permit
        get_permit_query_param = as_callable(PROCESS_INSTANCE_GET_PERMIT_QUERY_PARAM_FUNC)
        return get_permit_query_param(user, q_param)

    def get_base_queryset(self):
        user = self.request.user
        # company_list = Company.objects.all()

        # qs = ProcessInstance.objects.exclude(cur_node__status__in=['draft', 'given up'])
        qs = ProcessInstance.objects.filter(created_by=self.request.user)

        if not user.is_superuser:
            q_param = get_base_wf_permit_query_param(user, '')
            q_param = self.get_permit_query_param(user, q_param)
            qs = qs.filter(q_param)
        qs = qs.select_related(
            'process',
            'created_by',
            'cur_node'
        ).distinct()
        return qs





class MyWF(ListView):
    template_name = 'myworkflow/my_wf.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'no',
        'summary',
        'cur_node__name',
    ]
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        return context
    def get_base_queryset(self):
        return ProcessInstance.objects.filter(created_by=self.request.user)


class Todo(ListView):
    ordering = '-created_on'
    template_name = 'myworkflow/todo.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'instance__no',
        'instance__summary',
        'instance__cur_node__name',
        'instance__created_by__username',
    ]
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = True
        return context


    def get_base_queryset(self):
        user = self.request.user
        # 查询lbworkflow_task表，筛选条件：当前用户或者代理用户(目前代理用户数据表中都为空，不需考虑)，
        # 状态为 in progress(正在进行)
        qs = Task.objects.filter(
            Q(user=user) | Q(agent_user=user),
            status='in progress')
        # 查询三个字段，病去重
        qs = qs.select_related(
            'instance',
            'instance__process',
            'instance__cur_node'
        ).distinct()
        return qs

    # 查询lbworkflow_task表中receive_on字段为空，更新为当前时间，最后返回结果集
    def get_queryset(self):
        queryset = super(Todo, self).get_queryset()
        queryset.filter(receive_on=None).update(receive_on=timezone.now())
        return queryset

class Todo_inverted(ListView):
    ordering = 'created_on'
    template_name = 'myworkflow/todo.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'instance__no',
        'instance__summary',
        'instance__cur_node__name',
        'instance__created_by__username',
    ]
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = False
        return context


    def get_base_queryset(self):
        user = self.request.user
        # 查询lbworkflow_task表，筛选条件：当前用户或者代理用户(目前代理用户数据表中都为空，不需考虑)，
        # 状态为 in progress(正在进行)
        qs = Task.objects.filter(
            Q(user=user) | Q(agent_user=user),
            status='in progress')
        # 查询三个字段，病去重
        qs = qs.select_related(
            'instance',
            'instance__process',
            'instance__cur_node'
        ).distinct()
        return qs

    # 查询lbworkflow_task表中receive_on字段为空，更新为当前时间，最后返回结果集
    def get_queryset(self):
        queryset = super(Todo_inverted, self).get_queryset()
        queryset.filter(receive_on=None).update(receive_on=timezone.now())
        return queryset

