from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.shortcuts import render, HttpResponseRedirect
from systemsettings.models import User,MyUser,Company,Department,SupervisionType
from .models import WeekWorkPlan
from systemsettings.views import checkpower
from django.db.models import Q
from datetime import datetime
import os
from django.http import FileResponse
def handle_uploaded_file(f):
    baseDir = os.path.dirname(os.path.abspath(__name__))  # 获取运行路径
    jpgdir = os.path.join(baseDir, 'static')  # 加上static路径
    filename = os.path.join(jpgdir, f.name)
    fobj = open(filename, 'wb+')  # 打开上传文件
    for x in f.chunks():
        fobj.write(x)  # request.FILES,文件专用
    fobj.close()


# 下载附件
def down_file(request):
    home = 'media/' + request.GET.get('data')  # 获取文件数据库路径
    file = open(home, 'rb')  # 写入文件
    response = FileResponse(file)  # 返回response对象
    response['Content-Type'] = 'application/octet-stream'  # 定义response对象返回类型
    home_cut = str(home).split('/')[-1]  # 定义文件名称和格式
    response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(home_cut))  # 把文件名称写入response对象
    return response


#  ——————————— 周期检测 ——————————— 陈桂林

# 查询周期检测计划
@csrf_exempt
def periodic_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    place = Company.objects.filter(comname=place).first().id
    supervision_major_list = SupervisionType.objects.all()
    # print("place",place)
    data_user = MyUser.objects.filter(company=place)
    # 获取该登录人的组织机构
    # Department = request.session.get('Department')
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # periodic_list = []
    # 获取前端传来的数据
    planner = request.GET.get('planner','')
    execute_user = request.GET.get('execute_user','')
    content = request.GET.get('content','')
    supervision_major = request.GET.get('supervision_major','')
    # print('qqq',execute_user)
    # print('qqq',content)
    if supervision_major == '':
        if planner == '':
            if execute_user =='':
                periodic_list = WeekWorkPlan.objects.filter(Q(is_activate=1),Q(place_id=place),Q(plan__icontains=content))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(execute_user_id=execute_user),Q(is_activate=1), Q(place_id=place),Q(plan__icontains=content))
        else:
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(planner_id=planner),Q(is_activate=1), Q(place_id=place), Q(plan__icontains=content))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(planner_id=planner),Q(execute_user_id=execute_user), Q(is_activate=1),
                                                            Q(place_id=place), Q(plan__icontains=content))

    else:
        if planner == '':
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(is_activate=1), Q(place_id=place),
                                                            Q(plan__icontains=content))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(execute_user_id=execute_user), Q(is_activate=1),
                                                            Q(place_id=place), Q(plan__icontains=content))
        else:
            if execute_user == '':
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(planner_id=planner), Q(is_activate=1), Q(place_id=place),
                                                            Q(plan__icontains=content))
            else:
                periodic_list = WeekWorkPlan.objects.filter(Q(supervision_major_id=supervision_major),Q(planner_id=planner), Q(execute_user_id=execute_user),
                                                            Q(is_activate=1),
                                                            Q(place_id=place), Q(plan__icontains=content))

    # periodic_list = WeekWorkPlan.objects.filter(Q(planner_id=planner),Q(execute_user_id=execute_user),Q(is_activate=1),Q(place_id=place))

    # print(periodic_list)
    # orgid = request.POST['orgid']
    # number = request.POST['number']
    # plan = request.POST['plan']
    # time_limit = request.POST['time_limit']
    # plan_time = request.POST['plan_time']
    # if len(number) == 0:
    #     number = ''
    # if len(orgid) == 0:
    #     orgid = ""
    # elif len(plan) == 0:
    #     plan = ""
    # elif len(time_limit) == 0:
    #     time_limit = ""
    # elif len(plan_time) == 0:
    #     plan_time = ""
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM weekworkplan_weekworkplan where orgid like '%%%%%s%%%%' and number like '%%%%%s%%%%' and is_activate=1 and plan like '%%%%%s%%%%' and time_limit like '%%%%%s%%%%' and plan_time like '%%%%%s%%%%' " % (
    #         orgid, number, plan, time_limit, plan_time))
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
    #     periodic_rece_plan = WeekWorkPlan.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=periodic_rece_plan.orgid) in orgid_list:
    #         periodic_list.append(periodic_rece_plan)
    # cursor.close()
    # 去重
    data = list(set(periodic_list))
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

    return render(request, 'week_work_plan/show_periodic_list.html',locals())


# # 展示周期检测计划列表
def show_periodic_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    data_user = MyUser.objects.filter(company=place)
    supervision_major_list = SupervisionType.objects.all()
    weekworkplan_list = []
    # if user.is_superuser:
    data_list = WeekWorkPlan.objects.filter(is_activate=1,place=place).order_by('-created_at')  # 最新添加内容靠前显示
    # print(data_list)
    # for d in data_list:
    #     weekworkplan_list.append(d)
    # # else:
    # #     data_list = WeekWorkPlan.objects.filter(is_activate=1, place=place)
    # #     for d in data_list:
    # #         weekworkplan_list.append(d)
    # weekworkplan_list=list(set(weekworkplan_list))
    # print(weekworkplan_list)
    weekworkplan_list = data_list
    paginator = Paginator(weekworkplan_list, 15)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        weekworkplan_list = paginator.page(page)
    except PageNotAnInteger:
        weekworkplan_list = paginator.page(1)
    except EmptyPage:
        weekworkplan_list = paginator.page(paginator.num_pages)

    # 总数
    total_counts = WeekWorkPlan.objects.filter(is_activate=1,place=place).count()
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

    return render(request, 'week_work_plan/show_periodic_list.html',
                  {'data': weekworkplan_list, 'action': action,'data_user':data_user,'page_range':page_range,
                   'supervision_major_list':supervision_major_list,'total_counts':total_counts,'page_last':page_last,'total_page':total_page})
# 'page_last':page_last,'total_page':total_page,'total_counts':total_counts


# 展示一个周期检测计划
def show_one_periodic(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = WeekWorkPlan.objects.filter(id=wid).first()
    try:
        file_name = data.enclosure.name.split('/')[1]
    except:
        file_name = ''
    # home = data.enclosure
    # home_cut = str(home).split('/')[-1]
    return render(request, 'week_work_plan/show_one_periodic.html', locals())


# 添加周期检测计划
def add_periodic_plan(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    if request.method == 'GET':
        data_user = MyUser.objects.filter(company=place)
        supervision_major_list = SupervisionType.objects.all()
        return render(request, 'week_work_plan/add_periodic_plan.html',
                      {'data': data_user,
                        'place': place, 'action': action,'supervision_major_list':supervision_major_list})
    elif request.method == 'POST':
        created_by = last_updated_by = request.session.get('mylogin').myuser
        created_at = last_updated_at = datetime.now()
        number = place.comsimplename + datetime.now().strftime("%Y%m%d")
        plan = request.POST.get('plan')
        third_org = request.POST.get('third_org')
        rate_desc = request.POST.get('rate_desc')
        rate_code = request.POST.get('rate_code')
        time_limit = request.POST.get('time_limit')
        state = '拟定'
        planner = user.myuser
        plan_time = request.POST.get('plan_time')
        supervision_major = request.POST.get('supervision_major')
        execute_user = MyUser.objects.get(id=request.POST.get('execute_user'))
        enclosure = request.FILES.get('enclosure')
        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
        # 获取上传的文件
        # handle_uploaded_file(enclosure)
        all_data = WeekWorkPlan.objects.create(place=place, state=state,rate_code=rate_code,
                                               number=number, created_by=created_by, created_at=created_at,
                                               last_updated_by=last_updated_by, last_updated_at=last_updated_at,
                                               plan=plan, third_org=third_org, rate_desc=rate_desc,
                                               time_limit=time_limit, execute_user=execute_user,
                                               planner=planner, enclosure=enclosure,
                                               plan_time=plan_time,supervision_major_id=supervision_major)
        all_data.save()
        return HttpResponseRedirect('/weekworkplan/'+str(all_data.id)+'/detail/?action=detail&menuid=34')


# 修改一个周期检测计划
def edit_periodic_plan(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company

    if request.method == 'GET':
        data_plan = WeekWorkPlan.objects.get(id=wid)
        # data_sup = User.objects.all()
        data = MyUser.objects.filter(company=place)
        return render(request, 'week_work_plan/edit_periodic_plan.html',locals())
    elif request.method == 'POST':
        all_data = WeekWorkPlan.objects.get(id=wid)

        all_data.plan = request.POST.get('plan')
        all_data.third_org = request.POST.get('third_org')
        all_data.time_limit = request.POST.get('time_limit')
        all_data.plan_time = request.POST.get('plan_time')
        all_data.execute_user = MyUser.objects.get(id=request.POST.get('execute_user'))

        all_data.save()
        return HttpResponseRedirect('/weekworkplan/list/?action=list&menuid=34')


# 删除周期检测计划
def del_periodic(request, wid):
    data = WeekWorkPlan.objects.filter(id=wid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/weekworkplan/list/?action=list&menuid=34')