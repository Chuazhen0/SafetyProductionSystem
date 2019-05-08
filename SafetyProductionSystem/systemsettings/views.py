from typing import List, Any
from django.shortcuts import render,redirect
from itertools import chain
from django.contrib.auth import authenticate,login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import uuid
from lbworkflow.core.datahelper import create_app
from .models import User, Role, Operation, Menu, Department, MyUser, Company,Job,EquipmentMajor,SupervisionType,MyGroup
from datetime import datetime
from lbworkflow.core.datahelper import create_user
from regularworktask.models import RegularWorkTask
from regularworkplan.models import RegularWorkPlan
from monworkexe.models import MonWorkExe
from weekworkplan.models import WeekWorkPlan
from lbworkflow.models import Task
from django.http import StreamingHttpResponse
from django.db.models import Q

from warning.models import WarningNotice
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
import xlrd


def my_create_app():
    create_app(uuid.uuid1(), 'regularworktask')
    create_app(uuid.uuid1(), 'mon_plan_sum')
    create_app(uuid.uuid1(), 'yearplan')
    create_app(uuid.uuid1(), 'warning')
    create_app(uuid.uuid1(), 'warningre')
    create_app(uuid.uuid1(), 'weekworkplan')
    create_app(uuid.uuid1(), 'weekworktask')
#------------------------首页------------------
# 菜单栏数据
def menu_data(menu_id):
    menu_id = list(set(menu_id))
    if menu_id == []:
        menu_list = Menu.objects.none()  # 所有菜单列表
        return chain(menu_list)
    else:
        menu_list = []
        for i in menu_id:
            menu = Menu.objects.get(id=i)
            if menu.is_active == 1:
                menu_list.append(menu)
        for menu in menu_list:
            if menu.parent == None:# 如果该菜单没有父级菜单
                pass
            else:  # 如果该菜单有父级菜单
                if menu.parent.parent == None:# 如果为两级菜单
                    menu_list.append(menu.parent)      # 将该父级菜单加入
                else:# 如果为三级菜单
                    menu_list.append(menu.parent)
                    menu_list.append(menu.parent.parent)
    menu_list = list(set(menu_list))  # type: List[Any]
    return menu_list

# 根据菜单id，用户名称，角色id，判断登录用户拥有的操作权限，返回到base页面中
def checkpower(menuid, username, roleid):
    powerdata = []
    cursor = connection.cursor()
    for id in roleid:
        sqlStr = "SELECT DISTINCT e.url , e.title , e.key FROM systemsettings_role AS a , systemsettings_myuser AS b , systemsettings_myuser_roles AS c ,auth_user AS f,systemsettings_role_operations AS d , systemsettings_operation AS e WHERE a.id = c.role_id AND b.id = c.myuser_id AND a.id = d.role_id AND d.operation_id = e.id AND f.username = '%s' AND e.menu_id ='%s' AND  a.id = '%s'" % (
            username, menuid, id)
        cursor.execute(sqlStr)
        for row in cursor.fetchall():
            data = {
                'key': row[2],
                'url': row[0],
                'title': row[1]
            }
            powerdata.append(data)
    cursor.close()

    return powerdata

# 用户登录
@csrf_exempt
def mylogin(request):
    # RegularWorkTask.objects.filter().delete()
    # 清空表中数据
    if request.method == "GET":
        return render(request, "user/login.html")
    elif request.method == "POST":
        # 获取用户数据
        username = request.POST["username"]
        password = request.POST["password"]
        # 如果信息正确,返回一个user对象
        current_user = authenticate(username=username, password=password)
        if not current_user:
            return render(request, "user/login.html", {"error": '用户名或密码错误'})
        else:
            login(request, current_user)
            request.session["mylogin"] = current_user
            # 获取登录用户配置信息
            myuser = current_user.myuser
            cursor = connection.cursor()
            # 配置和role是多对多的关系
            cursor.execute("SELECT * FROM systemsettings_myuser_roles WHERE myuser_id='%s'" % myuser.id)
            role_id = []
            for row in cursor.fetchall():
                id=row[2]
                role_id.append(id)
                # 获取该用户配置绑定的角色id
            request.session['role_id'] = role_id
            role_list=[]  #  保存角色对象列表
            for id in role_id:
                 role = Role.objects.filter(id=id).first()
                 role_list.append(role)
            # 角色和部门都已经确定，由此可以确定首页展示的数据
            userdata = []
            # 从角色，用户及其中间表中取他们相对应的关系
            for r_id in role_id:
                cursor.execute(
                    "SELECT DISTINCT  * FROM systemsettings_role AS a , systemsettings_myuser AS b , systemsettings_myuser_roles AS c ,systemsettings_role_operations AS d , systemsettings_operation AS e,auth_user AS f  WHERE a.id = c.role_id AND b.id = c.myuser_id AND a.id = d.role_id AND d.operation_id = e.id AND f.username = '%s' AND a.id = '%s' " % (
                     request.session["mylogin"].username, r_id))
                for row in cursor.fetchall():
                    usertable = {
                        'menu_id': row[32],
                        'key': row[31],
                        'url': row[29]
                    }
                    userdata.append(usertable)
            cursor.close()
            request.session['menu'] = userdata   # menu_id,url,key
            menudata = []
            for i in userdata:
                menudata.append(i['menu_id'])
            request.session['menu_id'] = menudata
            menu_list = menu_data(menudata)
            request.session['menudata']=menu_list
            # 从数据库中查询所有数据
            yidu_list = RegularWorkTask.objects.filter(has_readed=True, is_activate=1)
            # 实例化结果集, 每页15条， 少于2条合并到上一页
            paginator = Paginator(yidu_list, 10)
            # 网页中的page值
            page = request.GET.get("page")
            try:
                # 传递HTML当前页对象
                yidu_list = paginator.page(page)
            except PageNotAnInteger:
                yidu_list = paginator.page(1)
            except EmptyPage:
                yidu_list = paginator.page(paginator.num_pages)

            weidu_list = RegularWorkTask.objects.filter(has_readed=False, is_activate=1)
            # 实例化结果集, 每页15条， 少于2条合并到上一页
            paginator = Paginator(weidu_list, 10)
            # 网页中的page值
            page = request.GET.get("page")
            try:
                # 传递HTML当前页对象
                weidu_list = paginator.page(page)
            except PageNotAnInteger:
                weidu_list = paginator.page(1)
            except EmptyPage:
                weidu_list = paginator.page(paginator.num_pages)
            return HttpResponseRedirect('/systemsettings/starter/?weidu_list=%s?yidu_list=%s' % (weidu_list,yidu_list))
            #return redirect(reverse("myform:show_user_data")
            # if 27 in request.session['role_id']:
            #     return redirect('/myform/watch_form/?action=list&menuid=17')
            # else:
            #     return redirect('/myform/show_all_form/?action=list&menuid=16')

# 用户退出
def login_out(request):
    # 清除session缓存
    request.session.flush()
    #     跳转至登录页面
    return redirect('/systemsettings/login/')


# 首页
def starter(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取用户的登录信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    # 获取首页展示定期工作的信息
    regular_work_list = RegularWorkTask.objects.filter(is_activate=1, place=place).order_by('-id')
    regular_work_list = list(regular_work_list)[:4:]
    # 获取首页展示周期检测的信息
    weekworkplan_list = WeekWorkPlan.objects.filter(is_activate=1, place=place).order_by('-id')
    weekworkplan_list = list(weekworkplan_list)[:3:]
    # 获取首页展示月度工作执行的信息
    monworkexe_list = MonWorkExe.objects.filter(is_activate=1, place=place).order_by('-id')
    monworkexe_list = list(monworkexe_list)[:3:]
    # 获取首页展示告警管理的信息
    warning_list = WarningNotice.objects.filter(is_activate=1, place=place).order_by('-id')
    warning_list = list(warning_list)[:3:]
    # 获取首页展示通知的内容(工作流和定期工作任务)
    regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1,exe_user=user.myuser,place=place).order_by('-id') # 获取执行人为当前登录用户的所有定期工作策划记录
    if user.is_superuser:
        regular_work_list = RegularWorkTask.objects.filter(is_activate=1).order_by('-id')
        regular_work_list = list(regular_work_list)[:4:]
        # 获取首页展示周期检测的信息
        weekworkplan_list = WeekWorkPlan.objects.filter(is_activate=1).order_by('-id')
        weekworkplan_list = list(weekworkplan_list)[:3:]
        # 获取首页展示月度工作执行的信息
        monworkexe_list = MonWorkExe.objects.filter(is_activate=1).order_by('-id')
        monworkexe_list = list(monworkexe_list)[:3:]
        # 获取首页展示告警管理的信息
        warning_list = WarningNotice.objects.filter(is_activate=1).order_by('-id')
        warning_list = list(warning_list)[:3:]
        # 获取首页展示通知的内容(工作流和定期工作任务)
        regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1, exe_user=user.myuser).order_by(
            '-id')  # 获取执行人

# TODO:首页定期工作任务列表（待完成的定期工作任务）
    regular_task_list_todo_jsjd = [] # 未完成的（包括已读的和未读的）定期工作任务消息，放置在首页定期工作任务待办列表中   技术监督
    regular_task_list_todo_fc = [] # 未完成的（包括已读的和未读的）定期工作任务消息，放置在首页定期工作任务待办列表中   二十五项反措
    regular_task_list_todo_jsjd_and_fc = [] # 未完成的（包括已读的和未读的）定期工作任务消息，放置在首页定期工作任务待办列表中   技术监督+二十五项反措
# TODO:未读消息
    all_info_list_weidu = []  # 所有的未读消息
    '''
        任务分类展示，1技术监督;2二十五项反措;3技术监督+二十五项反措
    '''
    for myplan in regular_plan_list:
        regular_task = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan,has_readed=0).order_by('-id')
        # 1技术监督   jsjd
        regular_task_todo_jsjd = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan, regularwork__resource='技术监督').order_by('-id')
        # 2二十五项反措 fc
        regular_task_todo_fc = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan, regularwork__resource='二十五项反措').order_by('-id')
        # 3技术监督+二十五项反措  jsjd_and_fc
        regular_task_todo_jsjd_and_fc = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan, regularwork__resource='技术监督+二十五项反措').order_by('-id')
        for retask in regular_task:
            if retask != None:
                all_info_list_weidu.append(retask)
        for retask in regular_task_todo_jsjd:
            if retask != None:
                regular_task_list_todo_jsjd.append(retask)
        for retask in regular_task_todo_fc:
            if retask != None:
                regular_task_list_todo_fc.append(retask)
        for retask in regular_task_todo_jsjd_and_fc:
            if retask != None:
                regular_task_list_todo_jsjd_and_fc.append(retask)
    regular_task_list_todo_jsjd = regular_task_list_todo_jsjd[:3:] # 只显示3条
    regular_task_list_todo_fc = regular_task_list_todo_fc[:3:] # 只显示3条
    regular_task_list_todo_jsjd_and_fc = regular_task_list_todo_jsjd_and_fc[:3:] # 只显示3条
    # mytask_user_list = Task.objects.filter(user=user).exclude(status='completed').order_by('-id') # 获取到工作流执行的责任人
    mytask_user_list = Task.objects.filter(user=user,has_readed=0).exclude(status='completed').order_by('-id') # 获取到工作流执行的责任人
    for mytask in mytask_user_list:
        all_info_list_weidu.append(mytask)
    num1 = len(all_info_list_weidu) # num1 就是未读消息数量
    print(num1,1111111112222222222222)
# TODO:已读消息
    all_info_list_yidu = []  # 所有的已读消息
    for myplan in regular_plan_list:
        regular_task = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan,has_readed=1).order_by('-id')
        for retask in regular_task:
            if retask != None:
                all_info_list_yidu.append(retask)
    # mytask_user_list_yidu = Task.objects.filter(user=user).exclude(status='completed').order_by('-id')  # 获取到工作流执行的责任人
    mytask_user_list_yidu = Task.objects.filter(user=user, has_readed=1).exclude(status='completed').order_by('-id')  # 获取到工作流执行的责任人
    for mytask in mytask_user_list_yidu:
        all_info_list_yidu.append(mytask)
    num2 = len(all_info_list_yidu)  # num2 就是已读消息数量






    # # 分页函数  未读
    # all_info_list_weidu = list(set(all_info_list_weidu))
    # paginator = Paginator(all_info_list_weidu, 10)
    # page = request.GET.get("page")
    # print(page,1111111111111)
    # try:
    #     all_info_list_weidu = paginator.page(page)
    # except PageNotAnInteger:
    #     all_info_list_weidu = paginator.page(1)
    # except EmptyPage:
    #     all_info_list_weidu = paginator.page(paginator.num_pages)
    # # 分页函数  已读
    #     all_info_list_yidu = list(set(all_info_list_yidu))
    # paginator = Paginator(all_info_list_yidu, 10)
    # page = request.GET.get("page")
    # try:
    #     all_info_list_yidu = paginator.page(page)
    # except PageNotAnInteger:
    #     all_info_list_yidu = paginator.page(1)
    # except EmptyPage:
    #     all_info_list_yidu = paginator.page(paginator.num_pages)
    return render(request, 'user/starter.html',locals())


@csrf_exempt
def update_page(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取用户的登录信息
    user = request.session.get('mylogin')
    place = user.myuser.company



    all_info_list_weidu = []
    # mytask_user_list = Task.objects.filter(user=user, has_readed=0).exclude(status='completed').order_by('-id')  # 获取到工作流执行的责任人
    mytask_user_list = Task.objects.filter(user=user).order_by('-id')  # 获取到工作流执行的责任人
    for mytask in mytask_user_list:
        all_info_list_weidu.append(mytask)
    num1 = len(all_info_list_weidu)  # num1 就是未读消息数量

    # 分页函数  未读

    all_info_list_weidu = []
    regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1, exe_user=user.myuser, place=place).order_by(
        '-id')  # 获取执行人为当前登录用户的所有定期工作策划记录
    for myplan in regular_plan_list:
        regular_task = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan,has_readed=0).order_by('-id')
        for re in regular_task:
            all_info_list_weidu.append(re)
    all_info_list_weidu2 = list(set(all_info_list_weidu))
    all_info_list_weidu = sorted(all_info_list_weidu2,key=all_info_list_weidu.index)
    paginator = Paginator(all_info_list_weidu, 10)
    page = request.GET.get("page")
    try:
        all_info_list_weidu = paginator.page(page)
    except PageNotAnInteger:
        all_info_list_weidu = paginator.page(1)
    except EmptyPage:
        all_info_list_weidu = paginator.page(paginator.num_pages)
    data = []
    for res in all_info_list_weidu:
        print(type(res))
        data.append(res.regularwork.work_content)
    return JsonResponse({"data":data})

@csrf_exempt
def update_info2(request): # 点击定期工作任务，将对应的has——readed值改为1
    regularid = request.POST['regularid']
    regulartask = RegularWorkTask.objects.filter(id=regularid).first()
    regulartask.has_readed=1
    regulartask.save()
    return JsonResponse({'msg':'修改成功'})

@csrf_exempt
def update_info1(request): # 点击工作流程审批，将对应的has——readed值改为1
    taskid = request.POST['taskid']
    task = Task.objects.filter(id=taskid).first()
    task.has_readed=1
    task.save()
    return JsonResponse({'msg':'修改成功'})


# 查看角色
def show_role(request):
    # if request.method == "GET":
    action = request.GET.get("action")
    user_id = request.GET.get('user_id')
    roledata = []
    cursor = connection.cursor()
    # 从角色，用户及其中间表中取他们相对应的关系
    cursor.execute(
        "SELECT * FROM systemsettings_role AS a , systemsettings_myuser AS b , systemsettings_myuser_roles AS c  WHERE a.id = c.role_id AND b.id = c.myuser_id AND b.id = '%s' " % user_id)
    for row in cursor.fetchall():
        roletable = {
            'role_name': row[1]
        }
        roledata.append(roletable)
    cursor.close()
    return HttpResponse(json.dumps({"status": "ok", "data": roledata, 'action': action}),
                        content_type="application/json")


# 用户
def user_list(request):
    # 查询所有用户
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    if request.method == "GET":
        action = request.GET.get("action")
        menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    id = menuid
    company_list = Company.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    supervision_major_list = SupervisionType.objects.all()

    if request.session.get('mylogin').is_superuser == 1: # 超级管理员
        alluser = MyUser.objects.filter(is_activate=1)
        paginator = Paginator(alluser, 10)
        # 网页中的page值
        page = request.GET.get("page",'1')
        # print(sb)
        try:
            # 传递HTML当前页对象
            alluser = paginator.page(page)
        except PageNotAnInteger:
            alluser = paginator.page(1)
        except EmptyPage:
            alluser = paginator.page(paginator.num_pages)

        total_counts = MyUser.objects.filter(is_activate=1).count()
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
        return render(request, "user/user_list.html",locals())
    else: # 非超级管理员
        alluser = MyUser.objects.filter(is_activate=1,company=request.session.get('mylogin').myuser.company)
        paginator = Paginator(alluser, 10)
        # 网页中的page值
        page = request.GET.get("page",'1')
        # print(sb)
        try:
            # 传递HTML当前页对象
            alluser = paginator.page(page)
        except PageNotAnInteger:
            alluser = paginator.page(1)
        except EmptyPage:
            alluser = paginator.page(paginator.num_pages)

        total_counts = MyUser.objects.filter(is_activate=1,company=request.session.get('mylogin').myuser.company).count()
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
        return render(request, "user/user_list.html",locals())


# 搜索用户
def search_user(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    company_list = Company.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    # 获取公司，设备专业，监督专业，登录名
    company = request.GET.get('company','')
    equipment_major = request.GET.get('equipment_major','')
    supervision_major = request.GET.get('supervision_major','')
    login_user = request.GET.get('login_user','')

    if company == '':
        if equipment_major == '':
            if supervision_major == '':
                alluser = MyUser.objects.filter(Q(is_activate=1),Q(number__icontains=login_user))
            else:
                alluser = MyUser.objects.filter(Q(supervision_major_id=supervision_major),Q(is_activate=1),Q(number__icontains=login_user))

        else:
            if supervision_major == '':
                alluser = MyUser.objects.filter(Q(equipment_major_id=equipment_major),Q(is_activate=1), Q(number__icontains=login_user))
            else:
                alluser = MyUser.objects.filter(Q(equipment_major_id=equipment_major),Q(supervision_major_id=supervision_major), Q(is_activate=1),
                                                Q(number__icontains=login_user))

    else:
        if equipment_major == '':
            if supervision_major == '':
                alluser = MyUser.objects.filter(Q(company_id=company),Q(is_activate=1), Q(number__icontains=login_user))
            else:
                alluser = MyUser.objects.filter(Q(company_id=company),Q(supervision_major_id=supervision_major), Q(is_activate=1),
                                                Q(number__icontains=login_user))

        else:
            if supervision_major == '':
                alluser = MyUser.objects.filter(Q(company_id=company),Q(equipment_major_id=equipment_major), Q(is_activate=1),
                                                Q(number__icontains=login_user))
            else:
                alluser = MyUser.objects.filter(Q(company_id=company),Q(equipment_major_id=equipment_major),
                                                Q(supervision_major_id=supervision_major), Q(is_activate=1),
                                                Q(number__icontains=login_user))

    # alluser = MyUser.objects.filter(is_activate=1)

    # alluser = ''
    # print(alluser)
    paginator = Paginator(alluser, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    # print(sb)
    try:
        # 传递HTML当前页对象
        alluser = paginator.page(page)
    except PageNotAnInteger:
        alluser = paginator.page(1)
    except EmptyPage:
        alluser = paginator.page(paginator.num_pages)

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
    return render(request, "user/user_list.html", locals())


# 展示用户详情
def user_details(request, u_id):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = MyUser.objects.filter(id=u_id).first()
    return render(request, "user/user_detail.html",locals())


# 新增用户
def add_user(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    user_obj = request.session.get('mylogin')
    place = user_obj.myuser.company
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    company_list = Company.objects.all()
    equipment_major_list = EquipmentMajor.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    role_list = Role.objects.filter(is_activate=1)
    if user_obj.is_superuser:
        group_list = MyGroup.objects.all()
    else:
        group_list = MyGroup.objects.filter(place=place)
    if request.method == "GET":
        return render(request, "user/user_add.html",locals())
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.filter(username=username).first()# 先判断用户名是否有重复
        error = '账户已存在'
        if user:
            return render(request, "user/user_add.html",locals())
        else:
            is_superuser = request.POST['is_superuser']
            if is_superuser==1:
                create_user(username,is_superuser=True)# 创建并保存到数据库
            else:
                create_user(username)
            if password == '': # 如果没有输入密码,则使用默认的password
                pass
            else:# 如果输入密码
                user = User.objects.get(username=username)
                user.set_password(password)# 则将新密码设置为用户的密码
                user.save()
            name = request.POST['rel_name']  # 真实姓名
            number = username
            company = Company.objects.get(id=request.POST['company']) # 公司名称
            try:
                department = Department.objects.get(departname=request.POST['department'],company=company)  # 部门名称 departname
            except:
                department = None
            try:
                jobname = Job.objects.get(jobname=request.POST['jobname'],company=company) # 岗位名称 jobname
            except:
                jobname = None
            try:
                equipment_major = EquipmentMajor.objects.filter(id=request.POST['equipment_major']) .first()    # 设备专业
            except:
                equipment_major = None
            try:
                supervision_major = SupervisionType.objects.filter(id=request.POST['supervision_major']).first()  # 监督专业
            except:
                supervision_major = None
            # 非必填项
            headimage = request.FILES.get('headimage')   # 头像
            if headimage == None:
                headimage=''
            phone = request.POST['phone']   # 联系方式
            group = request.POST['group']   # 责任组

            # print(group)
            new_user = MyUser.objects.create(number=number, name=name, company=company, department=department,
                                             jobname=jobname, equipment_major=equipment_major,group_id=group, headimage=headimage,
                                             phone=phone, supervision_major=supervision_major, user=user)
            role_id_list = request.POST.getlist('role')
            new_user.roles.add(*role_id_list)
            new_user.save()
            return HttpResponseRedirect('/systemsettings/user_list/?action=list&menuid=39')


# excel导入用户
@csrf_exempt
def user_import_excel(request):
    from regularworktask.myviews import get_sheets_mg
    user_obj = request.session.get('mylogin')
    place = user_obj.myuser.company
    excel_file = request.FILES.get('excel_file', '')
    type_excel = excel_file.name.split('.')[1]
    if type_excel == 'xls' or type_excel == 'xlsx':
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read(), formatting_info=True)  # 打开xls文件
        # 获取表中的数据
        all_list_1 = get_sheets_mg(data, 0)
        # 向数据库写入表一数据
        i = 0
        while i < len(all_list_1):
            # User表中的username对应myuser中的number
            username = all_list_1[i][1]  # 用户名字
            number = all_list_1[i][2]   # 用户编号
            user = User.objects.filter(username=number).first()  # 判断用户编号是否重复
            MyUser_obj = MyUser.objects.filter(number=number).first()  # 判断用户编号是否重复
            if user:
                i += 1
                continue
            if MyUser_obj:
                i += 1
                continue
            else:
                is_superuser = all_list_1[i][16]
                # print(is_superuser)
                if is_superuser == 1 or is_superuser == '1':
                    create_user(number, is_superuser=True)  # 创建并保存到数据库
                else:
                    create_user(number)
                # create_user(number)
                # 如果没有输入密码,则使用默认的password
                user = User.objects.get(username=number)
                password = 'password'
                com_name=all_list_1[i][9]
                if com_name == '开封发电分公司':
                    password = 'kffdfgs'
                elif com_name == '南阳热电':
                    password = 'nyrd'
                elif com_name == '平东热电':
                    password = 'pdrd'
                elif com_name == '新乡豫新':
                    password = 'xxyy'
                elif com_name == '郑州燃气发电':
                    password = 'zzrqfd'
                user.set_password(password)  # 则将新密码设置为用户的密码
                user.save()
                name = username  # 真实姓名
                company = Company.objects.filter(comname=all_list_1[i][9]).first()# 公司名称
                try:
                    department = Department.objects.filter(departname=all_list_1[i][10],company=company).first()  # 部门名称 departname
                    if department == '':
                        department = None
                except:
                    department = None
                try:
                    jobname = Job.objects.filter(jobname=all_list_1[i][13], company=company).first()  # 岗位名称 jobname
                    if jobname == '':
                        jobname = None
                except:
                    jobname = None
                equipment_major_msg = all_list_1[i][11]
                if equipment_major_msg == '' or equipment_major_msg == None:
                    equipment_major_msg = '默认设备专业'
                try:
                    equipment_major = EquipmentMajor.objects.filter(name=equipment_major_msg).first()  # 设备专业
                except:
                    equipment_major = None
                supervision_major_msg = all_list_1[i][14]
                if supervision_major_msg == '' or supervision_major_msg == None:
                    supervision_major_msg = '默认监督专业'
                try:
                    supervision_major = SupervisionType.objects.filter(name=supervision_major_msg).first()  # 监督专业
                except:
                    equipment_major = None
                phone = all_list_1[i][3]  # 联系方式
                group_msg = all_list_1[i][12]   # 责任组
                if group_msg == '' or group_msg == None:
                    group_msg = '默认责任组'
                exe_group = MyGroup.objects.filter(name=group_msg,place=company).first()
                new_user = MyUser.objects.create(number=number, name=name, company=company, department=department,
                                                 jobname=jobname, equipment_major=equipment_major,group=exe_group,
                                                 phone=phone, supervision_major=supervision_major, user=user)
                role_id_list = str(all_list_1[i][15])
                role_id_list = role_id_list.split(',')
                new_user.roles.add(*role_id_list)
                new_user.save()
                i += 1
    else:
        err_msg = '请导入.xls或者.xlsx文件'
        # print(err_msg)
    # return redirect('systemsettings/user_list/?action=list&menuid=39')
    return HttpResponseRedirect('/systemsettings/user_list/?action=list&menuid=39')

@csrf_exempt
def check_department(request): # 用户选好公司后跳出该公司下部门
    company = Company.objects.get(id=request.POST['c_id'])
    department_list = company.department_set.all()
    job_list = company.job_set.all()
    serializers_list = serializers.serialize("json",department_list) # 字符串
    serializers_list2 = serializers.serialize("json",job_list) # 字符串
    serializers_list = eval(serializers_list) # 字符串转换为列表
    serializers_list2 = eval(serializers_list2) # 字符串转换为列表
    new_list=[] # 保存部门
    new_list2=[] # 保存岗位
    for i in range(0,len(serializers_list)):
        department=serializers_list[i]['fields']['departname']
        new_list.append(department)
    for i in range(0,len(serializers_list2)):
        job=serializers_list2[i]['fields']['jobname']
        new_list2.append(job)
    return JsonResponse({'department_list':new_list,'job_list':new_list2})



# 修改用户
def edit_user(request, u_id):
    #print("====in_edit_user")
    user_obj = request.session.get('mylogin')
    place = user_obj.myuser.company
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # user = User.objects.get(id=u_id)
    if request.method == "GET":
        myuser = MyUser.objects.get(number=u_id)
        user = User.objects.get(id=myuser.user_id)
        company_list = Company.objects.all()
        equipment_major_list = EquipmentMajor.objects.all()
        supervision_major_list = SupervisionType.objects.all()
        role_list = Role.objects.filter(is_activate=1)
        role_name_list = myuser.roles.all()  # 编辑的用户权限
        # role_id = request.GET.get('role_id')
        # roledata = []
        # cursor = connection.cursor()
        # cursor.execute(
        #     "SELECT * FROM systemsettings_role AS a , systemsettings_role_operations AS b , systemsettings_operation AS c ,systemsettings_menu AS d WHERE  d.id =c.menu_id AND  a.id = b.role_id AND c.id = b.operation_id AND a.id = '%s' " % role_id)
        # for row in cursor.fetchall():
        #     roletable = {
        #         'operation_id': row[7],
        #         'title': row[9],
        #         'menu_id': row[13],
        #         'menu_title': row[16],
        #     }
        #     roledata.append(roletable)
        # cursor.close()



        if user_obj.is_superuser:
            group_list = MyGroup.objects.all()
        else:
            group_list = MyGroup.objects.filter(place=place)
        return render(request, "user/user_edit.html",locals())
    elif request.method == "POST":
        username = request.POST.get('username','')
        name = request.POST['rel_name']  # 真实姓名
        company = Company.objects.get(id=request.POST['company'])  # 公司名称
        department = Department.objects.get(departname=request.POST['department'],company=company)  # 部门名称 departname
        # print(request.POST['jobname'],"request.POST['jobname']",company)
        # print(request.POST["password"], '==request.POST["password"]==')
        try:
            jobname = Job.objects.get(jobname=request.POST['jobname'], company=company)  # 岗位名称 jobname
        except:
            jobname = None
        equipment_major = EquipmentMajor.objects.filter(id=request.POST['equipment_major']).first()  # 设备专业
        supervision_major = SupervisionType.objects.filter(id=request.POST['supervision_major']).first()  # 监督专业
        phone = request.POST['phone']  # 联系方式
        group = request.POST['group']   # 责任组
        role_id_list = request.POST.getlist('role')
        # 修改数据
        username = request.POST["username"]
        name_list=[]
        user_list = User.objects.filter(is_active=1)
        password = request.POST["password"]
        # 如果没有输入密码,则使用默认的password
        if password == '':
            password = 'password'
        # 如果输入密码
        user_edit = User.objects.filter(username=username).first()
        # print(user_edit.myuser.name,"===print(user_edit.myuser.name)")
        user_edit.set_password(password)
        user_edit.save()
        exe_group = MyGroup.objects.filter(name=group, place=company).first()
        myuser_edit_te = MyUser.objects.filter(number=username)
        # print(myuser_edit_te,type(myuser_edit_te),"==myuser_edit_te")
        MyUser.objects.filter(number=username).update(company=company,
                                                        department=department,
                                                        jobname=jobname,
                                                        equipment_major=equipment_major,
                                                        supervision_major=supervision_major,
                                                        phone=phone,
                                                        group=exe_group,
                                                        name=name,
                                                      )
        myuser_edit = MyUser.objects.filter(number=username).first()
        #print(role_id_list)
        myuser_edit.roles.clear()
        myuser_edit.roles.add(*role_id_list)
        role_obj = myuser_edit.roles.all()
        # role_obj.delete()
        # print(role_obj,"===myuser_edit.roles_set.all()")
        # print(role_id_list,"==role_id_list")
        # print(role_obj,"====role_obj")
        myuser_edit.save()
        # print(myuser_edit,type(myuser_edit))
        # print(myuser_edit.name)


        # user_edit.myuser.company = company
        # user_edit.myuser.department = department
        # user_edit.myuser.jobname = jobname
        # user_edit.myuser.equipment_major = equipment_major
        # user_edit.myuser.supervision_major = supervision_major
        # user_edit.myuser.phone = phone
        # exe_group = MyGroup.objects.filter(name=group, place=company).first()
        # user_edit.myuser.group = exe_group
        # user_edit.myuser.name = name
        # print(role_id_list,"==role_id_list")
        # print(user_edit.myuser.roles,"===user_obj.myuser.roles")
        # user_edit.myuser.roles.add(*role_id_list)
        # # 更新数据
        # user_edit.save()
        # print(user_edit.myuser.name)
        # print(user_edit.myuser.roles.all(),"=111111111111")
        # print(user_edit,"==user_edit",type(user_edit))
        # print("===edit_done")
        return HttpResponseRedirect('/systemsettings/user_list/?action=list&menuid=39')
        # myuser = MyUser.objects.filter(number=username).first()
        #######20181121
        # return HttpResponseRedirect('/systemsettings/details/'+u_id+'/?action=detail&menuid=39')
        # else:
        #     return render(request, "user/user_edit.html",
        #                   {'pression': is_active[0][0],'action': action, 'user': user,'staff_list':staff_list,
        #                    "user_list": user_list})


# def edit_user(request, u_id):
#     action = request.GET.get("action")
#     menuid = request.GET.get("menuid")
#     power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
#     request.session['powerdata'] = power
#     print(u_id,"===u_id")
#     # user = User.objects.get(id=u_id)
#     myuser = MyUser.objects.get(id=u_id)
#     user = User.objects.get(id=myuser.user_id)
#
#     # 查询所有用户
#     user_list = User.objects.filter(is_active=1)
#     # 查找所有员工
#     staff_list = MyUser.objects.filter(is_activate=1)
#     cursor = connection.cursor()
#     # cursor.execute("SELECT is_active FROM auth_user  WHERE id = '%s'" % u_id)
#     cursor.execute("SELECT is_active FROM auth_user  WHERE id = '%s'" % myuser.user_id)
#     is_active = cursor.fetchall()
#     pression = is_active[0][0]
#     cursor.close()
#     if request.method == "GET":
#         return render(request, "user/user_edit.html",locals())
#     elif request.method == "POST":
#         # 修改数据
#         username = request.POST["username"]
#         name_list=[]
#         user_list = User.objects.filter(is_active=1)
#         for a in user_list:
#             name_list.append(a.username)
#         if username == user.username or username not in name_list :
#             staff = request.POST.getlist('staff')
#             if len(staff) == 0:
#                 pass
#             else:
#                 user.myuser.netstaff = MyUser.objects.filter(id=staff[0]).first()
#             password = request.POST["password"]
#             # 如果没有输入密码,则使用默认的password
#             if password == '':
#                 password = 'password'
#             # 如果输入密码
#             else:
#                 user = User.objects.get(username=username)
#                 user.set_password(password)
#             user.is_active = request.POST["is_active"]
#             # place = ''
#             # 获取员工信息和组织机构信息
#             # orgid =Department.objects.filter(company=None).first()
#             # orgid = orgid.departname
#             # 获取该登录人员的组织机构信息，找到其所在分公司
#             # login_user = request.session.get('mylogin')
#             # department = login_user.myuser.department
#             # department = Department.objects.filter(departname=place).first()
#             # user.myuser.department = department
#             # 更新数据
#             user.save()
#             return HttpResponseRedirect('/systemsettings/details/'+u_id+'/?action=detail&menuid=39')
#         else:
#             return render(request, "user/user_edit.html",
#                           {'pression': is_active[0][0],'action': action, 'user': user,'staff_list':staff_list,
#                            "user_list": user_list})


# 删除用户
def delete(request, u_id):
    # 从数据库中查询要删除的用户
    user = MyUser.objects.get(id=u_id)
    # 改变用户状态为不活动
    user.user.is_active = 0
    user.is_activate = 0
    # 更新到数据库
    user.user.save()
    user.save()
    return HttpResponseRedirect('/systemsettings/user_list/?action=list&menuid=39')


# 查看用户信息
def check_all_user(request):
    user_list = User.objects.filter(is_active=1)
    return render(request, "user/user_list.html",locals())

# 导出excel
def derive_excel(request, u_id):
    pass


# ------------------------角色------------------
# 展示所有角色
def role_list(request):
    # if request.method == "GET":
    action = request.GET.get("action")
    # menuid = request.GET.get("menuid")
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    all_role = Role.objects.filter(is_activate=1)
    print('11',all_role)
    paginator = Paginator(all_role, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        all_role = paginator.page(page)
    except PageNotAnInteger:
        all_role = paginator.page(1)
    except EmptyPage:
        all_role = paginator.page(paginator.num_pages)

    total_counts = Role.objects.filter(is_activate=1).count()
    #
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
    # print(page_range,'========111=====1')

    return render(request, 'user/role_list.html',locals())

def search_role(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取公司，设备专业，监督专业，登录名
    role_name = request.GET.get('role_name', '')

    # print('1111', login_user)
    all_role = Role.objects.filter(Q(name__icontains=role_name),Q(is_activate=1))

    # print(alluser)
    paginator = Paginator(all_role, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    # print(sb)
    try:
        # 传递HTML当前页对象
        all_role = paginator.page(page)
    except PageNotAnInteger:
        all_role = paginator.page(1)
    except EmptyPage:
        all_role = paginator.page(paginator.num_pages)

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
    return render(request, "user/role_list.html", locals())



# 新建角色
def new_role(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'].username, request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        mymenu_list = Menu.objects.filter(is_active=1).exclude(url="#")
        return render(request, 'user/role_add.html',locals())
    elif request.method == 'POST':  # 获取前端数据
        username = request.POST.get('username')
        is_activate = request.POST.get('is_select')
        operation_id = []
        add_list = request.POST.getlist("fetadd")
        detail_list = request.POST.getlist("fetdetail") # key为2,找到key为6和7
        for detail in detail_list:
            menu = Operation.objects.filter(id=detail).first().menu
            detail2= Operation.objects.filter(key=6,menu=menu).first()
            detail3= Operation.objects.filter(key=7,menu=menu).first()
            operation_id.append(detail2.id)
            operation_id.append(detail3.id)
        del_list = request.POST.getlist("fetdel")
        edit_list = request.POST.getlist("fetedit")
        for edit in edit_list:
            menu = Operation.objects.get(id=edit).menu
            edit= Operation.objects.get(key=4,menu=menu)
            operation_id.append(edit.id)
        for add in add_list:
            operation_id.append(add)
        for mydel in del_list:
            operation_id.append(mydel)
        repeat_username = Role.objects.filter(name=username)
        if not repeat_username:
            all_data = Role.objects.create(updated_at=datetime.now(), created_at=datetime.now(), name=username, is_activate=is_activate)
            all_data.operations.add(*operation_id)
            return HttpResponseRedirect('/systemsettings/role_list/?action=list&menuid=38')
        else:
            error = '角色已经存在'
            return HttpResponseRedirect('/systemsettings/role_add/?action=new&menuid=38')


# 编辑角色信息
def edit_role(request, rid):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == "GET":
        role_id = rid
        role = Role.objects.filter(id=rid).first()
        operation_list = Operation.objects.all()
        # 查询当前角色拥有的权限
        role_power = role.operations.all()
        power_have_list = []
        for power in role_power:
            power_have_list.append(power.id)
        cursor = connection.cursor()
        cursor.execute("SELECT is_activate FROM systemsettings_role  WHERE id = '%s'" % role_id)
        is_activate = cursor.fetchall()  # 取出此角色是否被启用
        cursor.close()
        pression = is_activate[0]
        return render(request, 'user/role_edit.html',locals())
    elif request.method == "POST":
        username = request.POST.get('name')
        is_activate = request.POST.get('is_select')
        operation_id = request.POST.getlist('operation_id')
        all_data = Role.objects.get(id=rid)
        all_data.name = username
        all_data.is_activate = is_activate
        all_data.updated_at = datetime.now()
        all_data.save()
        all_data.operations.clear()
        all_data.operations.add(*operation_id)
        return HttpResponseRedirect('/systemsettings/role_list/?action=list&menuid=38')


# 停用角色
def del_role(request,rid):
    # role_id = request.GET.get('rid')
    role = Role.objects.get(id=rid)
    role.is_activate=0
    role.save()
    return HttpResponseRedirect("/systemsettings/role_list/?action=list&menuid=38")


# 查询权限
def show_opeartion(request):
    role_id = request.GET.get('role_id')
    roledata = []
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM systemsettings_role AS a , systemsettings_role_operations AS b , systemsettings_operation AS c ,systemsettings_menu AS d WHERE  d.id =c.menu_id AND  a.id = b.role_id AND c.id = b.operation_id AND a.id = '%s' " % role_id)
    for row in cursor.fetchall():
        roletable = {
            'operation_id': row[7],
            'title': row[9],
            'menu_id': row[13],
            'menu_title': row[16],
        }
        roledata.append(roletable)
    cursor.close()
    return HttpResponse(json.dumps({"status": "ok", "data": roledata}), content_type="application/json")
@csrf_exempt
def self_detail(request,u_id):
    myuser = request.session['mylogin'].myuser
    if request.method == 'GET':
        return render(request,'user/self_detail.html')
    elif request.method=='POST':
        password = request.POST['password']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        test_password = authenticate(username=request.session['mylogin'].username, password=password)   # 验证旧帐号密码是否正确
        if test_password:
            if password1 == password2:
                msg = '添加成功！'
                # request.session['mylogin'].password=password1
                # request.session['mylogin'].save()
                user_edit = User.objects.filter(username=request.session['mylogin'].username).first()
                user_edit.set_password(password1)
                user_edit.save()
                # return render(request,'user/self_detail.html',locals())
                return redirect('/systemsettings/login/')
            else:
                msg = '两次输入密码不一致！'
                return render(request, 'user/self_detail.html', locals())
        else:
            msg = '原始密码输入错误！'
            return render(request, 'user/self_detail.html', locals())
@csrf_exempt
def check_password(request):
    num = request.POST['num']
    # print(11111,num)
    # print(make_password(num))
    # print(request.session['mylogin'].password)
    test_password = authenticate(username=request.session['mylogin'].username, password=num)  # 验证旧帐号密码是否正确
    if test_password:
        return JsonResponse({'msg':' '})
    else:
        return JsonResponse({'msg': '原始密码输入错误'})


@csrf_exempt
def check_info(request):
    user = request.session['mylogin']
    # 获取首页展示通知的内容(工作流和定期工作任务)

    # 跟具提前提醒天数通知定期任务
    future_regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1, exe_user=user.myuser, )
    regular_plan_list = RegularWorkPlan.objects.filter(is_activate=1, exe_user=user.myuser)  # 获取执行人为当前登录用户的所有定期工作策划记录

    # 符合条件的当前登录人未完成的定期工作任务通知
    regular_task_list = []
    for myplan in regular_plan_list:
        regular_task = RegularWorkTask.objects.filter(is_activate=1, result='', regularwork=myplan,tanchuang=0).first()
        if regular_task != None:
            regular_task_list.append(regular_task)
            regular_task.tanchuang=1
            regular_task.save()
    num1 = len(regular_task_list)  # 定期工作任务的数量
    mytask_user_list=[]
    mytask_user_list2 = Task.objects.filter(user=user,tanchuang=0).exclude(status='completed')  # 获取到工作流执行的责任人
    for mytask in mytask_user_list2:
        if mytask != None:
            mytask_user_list.append(mytask)
            mytask.tanchuang=1
            mytask.save()
    num2 = len(mytask_user_list)
    if num1 == 0 and num2 != 0: # 无定期工作任务,有待我审批的工作流程
        # title,url,intro
        return JsonResponse({'num': 1,'a':'我的代办','b':'http://10.69.77.153:8090/wf/todo/','c':'您有%s条工作流程待审批'%num2})
    elif num1 != 0 and num2 == 0:
        return JsonResponse({'num': 1, 'a': '我的代办', 'b': 'http://10.69.77.153:8090/regularworktask/my_list/', 'c': '您有%s条定期工作任务待完成' % num1})

    elif num1 != 0 and num2 != 0:
        return JsonResponse({'num': 2, 'a': '我的代办', 'b': 'http://10.69.77.153:8090/regularworktask/my_list/',
                      'c': '您有%s条定期工作任务待完成' % num1,'d':'我的代办','e':'http://10.69.77.153:8090/wf/todo/','f':'您有%s条工作流程待审批'%num2})
    elif num1 == 0 and num2 == 0:

        return JsonResponse({'num': 0})


"""
    组织机构
"""
from .models import TreeNode
from django.http import JsonResponse
from django.shortcuts import render


#   展示树形结构方法, get_dept_tree, show, tree
def get_dept_tree(parents):
    display_tree = []
    for data in parents:

        for p in [data]:
            node = TreeNode()
            node.expanded = False

            node.id = p.id
            node.href = str(p.id) + "/detail/"
            node.text = p.comname
            # children = p.categories.all()
            # if len(children) > 0:
            #     node.nodes = get_dept_tree(children)
            # man_id = Department.objects.filter(company_id=p.comnumber).first()
            # print()
            # man = Employee.objects.filter(job=man_id)
            # state = man.state
            # if state == 1:

            display_tree.append(node.to_dict())
    return display_tree


def show(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    print(power,"==pow")
    add_power = '0'   # 0无权限,1有权限
    del_power = '0'
    edit_power = '0'
    detail_power = '0'

    for power_msg in power:
        if power_msg['key'] == '1':
            add_power = '1'  # 添加权限
        if power_msg['key'] == '3':
            del_power = '1'  # 删除权限
        if power_msg['key'] == '5':
            edit_power = '1'  # 编辑权限
        if power_msg['key'] == '6':
            detail_power = '1'   # 详情权限


    return render(request, "organization/show_v2.html",locals())


def tree(request):
    alltree = []
    root = Company.objects.all()
    for i in root:
        alltree.append(i)

    tree = get_dept_tree(alltree)

    return JsonResponse(tree, safe=False)


# sql连接函数
def org_sql_con(sqlStr):
    cursor = connection.cursor()
    cursor.execute(sqlStr)
    company_msg = cursor.fetchall()
    cursor.close()
    return company_msg


def all_organiza(request):
    data = []
    sqlStr_company = "select * from systemsettings_company"
    company_msg = org_sql_con(sqlStr_company)
    # print(cursor.fetchall(),"=====cursor.fetchall():")
    for row in company_msg:
        # eledata = {
        #     'id':row[0],
        #     'name':row[1],
        #     'number':row[2],
        #     'type':row[3],
        #     'parent_id':row[5]
        # }
        eledata = {
            'id': row[0] + 1000,
            'name': row[2],
            'number': row[1],
            'simplename': row[3],
            'parent_id': '',
            'real_id': row[0],  # 数据库中的id
            'tree_level': 1
        }
        # print(eledata,"====eledata")
        data.append(eledata)
    sqlStr_department = "select * from systemsettings_department"
    department_msg = org_sql_con(sqlStr_department)
    for row in department_msg:
        eledata = {
            'id': row[0] + 2000,
            'name': row[2],
            'number': row[1],
            'simplename': row[3],
            'parent_id': row[4] + 1000,
            'real_id': row[0],  # 数据库中的id
            'tree_level': 2
        }
        data.append(eledata)

    # sqlStr_department = "select * from systemsettings_department"
    # department_msg = org_sql_con(sqlStr_department)
    # for row in department_msg:
    #     eledata = {
    #         'id': row[0] + 2000,
    #         'name': row[2],
    #         'number': row[1],
    #         'parent_id': row[4] + 1000,
    #         'real_id': row[0]  # 数据库中的id
    #     }
    #     print(eledata, "====eledata")
    #     data.append(eledata)

    return HttpResponse(json.dumps( {'data':data}), content_type="application/json")


# 展示一个组织机构信息
def show_one_organization(request, mid, tid):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if tid == '1':
        data = Company.objects.filter(id=mid).first()
        org_level = 1
    elif tid == '2':
        data = Department.objects.filter(id=mid).first()
        org_level = 2
    return render(request, 'organization/show_one_organization.html', {'data': data, 'action': action, 'org_level':org_level,
                                                                       'menu_list': menu_data(request.session['menu_id'])})


# 组织机构添加
def add_organization(request, mid, tid):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    org_level = tid
    if request.method == 'GET':
        if tid == '2':
            data = Company.objects.filter(id=mid).first()
            print(data)
            return render(request, 'organization/add_organization.html', {'data': data, 'action': action, 'org_level': org_level,
                                                                          'mid': mid, 'tid': tid,
                                                                 'menu_list': menu_data(request.session['menu_id'])})
        elif tid == '1':
            return render(request, 'organization/add_organization.html', {'action': action, 'org_level': org_level,
                                                                          'mid': mid, 'tid': tid,
                                                                          'menu_list': menu_data(request.session['menu_id'])})
    elif request.method == 'POST':  # 获取前端数据
        name = request.POST.get('name')
        number = request.POST.get('number')
        simplename = request.POST.get('simplename')
        if tid == '1':
            all_data = Company.objects.create(comname=name, comnumber=number, comsimplename=simplename)
        elif tid == '2':
            type = request.POST.get('type')
            all_data = Department.objects.create(departname=name, departnumber=number, company_id=type, simple_name=simplename)

        # all_data = Department.objects.create(name=name, number=number, parent_id=mid, type=type)
        all_data.save()
        return HttpResponseRedirect('/systemsettings/show_og/?action=list&menuid=56')


# 组织机构修改
def edit_organization(request, mid, tid):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    org_level = tid
    if request.method == 'GET':
        if tid == '1':
            data = Company.objects.filter(id=mid).first()
            return render(request, 'organization/edit_organization.html',
                          {'data': data, 'action': action,'org_level': org_level,'mid': mid, 'tid': tid,
                           'menu_list': menu_data(request.session['menu_id'])})
        elif tid == '2':
            data = Department.objects.filter(id=mid).first()
            return render(request, 'organization/edit_organization.html',
                          {'data': data, 'action': action,'org_level': org_level,'mid': mid, 'tid': tid,
                           'menu_list': menu_data(request.session['menu_id'])})

        # number = [[1, '总公司'], [2, '技术中心'], [3, '分公司'], [4, '部门'], [5, '班组']]
        # return render(request, 'organization/edit_organization.html', {'data': data, 'number': number, 'action': action,
        #                                                      'menu_list': menu_data(request.session['menu_id'])})
    elif request.method == 'POST':  # 获取前端数据
        name = request.POST.get('name')
        number = request.POST.get('number')
        simplename = request.POST.get('simplename')
        if tid == '1':
            all_data = Company.objects.filter(id=mid).first()
            all_data.comname = name
            all_data.comsimplename = simplename
            all_data.comnumber = number
            all_data.save()
        elif tid == '2':
            # type = request.POST.get('type')
            all_data = Department.objects.filter(id=mid).first()
            all_data.departname = name
            all_data.simple_name = simplename
            all_data.departnumber = number
            all_data.save()

        # all_data = Department.objects.create(name=name, number=number, parent_id=mid, type=type)

        return HttpResponseRedirect('/systemsettings/show_og/?action=list&menuid=56')
        # return redirect('organization:dept_show')


# 组织机构删除
def delete_origaniza(request, mid, tid):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if tid == '1':
        del_data = Company.objects.filter(id=mid).first()
        del_data2 = Department.objects.filter(company_id=del_data.id)
        del_data2.delete()
        del_data.delete()
    elif tid == '2':
        del_data = Department.objects.filter(id=mid).first()
        del_data.delete()
    return HttpResponseRedirect('/systemsettings/show_og/?action=list&menuid=56')



# 用户导入模板excel  # 已用其他方式实现暂时不使用
def download_user_mould(request):
    def file_iterator(file_name,chunk_size=512):  # 用于形成二进制数据
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = "/home/wangyifan/work_space/files/user_test.xls"   # 要下载的文件路径
    response = StreamingHttpResponse(file_iterator(the_file_name))  # 这里创建返回
    response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
    response['Content-Disposition'] = 'attachment; filename="用户导入模板.xls"'   # 注意filename 这个是下载后的名字
    return response


# 责任组列表
def duty_group_list(request):
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    id = menuid
    login_user = request.session.get('mylogin')   # 当前登录用户对象
    duty_group_list_obj = MyGroup.objects.filter(place=login_user.myuser.company)   # 获取当前登录人所属电厂的责任组对象
    paginator = Paginator(duty_group_list_obj, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    # print(sb)
    try:
        # 传递HTML当前页对象
        duty_group_list = paginator.page(page)
    except PageNotAnInteger:
        duty_group_list = paginator.page(1)
    except EmptyPage:
        duty_group_list = paginator.page(paginator.num_pages)
    total_counts = duty_group_list_obj = MyGroup.objects.filter(place=login_user.myuser.company).count()
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
    return render(request, "duty_group/duty_group_list.html", {"menuid": menuid,
                                                               "menu_this": menu_this,
                                                               "action": action,
                                                               "id": id,
                                                               "duty_group_list": duty_group_list,
                                                               "page": page,
                                                               "page_range": page_range,
                                                               "total_counts":total_counts,
                                                               "page_last":page_last,
                                                               "total_page":total_page})


def duty_group_search(request):
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    login_user = request.session.get('mylogin')   # 当前登录用户对象
    group_name = request.GET.get('group_name','')
    duty_group_list_obj = MyGroup.objects.filter(Q(name__icontains=group_name),Q(place=login_user.myuser.company))
    paginator = Paginator(duty_group_list_obj, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    # print(sb)
    try:
        # 传递HTML当前页对象
        duty_group_list = paginator.page(page)
    except PageNotAnInteger:
        duty_group_list = paginator.page(1)
    except EmptyPage:
        duty_group_list = paginator.page(paginator.num_pages)
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


    return render(request, "duty_group/duty_group_list.html",locals())





# 责任组新建
def duty_group_add(request):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    menu_this = Menu.objects.filter(number=menuid).first()
    user_obj = request.session.get('mylogin')
    place = user_obj.myuser.company
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == "GET":
        user_list = MyUser.objects.filter(company=place, is_activate=1)   # 获取当前用户所属电厂的所有人员
        return render(request, "duty_group/duty_group_add.html", {"menuid": menuid,
                                                                  "menu_this": menu_this,
                                                                  "action": action,
                                                                  "user_list": user_list})
    elif request.method == "POST":
        duty_group_name = request.POST.get("group_name","")
        duty_user_list = request.POST.getlist("user_id","")

        duty_group_obj = MyGroup.objects.create(name=duty_group_name,place=place)
        duty_group_obj.number = duty_group_obj.id
        duty_group_obj.duty_user.add(*duty_user_list)
        duty_group_obj.save()
        return HttpResponseRedirect('/systemsettings/duty_group_list/?action=list&menuid=60')



# 责任组详情
def duty_group_detail(request,group_id):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    duty_group_obj = MyGroup.objects.filter(id=group_id).first()    # 获取责任组对象
    return render(request, "duty_group/duty_group_detail.html", {"menuid": menuid,
                                                                 "menu_this": menu_this,
                                                                 "action": action,
                                                                 "duty_group_obj": duty_group_obj})

#  责任组删除
def duty_group_delete(request,group_id):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    duty_group_obj = MyGroup.objects.filter(id=group_id).first()  # 获取责任组对象
    duty_group_obj.delete()   # 删除责任组
    return HttpResponseRedirect('/systemsettings/duty_group_list/?action=list&menuid=60')


# 编辑责任组
def duty_group_edit(request,group_id):
    action = request.GET.get("action")
    menuid = request.GET.get("menuid")
    menu_this = Menu.objects.filter(number=menuid).first()
    user_obj = request.session.get('mylogin')
    power = checkpower(menuid, user_obj, request.session['role_id'])
    place = user_obj.myuser.company
    request.session['powerdata'] = power
    duty_group_obj = MyGroup.objects.filter(id=group_id).first()    # 获取责任组对象
    if request.method == "GET":
        user_list = MyUser.objects.filter(company=place, is_activate=1)  # 获取当前用户所属电厂的所有人员
        return render(request, "duty_group/duty_group_edit.html", {"menuid": menuid,
                                                                     "menu_this": menu_this,
                                                                     "action": action,
                                                                     "duty_group_obj": duty_group_obj,
                                                                     "user_list": user_list})
    elif request.method == "POST":
        duty_group_name = request.POST.get("group_name", "")
        duty_user_list = request.POST.getlist("user_id", "")

        duty_group_obj = MyGroup.objects.filter(id=group_id).first()
        duty_group_obj.name = duty_group_name
        duty_group_obj.place = place
        duty_group_obj.number = duty_group_obj.id
        duty_group_obj.duty_user.clear()
        duty_group_obj.duty_user.add(*duty_user_list)
        duty_group_obj.save()
        return HttpResponseRedirect('/systemsettings/duty_group_list/?action=list&menuid=60')




def cale(operator,x,y):
    if operator=="multiply":
        return x*y
    if operator=="divide":
        return x/y
    if operator=="add":
        return x+y
    if operator=="subtract":
        return x-y



