from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from . import models
from django.db import connection
from systemsettings.views import  checkpower
from systemsettings.models import Department, User,MyUser,Company

from mon_plan_sum.models import MonPlanSum,SmallDatas
from django.contrib import messages
from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance

# Create your views here.
# 月度工作执行列表
def mon_work(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 该登录人登录时选择的组织机构信息
    place =user.myuser.company
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    mon_work_list = []
    if user.is_superuser:
        # 电厂列表
        company_list = Company.objects.all()
        # 找出组织机构为子机构的并且非删除的所有queryset对象
        mon_plan_list_2 = models.MonWorkExe.objects.filter(is_activate=1)
        #  显示非删除所有queryset 对象 总条数
        total_counts = models.MonWorkExe.objects.filter(is_activate=1).count()
        # 遍历每一个组织为下属机构的月度计划与总结列表
        for mon in mon_plan_list_2:
            # 加入到list中保存
            mon_work_list.append(mon)
    else:
        # 电厂列表
        company_list = [place]
        # 找出组织机构为子机构的并且非删除的所有queryset对象
        mon_plan_list_2 = models.MonWorkExe.objects.filter(is_activate=1, place=place, execute_user=user.myuser.id)
        total_counts = models.MonWorkExe.objects.filter(is_activate=1, place=place, execute_user=user.myuser.id).count()
        # 遍历每一个组织为下属机构的月度计划与总结列表
        for mon in mon_plan_list_2:
            # 加入到list中保存
            mon_work_list.append(mon)

    mon_work_list = list(set(mon_work_list))
    # 分页
    paginator = Paginator(mon_work_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        mon_work_list = paginator.page(page)
    except PageNotAnInteger:
        mon_work_list = paginator.page(1)
    except EmptyPage:
        mon_work_list = paginator.page(paginator.num_pages)

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
    return render(request, 'mon_work_exe/mon_work_exe.html',locals())


# 新增月度工作执行
@csrf_exempt
def mon_work_add(request):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    place = user.myuser.company
    small_plan_list_all = SmallDatas.objects.filter(exe_user=user.myuser, is_activate=1)   # 全部工作任务
    # 查询该月度任务在审批流中的状态,如果该任务计划为归档状态,则将该任务添加至mon_plan_sum_list列表中
    small_plan_list = []  # 已归档的工作任务
    for plan in small_plan_list_all:
        try:
            if plan.monplansum.pinstance.cur_node.mynode.node_name == "归档":
                # print(plan.monplansum.pinstance.cur_node.mynode.node_name)
                small_plan_list.append(plan)
        except:
            # print('pass')
            pass
    department = user.myuser.department
    now =  datetime.now()
    if request.method == 'GET':
        # get 方式访问
        year = datetime.now().year
        month = datetime.now().month
        return render(request, 'mon_work_exe/mon_work_add.html',locals())

    elif request.method == 'POST':
        place = place
        created_at = datetime.now()
        last_updated_at = datetime.now()
        plan_content = request.POST['plan_content']
        plan_smallnumber = request.POST['plan_smallnumber']
        plan_smallnumber = SmallDatas.objects.filter(id=plan_smallnumber).first()
        plan_number = plan_smallnumber.monplansum
        finish_time = plan_smallnumber.finish_time
        execute_desc = request.POST['execute_desc']
        execute_user = user.myuser
        problem_desc = request.POST['problem_desc']
        remarks = request.POST['remarks']
        num = request.POST['num2']
        new_mon_work = models.MonWorkExe.objects.create( created_at=created_at,
                                                        last_updated_at=last_updated_at,
                                                        plan_content=plan_content,
                                                        finish_time=finish_time,plan_number=plan_number,
                                                        plan_smallnumber=plan_smallnumber,execute_user=execute_user,
                                                        execute_desc=execute_desc,
                                                        problem_desc=problem_desc, remarks=remarks, state='拟定',
                                                        place=place)
        new_mon_work.save()
        my_process = MyProcess.objects.filter(app_name='月度工作执行',
                                              is_activate=1, company=place).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            messages.info(request, 'Success %s: %s,%s' % ('保存', new_mon_work, '暂无匹配的工作流程,请先去配置流程后再提交！'))
            return HttpResponseRedirect(
                    '/monworkexe/' + str(new_mon_work.id) + '/detail/?action=detail&menuid=8')
        process = my_process.process

        new_mon_work.created_by = request.session['mylogin']
        new_mon_work.save()
        if num == '1':
            new_mon_work.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", new_mon_work))
            return HttpResponseRedirect(
                '/monworkexe/' + str(new_mon_work.id) + '/detail2/?action=detail&menuid=8')
        elif num == '2':
            new_mon_work.create_pinstance(process=process, submit=True)
            new_mon_work.created_by = request.user
            new_mon_work.save()
            new_processinstance = new_mon_work.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', new_mon_work))

            return HttpResponseRedirect(
                '/monworkexe/' + str(new_mon_work.id) + '/detail/?action=detail&menuid=8&pinstance_id=' + str(
                    new_processinstance.id))
        



@csrf_exempt
def check(request):
    number = request.POST['id']
    # 获取员工对象
    content = SmallDatas.objects.get(id=number)
    return JsonResponse({ 'content':content.content})


# 删除月度工作执行
def mon_work_delete(request, m_id):
    mon_work = models.MonWorkExe.objects.get(id=m_id)
    mon_work.is_activate = 0
    mon_work.save()
    return HttpResponseRedirect('/monworkexe/list/?action=list&menuid=8')


# 编辑月度工作执行
@csrf_exempt
def mon_work_edit(request, m_id):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    mon_work = models.MonWorkExe.objects.get(id=m_id)
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    Department = user.myuser.Department
    # 找到其所在分公司
    place = check_place(Department)
    # 定义一个空的列表,用于保存组织机构列表
    Department_list = []
    # 定义一个空的列表，用于保存人员
    user_lists = []
    # 找到该登录人的组织机构所有下属机构
    orgid = Department.objects.filter(parent=Department)
    # 遍历下属机构
    for org in orgid:
        Department_list.append(org)
        # 找出组织机构为子机构的并且非删除的所有queryset对象
        user_list = User.objects.filter(is_active=1)
        # 遍历每一个组织为下属机构的月度计划与总结列表
        for user in user_list:
            if user.myuser.Department.name == org or user.myuser.Department == Department:
                # 加入到list中保存
                user_lists.append(user)
    Department_list.append(Department)
    orgid = Department_list
    now = datetime.now()
    staff_list = user_lists
    if request.method == 'GET':
        # get 方式访问
        return render(request, 'mon_work_exe/mon_work_edit.html',locals())

    elif request.method == 'POST':
        last_updated_at = datetime.now()
        last_updated_by = request.session.get('mylogin')
        plan_content = request.POST['plan_content']
        finish_time = request.POST['finish_time']
        execute_department_number = request.POST['execute_department_number']
        execute_department = Department.objects.filter(number=execute_department_number).first()
        execute_staff_number = request.POST['execute_staff_number']
        execute_staff = User.objects.filter(username=execute_staff_number).first()
        execute_desc = request.POST['execute_desc']
        problem_desc = request.POST['problem_desc']
        remarks = request.POST['remarks']
        orgid = request.POST['orgid']
        mon_work.last_updated_at = last_updated_at
        mon_work.last_updated_by = last_updated_by.myuser
        mon_work.plan_content = plan_content
        mon_work.finish_time = finish_time
        mon_work.execute_department = execute_department
        mon_work.execute_staff = execute_staff.myuser
        mon_work.execute_desc = execute_desc
        mon_work.problem_desc = problem_desc
        mon_work.remarks = remarks
        mon_work.orgid = orgid
        mon_work.save()
        return HttpResponseRedirect('/monworkexe/' + m_id + '/detail/?action=detail&menuid=8')


# 月度工作执行详情
def mon_work_detail(request, m_id):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 根据id获取记录
    mon_work = models.MonWorkExe.objects.get(id=m_id)
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = mon_work.pinstance
    if processinstance != None:
        return render(request, 'mon_work_exe/mon_work_detail.html', locals())
    else:
        return render(request, 'mon_work_exe/mon_work_detail2.html', locals())


# 月度工作执行查询
@csrf_exempt
def mon_work_search(request):
    action = 'list'
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    if user.is_superuser:
        # 电厂列表
        company_list = Company.objects.all()
    else:
        # 电厂列表
        company_list = [place]
    # 获取该登录人的组织机构
    Department = user.myuser.department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # print(Department,"====Department")
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    mon_work_list = []
    # 获取前端传来的数据
    orgid = request.GET.get('orgid','')
    desc1 = request.GET.get('desc','')
    time1 = request.GET.get('time1','')  # 起始时间
    time2 = request.GET.get('time2','')  # 结束时间
    staff = request.GET.get('staff','')  # 责任人,外键
    # Department = request.POST['Department']  # 责任部门，外键
    # 关于外键，要判断不为空时找到id
    if len(staff) == 0:
        staff = ''
    else:
        # 找到关联的外键记录
        staff_obj = User.objects.filter(Q(username__icontains=staff)).first()
        if staff_obj == None:
            staff = '#'
        else:
            # 获取id
            staff = staff_obj.id

    # if len(Department) == 0:
    #     Department = ''
    # else:
    #     Department_obj = Department.objects.filter(Q(name__icontains=Department)).first()
    #     if Department_obj == None:
    #         Department = '#'
    #     else:
    #         Department = Department_obj.id
    if len(orgid) == 0:
        orgid = ""
    if len(desc1) == 0:
        desc = ""
    if len(time1) == 0:
        time1 = '2000-01-01'
    if len(time2) == 0:
        time2 = '2021-10-10'
    if len(str(staff)) == 0:
        staff = ''
    # if len(Department) == 0:
    #     Department = ''
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM monworkexe_monworkexe where place_id like '%%%%%s%%%%'  and is_activate=1 and plan_content like '%%%%%s%%%%' and finish_time between '%s' and '%s'  and execute_user_id like '%%%%%s%%%%' " % (
            orgid, desc1, time1, time2, staff))
    # cursor.execute(
    # "SELECT id FROM supervision_monworkexe where orgid like '%%%%国家%%%%'  and is_activate=1 and plan_content like '%%%%%%%%' and finish_time between '2000-10-01' and '2020-10-10' and execute_department_id like '%%%%%%%%' and execute_staff_id like '%%%%%%%%' " )

    # id 列表
    data = list(cursor.fetchall())
    id_list = []
    for row in data:
        # 将id取出，存入列表
        id_list.append(row[0])
    #     id_list.append(row)

    for id in id_list:
        # 通过id获取到数据对象
        mon_work = models.MonWorkExe.objects.get(id=id)
        # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
        # if Department.objects.get(name=mon_work.orgid) in orgid_list:
        mon_work_list.append(mon_work)
    cursor.close()
    # 去重
    mon_work_list = list(set(mon_work_list))
    # 分页
    paginator = Paginator(mon_work_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        mon_work_list = paginator.page(page)
    except PageNotAnInteger:
        mon_work_list = paginator.page(1)
    except EmptyPage:
        mon_work_list = paginator.page(paginator.num_pages)
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

    return render(request, 'mon_work_exe/mon_work_exe.html',locals())