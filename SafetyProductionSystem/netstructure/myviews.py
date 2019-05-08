from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from .models import NetStructure
from systemsettings.views import menu_data, checkpower
from datetime import datetime
from django.db import connection
from django.urls import reverse

from systemsettings.models import MyUser,Company
from datetime import datetime
from netstaff.models import NetStaff
import xlrd
from systemsettings.models import Menu
from django.db.models import Q


# Create your views here.
# --------------------------------- 技术监督——监督网络管理---朱洪立 ------------------------------
# 1. 网络结构
# 展示网络结构列表
def show_structure_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    menu_this = Menu.objects.filter(number=menuid).first()
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')
    company_list = Company.objects.filter()

    # 获取该登录人员的组织机构信息，找到其所在分公司
    place = user.myuser.company

    # 从数据库中获取所有数据
    structure_list =[]
    if user.is_superuser:
        structure_list = NetStructure.objects.filter(is_activate=1)
        #  总共显示多少条
        total_counts = NetStructure.objects.filter(is_activate=1).count()
    else:
        structure_list = NetStructure.objects.filter(is_activate=1, place=place)
        total_counts = NetStructure.objects.filter(is_activate=1, place=place).count()



    # 实例化结果集, 每页10条， 少于2条合并到上一页
    paginator = Paginator(structure_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        structure_list = paginator.page(page)
    except PageNotAnInteger:
        structure_list = paginator.page(1)
    except EmptyPage:
        structure_list = paginator.page(paginator.num_pages)


    page_last = (int(page) - 1) * 10
    # 总页数
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

    return render(request, 'net_structure/show_net_structure.html',locals())


# 查看网络结构详情
def structure_detail(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 查询网络机构的基本信息
    structure = NetStructure.objects.get(id=u_id)
    data_netstaff = NetStaff.objects.filter(netstructure_id=u_id)   # 查询监督网络下的人员网络信息
    # 分别获取生技部主任，监督专责，执行人下的人员
    person_list = []  # 监督网络下的人员列表
    # print(data_netstaff,"=========data_netstaff==========")
    for msg in data_netstaff:
        msg_person_list = msg.user.all()
        for person_obj in msg_person_list:
            person_dic = {"number": person_obj.number, "name": person_obj.name, "jobname": person_obj.jobname, "department": person_obj.department}
            if person_dic in person_list:
                pass
            else:
                person_list.append(person_dic)



    # if data_netstaff.user.exists():
    #     data = data_netstaff.user.all()
    # else:
    #     data = ''

    return render(request, "net_structure/structure_detail.html",locals())


# 新建网络结构
def new_structure(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')

    # 获取该登录人员的组织机构信息，找到其所在分公司
    place = user.myuser.company
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == 'GET':
        # 查找所有职员
        user_all = MyUser.objects.filter(company=place)
        # 查询所有网络
        structure_list = NetStructure.objects.filter(place=place, is_activate=1)
        now_time = datetime.now()
        place = place.comsimplename
        return render(request, 'net_structure/add_structure.html', locals())
    elif request.method == 'POST':
        desc = request.POST["desc"]
        classify = request.POST["classify"]
        created_by_id = request.session.get('mylogin')
        created_by = created_by_id.myuser
        created_at = datetime.now()
        last_updated_by_id = request.session.get('mylogin')
        last_updated_by = last_updated_by_id.myuser
        last_updated_at = datetime.now()
        parent_id = request.POST['structure_list_id']
        level = request.POST['level']
        state = '拟定'
        # 判断网络结构的父级网络
        if parent_id == 'null':
            structure = NetStructure.objects.create(place=place, level=level,
                                                    number=number, desc=desc,
                                                    classify=classify,
                                                    state=state, created_at=created_at,
                                                    last_updated_at=last_updated_at,
                                                    created_by=created_by,
                                                    last_updated_by=last_updated_by)
            # 保存数据
            structure.save()
            return HttpResponseRedirect('/netstructure/'+str(structure.id)+'/detail/?action=list&menuid=3')
        else:
            # 把数据存入到数据库
            structure = NetStructure.objects.create(place=place, level=level,
                                                    number=number, desc=desc,
                                                    classify=classify,
                                                    state=state, created_at=created_at,
                                                    created_by=created_by, parent_id=parent_id,
                                                    last_updated_at=last_updated_at,
                                                    last_updated_by=last_updated_by
                                                    )
            # 保存数据
            structure.save()
            return HttpResponseRedirect('/netstructure/'+str(structure.id)+'/detail/?action=list&menuid=3')


# 网络结构导入excel文件
@csrf_exempt
def structure_import_excel(request):
    from regularworktask.myviews import get_sheets_mg
    from systemsettings.models import Company
    user_obj = request.session.get('mylogin')
    excel_file = request.FILES.get('excel_file', '')
    type_excel = excel_file.name.split('.')[1]
    if type_excel == 'xls' or type_excel == 'xlsx':
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read(), formatting_info=True)  # 打开xls文件
        # 获取表中的数据
        all_list_1 = get_sheets_mg(data, 0)
        # 向数据库写入表一数据
        i = 0
        while i < len(all_list_1):
            number = all_list_1[i][2]   # 编号
            number_check = NetStructure.objects.filter(number=number).first()
            if number_check:
                i += 1
                continue
            desc = all_list_1[i][3]   # 描述
            classify = all_list_1[i][4]    # 监督类别
            created_by_id = request.session.get('mylogin')
            created_by = created_by_id.myuser
            created_at = datetime.now()
            last_updated_by_id = request.session.get('mylogin')
            last_updated_by = last_updated_by_id.myuser
            last_updated_at = datetime.now()
            # parent_id = all_list_1[i][13]   # 父级id
            parent_num = all_list_1[i][14]   # 父级编号
            level = all_list_1[i][10]    # 等级
            state = all_list_1[i][5]   # 状态
            place_name = all_list_1[i][16]
            place = Company.objects.filter(comname=place_name).first()
            # 判断网络结构的父级网络
            # print(level,'=level',place,"==place",number,"==number", desc,"==desc", classify,"==classify",state,"==state",
            #       created_at,"==created_at",last_updated_at,"==last_updated_at", created_by,"==created_by",last_updated_by,"==last_updated_by")
            if parent_num == None or parent_num == '':
                structure = NetStructure.objects.create(place=place, level=level,
                                                        number=number, desc=desc,
                                                        classify=classify,
                                                        state=state, created_at=created_at,
                                                        last_updated_at=last_updated_at,
                                                        created_by=created_by,
                                                        last_updated_by=last_updated_by)
                # 保存数据
                structure.save()
            else:
                parent_id = NetStructure.objects.filter(number=parent_num).first()
                # 把数据存入到数据库
                structure = NetStructure.objects.create(place=place, level=level,
                                                        number=number, desc=desc,
                                                        classify=classify,
                                                        state=state, created_at=created_at,
                                                        created_by=created_by, parent_id=parent_id,
                                                        last_updated_at=last_updated_at,
                                                        last_updated_by=last_updated_by
                                                        )
                # 保存数据
                structure.save()
            i += 1
    else:
        err_msg = '请导入.xls或者.xlsx文件'
        # print(err_msg)
    return HttpResponseRedirect('/netstructure/list/?action=list&menuid=3')


# 编辑网络结构
def edit_structure(request, u_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取员工信息和组织机构信息
    user = request.session.get('mylogin')

    # 获取该登录人员的组织机构信息，找到其所在分公司
    place = user.myuser.company
    if request.method == "GET":
        structure_list = NetStructure.objects.filter(place=place,is_activate=1)
        date = NetStructure.objects.get(id=u_id)

        return render(request, "net_structure/edit_structure.html", locals())
    elif request.method == "POST":
        structure = NetStructure.objects.filter(id=u_id).first()
        # 获取前端发来的数据
        structure.number = request.POST["number"]
        structure.desc = request.POST["desc"]
        structure.classify = request.POST["classify"]
        # 父级网络
        structure.parent_id = request.POST["structure_list"]
        # 最后更新时间
        structure.last_updated_at = datetime.now()
        # 最后更新人
        # structure.last_updated_by = request.session.get('mylogin').profile
        structure.last_updated_by = request.session.get('mylogin').myuser

        # 更新到数据库
        structure.save()

        return HttpResponseRedirect('/netstructure/list/?action=list&menuid=3')


# 删除网络结构
def delete_structure(request, u_id, m_id):
    # 从数据库中获取要删除的网络监督结构
    structure = NetStructure.objects.filter(id=u_id).first()
    structure.is_activate = 0
    structure.save()
    if m_id == '2':
        return HttpResponseRedirect('/netstaff/list/?action=list&menuid=4')
    else:
        return HttpResponseRedirect('/netstructure/list/?action=list&menuid=3')

#  查询网络结构
@csrf_exempt
def netstructure_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    company_list = Company.objects.filter()

    # 获取该登录人的组织机构
    # Department = user.profile.Department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # 获取前端传来的数据
    # number = request.POST['number']
    company = request.GET.get('company','')
    desc = request.GET.get('desc','')
    classify = request.GET.get('classify','')
    if company == '':
        if classify == '':
            structure_list = NetStructure.objects.filter(Q(desc__icontains=desc),Q(is_activate=1))
        else:
            structure_list = NetStructure.objects.filter(Q(classify=classify),Q(desc__icontains=desc),Q(is_activate=1))
    else:
        if classify == '':
            structure_list = NetStructure.objects.filter(Q(place_id=company),Q(desc__icontains=desc), Q(is_activate=1))
        else:
            structure_list = NetStructure.objects.filter(Q(place_id=company),Q(classify=classify), Q(desc__icontains=desc),
                                                         Q(is_activate=1))

    # if len(number) == 0:
    #     number = ''
    # elif len(desc) == 0:
    #     desc = ''
    # elif len(classify) == 0:
    #     classify = ''
    # cursor = connection.cursor()
    # # print(orgid, supervision_major, desc, year, month)
    # cursor.execute(
    #     "SELECT id FROM netstructure_netstructure where number like '%%%%%s%%%%' and is_activate=1 and `desc` like '%%%%%s%%%%' and `classify`like '%%%%%s%%%%' " % (
    #         number, desc, classify))
    # id 列表
    # data = list(cursor.fetchall())
    # id_list = []
    # for row in data:
    #     # 将id取出，存入列表
    #     id_list.append(row[0])
    # #     id_list.append(row)
    #
    # for id in id_list:
    #     # 通过id获取到数据对象
    #     netstructure_list = NetStructure.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=netstructure_list.orgid) in orgid_list:
    #         structure_list.append(netstructure_list)
    # cursor.close()
    # 去重
    structure_list = list(set(structure_list))
    # 分页
    paginator = Paginator(structure_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        structure_list = paginator.page(page)
    except PageNotAnInteger:
        structure_list = paginator.page(1)
    except EmptyPage:
        structure_list = paginator.page(paginator.num_pages)

    page_last = (int(page) - 1) * 10
    total_page = paginator.num_pages
    if total_page > 5:
        print("大于大于大于大于大于大于大于555555555555555555555555555555555555555555555555555555555555555555555555")
        if page != '':
            page = int(page)
            if page < 5:
                page_range = list(range(1, 6))
            elif page >= 5:
                page_range = list(range(page - 4, page + 1))
    else:
        page_range = list(range(1, total_page + 1))
        print("小于小于小于小于小于小于小于555555555555555555555555555555555555555555555555555555555555555555555555")



    return render(request, 'net_structure/show_net_structure.html',locals())


# 网络结构导入模板excel
def download_net_mould(request):
    def file_iterator(file_name,chunk_size=512):  # 用于形成二进制数据
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = "/home/wangyifan/work_space/files/net_test.xls"   # 要下载的文件路径
    response = StreamingHttpResponse(file_iterator(the_file_name))  # 这里创建返回
    response['Content-Type'] = 'application/vnd.ms-excel'  # 注意格式
    response['Content-Disposition'] = 'attachment; filename="网络结构导入模板.xls"'   # 注意filename 这个是下载后的名字
    return response