from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import NetStructure
from systemsettings.views import menu_data, checkpower, MyUser
from datetime import datetime
from django.db import connection

from systemsettings.models import MyUser, Department
from netstaff.models import NetStaff

import json
# Create your views here.
# 展示网络结构
def show_structure(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    # 获取该登录人员的组织机构信息，找到其所在分公司
    place = user.myuser.company
    list1 = []
    list2 = []
    list3 = []
    data_list = []
    data1_list = []
    data2_list = []
    data3_list = []
    data4_list = []
    num_list = []
    # 从数据库中获取所有数据
    structure_list = NetStructure.objects.filter(is_activate=1,place=place)   # 获取所有网络结构信息
    # print('1111111111',structure_list)

    structure_list1 = NetStructure.objects.filter(is_activate=1,place=place)    # 获取当前电厂的所有网络结构信息
    netstaff_list = NetStaff.objects.filter(is_activate=1)    # 获取所有的网络人员
    a = 100000
    b = 200000
    for structre in structure_list:
        pid = structre.parent_id   # 获取当前监督网络的上级监督网络id
        if pid is not None:
            pid = structre.parent_id   # 如果上级监督网络存在，起始id等于上级监督网络的id
        else:
            pid = 0   # 起始id=0
        data = {
            'id': structre.id,
            'name': structre.desc,
            'pid': pid,
        }
        data_list.append(data)

        for user_data in netstaff_list:
            name = ''
            if structre.id == user_data.netstructure_id:
                if user_data.net_name == 1:
                    name = '生技部主任'
                elif user_data.net_name == 2:
                    name = '监督专责'
                elif user_data.net_name == 3:
                    name = '执行人'
                # 职位
                data1 = {
                    'id': a,
                    'name': name,
                    'pid': structre.id,
                }
                data_list.append(data1)
                #demo_list = NetStaff.objects.filter(netstructure_id=user_data.netstructure_id)   # 获取相应的人员表，以此获取相应的用户
                if netstaff_list.exists():

                    userlist = user_data.user.all()
                    for user in userlist:
                        data3 = {
                            'id': b,
                            'name': user.name,
                            'pid': a,
                        }
                        data_list.append(data3)

                        b += 1
                a += 1





    # # 实例化结果集, 每页10条， 少于2条合并到上一页
    # paginator = Paginator(netstaff_list, 10)
    # # 网页中的page值
    # page = request.GET.get("page")
    # try:
    #     # 传递HTML当前页对象
    #     structure_list = paginator.page(page)
    # except PageNotAnInteger:
    #     structure_list = paginator.page(1)
    # except EmptyPage:
    #     structure_list = paginator.page(paginator.num_pages)
    return render(request, 'net_staff/show_structure.html', {'netstaff_list': netstaff_list, 'action': action,
                                                             'structure_list1': structure_list1, 'data1_list': data1_list,
                                                             'list1': list1, 'list2': list2,
                                                             'data_list': json.dumps(data_list),
                                                             'list3': list3, 'num_list': num_list,
                                                             'menu_list': request.session['menudata']})


# 查看网络机构人员信息
def net_staff(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询某个结构详情
    staff_info = NetStaff.objects.filter(netstructure=u_id)
    staff_list = NetStaff.objects.all()
    # 实例化结果集, 每页10条， 少于2条合并到上一页
    paginator = Paginator(staff_list, 10)
    # 网页中的page值
    page = request.GET.get("page")
    try:
        # 传递HTML当前页对象
        staff_list = paginator.page(page)
    except PageNotAnInteger:
        staff_list = paginator.page(1)
    except EmptyPage:
        staff_list = paginator.page(paginator.num_pages)
    # 查询所有的网络机构
    return render(request, "net_staff/net_staff_info.html",locals())


# 新增网络机构人员
def add_staff(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    # 获取该登录人员的组织机构信息，找到其所在分公司
    company = user.myuser.company
    if request.method == "GET":
        # 展示可增加的员工， 查询员工表
        user = MyUser.objects.filter(company=company,is_activate=1)
        # if company.comname == '河南公司本部':
        #     data = NetStructure.objects.all()
        # else:
        data = NetStructure.objects.filter(place=company, is_activate=1)
        depart = Department.objects.filter(company=company)

        return render(request, "net_staff/add_net_staff.html",locals())

    elif request.method == "POST":
        # 联系方式
        phone = request.POST["phone"]
        # 部门
        department = Department.objects.filter(id=request.POST.get("department_data")).first()
        # 岗位
        net_name = request.POST.get("net_name")
        # 所属监督网络
        NetStructure_data = NetStructure.objects.filter(id=request.POST.get("netstructure_data")).first()
        # 对应人员
        user_data_list = request.POST.getlist('user_id')
        # print(user_data_list,"---------------------------1")

        # 创建人
        created_by = last_updated_by = user.myuser
        # 创建时间
        created_at = datetime.now()
        # 最后更新时间
        last_updated_at = datetime.now()
        # print('post')

        # 判断当前岗位下是否已经有了人员
        netstaff_list = NetStaff.objects.filter(is_activate=1,netstructure_id=NetStructure_data.id)  # 获取所有的网络人员
        job_flag = 0  # 0:岗位下没有人员;1:岗位下有人员
        job_name_list = []  # 工作岗位列表
        for netstaff_obj in netstaff_list:
            job_name_list.append(netstaff_obj.net_name)
            if int(net_name) == netstaff_obj.net_name:   # 该岗位下已经有人员
                netstaff_id = netstaff_obj.id
        if int(net_name) in job_name_list:
            job_flag = 1
        else:
            job_flag = 0


        # 如果有，在现有岗位下更新用户
        if job_flag == 1:
            # 获得对应的网络人员表对象
            netstaff_obj = NetStaff.objects.filter(is_activate=1, id=netstaff_id).first()  # 获取所有的网络人员
            netstaff_obj.user.clear()

        # 如果没有，新建对应岗位下的用户
        if job_flag == 0:
            # 保存数据库
            netstaff_obj = NetStaff.objects.create(place=company, phone=phone,
                                                net_name=net_name, department=department,
                                                netstructure=NetStructure_data,
                                                created_by=created_by, created_at=created_at,
                                                last_updated_by=last_updated_by, last_updated_at=last_updated_at
                                                )

        netstaff_obj.user.add(*user_data_list)
        # 保存数据库
        netstaff_obj.save()
        #  return redirect(reverse('supervision:net_staff', args=[u_id, action, menuid]))
        return HttpResponseRedirect('/netstaff/list/?action=list&menuid=4')


# 编辑网络机构人员
def edit_net_staff(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    if request.method == "GET":
        # 查询当前网络机构人员
        staff = User.objects.filter(id=u_id).first()

        return render(request, 'net_staff/edit_net_staff.html',locals())
    elif request.method == 'POST':
        # 查找要修改的人员
        staff = NetStaff.objects.filter(id=u_id).first()
        # 从前端获取数据
        staff.number = request.POST["number"]
        staff.desc = request.POST["desc"]
        staff.phone = request.POST["phone"]
        staff.department = request.POST["department"]
        staff.net_name = request.POST["net_name"]
        # 最后更新时间
        staff.last_updated_at = datetime.now()

        # 最后更新人
        staff.last_updated_by = request.session.get('mylogin')

        # 保存到数据库
        staff.save()
        return HttpResponseRedirect('/netstaff/list/?action=list&menuid=19')


# 删除网络机构人员
def delete_staff(request, u_id):
    # 获取当前网络结构的ID
    # 先找到要删除的员工， 通过员工找到它关联的网络结构
    staff = NetStaff.objects.filter(id=u_id)
    structure_id = ''
    for structure in staff:
        structure_id = structure.netstructure_id
    # 从数据库中查询要删除的网络人员
    net_staff = NetStaff.objects.filter(id=u_id).first()
    net_staff.is_activate = 0
    net_staff.save()
    return HttpResponseRedirect('/netstaff/list/?action=list&menuid=19')


#  查询网络结构
@csrf_exempt
def structure_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    Department = user.profile.Department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    orgid_list = Department.objects.filter(parent=Department)
    orgid_list = list(orgid_list)
    orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    structure_list = []
    # 获取前端传来的数据
    number = request.POST['number']
    desc = request.POST['desc']
    classify = request.POST['classify']

    if len(number) == 0:
        number = ''
    elif len(desc) == 0:
        desc = ''
    elif len(classify) == 0:
        classify = ''

    cursor = connection.cursor()
    # print(orgid, supervision_major, desc, year, month)
    cursor.execute(
        "SELECT id FROM netstructure_netstructure where number like '%%%%%s%%%%' and is_activate=1 and `desc` like '%%%%%s%%%%' and `classify`like '%%%%%s%%%%' " % (
            number, desc, classify))
    # id 列表
    data = list(cursor.fetchall())
    id_list = []
    for row in data:
        # 将id取出，存入列表
        id_list.append(row[0])
    #     id_list.append(row)

    for id in id_list:
        # 通过id获取到数据对象
        netstructure_list = NetStructure.objects.get(id=id)
        # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
        if Department.objects.get(name=netstructure_list.orgid) in orgid_list:
            structure_list.append(netstructure_list)
    cursor.close()
    # 去重
    structure_list = list(set(structure_list))
    # 分页
    paginator = Paginator(structure_list, 10)
    # 网页中的page值
    page = request.GET.get("page")
    try:
        # 传递HTML当前页对象
        structure_list = paginator.page(page)
    except PageNotAnInteger:
        structure_list = paginator.page(1)
    except EmptyPage:
        structure_list = paginator.page(paginator.num_pages)
    return render(request, 'net_staff/show_structure.html',locals())