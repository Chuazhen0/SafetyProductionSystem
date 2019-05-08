from django.http import HttpResponseRedirect,FileResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import WarningNotice, WarningResource
from django.db import connection
from systemsettings.views import checkpower
from systemsettings.models import Department, User, MyUser, KKS
import os
from django.utils.http import urlquote

from systemsettings.models import SupervisionType, Company
from problemlog.models import Problemlog
from django.contrib import messages
from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance

# 上传文件
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
    home = 'media/' + request.GET.get('data') # 获取文件数据库路径
    file = open(home, 'rb')  # 写入文件
    response = FileResponse(file)  # 返回response对象
    response['Content-Type'] = 'application/octet-stream'  # 定义response对象返回类型
    home_cut = str(home).split('/')[-1]  # 定义文件名称和格式
    response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(home_cut))  # 把文件名称写入response对象
    return response


# 新建告警管理
def add_warningnotice(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取员工信息和公司信息
    user = request.session.get('mylogin')
    place = user.myuser.company

    # 设置number为在前段页面固定的 公司名称+时间戳
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == 'GET':
        supervision_major_list = SupervisionType.objects.all()
        resource = WarningResource.objects.all()
        exetuct_user = MyUser.objects.filter(is_activate=1, company=place)
        kks = KKS.objects.filter(place=place)
        problem = Problemlog.objects.filter(place=place)
        return render(request, 'warningnotice/add_warningnotice.html',locals())
    elif request.method == 'POST':
        # 创建一个告警通知单
        resource_id = request.POST.get('resource')
        resource_data = WarningResource.objects.filter(id=resource_id).first()
        created_at = last_updated_at = datetime.now()
        title = request.POST.get('title')
        supervise_id = request.POST.get('supervise_major')
        supervise_data = SupervisionType.objects.get(id=supervise_id)
        abnormal = request.POST.get('abnormal')
        result = request.POST.get('result')
        suggest = request.POST.get('suggest')
        time_require = request.POST.get('time_require')
        equipment_id = request.POST.get('equipment')
        equipment_data = KKS.objects.filter(id=equipment_id).first()
        problem_id = request.POST.get('problem')
        problem_data = Problemlog.objects.filter(id=problem_id).first()
        exetuct_user = request.POST.get('exetuct_user')
        exetuct_data = MyUser.objects.filter(id=exetuct_user).first()
        enclosure = request.FILES.get('enclosure')
        num = request.POST['num2']
        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
        if problem_data != None:
            all_data = WarningNotice.objects.create(place=place,
                                                    state='拟定',
                                                    number=number,
                                                    resource=resource_data,
                                                    enclosure=enclosure,
                                                    title=title,
                                                    supervise_major=supervise_data,
                                                    exetuct_user=exetuct_data,
                                                    abnormal=abnormal,
                                                    result=result,
                                                    suggest=suggest,
                                                    time_require=time_require,
                                                    last_updated_at=last_updated_at,
                                                    equipment=equipment_data,
                                                    problem=problem_data
                                                    )
            all_data.save()
        else:
            all_data = WarningNotice.objects.create(place=place,
                                                    state='拟定',
                                                    number=number,
                                                    resource=resource_data,
                                                    enclosure=enclosure,
                                                    title=title,
                                                    supervise_major=supervise_data,
                                                    exetuct_user=exetuct_data,
                                                    abnormal=abnormal,
                                                    result=result,
                                                    suggest=suggest,
                                                    time_require=time_require,
                                                    last_updated_at=last_updated_at,
                                                    equipment=equipment_data,
                                                    )
            all_data.save()

        all_data.created_by = request.user
        my_process = MyProcess.objects.filter(app_name='告警通知', supervision_major=all_data.supervise_major,
                                              is_activate=1, company=place).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='告警通知', is_activate=1, company=place).first()
            if my_process == None:
                messages.info(request, 'Success %s: %s,%s' % ('保存', all_data, '暂无匹配的工作流程,请先去配置流程后再提交！'))
                return HttpResponseRedirect(
                    '/warning/' + str(all_data.id) + '/detail/?action=detail&menuid=13')
        process = my_process.process
        all_data.created_by = request.session['mylogin']
        all_data.save()
        if num == '1':
            all_data.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", all_data))
            return HttpResponseRedirect(
                '/warning/' + str(all_data.id) + '/detail2/?action=detail&menuid=13')
        elif num == '2':
            all_data.create_pinstance(process=process, submit=True)
            all_data.created_by = request.user
            all_data.save()
            new_processinstance = all_data.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', all_data))

            return HttpResponseRedirect(
                '/warning/' + str(all_data.id) + '/detail/?action=detail&menuid=13&pinstance_id=' + str(
                    new_processinstance.id))



# 展示一个告警详细信息
def show_one_warningnotice(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    data = WarningNotice.objects.filter(id=wid).first()
    try:
        file_name = data.enclosure.name.split('/')[1]
    except:
        file_name = ''
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = data.pinstance
    if processinstance != None:
        return render(request, 'warningnotice/show_one_warningnotice.html', locals())
    else:
        return render(request, 'warningnotice/show_one_warningnotice2.html', locals())




# 搜索告警管理
@csrf_exempt
def warning_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get("mylogin")
    place = user.myuser.company
    warning_list = []
    exetuct_user = MyUser.objects.filter(is_activate=1, company=place)
    supervision_major_list = SupervisionType.objects.all()
    resource = WarningResource.objects.all()

    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的所属公司
    # company_list = Company.objects.filter(comname=company).first()
    # company_list = list(company_list)
    # 定义空的列表，用于保存筛选好的数据
    warning_list = []
    # 获取前端传来的数据
    execute_user = request.GET.get('execute_user','')
    Supervision_type= request.GET.get('Supervision_type','')
    resourc = request.GET.get('resource','')
    data_warn = ''
    # print('111',execute_user)
    # print('222',Supervision_type)
    # print('333',resource)
    if execute_user == '':
        if Supervision_type == '':
            if resourc == '':
                data_warn = WarningNotice.objects.filter(is_activate=1,place=place)
            else:
                data_warn = WarningNotice.objects.filter(resource_id=resourc,is_activate=1,place=place)
        else:
            if resourc == '':
                data_warn = WarningNotice.objects.filter(supervise_major_id=Supervision_type,is_activate=1, place=place)
            else:
                data_warn = WarningNotice.objects.filter(supervise_major_id=Supervision_type,resource_id=resourc, is_activate=1, place=place)

    else:
        if Supervision_type == '':
            if resourc == '':
                data_warn = WarningNotice.objects.filter(exetuct_user_id=execute_user,is_activate=1, place=place)
            else:
                data_warn = WarningNotice.objects.filter(exetuct_user_id=execute_user,resource_id=resourc, is_activate=1, place=place)
        else:
            if resourc == '':
                data_warn = WarningNotice.objects.filter(exetuct_user_id=execute_user,supervise_major_id=Supervision_type, is_activate=1,
                                                         place=place)
            else:
                data_warn = WarningNotice.objects.filter(exetuct_user_id=execute_user,supervise_major_id=Supervision_type, resource_id=resourc,
                                                         is_activate=1, place=place)

    # data = WarningNotice.objects.filter(is_activate=1)
    # user = MyUser.objects.filter(name=user).first().id
    # place = request.POST['place']
    # place = SupervisionType.objects.filter(name=place).first().id
    # resource = request.POST['resource']
    # resource= WarningResource.objects.filter(name=resource).first().id
    # time_require = request.POST['time_require']
    # result = request.POST['result']
    # if len(number) == 0:
    #     number = ''
    # if len(place) == 0:
    #     place = ""
    # elif len(title) == 0:
    #     title = ""
    # elif len(time_require) == 0:
    #     time_require = ""
    # elif len(result) == 0:
    #     result = ""
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM warning_warningnotice where place like '%%%%%s%%%%' and number like '%%%%%s%%%%' and is_activate=1 and title like '%%%%%s%%%%' and time_require like '%%%%%s%%%%' and result like '%%%%%s%%%%' " % (
    #         place, number, title, time_require, result))
    # cursor.execute(
    #     "SELECT id FROM warning_warningnotice where exetuct_user_id=%s and supervise_major_id=%s and is_activate=1 and resource_id=%s" % (
    #         user, place,resource))
    # id 列表
    # data = list(cursor.fetchall())
    # print(data)
    # id_list = []
    # for row in data:
    #     # 将id取出，存入列表
    #     id_list.append(row[0])
    #
    # for id in id_list:
    #     # 通过id获取到数据对象
    #     warningnotice_plan = WarningNotice.objects.get(id=id)
    #     print(warningnotice_plan.place.comname)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Company.objects.get(comname=warningnotice_plan.place.comname) in company_list:
    #         warning_list.append(warningnotice_plan)
    # cursor.close()
    # 去重
    data = list(set(data_warn))
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
    return render(request, 'warningnotice/show_warningnotice.html',locals())


# 告警通知展示列表
def show_warningnotice(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取员工信息和公司
    user = request.session.get("mylogin")
    place = user.myuser.company
    warning_list = []
    exetuct_user = MyUser.objects.filter(is_activate=1, company=place)
    supervision_major_list = SupervisionType.objects.all()
    resource = WarningResource.objects.all()

    # if user.is_superuser:
    # 获取该登录人员所属公司
    #     warning_list = WarningNotice.objects.filter(is_activate=1)
    # else:
    warning_list = WarningNotice.objects.filter(is_activate=1, place=place).order_by('-id')

    # 总条数
    total_counts = WarningNotice.objects.filter(is_activate=1).count()

    # 分页展示列表列表
    paginator = Paginator(warning_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        warning_list = paginator.page(page)
    except PageNotAnInteger:
        warning_list = paginator.page(1)
    except EmptyPage:
        warning_list = paginator.page(paginator.num_pages)

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
    return render(request, 'warningnotice/show_warningnotice.html',
                  {'data': warning_list,'action':action,'menuid':menuid,'place':place,'exetuct_user':exetuct_user,
                   'supervision_major_list':supervision_major_list,'resource':resource,'page_range':page_range,'total_counts':total_counts,'page_last':page_last,'total_page':total_page})


# 编辑一个告警管理信息
@csrf_exempt
def one_warningnotice(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取员工信息和公司信息
    user = request.session.get('mylogin')
    place = user.myuser.company

    # 设置number为在前段页面固定的 公司名称+时间戳
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == 'GET':
        supervision_major_list = SupervisionType.objects.all()
        resource = WarningResource.objects.all()
        exetuct_user = MyUser.objects.filter(is_activate=1, company=place)
        kks = KKS.objects.filter(place=place)
        problem = Problemlog.objects.filter(place=place)
        data = WarningNotice.objects.filter(id=wid).first()
        return render(request, 'warningnotice/one_warningnotice.html',locals())
    elif request.method == 'POST':
        # 创建一个告警通知单
        resource_id = request.POST.get('resource')
        resource_data = WarningResource.objects.filter(id=resource_id).first()
        created_at = last_updated_at = datetime.now()
        title = request.POST.get('title')
        supervise_id = request.POST.get('supervise_major')
        supervise_data = SupervisionType.objects.get(id=supervise_id)
        abnormal = request.POST.get('abnormal')
        result = request.POST.get('result')
        suggest = request.POST.get('suggest')
        time_require = request.POST.get('time_require')
        equipment_id = request.POST.get('equipment')
        equipment_data = KKS.objects.filter(id=equipment_id).first()
        problem_id = request.POST.get('problem')
        problem_data = Problemlog.objects.filter(id=problem_id).first()
        exetuct_user = request.POST.get('exetuct_user')
        exetuct_data = MyUser.objects.filter(id=exetuct_user).first()
        num = request.POST['num2']
        warning_obj = WarningNotice.objects.filter(id=wid).first()
        if problem_data != None:
            warning_obj.place=place
            warning_obj.state='拟定'
            warning_obj.number=number
            warning_obj.resource=resource_data
            warning_obj.title=title
            warning_obj.supervise_major=supervise_data
            warning_obj.exetuct_user=exetuct_data
            warning_obj.abnormal=abnormal
            warning_obj.result=result
            warning_obj.suggest=suggest
            warning_obj.time_require=time_require
            warning_obj.last_updated_at=last_updated_at
            warning_obj.equipment=equipment_data
            warning_obj.problem=problem_data
            warning_obj.save()
        else:
            warning_obj.place = place
            warning_obj.state = '拟定'
            warning_obj.number = number
            warning_obj.resource = resource_data
            warning_obj.title = title
            warning_obj.supervise_major = supervise_data
            warning_obj.exetuct_user = exetuct_data
            warning_obj.abnormal = abnormal
            warning_obj.result = result
            warning_obj.suggest = suggest
            warning_obj.time_require = time_require
            warning_obj.last_updated_at = last_updated_at
            warning_obj.equipment = equipment_data
            warning_obj.save()
        return HttpResponseRedirect('/warning/list/?action=list&menuid=13')


# 删除告警管理
def del_warningnotice(request, wid):
    data = WarningNotice.objects.filter(id=wid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/warning/list/?action=list&menuid=13')