from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render , redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from . import models
import re
from django.db import connection
from systemsettings.views import checkpower
from django.db.models import Q
from systemsettings.models import  MyUser,User,SupervisionType,EquipmentMajor,KKS,MyGroup
from datetime import datetime
from django.contrib import messages
from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance, Task
import xlrd
from datetime import timedelta
from  regularworkplan.models import RegularWorkPlan, WorkContent, WorkData, WorkCare, PreWork
import time
from regularworkplan.models import PreWork,WorkCare,WorkContent,WorkData
from systemsettings.models import Menu


# Create your views here.
# 定期工作任务列表
def regularwork(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin') # 获取登录人信息
    place = user.myuser.company # 找到其所在分公司
    user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    regularwork_list1 = []# 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    if user.is_superuser:
        regularwork_list_2 = models.RegularWorkTask.objects.filter(is_activate=1).order_by("-created_on")#
        total_counts = models.RegularWorkTask.objects.filter(is_activate=1).order_by("-created_on").count()
        for mon in regularwork_list_2:
            regularwork_list1.append(mon)
    else:
        regularwork_list_2 = models.RegularWorkTask.objects.filter(is_activate=1, place=place).order_by("-created_on")  #
        total_counts = models.RegularWorkTask.objects.filter(is_activate=1, place=place).order_by("-created_on")  #
        for mon in regularwork_list_2:
            regularwork_list1.append(mon)


    # 去重
    regularwork_list = list(set(regularwork_list1))
    regularwork_list.sort(key=regularwork_list1.index)
    # 分页
    paginator = Paginator(regularwork_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    all_info_list_weidu = []
    regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1, exe_user=user.myuser, place=place).order_by('-id') # 获取到工作流执行的责任人
    for mytask in regular_plan_list:
        all_info_list_weidu.append(mytask)
    num1 = len(all_info_list_weidu)
    try:
        # 传递HTML当前页对象
        regularwork_list = paginator.page(page)
    except PageNotAnInteger:
        regularwork_list = paginator.page(1)
    except EmptyPage:
        regularwork_list = paginator.page(paginator.num_pages)

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

    return render(request, 'regular_work_task/regular_work_task.html',locals())



# 定期工作任务新建
@csrf_exempt
def regularwork_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1)
    if request.method == 'GET':
        return render(request, 'regular_work_task/regular_work_task_add.html',locals())

    elif request.method == 'POST':
        regular_number = request.POST['regular_number']
        regular_plan = RegularWorkPlan.objects.get(number=regular_number)
        finish_desc = request.POST['finish_desc']
        num = request.POST['num2']
        regularworktask = models.RegularWorkTask.objects.create(regularwork=regular_plan, place=place, result=finish_desc)
        regularworktask.save()
        regularworktask.created_by = request.user
        my_process = MyProcess.objects.filter(app_name='定期工作策划', supervision_major=regular_plan.supervision_major,
                                              is_activate=1, company=place,app_object_id=regular_number).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place,
                                                  app_object_id=regular_plan.number).first()
            if my_process == None:  # 如果未指定n监督专业，指定的number的也没有，就找指定监督专业，未指定number的
                my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place,
                                                      supervision_major=regular_plan.supervision_major).first()
                if my_process == None:
                    my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place).first()
                    if my_process == None:
                        messages.info(request, 'Success %s: %s,%s' % ('保存', regularworktask, '暂无匹配的工作流程,请先去配置流程后再提交！'))
                        return HttpResponseRedirect(
                            '/regularworktask/' + str(regularworktask.id) + '/detail/?action=detail&menuid=49')
        process = my_process.process

        if num == '1':
            regularworktask.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", regularworktask))
            return HttpResponseRedirect(
                '/regularworktask/' + str(regularworktask.id) + '/detail/?action=detail&menuid=49')
        elif num == '2':
            regularworktask.create_pinstance(process=process, submit=True)
            regularworktask.created_by = request.user
            regularworktask.save()
            new_processinstance = regularworktask.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', regularworktask))

            return HttpResponseRedirect(
                '/regularworktask/' + str(
                    regularworktask.id) + '/detail/?action=detail&menuid=49&pinstance_id=' + str(
                    new_processinstance.id))


# 定期工作任务详情
def regularwork_detail(request, e_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    regularworktask = models.RegularWorkTask.objects.get(id=e_id)
    processinstance =regularworktask.pinstance

    regularworkplan = regularworktask.regularwork
    work_ready = PreWork.objects.filter(regular_work=regularworkplan.id)
    work_matters = WorkCare.objects.filter(regular_work=regularworkplan.id)
    work_contents = WorkContent.objects.filter(regular_work=regularworkplan.id)
    work_datas = WorkData.objects.filter(regular_work=regularworkplan.id)
    if processinstance != None:
        return render(request, 'regular_work_task/regular_work_task_detail.html',locals())
    else:
        return render(request, 'regular_work_task/regular_work_task_detail2.html', locals())


# 定期工作任务编辑
@csrf_exempt
def regularwork_edit(request, e_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    Department = user.profile.Department
    # 找到其所在分公司
    place = check_place(Department)
    # 找到该登录人的组织机构所有下属机构
    regularwork = models.RegularWorkTask.objects.get(id=e_id)
    # 根据id获取对象
    if request.method == 'GET':
        # get 方式访问
        # 将监督类型列表查询
        supervision_major_list = SupervisionType.objects.filter(is_activate=1)
        # 设备专业列表查询
        equipment_major_list = EquipmentMajor.objects.all()
        # 人员查询
        # 定义一个空的列表，用于保存人员
        user_list = []
        Department_list = []
        user_activate = User.objects.filter(is_active=1)
        # 找到该登录人的组织机构所有下属机构
        orgid = Department.objects.filter(parent=Department)
        # 遍历下属机构
        for org in orgid:
            Department_list.append(org)
            for user in user_activate:
                if user.profile.Department == org:
                    user_list.append(user)
        Department_list.append(Department)
        for user in user_activate:
            if user.profile.Department == Department:
                user_list.append(user)

        # 定期工作任务的周期描述需要拆分显示
        num = re.search('\d+', regularwork.weekend_desc)
        weekend_desc = re.search('\D+', regularwork.weekend_desc)
        if num != None:
            num = num.group()
        else:
            num = ''
        if weekend_desc != None:
            weekend_desc = weekend_desc.group()
        else:
            weekend_desc = ''
        return render(request, 'regular_work_task/regular_work_plan_edit.html',locals())
    elif request.method == 'POST':
        cursor = connection.cursor()
        fields_list = request.POST
        for field in list(set(list(fields_list))):
            if field == 'work_area' and fields_list[field] == 'None':
                continue
            if field == 'work_area' and fields_list[field] != 'None':
                work_area = models.WorkArea.objects.get(area=fields_list[field])
                cursor.execute(
                    "update regularwork_regularwork set work_area_id='%s' where id='%s'" % (
                        work_area.id, e_id))
                continue
            if field == 'equipment_major':
                cursor.execute(
                    "update regularwork_regularwork set equipment_major_id='%s' where id='%s'" % (
                        fields_list[field], e_id))
                continue
            elif field == 'exe_user':
                user = User.objects.filter(username=fields_list[field]).first()
                cursor.execute(
                    "update regularwork_regularwork set exe_user_id='%s' where id='%s'" % (
                        user.id, e_id))
                continue
            elif field == 'supervision_major' and fields_list[field]:
                cursor.execute(
                    "update regularwork_regularwork set supervision_major_id='%s' where id='%s'" % (
                        fields_list[field], e_id))
                continue
            elif field == 'num':
                continue
            elif field == 'score' and fields_list[field] == '':
                cursor.execute(
                    "update regularwork_regularwork set score='0' where id='%s'" % (
                        e_id))
                continue
            elif field == 'weekend_desc':
                weekend_desc = fields_list['num'] + fields_list[field]
                cursor.execute(
                    "update regularwork_regularwork set %s='%s' where id='%s'" % (field, weekend_desc, e_id))
                continue
            else:
                cursor.execute(
                    "update regularwork_regularwork set %s='%s' where id='%s'" % (field, fields_list[field], e_id))

        cursor.close()
        # return redirect(reverse('regularworktask:detail', args=[e_id]))
        return HttpResponseRedirect('/regularworktask/' + str(e_id) + '/detail/?action=detail&menuid=49')


# 定期工作任务删除
def regularwork_delete(request, e_id):
    # 获取定期工作任务
    regularwork = models.RegularWorkTask.objects.get(id=e_id)
    regularwork.is_activate = 0
    regularwork.save()
    return HttpResponseRedirect('/regularworktask/list/?action=list&menuid=49')


# 搜索定期工作任务
@csrf_exempt
def regularwork_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company  # 找到其所在分公司
    user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    supervision_major = request.GET.get('supervision_major','')
    equipment_major = request.GET.get('equipment_major','')
    type = request.GET.get('type','')
    exe_user = request.GET.get('exe_user','')


    if supervision_major == '':
        if equipment_major == '':
            if type == '':
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(exe_user_id=exe_user,is_activate=1)

            else:
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(type=type,is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(type=type,exe_user_id=exe_user, is_activate=1)

        else:
            if type == '':
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,type=type, is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,type=type, exe_user_id=exe_user,
                                                                                       is_activate=1)
    else:
        if equipment_major == '':
            if type == '':
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,type=type, is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,type=type, exe_user_id=exe_user,
                                                                             is_activate=1)

        else:
            if type == '':
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             type=type, is_activate=1)
                else:
                    regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             type=type, exe_user_id=exe_user,is_activate=1)

    regularwork_list = []
    for i in regularwork_plan_list:
        regularwork_list.extend(models.RegularWorkTask.objects.filter(regularwork=i,is_activate=1))





    # 去重
    regularwork_list = list(set(regularwork_list))

    # 分页
    paginator = Paginator(regularwork_list, 10, 2)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        regularwork_list = paginator.page(page)
    except PageNotAnInteger:
        regularwork_list = paginator.page(1)
    except EmptyPage:
        regularwork_list = paginator.page(paginator.num_pages)

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


    return render(request, 'regular_work_task/regular_work_task.html',locals())


def my_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    user = request.session['mylogin']
    # place = user.myuser.company  # 找到其所在分公司
    # user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()

    regularworkplan_list = RegularWorkPlan.objects.filter(is_activate=1,exe_user=user.myuser)
    myregularworktask_list = []
    for regularworkplan in regularworkplan_list:
        # regularworktask = models.RegularWorkTask.objects.filter(is_activate=1,result='',regularwork=regularworkplan)
        # regularworktask = models.RegularWorkTask.objects.filter(is_activate=1,regularwork=regularworkplan)

        regularworktask = models.RegularWorkTask.objects.filter(Q(is_activate=1,regularwork=regularworkplan,result='')|Q(is_activate=1,regularwork=regularworkplan,pinstance__cur_node__name="Rejected"))

        for retask in regularworktask:
            myregularworktask_list.append(retask)

    # 总数
    total_counts = RegularWorkPlan.objects.filter(is_activate=1,exe_user=user.myuser).count()

    # 分页
    paginator = Paginator(myregularworktask_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        myregularworktask_list = paginator.page(page)
    except PageNotAnInteger:
        myregularworktask_list = paginator.page(1)
    except EmptyPage:
        myregularworktask_list = paginator.page(paginator.num_pages)

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
    return render(request,'regular_work_task/my_list.html',locals())


def my_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # place = user.myuser.company  # 找到其所在分公司
    # user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    supervision_major = request.GET.get('supervision_major', '')
    equipment_major = request.GET.get('equipment_major', '')
    type = request.GET.get('type', '')

    if supervision_major == '':
        if equipment_major == '':
            if type == '':
                regularwork_plan_list = RegularWorkPlan.objects.filter(is_activate=1,exe_user=user.myuser)

            else:
                regularwork_plan_list = RegularWorkPlan.objects.filter(type=type, is_activate=1,exe_user=user.myuser)

        else:
            if type == '':
                regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,
                                                                           is_activate=1,exe_user=user.myuser)

            else:
                regularwork_plan_list = RegularWorkPlan.objects.filter(equipment_major_id=equipment_major,
                                                                           type=type, is_activate=1,exe_user=user.myuser)

    else:
        if equipment_major == '':
            if type == '':
                regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,
                                                                           is_activate=1,exe_user=user.myuser)

            else:
                regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,
                                                                           type=type, is_activate=1,exe_user=user.myuser)

        else:
            if type == '':
                regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,
                                                                           equipment_major_id=equipment_major,
                                                                           is_activate=1,exe_user=user.myuser)

            else:
                regularwork_plan_list = RegularWorkPlan.objects.filter(supervision_major_id=supervision_major,
                                                                           equipment_major_id=equipment_major,
                                                                           type=type, is_activate=1,exe_user=user.myuser)

    myregularworktask_list = []
    for i in regularwork_plan_list:
        myregularworktask_list.extend(models.RegularWorkTask.objects.filter(regularwork=i, is_activate=1))

    # 去重
    myregularworktask_list = list(set(myregularworktask_list))
    # 分页
    paginator = Paginator(myregularworktask_list, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    try:
        # 传递HTML当前页对象
        myregularworktask_list = paginator.page(page)
    except PageNotAnInteger:
        myregularworktask_list = paginator.page(1)
    except EmptyPage:
        myregularworktask_list = paginator.page(paginator.num_pages)

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
    return render(request,'regular_work_task/my_list.html',locals())


@csrf_exempt
def my_add(request,e_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    regularworktask = models.RegularWorkTask.objects.filter(id=e_id).first()
    regularworkplan = regularworktask.regularwork
    work_ready = PreWork.objects.filter(regular_work=regularworkplan.id)
    work_matters = WorkCare.objects.filter(regular_work=regularworkplan.id)
    work_contents = WorkContent.objects.filter(regular_work=regularworkplan.id)
    work_datas = WorkData.objects.filter(regular_work=regularworkplan.id)
    if request.method == 'GET':

        return render(request,'regular_work_task/my_add.html',locals())

    elif request.method == 'POST':
        finish_desc = request.POST['finish_desc']
        task_file = request.FILES.get('task_file')   # 附件
        if task_file is not None:
            task_file.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(task_file.name)
        num = request.POST['num2']

        # regularworktask = models.RegularWorkTask.objects.create(regularwork=regularworkplan, place=place,
        #                                                         result=finish_desc)
        # regularworktask.save()

        regularworktask = models.RegularWorkTask.objects.filter(id=e_id,regularwork=regularworkplan,place=place).first()
            # .update(regularwork=regularworkplan, place=place,result=finish_desc, enclosure_file=task_file)
        regularworktask.regularwork=regularworkplan
        regularworktask.place=place
        regularworktask.result=finish_desc
        regularworktask.enclosure_file=task_file
        regularworktask.save()

        regularworktask = models.RegularWorkTask.objects.filter(id=e_id,regularwork=regularworkplan, place=place,result=finish_desc).first()
        regularworktask.created_by = request.user
        my_process = MyProcess.objects.filter(app_name='定期工作策划', supervision_major=regularworkplan.supervision_major,
                                              is_activate=1, company=place, app_object_id=regularworkplan.number).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place,
                                                  app_object_id=regularworkplan.number).first()
            if my_process == None:  # 如果未指定n监督专业，指定的number的也没有，就找指定监督专业，未指定number的
                my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place,
                                                      supervision_major=regularworkplan.supervision_major).first()
                if my_process == None:
                    my_process = MyProcess.objects.filter(app_name='定期工作策划', is_activate=1, company=place).first()
                    if my_process == None:
                        return HttpResponseRedirect(
                            '/regularworktask/' + str(regularworktask.id) + '/detail/?action=detail&menuid=49')
        process = my_process.process

        if num == '1':
            regularworktask.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", regularworktask))
            return HttpResponseRedirect(
                '/regularworktask/' + str(regularworktask.id) + '/detail2/?action=detail&menuid=49')
        elif num == '2':

            regularworktask.create_pinstance(process=process, submit=True)

            regularworktask.created_by = request.user
            print("============www===",request.user)
            regularworktask.save()
            new_processinstance = regularworktask.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', regularworktask))

            return HttpResponseRedirect(
                '/regularworktask/' + str(regularworktask.id) + '/detail/?action=detail&menuid=49&pinstance_id=' + str(
                    new_processinstance.id))


# 定期工作导入excel文件
@csrf_exempt
def regularwork_import_excel(request):
    from systemsettings.models import Company
    user_obj = request.session.get('mylogin')
    place = user_obj.myuser.company
    excel_file = request.FILES.get('excel_file','')
    type_excel = excel_file.name.split('.')[1]
    if type_excel == 'xls' or type_excel == 'xlsx':
        if type_excel == 'xls':
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read(), formatting_info=True)  # 打开xls文件
        else:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())  # 打开xlsx文件
        # 分别获取5张表中的数据
        # 工作项目表
        all_list_1 = get_sheets_mg(data, 0)
        all_list_2 = get_sheets_mg(data, 1)
        all_list_3 = get_sheets_mg(data, 2)
        all_list_4 = get_sheets_mg(data, 3)
        all_list_5 = get_sheets_mg(data, 4)
        # print(all_list_1,"==")
        # 向数据库写入表一数据
        i = 0
        while i < len(all_list_1):
            user_num = all_list_1[i][3]
            supervision_major = all_list_1[i][7]
            if supervision_major == '' or supervision_major == None:
                supervision_major = '默认监督专业'
            supervision_major = SupervisionType.objects.get(name=supervision_major)
            place_name = all_list_1[i][22]
            place = Company.objects.filter(comname=place_name).first()
            number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")
            KKS_code = KKS.objects.filter(KKS_code=all_list_1[i][1]).first()
            KKS_codename = all_list_1[i][2]
            nature = all_list_1[i][8]
            score = all_list_1[i][10]
            if score == '':
                score = 0
            equipment_major = all_list_1[i][6]
            if equipment_major == '' or equipment_major == None:
                equipment_major = '默认设备专业'
            equipment_major = EquipmentMajor.objects.get(name=equipment_major)
            work_content = all_list_1[i][11]
            if work_content == '' or work_content == None:
                work_content = '工作任务未填写'
            user_num = all_list_1[i][3]
            user = all_list_1[i][4]
            group = all_list_1[i][5]
            warinig_time = all_list_1[i][15]
            if warinig_time == '' or warinig_time == None or warinig_time == '手动触发' or warinig_time == '手动':
                warinig_time = 0
            overdue_1 = all_list_1[i][16]
            if overdue_1 == '' or overdue_1 == None:
                overdue_1 = 0
            overdue_2 = all_list_1[i][17]
            if overdue_2 == '' or overdue_2 == None:
                overdue_2 = 0
            overdue_3 = all_list_1[i][18]
            if overdue_3 == '' or overdue_3 == None:
                overdue_3 =0
            resource = all_list_1[i][19]
            start_time = all_list_1[i][20]
            end_time = all_list_1[i][21]
            if end_time == '':
                new_start_date = datetime.strptime(start_time, "%Y-%m-%d")
                new_enddate = datetime(new_start_date.year, new_start_date.month, new_start_date.day)
                end_time = (new_enddate + timedelta(days=1825)).date()
            type = all_list_1[i][9]
            if type == None:
                type = ''
            weekend_desc = all_list_1[i][12]  # 小时  天   周   月   年  一次  周期描述
            # print(weekend_desc,"==weekend_desc")
            if weekend_desc == '周':
                num1 = str(all_list_1[i][13])
                num_list = str(all_list_1[i][14])
                # print(num_list,"===num_list")
                num_list = num_list.split(',')
                num2 = ''
                for num in num_list:
                    if num != '':
                        num2 += num + ','
                num2 = num2[0:len(num2) - 1]
            elif weekend_desc == '' or weekend_desc == None:
                weekend_desc = '一次性工作计划 '
                num1 = str(all_list_1[i][13])  # 周期描述1
                num2 = str(all_list_1[i][14])  # 周期描述2

            else:
                num1 = str(all_list_1[i][13])  # 周期描述1
                num2 = str(all_list_1[i][14])  # 周期描述2
            exe_group = MyGroup.objects.filter(name=group).first()
            # print(warinig_time,overdue_1,overdue_2,overdue_3,"======overdue_3")
            if user == '' or user == None or user_num == '' or user_num == None:
                if user:
                    exe_user = MyUser.objects.filter(name=user).first()
                    regularwork = RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                 work_content=work_content,
                                                                 number=number,
                                                                 KKS_code=KKS_code, KKS_codename=KKS_codename,
                                                                 type=type, score=score, exe_user=exe_user,
                                                                 warinig_time=warinig_time, overdue_1=overdue_1,
                                                                 overdue_2=overdue_2, place=place,
                                                                 equipment_major=equipment_major,
                                                                 overdue_3=overdue_3, nature=nature,
                                                                 resource=resource,
                                                                 start_time=datetime.strptime(start_time, "%Y-%m-%d"),
                                                                 end_time=datetime.strptime(end_time, "%Y-%m-%d"),
                                                                 weekend_desc=weekend_desc, exe_group=exe_group,
                                                                 num1=num1,
                                                                 num2=num2
                                                                 )
                elif user_num:
                    exe_user = MyUser.objects.filter(number=user_num).first()
                    regularwork = RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                 work_content=work_content,
                                                                 number=number,
                                                                 KKS_code=KKS_code, KKS_codename=KKS_codename,
                                                                 type=type, score=score, exe_user=exe_user,
                                                                 warinig_time=warinig_time, overdue_1=overdue_1,
                                                                 overdue_2=overdue_2, place=place,
                                                                 equipment_major=equipment_major,
                                                                 overdue_3=overdue_3, nature=nature,
                                                                 resource=resource,
                                                                 start_time=datetime.strptime(start_time, "%Y-%m-%d"),
                                                                 end_time=datetime.strptime(end_time, "%Y-%m-%d"),
                                                                 weekend_desc=weekend_desc, exe_group=exe_group,
                                                                 num1=num1,
                                                                 num2=num2
                                                                 )

                else:
                    regularwork = RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                        work_content=work_content,
                                                                        number=number,
                                                                        KKS_code=KKS_code, KKS_codename=KKS_codename,
                                                                        type=type, score=score,
                                                                        warinig_time=warinig_time, overdue_1=overdue_1,
                                                                        overdue_2=overdue_2,
                                                                        overdue_3=overdue_3, nature=nature,
                                                                        resource=resource, start_time=datetime.strptime(start_time, "%Y-%m-%d"),
                                                                        end_time=datetime.strptime(end_time, "%Y-%m-%d"), equipment_major=equipment_major,
                                                                        place=place, weekend_desc=weekend_desc,
                                                                        exe_group=exe_group, num1=num1, num2=num2
                                                                        )

            else:
                # print(user_num,"==user_num")
                exe_user = MyUser.objects.filter(number=user_num).first()
                if exe_user.group == None:
                    # print(exe_group, "====2")
                    # print(supervision_major,work_content,number,KKS_code,KKS_codename,type, score,exe_user,
                    #        warinig_time, overdue_1,overdue_2,place,equipment_major,overdue_3, nature,
                    #        resource,datetime.strptime(start_time, "%Y-%m-%d"),datetime.strptime(end_time, "%Y-%m-%d"),
                    #        weekend_desc, num1,num2)
                    regularwork = RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                        work_content=work_content,
                                                                        number=number,
                                                                        KKS_code=KKS_code, KKS_codename=KKS_codename,
                                                                        type=type, score=score, exe_user=exe_user,
                                                                        warinig_time=warinig_time, overdue_1=overdue_1,
                                                                        overdue_2=overdue_2,place=place,equipment_major=equipment_major,
                                                                        overdue_3=overdue_3, nature=nature,
                                                                        resource=resource,
                                                                        start_time=datetime.strptime(start_time, "%Y-%m-%d"),
                                                                        end_time=datetime.strptime(end_time, "%Y-%m-%d"),
                                                                        weekend_desc=weekend_desc, exe_group=exe_group, num1=num1,
                                                                        num2=num2
                                                                        )


                else:
                    # print(exe_group, "====2")
                    regularwork = RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                        work_content=work_content,
                                                                        number=number,
                                                                        KKS_code=KKS_code, KKS_codename=KKS_codename,
                                                                        type=type, score=score, exe_user=exe_user,
                                                                        warinig_time=warinig_time, overdue_1=overdue_1,
                                                                        overdue_2=overdue_2,
                                                                        overdue_3=overdue_3, nature=nature,
                                                                        resource=resource, start_time=datetime.strptime(start_time, "%Y-%m-%d"),
                                                                        end_time=datetime.strptime(end_time, "%Y-%m-%d"), equipment_major=equipment_major,
                                                                        place=place, weekend_desc=weekend_desc,
                                                                        exe_group=exe_group, num1=num1, num2=num2
                                                                        )
            regularwork.save()

            # 工作内容表
            work_plan = RegularWorkPlan.objects.filter(id=regularwork.id).first()
            # no_end = str(regularwork.id)[-4:]
            # no_end = "%04d" % int(no_end)
            number = int(datetime.strftime(datetime.now(), '%Y%m%d')[-6:]+str(time.time()).replace('.', '')[-4:])
            # number = str(time.time()).replace('.', '')[-9:]
            content = all_list_2[i][0]
            if content == '' or content == None:
                content = '暂无'
            # 创建时间
            created_at = datetime.now()
            # 最后更新人
            created_by = last_updated_by = user_obj.myuser
            # 最后更新时间
            last_updated_at = datetime.now()

            # 保存到数据库
            ready_data_1 = WorkContent.objects.create(created_by=created_by,
                                                           created_at=created_at, last_updated_by=last_updated_by,
                                                           last_updated_at=last_updated_at,
                                                           number=number, regular_work=work_plan,
                                                           content=content)
            ready_data_1.save()

            # 工作准备
            # 获取从前端发来的数据
            # number = datetime.strftime(datetime.now(), '%Y%m%d')+str(regularwork.id)
            # number = str(time.time()).replace('.', '')[-9:]
            # no_end = str(regularwork.id)[-4:]
            # no_end = "%04d" % int(no_end)
            number = int(datetime.strftime(datetime.now(), '%Y%m%d')[-6:] + str(time.time()).replace('.', '')[-4:])
            content = all_list_3[i][0]
            if content == '' or content == None:
                content = '暂无'
            # 创建时间
            created_at = datetime.now()
            # 最后更新人
            created_by = last_updated_by = user_obj.myuser
            # 最后更新时间
            last_updated_at = datetime.now()

            # 保存到数据库
            ready_data_2 = PreWork.objects.create(created_by=created_by,
                                                       created_at=created_at, last_updated_by=last_updated_by,
                                                       last_updated_at=last_updated_at,
                                                       number=number, regular_work=work_plan,
                                                       content=content)
            ready_data_2.save()

            # 注意事项表
            # 获取从前端发来的数据
            # number = datetime.strftime(datetime.now(), '%Y%m%d')+str(regularwork.id)
            # number = str(time.time()).replace('.', '')[-9:]
            # no_end = str(regularwork.id)[-4:]
            # no_end = "%04d" % int(no_end)
            number = int(datetime.strftime(datetime.now(), '%Y%m%d')[-6:] + str(time.time()).replace('.', '')[-4:])
            content = all_list_4[i][0]
            if content == '' or content == None:
                content = '暂无'
            # 创建时间
            created_at = datetime.now()
            # 最后更新人
            created_by = last_updated_by = user_obj.myuser
            # 最后更新时间
            last_updated_at = datetime.now()

            # 保存到数据库
            ready_data_3 = WorkCare.objects.create(created_by=created_by,
                                                        created_at=created_at, last_updated_by=last_updated_by,
                                                        last_updated_at=last_updated_at,
                                                        number=number, regular_work=work_plan,
                                                        content=content)
            ready_data_3.save()

            # 工作数据表
            # 获取从前端发来的数据
            # number = datetime.strftime(datetime.now(), '%Y%m%d')+str(regularwork.id)
            # number = str(time.time()).replace('.', '')[-9:]
            # no_end = str(regularwork.id)[-4:]
            # no_end = "%04d" % int(no_end)
            number = int(datetime.strftime(datetime.now(), '%Y%m%d')[-6:] + str(time.time()).replace('.', '')[-4:])
            data_name = all_list_5[i][0]
            if data_name == '' or data_name == None:
                data_name = '暂无'
            data_value = all_list_5[i][1]
            if data_value == '' or data_value == None:
                data_value = '暂无'
            # 保存到数据库
            ready_data_4 = WorkData.objects.create(number=number, regular_work=work_plan,
                                                        place=place, data_name=data_name,
                                                        data_value=data_value)
            ready_data_4.save()


            i += 1


    else:
        err_msg = '请导入.xls或者.xlsx文件'
        # print(err_msg)

    return redirect('regularworktask/list/?action=list&menuid=49')


# exce获取表中的数据列表
def get_sheets_mg(data, num):
    table = data.sheets()[num]  # 打开第一张表
    nrows = table.nrows  # 获取表的行数
    ncole = table.ncols  # 获取列数
    all_list = []
    for i in range(nrows):  # 循环逐行打印
        one_list = []
        for j in range(ncole):
            cell_value = table.row_values(i)[j]
            # if table.row_values(i)[j] in one_list:
            #     continue
            # else:
            if (cell_value is None or cell_value == ''):
                cell_value = (get_merged_cells_value(table, i, j))
            # one_list.append(table.row_values(i)[j])
            one_list.append(cell_value)
        all_list.append(one_list)
    del (all_list[0])  # 删除标题
    return all_list

def get_merged_cells_value(sheet, row_index, col_index):
    """
    先判断给定的单元格，是否属于合并单元格；
    如果是合并单元格，就返回合并单元格的内容
    :return:
    """
    merged = get_merged_cells(sheet)
    # print(merged,"==hebing")
    for (rlow, rhigh, clow, chigh) in merged:
        if (row_index >= rlow and row_index < rhigh):
            if (col_index >= clow and col_index < chigh):
                cell_value = sheet.cell_value(rlow, clow)
                # print('该单元格[%d,%d]属于合并单元格，值为[%s]' % (row_index, col_index, cell_value))
                return cell_value
                break
    return None

def get_merged_cells(sheet):
    """
    获取所有的合并单元格，格式如下：
    [(4, 5, 2, 4), (5, 6, 2, 4), (1, 4, 3, 4)]
    (4, 5, 2, 4) 的含义为：行 从下标4开始，到下标5（不包含）  列 从下标2开始，到下标4（不包含），为合并单元格
    :param sheet:
    :return:
    """
    return sheet.merged_cells

