from django.db.models import Q
from django.http import HttpResponseRedirect,JsonResponse,HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from . import models
from django.db import connection
from systemsettings.views import menu_data, checkpower
from systemsettings.models import Department, User,MyUser,Company, SupervisionType
from .models import StandardList, StandardDetails, StandardFill, StandardEntry


# -----------------------指标管理----------------陈桂林---------
# 展示所有指标定义的列表
def show_all_standard(request):
    data = StandardList.objects.filter(is_activate=1)
    supervise_list = SupervisionType.objects.all()
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    # 显示总数
    total_counts = StandardList.objects.filter(is_activate=1).count()

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
    return render(request, 'standard/show_all_standard.html',locals())


# 展示一个指标定义
def show_one_standard(request, sid):
    data = StandardList.objects.filter(id=sid).first()
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    return render(request, 'standard/show_one_standard.html',locals())


# 添加一个指标定义
def add_standard(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        supervise_list = SupervisionType.objects.all()
        return render(request, 'standard/add_standard.html',locals())
    if request.method == 'POST':
        number = request.POST['number']
        describe = request.POST['describe']
        supervision_type = SupervisionType.objects.filter(id=request.POST['Supervision_type']).first()
        cycle = request.POST['cycle']
        state = request.POST['state']
        all_data = StandardList.objects.create(number=number, describe=describe, cycle=cycle,
                                               Supervision_type=supervision_type, state=state)
        all_data.save()
        return HttpResponseRedirect('/standard/standard/?action=list&menuid=19')


# 编辑一个指标定义列表
def edit_standard(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        supervise_list = SupervisionType.objects.all()
        data = StandardList.objects.filter(id=sid).first()
        return render(request, 'standard/one_standard.html',locals())
    if request.method == 'POST':
        data = StandardList.objects.filter(id=sid).first()
        data.number = request.POST['number']
        data.describe = request.POST['describe']
        data.Supervision_type = SupervisionType.objects.filter(id=request.POST['Supervision_type']).first()
        data.cycle = request.POST['cycle']
        data.state = request.POST['state']
        data.save()
        return HttpResponseRedirect('/standard/standard/?action=list&menuid=19')


# 删除一个指标定义列表
def del_standard(request, sid):
    data = StandardList.objects.filter(id=sid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/standard/standard/?action=list&menuid=19')


# -------------指标定义详情--------------
# 指标定义详情
def show_standard_details(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = StandardDetails.objects.filter(maintenance_staff=sid, is_activate=1)
    supervise_list = SupervisionType.objects.all()
    return render(request, 'standard/show_standard_details.html',locals())


# 展示一个指标定义详情
def show_one_stand_details(request, did, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = StandardDetails.objects.filter(id=did).first()
    return render(request, 'standard/show_one_stand_details.html',locals())


# 添加指标定义详情
def add_stand_details(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        standard = StandardList.objects.filter(id=sid).first()
        user = None
        user_data = request.session.get('mylogin')
        # 获取该登录人的组织机构
        Department = user_data.Department
        # 找到其所在分公司
        place = Department.type
        # 找到该登录人的组织机构所有下属机构
        if place == 1 or place == 2:
            user = User.objects.filter(is_active=1)
        elif place == 3:
            user = User.objects.filter(Department=Department.id)
        return render(request, 'standard/add_stand_details.html',locals())
    if request.method == 'POST':
        definition = StandardList.objects.filter(id=sid).first()
        standard_name = request.POST['standard_name']
        sis_text = request.POST['sis_text']
        maintenance_staff = User.objects.filter(id=request.POST['maintenance_staff']).first()
        standard_value = request.POST['standard_value']
        upper_limit_value = request.POST['upper_limit_value']
        lower_limit_value = request.POST['lower_limit_value']
        all_data = StandardDetails.objects.create(definition=definition, standard_name=standard_name,
                                                  sis_text=sis_text, maintenance_staff=maintenance_staff,
                                                  standard_value=standard_value, upper_limit_value=upper_limit_value,
                                                  lower_limit_value=lower_limit_value)
        all_data.save()
        return HttpResponseRedirect('/standard/%s/standard_one_detail/?action=list&menuid=20' % sid)


# 修改指标定义详情
def edit_stand_details(request, did, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        data = StandardDetails.objects.filter(id=did).first()
        user = None
        user_data = request.session.get('mylogin')
        # 获取该登录人的组织机构
        Department = user_data.Department
        # 找到其所在分公司
        place = Department.type
        # 找到该登录人的组织机构所有下属机构
        if place == 1 or place == 2:
            user = User.objects.filter(is_active=1)
        elif place == 3:
            user = User.objects.filter(Department=Department.id)
        return render(request, 'standard/one_stand_details.html',locals())
    if request.method == 'POST':
        all_data = StandardDetails.objects.filter(id=did).first()
        all_data.definition = StandardList.objects.filter(id=sid).first()
        all_data.standard_name = request.POST['standard_name']
        all_data.sis_text = request.POST['sis_text']
        all_data.maintenance_staff = User.objects.filter(id=request.POST['maintenance_staff']).first()
        all_data.standard_value = request.POST['standard_value']
        all_data.upper_limit_value = request.POST['upper_limit_value']
        all_data.lower_limit_value = request.POST['lower_limit_value']
        all_data.save()
        return HttpResponseRedirect('/standard/%s/standard_one_detail/?action=list&menuid=20' % sid)


# 删除一个指标定义详情
def del_stand_details(request, did, sid):
    details = StandardDetails.objects.filter(id=did).first()
    details.is_activate = 0
    details.save()
    return HttpResponseRedirect('/standard/%s/standard_one_detail/?action=list&menuid=20' % sid)


# -----------------指标填报-------------陈桂林----------
# 展示指标填报
def show_all_standardfill(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    supervise_list = SupervisionType.objects.all()
    # 获取登录人信息
    user = request.session.get('mylogin')
    data = StandardFill.objects.filter(is_activate=1,place=str(user.myuser.company))
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    # 总条数
    total_counts = models.StandardFill.objects.filter(is_activate=1,place=str(user.myuser.company)).count()
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

    return render(request, 'standard_fill/show_all_standardfill.html',locals())


# 新建指标填报
def add_standardfill(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    if request.method == 'GET':
        place = Company.objects.all()
        supervise_list = SupervisionType.objects.all()
        definition = StandardList.objects.filter(is_activate=1)
        return render(request, 'standard_fill/add_standardfill.html',locals())
    if request.method == 'POST':
        number = request.POST['number']
        describe = request.POST['describe']
        supervision_type = SupervisionType.objects.filter(id=request.POST['Supervision_type']).first()
        definition = StandardList.objects.filter(id=request.POST['definition']).first()
        fill_time = request.POST['fill_time']
        # place = request.POST['place']
        place = str(user.myuser.company)
        # print('22222',type(place),place)
        all_data = StandardFill.objects.create(number=number, describe=describe, Supervision_type=supervision_type,
                                               definition=definition, fill_time=fill_time, place=place)
        all_data.save()
        return HttpResponseRedirect('/standard/standard_fill/?action=list&menuid=21')


#根据监督类型，选择测点类型
def change_station(request):
    super_version = request.GET['super_version']
    definition = StandardList.objects.filter(is_activate=1,Supervision_type_id=super_version)
    list_version = []
    for i in range(len(definition)):
        list_version.append({"id":definition[i].id,
                             "number":definition[i].number,
                              "describe":definition[i].describe})


    return JsonResponse({"dict_version":list_version,'length':len(list_version)})


# 编辑指标填报信息
def edit_standardfill(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        data = StandardFill.objects.filter(id=sid).first()
        supervise_list = SupervisionType.objects.all()
        definition = StandardList.objects.filter(is_activate=1)
        return render(request, 'standard_fill/edit_standardfill.html',locals())
    if request.method == 'POST':
        all_data = StandardFill.objects.filter(id=sid).first()
        all_data.number = request.POST['number']
        all_data.describe = request.POST['describe']
        all_data.supervision_type = SupervisionType.objects.filter(id=request.POST['Supervision_type']).first()
        all_data.definition = StandardList.objects.filter(id=request.POST['definition']).first()
        all_data.fill_time = request.POST['fill_time']
        all_data.save()
        return HttpResponseRedirect('/standard/standard_fill/?action=list&menuid=21')


# 删除指标填报
def del_standardfill(request, sid):
    data = StandardFill.objects.filter(id=sid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/standard/standard_fill/?action=list&menuid=21')


# 搜索指标定义列表
@csrf_exempt
def standard_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    supervise_list = SupervisionType.objects.all()

    Supervision_type = request.GET.get('Supervision_type','')
    describe = request.GET.get('describe','')
    if Supervision_type == '':
        standardfill_list = models.StandardList.objects.filter(Q(describe__icontains=describe),Q(is_activate=1))
    else:
        standardfill_list = models.StandardList.objects.filter(Q(Supervision_type_id=Supervision_type),
                                                               Q(describe__icontains=describe),Q(is_activate=1))

    data = list(set(standardfill_list))
    # 分页
    paginator = Paginator(data, 10)
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

    return render(request, 'standard/show_all_standard.html',locals())

# 搜索测点填报列表
@csrf_exempt
def standardfill_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    # Department = request.session.get('Department')
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # standardfill_list = []
    # 获取前端传来的数据
    supervise_list = SupervisionType.objects.all()
    # number = request.POST['number']
    # place = request.POST['place']
    Supervision_type = request.GET.get('Supervision_type','')
    describe = request.GET.get('describe','')
    if Supervision_type == '':
        standardfill_list = models.StandardFill.objects.filter(Q(describe__icontains=describe),Q(place=str(user.myuser.company)),Q(is_activate=1))
    else:
        standardfill_list = models.StandardFill.objects.filter(Q(Supervision_type_id=Supervision_type),Q(describe__icontains=describe),Q(place=str(user.myuser.company)),Q(is_activate=1))

    # state = request.POST['state']
    # if len(number) == 0:
    #     number = ''
    # if len(place) == 0:
    #     place = ""
    # elif len(describe) == 0:
    #     describe = ""
    # elif len(state) == 0:
    #     state = ""
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM standard_standardfill where number like '%%%%%s%%%%' and place like '%%%%%s%%%%' and is_activate=1 and `describe` like '%%%%%s%%%%' and `state` like '%%%%%s%%%%' " % (
    #         number, place, describe, state))
    # id 列表
    # data = list(cursor.fetchall())
    # id_list = []
    # for row in data:
        # 将id取出，存入列表
        # id_list.append(row[0])
    #     id_list.append(row)

    # for id in id_list:
        # 通过id获取到数据对象
        # standardfill_plan = models.StandardFill.objects.get(id=id)
        # if standardfill_plan.type == Department.name:
        # standardfill_list.append(standardfill_plan)
        # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    # cursor.close()


    # 去重
    data = list(set(standardfill_list))
    # 分页
    paginator = Paginator(data, 10)
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

    return render(request, 'standard_fill/show_all_standardfill.html',locals())


# ----------------测点填报详情-------------陈桂林-------------
# 展示测点填报详情列表
def show_all_standardfill_details(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    standardfill = StandardFill.objects.filter(id=sid).first()
    standardfill_details = StandardEntry.objects.filter(standard_fill=sid, is_activate=1)
    # 总条数
    # total_counts = models.StandardFill.objects.filter(is_activate=1).count()
    return render(request, 'standard_fill/show_all_standardfill_details.html',locals())


# 新建测点填报详细信息
def add_standardfill_details(request, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user_data = request.session.get('mylogin')
    if request.method == 'GET':
        place = Company.objects.all()
        # 找到其所在分公司
        # 找到该登录人的组织机构所有下属机构
        user = User.objects.filter(is_active=1)
        standard_fill = StandardFill.objects.filter(id=sid).first()
        return render(request, 'standard_fill/add_standardfill_details.html',locals())
    if request.method == 'POST':
        name = request.POST['name']
        sis_text = request.POST['sis_text']
        maintenance_staff = MyUser.objects.filter(id=request.POST['maintenance_staff']).first()
        last_updated_by = user_data.myuser
        measured_value = request.POST['measured_value']
        sis_modify = request.POST['sis_modify']
        standard_value = request.POST['standard_value']
        upper_limit_value = request.POST['upper_limit_value']
        lower_limit_value = request.POST['lower_limit_value']
        standard_fill = StandardFill.objects.filter(id=request.POST['standard_fill']).first()
        all_data = StandardEntry.objects.create(name=name, sis_text=sis_text, maintenance_staff=maintenance_staff,
                                                last_updated_by=last_updated_by, measured_value=measured_value,
                                                sis_modify=sis_modify, standard_value=standard_value,
                                                standard_fill=standard_fill,
                                                upper_limit_value=upper_limit_value,
                                                lower_limit_value=lower_limit_value)
        all_data.save()
        return HttpResponseRedirect('/standard/%s/standard_detail_fill/?action=list&menuid=22' % sid)


# 查看一个测点填报详情
def show_one_standardfill_details(request, did, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = StandardEntry.objects.filter(id=did).first()
    return render(request, 'standard_fill/show_one_standfill_details.html',locals())


# 编辑一个测点填报详情
def edit_standardfill_details(request, did, sid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == 'GET':
        data = StandardEntry.objects.filter(id=did).first()
        user = None
        user_data = request.session.get('mylogin')
        # 获取该登录人的组织机构
        Department = user_data.Department
        # 找到其所在分公司
        place = Department.type
        # 找到该登录人的组织机构所有下属机构
        if place == 1 or place == 2:
            user = User.objects.filter(is_active=1)
        elif place == 3:
            user = User.objects.filter(Department=Department.id)
        return render(request, 'standard_fill/edit_one_standardfill_details.html',locals())
    if request.method == 'POST':
        all_data = StandardEntry.objects.filter(id=did).first()
        all_data.name = request.POST['name']
        all_data.sis_text = request.POST['sis_text']
        all_data.maintenance_staff = User.objects.filter(id=request.POST['maintenance_staff']).first()
        all_data.last_updated_by = request.session.get('mylogin')
        all_data.measured_value = request.POST['measured_value']
        all_data.sis_modify = request.POST['sis_modify']
        all_data.standard_value = request.POST['standard_value']
        all_data.upper_limit_value = request.POST['upper_limit_value']
        all_data.lower_limit_value = request.POST['lower_limit_value']
        all_data.save()
        return HttpResponseRedirect('/standard/%s/standard_detail_fill/?action=list&menuid=22' % sid)


# 删除一个测点填报详情
def del_standardfill_details(request, did, sid):
    data = StandardEntry.objects.filter(id=did).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/standard/%s/standard_detail_fill/?action=list&menuid=22' % sid)

