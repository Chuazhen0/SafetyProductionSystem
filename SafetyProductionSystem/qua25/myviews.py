from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, redirect
from datetime import datetime
from .models import Qua
from systemsettings.models import User, MyUser,Department
from mon_plan_sum.models import SupervisionType
from systemsettings.views import checkpower

from quatype.models import QuaType


# ----------------  人员资质维护 ---------  朱洪立
# 展示资质列表
def qua_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 从数据库中查询有效的数据
    qua_list=[]
    # if request.session['mylogin'].is_superuser:
    #     qua_list = Qua.objects.filter(is_activate=1)
    # else:
    qua_list = Qua.objects.filter(is_activate=1,place=request.session['mylogin'].myuser.company)

    # 总数
    total_counts = Qua.objects.filter(is_activate=1,place=request.session['mylogin'].myuser.company).count()

    # 实例化结果集, 每页10条， 少于2条合并到上一页
    paginator = Paginator(qua_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        qua_list = paginator.page(page)
    except PageNotAnInteger:
        qua_list = paginator.page(1)
    except EmptyPage:
        qua_list = paginator.page(paginator.num_pages)

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

    return render(request, 'qua/show_qua.html', locals())


# 增加资质信息
def add_qua_info(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取登录人员及公司
    user = request.session.get('mylogin')
    place = user.myuser.company

    # 设置number为在前段页面固定的
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == "GET":
        # 定义一个人员列表用来存放已被激活的用户
        data = []
        # 获取已被选用的用户
        qua_user_list = QuaType.objects.filter(is_activate=1, place=place)

        # 遍历选用的用户
        for qua in qua_user_list:
            data.append(qua)
        return render(request, 'qua/add_qua_info.html', locals())
    elif request.method == "POST":
        # 获取前端传来的数据
        name = request.POST.get('name')
        warining_time = request.POST.get('warining_time')
        qua_type_id = request.POST.get('qua_type')
        qua_type = QuaType.objects.filter(id=qua_type_id).first()

        # 保存到数据库
        qua = Qua.objects.create(
                                 place=place,
                                 number=number,
                                 name=name,
                                 qua_type=qua_type,
                                 warining_time=warining_time
                                )
        qua.save()
        return HttpResponseRedirect('/qua25/'+str(qua.id)+'/detail/?action=list&menuid=31')


# 编辑资质信息
def edit_staff(request,u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power


    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    department = user.myuser.department
    # 找到其所在分公司
    # place = check_place(department)
    place = user.myuser.company
    # 找到该登录人的组织机构所有下属机构
    # place=check_place(Department)
    orgid = Department.objects.filter(departname=department).first()
    orgid = orgid.departname
    Department_list=[]
    employee=[]
    if request.method == "GET":
        qua_user_list = QuaType.objects.filter(is_activate=1, place=place)
        # 查询资质信息
        qua = Qua.objects.filter(id=u_id).first()
        # 找到该登录人的组织机构所有下属机构
        orgid_list = Department.objects.filter(departname=department)
        # 遍历下属机构
        for org in orgid_list:
            Department_list.append(org)
            # 找出组织机构为子机构的并且非删除的所有queryset对象
            # user_list = MyUser.objects.filter(is_activate=1)
            # # 遍历每一个组织为下属机构的月度计划与总结列表
            # for user in user_list:
            #     if user.department.departname == org or user.department.departname == Department:
            #         # 加入到list中保存
            #         employee.append(user)
        Department_list.append(Department)
        return render(request, "qua/edit_qua.html", {'qua_user_list':qua_user_list,'qua': qua, 'u_id': u_id, 'employee': employee,
                                                     'Department': Department_list, 'action': action,
                                                     'menu_list': request.session['menudata']})
    elif request.method == 'POST':
        qua = Qua.objects.filter(id=u_id).first()
        # 获取数据

        # name = request.POST.get('name')
        warining_time = request.POST.get('warining_time')
        qua_type_id = request.POST.get('qua_type')
        # qua.place = request.POST["place"]
        qua.number = request.POST["number"]
        # 资质编码
        qua.name = request.POST["name"]
        # 资质名称
        qua_type_id = request.POST["qua_type"]
        qua.qua_type = QuaType.objects.filter(id=qua_type_id).first()
        # 资质类型
        qua.warining_time = request.POST["warining_time"]
        # 提前提醒天数

        qua.save()
        return HttpResponseRedirect('/qua25/' + u_id + '/detail/?action=detail&menuid=31')

# 查看资质详情
def qua_detail(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 查找对应的资质编码信息
    data = Qua.objects.filter(id=u_id).first()
    return render(request, 'qua/show_detail.html',locals())


# 删除人员
def delete_staff(request, u_id):
    qua = Qua.objects.filter(id=u_id).first()
    qua.is_activate = 0
    qua.save()
    return HttpResponseRedirect('/qua25/list/?action=list&menuid=31')



# 修改人员信息
# def edit_staff(request, u_id):
#     action = request.GET.get('action')
#     menuid = request.GET.get('menuid')
#     power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
#     request.session['powerdata'] = power
#
#     orgid = Department.objects.filter(parent=None).first()
#     orgid = orgid.name
#     # 获取员工信息和组织机构信息
#     user = request.session.get('mylogin')
#     # 获取该登录人员的组织机构信息，找到其所在分公司
#     Department = user.profile.Department
#     place=check_place(Department)
#     Department_list=[]
#     employee=[]
#     if request.method == "GET":
#         # 查询资质信息
#         qua = Qua.objects.filter(id=u_id).first()
#         # 找到该登录人的组织机构所有下属机构
#         orgid_list = Department.objects.filter(parent=Department)
#         # 遍历下属机构
#         for org in orgid_list:
#             Department_list.append(org)
#             # 找出组织机构为子机构的并且非删除的所有queryset对象
#             user_list = User.objects.filter(is_active=1)
#             # 遍历每一个组织为下属机构的月度计划与总结列表
#             for user in user_list:
#                 if user.profile.Department.name == org or user.profile.Department == Department:
#                     # 加入到list中保存
#                     employee.append(user)
#         Department_list.append(Department)
#         return render(request, "qua/edit_qua.html", {'qua': qua, 'u_id': u_id, 'employee': employee,
#                                                      'Department': Department_list, 'action': action,
#                                                      'menu_list': request.session['menudata']})
#     elif request.method == 'POST':
#         qua = Qua.objects.filter(id=u_id).first()
#         # 获取数据
#         publish_organ = request.POST["publish_organ"]
#         qua.publish_organ_id = Department.objects.filter(name=publish_organ)
#
#         qua.number = request.POST["number"]
#         qua.effect_time = request.POST["effect_time"]
#         staff = request.POST["staff"]
#         qua.staff_id = User.objects.filter(username=staff).first().profile
#
#         publish_organ = request.POST["publish_organ"]
#         qua.publish_organ_id = Department.objects.filter(name=publish_organ).first()
#         # 最后更新人
#         qua.last_updated_by = request.session.get('mylogin').profile
#         # 最后更新时间
#         qua.last_updated_at = datetime.now()
#
#         qua.save()
#         return HttpResponseRedirect('/qua25/' + u_id + '/detail/?action=detail&menuid=31')



# 查找人员
# 资质查询
def qua_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
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
    name = request.GET.get('name','')
    qua_list = Qua.objects.filter(Q(name__icontains=name),Q(place=place),Q(is_activate=1))
    # number = request.POST['number']
    # desc = request.POST['desc']
    # supervision = request.POST["supervision"]
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
    #     "SELECT id FROM quatype_quatype where number like '%%%%%s%%%%' and is_activate=1 and `desc` like '%%%%%s%%%%' and supervision_id like '%%%%%s%%%%' " % (
    #         number, desc, supervision))
    # id 列表
    # data = list(cursor.fetchall())
    # id_list = []
    # for row in data:
    #     # 将id取出，存入列表
    #     id_list.append(row[0])
    #     id_list.append(row)

    # for id in id_list:
    #     # 通过id获取到数据对象
    #     quatype_list = QuaType.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=quatype_list.orgid) in orgid_list:
    #         qua_type_list.append(quatype_list)
    # cursor.close()
    # 去重
    qua_list = list(set(qua_list))
    # 分页
    paginator = Paginator(qua_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        qua_list = paginator.page(page)
    except PageNotAnInteger:
        qua_list = paginator.page(1)
    except EmptyPage:
        qua_list = paginator.page(paginator.num_pages)
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

    return render(request, 'qua/show_qua.html',
                  {'qua_list': qua_list, 'action': action,
                   'menu_list': request.session['menudata'],'name':name,'page_range':page_range})


# -----------------资质人员添加--------------------

# def add_staff_encrypt(request):
#     action = request.GET.get('action')
#     menuid = request.GET.get('menuid')
#     power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
#     request.session['powerdata'] = power
#     # 获取员工信息和组织机构信息
#     user = request.session.get('mylogin')
#     # 获取该登录人员的组织机构信息，找到其所在分公司
#     Department = user.myuser.company
#     if request.method == 'GET':
#         QuaType = QuaType.objects.filter(is_activate=1).first()
#         return render(request, 'qua25/add_staff_encrypt.html', {QuaType: 'QuaType', 'action': action,
#                       'menu_list': request.session['menudata']})
#     elif request.method == 'POST':
#         place = Department
#         number = request.post['number']
#         name = request.post['name']
#         qua_type = QuaType.objects.filter(number=request.post['type_number']).first()
#         warining_time = request.post['warining_time']
#         qua = Qua.objects.create(place=place, number=number, name=name,
#                                  qua_type=qua_type, warining_time=warining_time)
#         qua.save()
#
#         # return redirect(reverse('qua25:detail', args=[u_id]))
#         return HttpResponseRedirect('/qua25/list/?action=list&menuid=31')


# --------------展示所有人员资质---------------
# def show_staff_encrypt(request):
#     action = request.GET.get('action')
#     menuid = request.GET.get('menuid')
#     power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
#     request.session['powerdata'] = power
#     data = Qua.objects.all()
#     return render(request, 'qua25/show_staff_encrypt.html', {data: 'data', 'action': action,
#                   'menu_list': request.session['menudata']})
