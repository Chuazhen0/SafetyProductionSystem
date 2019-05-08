from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.shortcuts import render,HttpResponseRedirect
from datetime import datetime
from weekworkplan.models import WeekWorkPlan
from .models import  WeekWorkTask
from systemsettings.views import  checkpower
from systemsettings.models import SupervisionType,MyUser,Company,Menu
from datetime import datetime
from django.db.models import Q
from myworkflow.models import MyProcess
from django.contrib import messages

# 查询周期工作任务
@csrf_exempt
def periodic_task_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    company_list = Company.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    data_user = MyUser.objects.filter(company=place)

    # 获取前端传来的数据
    company_name = request.GET.get('company_name')
    execute_user = request.GET.get('execute_user')
    supervision_major = request.GET.get('supervision_major')
    if supervision_major == '':
        if company_name == '':
            if execute_user =='':
                periodic_list = WeekWorkPlan.objects.filter(Q(is_activate=1))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(execute_user_id=execute_user),Q(is_activate=1))
        else:
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(place_id=company_name),Q(is_activate=1))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(place_id=company_name),Q(execute_user_id=execute_user), Q(is_activate=1))
    else:
        if company_name == '':
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(is_activate=1))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(execute_user_id=execute_user), Q(is_activate=1))
        else:
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(place_id=company_name), Q(is_activate=1))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(place_id=company_name), Q(execute_user_id=execute_user),
                                                            Q(is_activate=1))

    periodic_task_list = []

    for i in periodic_list:
        periodic_task_list.extend(WeekWorkTask.objects.filter(plan=i, is_activate=1))

    # if len(number) == 0:
    #     number = ''
    # if len(orgid) == 0:
    #     orgid = ""
    # elif len(task_name) == 0:
    #     task_name = ""
    # elif len(time_limit) == 0:
    #     time_limit = ""
    # elif len(state) == 0:
    #     state = ""
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM weekworktask_weekworktask where orgid like '%%%%%s%%%%' and number like '%%%%%s%%%%' and is_activate=1 and task_name like '%%%%%s%%%%' and time_limit like '%%%%%s%%%%' and state like '%%%%%s%%%%' " % (
    #         orgid, number, task_name, time_limit, state))
    # # id 列表
    # data = list(cursor.fetchall())
    # id_list = []
    # for row in data:
    #     # 将id取出，存入列表
    #     id_list.append(row[0])
    # #     id_list.append(row)
    #
    # for id in id_list:
    #     # 通过id获取到数据对象
    #     periodic_task_plan = WeekWorkTask.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=periodic_task_plan.orgid) in orgid_list:
    #         periodic_task_list.append(periodic_task_plan)
    # cursor.close()
    # 去重
    data = list(set(periodic_task_list))
    # 分页
    paginator = Paginator(data, 15)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    total_page = paginator.num_pages
    if total_page > 5:
        if page != '':
            page = int(page)
            if page < 5:
                page_range = list(range(1, 6))
            elif page >= 5:
                page_range = list(range(page - 4, page + 1))
    else:
        page_range = list(range(1, total_page + 1))
    page = int(page)
    return render(request, 'week_work_task/show_periodic_task_list.html',locals())


# 展示所有周期工作任务
def show_periodic_task_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    task_data = []
    company_list = Company.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    data_user = MyUser.objects.filter(company=place)

    if user.is_superuser:
        data_list = WeekWorkTask.objects.filter(is_activate=1)
        total_counts = WeekWorkTask.objects.filter(is_activate=1).count()

        for d in data_list:
            task_data.append(d)
    else:
        data_list = WeekWorkTask.objects.filter(is_activate=1, place=place)
        total_counts = WeekWorkTask.objects.filter(is_activate=1, place=place).count()
        for d in data_list:
            task_data.append(d)

    paginator = Paginator(task_data, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        task_data = paginator.page(page)
    except PageNotAnInteger:
        task_data = paginator.page(1)
    except EmptyPage:
        task_data = paginator.page(paginator.num_pages)

    page_last = (int(page) - 1) * 10
    total_page = paginator.num_pages
    if total_page > 5:
        if page != '':
            page = int(page)
            if page < 5:
                page_range = list(range(1, 6))
            elif page >= 5:
                page_range = list(range(page - 4, page + 1))
    else:
        page_range = list(range(1, total_page + 1))

    page = int(page)
    return render(request, 'week_work_task/show_periodic_task_list.html',
                  {'task_data': task_data, 'action': action,'supervision_major_list':supervision_major_list,
                   'data_user':data_user,'page_range':page_range,'company_list':company_list,'page':page,'total_counts':total_counts,'page_last':page_last,'total_page':total_page})


# 展示一个周期工作任务详情
def show_one_task(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = WeekWorkTask.objects.filter(id=wid).first()
    try:
        file_name = data.plan.enclosure.name.split('/')[1]
    except:
        file_name = ''
    return render(request, 'week_work_task/show_one_task.html', locals())


# 删除一个周期工作任内务详情
def del_task(request, wid):
    data = WeekWorkTask.objects.filter(id=wid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/weekworktask/list/?action=list&menuid=35')


# 添加一个周期工作任务
def add_periodic_task(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    if request.method == 'GET':
        data = WeekWorkPlan.objects.filter(execute_user=user)
        return render(request, 'week_work_task/add_periodic_task.html',locals())
    elif request.method == 'POST':
        created_by = last_updated_by = request.session.get('mylogin').myuser
        created_at = last_updated_at = datetime.now()
        number = place.comsimplename + datetime.now().strftime("%Y%m%d")
        task_name = request.POST.get('task_name')
        plan_number = request.POST.get('plan_number')
        task_start_time = request.POST.get('task_start_time')
        time_limit = request.POST.get('time_limit')
        all_data = WeekWorkTask.objects.create( place=place, state='拟定',
                                               number=number, created_by=created_by, created_at=created_at,
                                               last_updated_by=last_updated_by, last_updated_at=last_updated_at,
                                               task_name=task_name, plan_number=plan_number,
                                               task_start_time=task_start_time, time_limit=time_limit)
        all_data.save()
        return HttpResponseRedirect('/weekworktask/list/?action=list&menuid=35')


# 修改一个周期工作任务
def edit_periodic_task(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    orgid = Department.objects.filter(parent=None).first()
    orgid = orgid.name
    place = ''
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    # 获取该登录人员的组织机构信息，找到其所在分公司
    Department = user.myuser.Department
    if Department.type == 1:  # 河南公司
        place = orgid
    elif Department.type == 2:  # 技术中心
        # 找到其所在分公司
        place = Department.name
    elif Department.type == 3:  # 分公司（各电厂）
        place = Department.name
    elif Department.type == 4:  # 部门
        place = Department.parent.name
    elif Department.type == 5:  # 班组
        if Department.parent is None:
            place = Department.parent.name
        else:
            place = Department.parent.parent.name
    else:
        if Department.parent.parent is None:
            place = orgid
        else:
            place = Department.parent.parent.parent.name
    orgid = Department.objects.filter(parent=Department)
    if request.method == 'GET':
        data = WeekWorkTask.objects.filter(id=wid).first()
        return render(request, 'week_work_task/edit_periodic_task.html',locals())
    elif request.method == 'POST':
        all_data = WeekWorkTask.objects.filter(id=wid).first()
        all_data.last_updated_by = request.session.get('mylogin').myuser
        all_data.last_updated_at = datetime.now()
        all_data.orgid = request.POST.get('orgid')
        all_data.place = request.POST.get('place')
        all_data.number = request.POST.get('number')
        all_data.state = request.POST.get('state')
        all_data.task_name = request.POST.get('task_name')
        all_data.plan_number = request.POST.get('plan_number')
        all_data.task_start_time = request.POST.get('task_start_time')
        all_data.time_limit = request.POST.get('time_limit')
        all_data.save()
        return HttpResponseRedirect('/weekworktask/list/?action=list&menuid=35')



# 查看我的周期工作任务
def my_week_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session['mylogin']
    place = user.myuser.company


    weekworkplan_list = WeekWorkPlan.objects.filter(is_activate=1,execute_user=user.myuser)   # 责任人为当前登录用户的周期工作策划对象
    myweekworktask_list = []   # 我的周期工作任务列表
    for weekworkplan_obj in weekworkplan_list:
        # 责任人为当前登录用户并且未执行的周期工作任务对象
        weekworktask_obj_list = WeekWorkTask.objects.filter(Q(is_activate=1,plan=weekworkplan_obj,result=None)|Q(is_activate=1,plan=weekworkplan_obj,result='')|Q(is_activate=1,plan=weekworkplan_obj,pinstance__cur_node__name="Rejected"))
        for weektask in weekworktask_obj_list:
            myweekworktask_list.append(weektask)

    #总数
    total_counts = len(myweekworktask_list)
    print(total_counts)

    # 分页
    paginator = Paginator(myweekworktask_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        myweekworktask_list = paginator.page(page)
    except PageNotAnInteger:
        myweekworktask_list = paginator.page(1)
    except EmptyPage:
        myweekworktask_list = paginator.page(paginator.num_pages)

    page_last = (int(page) - 1) * 10
    total_page = paginator.num_pages
    if total_page > 5:
        if page != '':
            page = int(page)
            if page < 5:
                page_range = list(range(1, 6))
            elif page >= 5:
                page_range = list(range(page - 4, page + 1))
    else:
        page_range = list(range(1, total_page + 1))
    return render(request,'week_work_task/myweek_list.html',locals())



@csrf_exempt
def myweek_add(request,w_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company


    weekworktask_obj = WeekWorkTask.objects.filter(id=w_id).first()    #  周期工作任务对象
    weekworkplan_obj = weekworktask_obj.plan   # 周期工作策划对象
    if request.method == 'GET':
        try:  # 获取附件名
            file_name = weekworkplan_obj.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request,'week_work_task/myweek_add.html',locals())

    elif request.method == 'POST':
        finish_desc = request.POST['finish_desc']
        task_file = request.FILES.get('task_file')   # 附件
        if task_file is not None:
            task_file.name = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S_') + str(task_file.name)
        num = request.POST['num2']

        # weekworktask_obj = WeekWorkTask.objects.filter(id=w_id,plan=weekworkplan_obj,place=place).first()
        weekworktask_obj.result=finish_desc   # 周期工作结果描述
        weekworktask_obj.enclosure=task_file   # 周期工作任务附件
        weekworktask_obj.save()

        weekworktask_obj.created_by = request.user # 周期任务提交人

        # 从数据库中查找对应的工作流程
        my_process = MyProcess.objects.filter(app_name='周期检测任务', supervision_major=weekworkplan_obj.supervision_major,
                                              is_activate=1, company=place, app_object_id=weekworkplan_obj.number).first()


        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='周期检测任务', is_activate=1, company=place,
                                                  app_object_id=weekworkplan_obj.number).first()
            if my_process == None:  # 如果未指定n监督专业，指定的number的也没有，就找指定监督专业，未指定number的
                my_process = MyProcess.objects.filter(app_name='周期检测任务', is_activate=1, company=place,
                                                      supervision_major=weekworkplan_obj.supervision_major).first()
                if my_process == None:
                    my_process = MyProcess.objects.filter(app_name='周期检测任务', is_activate=1, company=place).first()
                    if my_process == None:
                        return HttpResponseRedirect(
                            '/weekworktask/' + str(weekworktask_obj.id) + '/detail/?action=detail&menuid=35')
        process = my_process.process

        if num == '1':
            weekworktask_obj.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", weekworktask_obj))
            return HttpResponseRedirect(
                '/weekworktask/' + str(weekworktask_obj.id) + '/detail2/?action=detail&menuid=49')
        elif num == '2':
            weekworktask_obj.create_pinstance(process=process, submit=True)
            # weekworktask_obj.created_by = request.user  # 周期任务提交人
            weekworktask_obj.save()
            new_processinstance = weekworktask_obj.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', weekworktask_obj))

            return HttpResponseRedirect(
                '/weekworktask/' + str(weekworktask_obj.id) + '/detail/?action=detail&menuid=49&pinstance_id=' + str(
                    new_processinstance.id))
