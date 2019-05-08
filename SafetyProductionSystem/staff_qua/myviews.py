from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from .models import StaffQua
from systemsettings.views import  checkpower
from datetime import datetime
from django.db import connection
from django.urls import reverse
from systemsettings.models import Company
from netstaff.models import NetStaff

from systemsettings.models import MyUser, SupervisionType, Department
from staff_qua.models import StaffQua
from qua25.models import Qua
# Create your views here.
# 展示员工， 可以通过员工管理资质
def show_employee(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询所有员工
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    # 获取该登录人员的组织机构信息，找到其所在分公司
    company = user.myuser.company
    employee = MyUser.objects.filter(company=company)
    if request.POST:
        user_id = request.POST.get("user_id")
        if user_id:
            employee = MyUser.objects.filter(company=company,id=user_id)
    return render(request, 'staffqua/show_employee.html',locals())


# 查看人员的资质
def show_staff_qua_datail(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    staff_list = StaffQua.objects.filter(user_id=u_id)
    # print(staff_list[0].qua_enclosure.url)
    data = MyUser.objects.filter(id=u_id, is_activate=1).first()

    return render(request, 'staffqua/staff_qua.html',locals())


# 添加人员资质
def add_staff_qua(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    data = MyUser.objects.filter(id=u_id).first()
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')

    # 获取该登录人员的组织机构信息，找到其所在分公司
    company = user.myuser.company
    if request.method == "GET":
        qua_data = Qua.objects.all()
        majordata = SupervisionType.objects.all()
        power_plan = Company.objects.all()

        return render(request, 'staffqua/add_staff_qua.html', locals())
    elif request.method == "POST":
        # 获取从前端发来的数据
        number = request.POST["number"]
        effect_time = request.POST["effect_time"]
        qua_id = request.POST["qua"]
        # print("===in1")
        qua = Qua.objects.filter(id=qua_id).first()
        supervision_major_id = request.POST["supervision_major"]
        supervision_major = SupervisionType.objects.filter(id=supervision_major_id).first()
        publisher_id = request.POST["publisher"]
        publisher = Department.objects.filter(id=2).first()
        # 20190320修改 model中新增company字段保存前端传过来的公司id，Department这个字段暂时设置默认值
        qua_file = request.FILES.get('qua_file')
        if qua_file is not None:
            qua_file.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(qua_file.name)
        # 创建时间
        created_at = datetime.now()
        # 最后更新人
        created_by = last_updated_by = user.myuser
        # 最后更新时间
        last_updated_at = datetime.now()

        # 保存到数据库
        staff_qua = StaffQua.objects.create(qua=qua, created_by=created_by, user=data,
                                            created_at=created_at, last_updated_by=last_updated_by,
                                            last_updated_at=last_updated_at, publisher=publisher,
                                            place=company, supervision_major=supervision_major,
                                            number=number, effect_time=effect_time,
                                            qua_enclosure=qua_file,company_id=1)
        staff_qua.save()

        # return redirect(reverse('staff_qua:show_staff_qua', args=[u_id, menuid, action]))
        # return HttpResponseRedirect('/staffqua/show_staff_qua/?action=list&menuid=5')
        # return redirect(reverse('staff_qua:show_staff_qua', args=[user_info.staff_id]))


        # return HttpResponseRedirect('/staff_qua/list/?action=list&menuid=5')
        return redirect(reverse('staff_qua:show_staff_qua_datail', args=[u_id]))
        # return render(request, 'staffqua/staff_qua.html',{staff_list:'staff_list',data:'data'})


# 编辑人员的资质
def edit_staff_qua(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    qua_info = StaffQua.objects.filter(id=u_id).first()
    if request.method == "GET":
        # 查找要编辑的信息
        # company = Company.objects.all()
        # department = Department.objects.all()
        majordata = SupervisionType.objects.all()
        power_plan = Company.objects.all()
        return render(request, 'staffqua/edit_staff_qua.html',locals())

    elif request.method == "POST":
        # 通过id找到要修改的资质
        # 找到要修改的人员资质
        staff_qua = StaffQua.objects.filter(id=u_id).first()
        # 获取从前端发来的数据
        staff_qua.supervision_major_id = request.POST.get("supervision_major")
        # ----------  获取组织名称 ---------------
        # company = request.POST["publisher"]
        # publisher_id = request.POST["publisher"]
        # publisher = Department.objects.filter(id=publisher_id).first()
        # ----------  在组织表中查找它的组织ID ------------ （组织与人员资质是外键关系）
        # staff_qua.publisher = Company.objects.filter(name=company).first()
        # staff_qua.publisher = Department.objects.filter(id=publisher_id).first()

        # staff_qua.number = request.POST["number"]
        staff_qua.effect_time = request.POST["effect_time"]
        # 最后更新人
        staff_qua.last_updated_by = request.session.get('mylogin').myuser
        # 最后更新时间
        staff_qua.last_updated_at = datetime.now()
        # 文件上传
        # staff_qua.qua = request.FILES.get('qua')
        #
        # # 保存到数据库
        staff_qua.save()
        action = "list"
        # return HttpResponseRedirect('/staff_qua/list/?action=list&menuid=5')
        return redirect(reverse('staff_qua:show_staff_qua_datail', args=[qua_info.user_id]))


# 人员资质删除
def delete_staff_qua(request, u_id):
    qua_info = StaffQua.objects.filter(id=u_id).first()
    # 从数据库中获取要删除的人员资质
    staff_qua = StaffQua.objects.filter(id=u_id).first()
    staff_qua.is_activate = 0
    # 假删除，改变表中is_active的值
    staff_qua.save()
    # return HttpResponseRedirect('/staffqua/show_staff_qua/?action=list&menuid=5')
    return redirect(reverse('staff_qua:show_staff_qua_datail', args=[qua_info.user_id]))


# 查询人员资质
# 20190326修改怎加人员资质查询.在列表展示中实现这个功能
def staff_qua_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询所有员工
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    # 获取该登录人员的组织机构信息，找到其所在分公司
    company = user.myuser.company
    employee = MyUser.objects.filter(company=company)
    if request.POST:
        user_id = request.POST.get("user_id")
        if user_id:
            employee = MyUser.objects.filter(company=company, id=user_id)
    return render(request, 'staffqua/show_employee.html', locals())


    #
    # orgid_list = company.objects.filter(parent=company)
    # orgid_list = list(orgid_list)
    # orgid_list.append(company)
    # # 定义空的列表，用于保存筛选好的数据
    # staff_qua = []
    # # 获取前端传来的数据
    # number = request.POST['number']
    # qua_type = request.POST['qua_type']
    #
    # if len(number) == 0:
    #     number = ''
    # elif len(qua_type) == 0:
    #     qua_type = ''
    #
    # cursor = connection.cursor()
    # # print(orgid, supervision_major, desc, year, month)
    # cursor.execute(
    #     "SELECT id FROM staff_qua_netstaffqua where number like '%%%%%s%%%%' and is_activate=1 and `qua_type` like '%%%%%s%%%%'" % (
    #         number, qua_type))
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
    #     netstaffqua_list = NetStaffQua.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if company.objects.get(name=netstaffqua_list.orgid) in orgid_list:
    #         staff_qua.append(netstaffqua_list)
    # cursor.close()
    # # 去重
    # staff_qua = list(set(staff_qua))
    # # 分页
    # paginator = Paginator(staff_qua, 10)
    # # 网页中的page值
    # page = request.GET.get("page")
    # try:
    #     # 传递HTML当前页对象
    #     staff_qua = paginator.page(page)
    # except PageNotAnInteger:
    #     staff_qua = paginator.page(1)
    # except EmptyPage:
    #     staff_qua = paginator.page(paginator.num_pages)
    # return render(request, 'staffqua/staff_qua.html',locals())