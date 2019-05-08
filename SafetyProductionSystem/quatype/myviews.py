from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, HttpResponseRedirect
from datetime import datetime
from .models import QuaType
from mon_plan_sum.models import SupervisionType
from systemsettings.views import checkpower
from systemsettings.models import Menu


# 展示资质类型列表
def qua_type_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询所有的专业
    supervision_list = SupervisionType.objects.all()
    # 从数据库中查询所有数据
    qua_type_list=[]
    # if request.session['mylogin'].is_superuser:
    #     qua_type_list = QuaType.objects.filter(is_activate=1)
    # else:
    qua_type_list = QuaType.objects.filter(is_activate=1,place = request.session['mylogin'].myuser.company)


    # 实例化结果集, 每页15条， 少于2条合并到上一页
    paginator = Paginator(qua_type_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        qua_type_list = paginator.page(page)
    except PageNotAnInteger:
        qua_type_list = paginator.page(1)
    except EmptyPage:
        qua_type_list = paginator.page(paginator.num_pages)

    # 总条数
    total_counts = QuaType.objects.filter(is_activate=1,place = request.session['mylogin'].myuser.company).count()

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

    return render(request, 'qua_type/show_quatype.html', locals())


# 添加资质类型
def qua_type_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取员工信息和公司信息
    user = request.session.get('mylogin')
    place = user.myuser.company

    # 设置number为在前段页面固定的
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == "GET":
        # 定义一个空列表用来存放被选的用户
        qua_list = []
        # 获取到被选用的用户
        qua_type = QuaType.objects.filter(is_activate=1)
        # 查询所有的专业
        supervision_list = SupervisionType.objects.all()
        # 获取创建时间
        created_at = datetime.now()

        for qua in qua_type:
            qua_list.append(qua)
        return render(request, 'qua_type/add_qua_type.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据，添加一条数据保存到数据库中

        desc = request.POST['desc']
        supervision_id = request.POST['supervision']
        supervision_data = SupervisionType.objects.filter(name=supervision_id).first()
        remark = request.POST["remark"]
        state = request.POST["state"]
        created_by = last_updated_by = user.myuser
        created_at = last_updated_at = datetime.now()

        # 保存到数据库
        qua_type = QuaType.objects.create(number=number,
                                          place=place,
                                          desc=desc,
                                          supervision=supervision_data,
                                          remark=remark,
                                          created_by=created_by,
                                          created_at=created_at,
                                          last_updated_by=last_updated_by,
                                          last_updated_at=last_updated_at,
                                          state=state,
                                          )
        qua_type.save()

        return HttpResponseRedirect('/quatype/'+str(qua_type.id)+'/detail/?action=list&menuid=30')


# 详情页
def qua_type_detail(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 查找对应的资质信息
    data = QuaType.objects.filter(id=u_id).first()
    return render(request, 'qua_type/show_detail.html',locals())


# 编辑资质
def qua_type_edit(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取要编辑资质的数据
    qua_info = QuaType.objects.filter(id=u_id).first()

    if request.method == "GET":
        # 查询所有的专业
        supervisions = SupervisionType.objects.all()

        return render(request, 'qua_type/edit_typequa.html',locals())

    elif request.method == "POST":
        # 通过id找到要修改的资质
        # 找到要修改的人员资质
        type_qua = QuaType.objects.filter(id=u_id).first()
        # 获取从前端发来的数据
        type_qua.number = request.POST["number"]
        type_qua.desc = request.POST["desc"]
        supervision = request.POST['supervision']
        type_qua.supervision_id = SupervisionType.objects.filter(name=supervision).first()

        type_qua.remark = request.POST['remark']
        # 最后更新人
        type_qua.last_updated_by = request.session['mylogin'].myuser
        # 最后更新时间
        type_qua.last_updated_at = datetime.now()
        # 文件上传
        # staff_qua.qua = request.FILES.get('qua')
        #
        # # 保存到数据库
        type_qua.save()
        return HttpResponseRedirect('/quatype/list/?action=list&menuid=30')

        # return redirect(reverse('countermeasureson25:qua_type_list'))
        # return render(request, 'qua_type/show_quatype.html', {'menu_list': request.session['menudata']})


# 删除资质类型
def qua_type_delete(request, u_id):
    # 从数据库中获取要删除的资质类型
    type_qua = QuaType.objects.filter(id=u_id).first()
    type_qua.is_activate = 0
    type_qua.save()
    return HttpResponseRedirect('/quatype/list/?action=list&menuid=30')


# 资质类型查询
def quatype_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询所有的专业
    supervision_list = SupervisionType.objects.all()
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    # Department = user.profile.Department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # qua_type_list = []
    # 获取前端传来的数据
    # number = request.POST['number']
    desc = request.GET.get('desc','')
    supervision = request.GET.get('supervision','')
    if supervision == '':
        qua_type_list = QuaType.objects.filter(Q(desc__icontains=desc),Q(place=request.session['mylogin'].myuser.company),Q(is_activate=1))
    else:
        qua_type_list = QuaType.objects.filter(Q(supervision_id=supervision),Q(desc__icontains=desc),Q(place=request.session['mylogin'].myuser.company),Q(is_activate=1))

    # if len(number) == 0:
    #     number = ''
    # elif len(desc) == 0:
    #     desc = ''
    # if len(supervision) == 0:
    #     supervision = ''
    # else:
    #     supervision_obj = SupervisionType.objects.filter(Q(supervision_major__icontains=supervision)).first()
    #     supervision = supervision_obj.id

    # if len(supervision_major) == 0:
    #     supervision_major = ''
    # else:
    #     supervision_major_obj = models.SupervisionType.objects.filter(Q(supervision_major__icontains=supervision_major)).first()
    #     supervision_major = supervision_major_obj.id
    # if len(orgid) == 0:
    #     orgid = ""
    # elif len(desc) == 0:
    #     desc = ""
    # elif len(year) == 0:
    #     year = ""
    # elif len(month) == 0:
    #     month = ""
    # elif len(state) == 0:
    #     state=''
    # cursor = connection.cursor()
    # print(orgid, supervision_major, desc, year, month)
    # cursor.execute(
    #     "SELECT id FROM quatype_quatype where number like '%%%%%s%%%%' and is_activate=1 and `desc` like '%%%%%s%%%%' and supervision_id like '%%%%%s%%%%'" % (
    #         number, desc, supervision))
    # id 列表

    # data = list(cursor.fetchall())

    # id_list = []
    # for row in data:
        # 将id取出，存入列表
    #     id_list.append(row[0])
    # #     id_list.append(row)
    # for id in id_list:
    #     # 通过id获取到数据对象
    #     quatype_list = QuaType.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=quatype_list.orgid) in orgid_list:
    #         qua_type_list.append(quatype_list)
    # cursor.close()
    # 去重
    qua_type_list = list(set(qua_type_list))

    # 分页
    paginator = Paginator(qua_type_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        qua_type_list = paginator.page(page)
    except PageNotAnInteger:
        qua_type_list = paginator.page(1)
    except EmptyPage:
        qua_type_list = paginator.page(paginator.num_pages)

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

    return render(request, 'qua_type/show_quatype.html',locals())
