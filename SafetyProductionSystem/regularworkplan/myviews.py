from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from . import models
import re
from django.db import connection
from systemsettings.views import checkpower
from systemsettings.models import MyUser, User, SupervisionType, EquipmentMajor, EquipmentCount, KKS, MyGroup, Department
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
from django.contrib import messages
from lbworkflow.views import processinstance
from SafetyProductionSystem.settings import CRONJOBS
from django.core.management import call_command
from django.http import StreamingHttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

# Create your views here.
# 定期工作列表
# @cache_page(60 * 1)
def regularwork(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')  # 获取登录人信息
    place = user.myuser.company  # 找到其所在分公司
    user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    regularwork_list1 = []  # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    if user.is_superuser:

        regularwork_list_2 = models.RegularWorkPlan.objects.filter(is_activate=1).order_by('-id')   # 遍历每一个组织为下属机构的月度计划与总结列表
        # 总数据
        total_counts = models.RegularWorkPlan.objects.filter(is_activate=1).count()
        for mon in regularwork_list_2:
            regularwork_list1.append(mon)
    else:
        regularwork_list_2 = models.RegularWorkPlan.objects.filter(is_activate=1, place=place).order_by('-id')   # 遍历每一个组织为下属机构的月度计划与总结列表
        # 总数据
        total_counts = models.RegularWorkPlan.objects.filter(is_activate=1, place=place).count()

        for mon in regularwork_list_2:
            regularwork_list1.append(mon)

    # 去重
    regularwork_list = list(set(regularwork_list1))
    # 分页
    regularwork_list.sort(key=regularwork_list1.index)
    paginator = Paginator(regularwork_list, 10,1)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        regularwork_list = paginator.page(page)
    except PageNotAnInteger:
        regularwork_list = paginator.page(1)
    except EmptyPage:
        regularwork_list = paginator.page(paginator.num_pages)
    # print(menuid,'===menuid')
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
    page = int(page)   # 将page值转换为int类型，方便在前段判断   否则会出现int类型的1 不等于 str类型的1 的情况
    return render(request, 'regular_work_plan/regular_work_plan.html', locals())


# 定期工作策划新建
@csrf_exempt
def regularwork_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    if request.method == 'GET':
        supervision_major_list = SupervisionType.objects.all()
        equipment_major_list = EquipmentMajor.objects.all()
        kks_list = KKS.objects.filter(place=place)
        user_list = MyUser.objects.filter(company=place)
        group_list = MyGroup.objects.filter(place=place)
        return render(request, 'regular_work_plan/regular_work_plan_add.html', locals())

    elif request.method == 'POST':
        supervision_major = request.POST['supervision_major']
        supervision_major = SupervisionType.objects.get(name=supervision_major)
        state = '拟定'
        place = place
        number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            KKS_code = KKS.objects.filter(KKS_code=request.POST['KKS_code']).first()
            print(KKS_code)
        except:
            KKS_code = ''
            print(1111111111111111)
        KKS_codename = request.POST['KKS_codename']
        nature = request.POST['nature']
        score = request.POST['score']
        if score == '':
            score = 0
        equipment_major = request.POST['equipment_major']
        equipment_major = EquipmentMajor.objects.get(id=equipment_major)
        work_content = request.POST['work_content']
        user = request.POST['exe_user']
        group = request.POST['exe_group']
        warinig_time = request.POST['warinig_time']
        overdue_1 = request.POST['overdue_major']
        overdue_2 = request.POST['overdue_dept']
        overdue_3 = request.POST['overdue_leader']
        resource = request.POST['resource']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        if end_time == '':
            new_start_date = datetime.strptime(start_time, "%Y-%m-%d")
            new_enddate = datetime(new_start_date.year, new_start_date.month, new_start_date.day)
            end_time = (new_enddate + timedelta(days=1825)).date()
        type = request.POST['type']
        weekend_desc = request.POST['weekend_desc']  # 小时  天   周   月   年  一次
        if weekend_desc == '周':
            num1 = request.POST['num1']
            num_list = request.POST.getlist('num2')
            num2 = ''
            for num in num_list:
                if num != '':
                    num2 += num + ','
            num2 = num2[0:len(num2) - 1]

        else:
            num1 = request.POST['num1']
            num2 = request.POST['num2']
        if user == '':
            # print("1111")
            exe_group = MyGroup.objects.filter(name=group).first()
            regularwork = models.RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                work_content=work_content,
                                                                state=state, number=number,
                                                                KKS_code=KKS_code,
                                                                KKS_codename=KKS_codename,
                                                                type=type, score=score,
                                                                warinig_time=warinig_time, overdue_1=overdue_1,
                                                                overdue_2=overdue_2,
                                                                overdue_3=overdue_3, nature=nature,
                                                                resource=resource, start_time=start_time,
                                                                end_time=end_time, equipment_major=equipment_major,
                                                                place=place, weekend_desc=weekend_desc,
                                                                exe_group=exe_group, num1=num1, num2=num2
                                                                )

        else:
            # print(2222)
            # print(user)
            exe_user = MyUser.objects.filter(name=user).first()
            if exe_user.group == None:
                regularwork = models.RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                    work_content=work_content,
                                                                    state=state, number=number,
                                                                    KKS_code=KKS_code,
                                                                    KKS_codename=KKS_codename,
                                                                    type=type, score=score, exe_user=exe_user,
                                                                    warinig_time=warinig_time, overdue_1=overdue_1,
                                                                    overdue_2=overdue_2,
                                                                    overdue_3=overdue_3, nature=nature,
                                                                    resource=resource, start_time=start_time,
                                                                    end_time=end_time, equipment_major=equipment_major,
                                                                    place=place, weekend_desc=weekend_desc, num1=num1,
                                                                    num2=num2
                                                                    )


            else:
                regularwork = models.RegularWorkPlan.objects.create(supervision_major=supervision_major,
                                                                    work_content=work_content,
                                                                    state=state, number=number,
                                                                    KKS_code=KKS_code,
                                                                    KKS_codename=KKS_codename,
                                                                    type=type, score=score, exe_user=exe_user,
                                                                    warinig_time=warinig_time, overdue_1=overdue_1,
                                                                    overdue_2=overdue_2,
                                                                    overdue_3=overdue_3, nature=nature,
                                                                    resource=resource, start_time=start_time,
                                                                    end_time=end_time, equipment_major=equipment_major,
                                                                    place=place, weekend_desc=weekend_desc,
                                                                    exe_group=exe_user.group, num1=num1, num2=num2
                                                                    )

        regularwork.save()
        return HttpResponseRedirect(
            '/regularworkplan/' + str(regularwork.id) + '/detail/?action=detail&menuid=48')


# 定期工作策划详情
def regularwork_detail(request, e_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    new_processinstance = processinstance.ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    regularworkplan = models.RegularWorkPlan.objects.get(id=e_id)
    pid = e_id
    work_ready = models.PreWork.objects.filter(regular_work=pid)
    work_matters = models.WorkCare.objects.filter(regular_work=pid)
    work_contents = models.WorkContent.objects.filter(regular_work=pid)
    work_datas = models.WorkData.objects.filter(regular_work=pid)
    return render(request, 'regular_work_plan/regular_work_plan_detail.html', locals())


# 定期工作策划编辑
@csrf_exempt
def regularwork_edit(request, e_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    if request.method == 'GET':
        supervision_major_list = SupervisionType.objects.all()
        equipment_major_list = EquipmentMajor.objects.all()
        kks_list = KKS.objects.filter(place=place)
        user_list = MyUser.objects.filter(company=place)
        group_list = MyGroup.objects.filter(place=place)
        equipment_plan = models.RegularWorkPlan.objects.filter(id=e_id).first()

        # 定期工作策划的周期描述需要拆分显示
        # num = re.search('\d+', equipment_plan.weekend_desc)
        # weekend_desc = re.search('\D+', equipment_plan.weekend_desc)
        # if num != None:
        #     num = num.group()
        # else:
        #     num = ''
        # if weekend_desc != None:
        #     weekend_desc = weekend_desc.group()
        # else:
        #     weekend_desc = ''
        return render(request, 'regular_work_plan/regular_work_plan_edit.html', locals())
    elif request.method == 'POST':
        supervision_major = request.POST['supervision_major']
        supervision_major = SupervisionType.objects.get(name=supervision_major)
        state = '拟定'
        place = place
        number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            KKS_code = KKS.objects.filter(KKS_code=request.POST['KKS_code']).first()
        except:
            KKS_code = ''
        KKS_codename = request.POST['KKS_codename']
        nature = request.POST['nature']
        score = request.POST['score']
        if score == '':
            score = 0
        equipment_major = request.POST['equipment_major']
        equipment_major = EquipmentMajor.objects.get(id=equipment_major)
        work_content = request.POST['work_content']
        user = request.POST['exe_user']
        group = request.POST['exe_group']
        warinig_time = request.POST['warinig_time']
        overdue_1 = request.POST['overdue_major']
        overdue_2 = request.POST['overdue_dept']
        overdue_3 = request.POST['overdue_leader']
        resource = request.POST['resource']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        if end_time == '':
            new_start_date = datetime.strptime(start_time, "%Y-%m-%d")
            new_enddate = datetime(new_start_date.year, new_start_date.month, new_start_date.day)
            end_time = (new_enddate + timedelta(days=1825)).date()
        type = request.POST['type']
        regularwork_obj = models.RegularWorkPlan.objects.filter(id=e_id).first()
        if user == '':
            exe_group = MyGroup.objects.filter(name=group).first()
            regularwork_obj.supervision_major=supervision_major
            regularwork_obj.work_content=work_content
            regularwork_obj.state=state
            regularwork_obj.number=number
            regularwork_obj.KKS_codename=KKS_codename
            regularwork_obj.type=type
            regularwork_obj.score=score
            regularwork_obj.warinig_time=warinig_time
            regularwork_obj.supervision_major=supervision_major
            regularwork_obj.overdue_1=overdue_1
            regularwork_obj.overdue_2=overdue_2
            regularwork_obj.overdue_3=overdue_3
            regularwork_obj.nature=nature
            regularwork_obj.resource=resource
            regularwork_obj.start_time=start_time
            regularwork_obj.end_time=end_time
            regularwork_obj.equipment_major=equipment_major
            regularwork_obj.place=place
            regularwork_obj.exe_group=exe_group
            regularwork_obj.save()


        else:
            exe_user = MyUser.objects.filter(name=user).first()
            if exe_user.group == None:
                regularwork_obj.supervision_major = supervision_major
                regularwork_obj.work_content = work_content
                regularwork_obj.state = state
                regularwork_obj.number = number
                regularwork_obj.KKS_codename = KKS_codename
                regularwork_obj.type = type
                regularwork_obj.score = score
                regularwork_obj.warinig_time = warinig_time
                regularwork_obj.supervision_major = supervision_major
                regularwork_obj.overdue_1 = overdue_1
                regularwork_obj.overdue_2 = overdue_2
                regularwork_obj.overdue_3 = overdue_3
                regularwork_obj.nature = nature
                regularwork_obj.resource = resource
                regularwork_obj.start_time = start_time
                regularwork_obj.end_time = end_time
                regularwork_obj.equipment_major = equipment_major
                regularwork_obj.place = place
                regularwork_obj.exe_user=exe_user
                regularwork_obj.save()

            else:
                exe_group = MyGroup.objects.filter(name=group).first()
                regularwork_obj.supervision_major = supervision_major
                regularwork_obj.work_content = work_content
                regularwork_obj.state = state
                regularwork_obj.number = number
                regularwork_obj.KKS_codename = KKS_codename
                regularwork_obj.type = type
                regularwork_obj.score = score
                regularwork_obj.warinig_time = warinig_time
                regularwork_obj.supervision_major = supervision_major
                regularwork_obj.overdue_1 = overdue_1
                regularwork_obj.overdue_2 = overdue_2
                regularwork_obj.overdue_3 = overdue_3
                regularwork_obj.nature = nature
                regularwork_obj.resource = resource
                regularwork_obj.start_time = start_time
                regularwork_obj.end_time = end_time
                regularwork_obj.equipment_major = equipment_major
                regularwork_obj.place = place
                regularwork_obj.exe_group=exe_user.group
                regularwork_obj.exe_user=exe_user
                regularwork_obj.save()
        return HttpResponseRedirect('/regularworkplan/' + str(regularwork_obj.id) + '/detail/?action=detail&menuid=48')


# 定期工作策划删除
def regularwork_delete(request, e_id):
    # 获取定期工作策划
    regularwork = models.RegularWorkPlan.objects.get(id=e_id)
    # regularwork_list = models.RegularWorkPlan.objects.filter(is_activate=1)
    # for regularwork in regularwork_list:
    #     regularwork.is_activate = 0
    #     regularwork.save()
    regularwork.is_activate = 0
    regularwork.save()
    return HttpResponseRedirect('/regularworkplan/list/?action=list&menuid=48')


# 搜索定期工作策划
@csrf_exempt
def regularwork_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    user_list = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    # 获取该登录人的组织机构
    # Department = user.profile.Department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # 获取前端传来的数据
    supervision_major = request.GET.get('supervision_major','')
    equipment_major = request.GET.get('equipment_major','')
    type = request.GET.get('type','')
    exe_user = request.GET.get('exe_user','')
    work_content = request.GET.get('work_content','')
    regularwork_list = ''

    if supervision_major == '':
        if equipment_major == '':
            if type == '':
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),Q(is_activate=1))
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),Q(exe_user_id=exe_user),Q(is_activate=1))

            else:
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),type=type,is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),type=type,exe_user_id=exe_user, is_activate=1)

        else:
            if type == '':
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),equipment_major_id=equipment_major,is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),equipment_major_id=equipment_major,exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),equipment_major_id=equipment_major,type=type, is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),equipment_major_id=equipment_major,type=type, exe_user_id=exe_user,
                                                                                       is_activate=1)
    else:
        if equipment_major == '':
            if type == '':
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,type=type, is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,type=type, exe_user_id=exe_user,
                                                                             is_activate=1)

        else:
            if type == '':
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             exe_user_id=exe_user, is_activate=1)

            else:
                if exe_user == '':
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             type=type, is_activate=1)
                else:
                    regularwork_list = models.RegularWorkPlan.objects.filter(Q(work_content__icontains=work_content),supervision_major_id=supervision_major,equipment_major_id=equipment_major,
                                                                             type=type, exe_user_id=exe_user,is_activate=1)

                                                                             # supervision_major_obj = models.SupervisionType.objects.filter(id=supervision_major).first()
    # supervision_major = supervision_major_obj.id
    # equipment_major_obj = models.EquipmentMajor.objects.filter(id=equipment_major).first()
    # equipment_major = equipment_major_obj.id
    # exe_user_obj = User.objects.filter(id=exe_user).first()
    # exe_user = exe_user_obj.id
    # if len(orgid) == 0:
    #     orgid = ""
    # if len(start_time) == 0:
    #     start_time = '2000-01-01'
    # if len(start_time_2) == 0:
    #     start_time_2 = '2021-10-10'
    # if len(end_time) == 0:
    #     end_time = '2000-01-01'
    # if len(end_time_2) == 0:
    #     end_time_2 = '2021-10-10'
    # if len(state) == 0:
    #     state = ''
    # if len(number) == 0:
    #     number = ''
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM regularworkplan_regularworkplan where orgid like '%%%%%s%%%%' and number like '%%%%%s%%%%' and is_activate=1 and work_content like '%%%%%s%%%%' and start_time between '%s' and '%s' and end_time between '%s' and '%s' and equipment_major_id = '%s' and exe_user_id = '%s' and  supervision_major_id = '%s' and state like '%%%%%s%%%%' " % (
    #         orgid, number, work_content, start_time, start_time_2, end_time, end_time_2, equipment_major, exe_user,
    #         supervision_major, state))
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
    #     regularwork = models.regularwork.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=regularwork.orgid) in orgid_list:
    #         regularwork_list.append(regularwork)
    # cursor.close()
    # # 去重
    # regularwork_list = list(set(regularwork_list))

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
        # 将监督类型列表查询
    # supervision_major_list = models.SupervisionType.objects.filter(is_activate=1)
    # # 设备专业列表查询
    # equipment_major_list = models.EquipmentMajor.objects.all()
    #
    # # 人员查询
    # # 定义一个空的列表，用于保存人员
    # user_list = []
    # Department_list = []
    # # 找到该登录人的组织机构所有下属机构
    # orgid = Department.objects.filter(parent=Department)
    # # 遍历下属机构
    # for org in orgid:
    #     Department_list.append(org)
    #     # 找出组织机构为子机构的并且非删除的所有queryset对象
    #     user = User.objects.filter(is_active=1, Department=org)
    #     for s in user:
    #         # 加入到list中保存
    #         user_list.append(s)
    # Department_list.append(Department)
    # for user in User.objects.filter(is_active=1, Department=Department):
    #     user_list.append(user)
    return render(request, 'regular_work_plan/regular_work_plan.html', locals())


# 定期工作策划 工作准备---------------------

# 展示列表
def show_work_ready(request, pid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power


# 新建
def add_work_ready(request, pid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    pid = pid
    work_plan = models.RegularWorkPlan.objects.filter(id=pid).first()
    if request.method == "GET":
        return render(request, 'regular_ready/add_ready.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据
        number = datetime.strftime(datetime.now(), '%Y%m%d')
        content = request.POST["content"]
        # 创建时间
        created_at = datetime.now()
        # 最后更新人
        created_by = last_updated_by = user.myuser
        # 最后更新时间
        last_updated_at = datetime.now()

        # 保存到数据库
        ready_data = models.PreWork.objects.create(created_by=created_by,
                                                   created_at=created_at, last_updated_by=last_updated_by,
                                                   last_updated_at=last_updated_at,
                                                   number=number, regular_work=work_plan,
                                                   content=content)
        ready_data.save()
        return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 详情
def show_one_ready(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    ready_data = models.PreWork.objects.filter(id=zid).first()
    return render(request, 'regular_ready/detail_ready.html', locals())


# 删除
def del_work_ready(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    models.PreWork.objects.get(id=zid).delete()
    return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


#  定期工作策划   注意事项------------------------
#  添加
def add_matter(request, pid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    pid = pid
    work_plan = models.RegularWorkPlan.objects.filter(id=pid).first()
    if request.method == "GET":
        return render(request, 'regular_matter/add_matter.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据
        number = datetime.strftime(datetime.now(), '%Y%m%d')
        content = request.POST["content"]
        # 创建时间
        created_at = datetime.now()
        # 最后更新人
        created_by = last_updated_by = user.myuser
        # 最后更新时间
        last_updated_at = datetime.now()

        # 保存到数据库
        ready_data = models.WorkCare.objects.create(created_by=created_by,
                                                    created_at=created_at, last_updated_by=last_updated_by,
                                                    last_updated_at=last_updated_at,
                                                    number=number, regular_work=work_plan,
                                                    content=content)
        ready_data.save()
        return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 展示详情
def show_one_matter(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    matter_data = models.WorkCare.objects.filter(id=zid).first()
    # print(matter_data)
    return render(request, 'regular_matter/detail_matter.html', locals())


# 删除
def del_work_matter(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    models.WorkCare.objects.get(id=zid).delete()
    return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 定期工作     工作内容-------------------------
#  添加
def add_work_content(request, pid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    pid = pid
    work_plan = models.RegularWorkPlan.objects.filter(id=pid).first()
    if request.method == "GET":
        return render(request, 'regular_work_content/add_work_content.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据
        number = datetime.strftime(datetime.now(), '%Y%m%d')
        content = request.POST["content"]
        # 创建时间
        created_at = datetime.now()
        # 最后更新人
        created_by = last_updated_by = user.myuser
        # 最后更新时间
        last_updated_at = datetime.now()

        # 保存到数据库
        ready_data = models.WorkContent.objects.create(created_by=created_by,
                                                       created_at=created_at, last_updated_by=last_updated_by,
                                                       last_updated_at=last_updated_at,
                                                       number=number, regular_work=work_plan,
                                                       content=content)
        ready_data.save()
        return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 展示详情
def show_one_content(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    work_content_data = models.WorkContent.objects.filter(id=zid).first()
    return render(request, 'regular_work_content/detail_work_content.html', locals())


# 删除
def del_work_content(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    models.WorkContent.objects.get(id=zid).delete()
    return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 定期工作     工作数据-------------------------
#  添加
def add_work_data(request, pid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    pid = pid
    work_plan = models.RegularWorkPlan.objects.filter(id=pid).first()
    if request.method == "GET":
        return render(request, 'regular_work_data/add_work_data.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据
        number = datetime.strftime(datetime.now(), '%Y%m%d')
        data_name = request.POST["data_name"]
        data_value = request.POST["data_value"]

        # 保存到数据库
        ready_data = models.WorkData.objects.create(number=number, regular_work=work_plan,
                                                    place=place, data_name=data_name,
                                                    data_value=data_value)
        ready_data.save()
        return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')


# 展示详情
def show_one_data(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    work_data_data = models.WorkData.objects.filter(id=zid).first()
    return render(request, 'regular_work_data/detail_work_data.html', locals())


# 删除
def del_work_data(request, pid, zid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    models.WorkData.objects.get(id=zid).delete()
    return HttpResponseRedirect('/regularworkplan/' + str(pid) + '/detail/?action=detail&menuid=48')

def download_regularworkplan_mould(request):
    def file_iterator(file_name,chunk_size=512):  # 用于形成二进制数据
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = "/home/wangyifan/work_space/files/dingqi_test.xls"   # 要下载的文件路径
    response = StreamingHttpResponse(file_iterator(the_file_name))  # 这里创建返回
    response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
    response['Content-Disposition'] = 'attachment; filename="定期工作任务导入模板.xls"'   # 注意filename 这个是下载后的名字
    return response
@csrf_exempt
def search_kks(request):
    user = request.session.get('mylogin')
    place = user.myuser.company
    if request.method == 'POST':
        kks_info = request.POST.get("kks_info",'')
        kks_list = KKS.objects.filter(Q(KKS_code__icontains=kks_info)|Q(KKS_codename__icontains=kks_info))
        # kks_list = KKS.objects.filter(place=place)
        list1 = []

        if kks_list:
            if len(kks_list) > 101:
                kks_list=kks_list[:100]
            for kks in kks_list:
                list1.append({'kks_code':kks.KKS_code,'kks_codename':kks.KKS_codename})
            re_dict = {'kks_list':list1}
            return JsonResponse(re_dict)