from django.http import HttpResponseRedirect,FileResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from systemsettings.views import checkpower
from warning.models import WarningNotice
import os
from django.utils.http import urlquote
from django.db.models import Q
from systemsettings.models import MyUser
from warningre.models import WarningReceipt
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
    home = 'media/' + request.GET.get('data')  # 获取文件数据库路径
    file = open(home, 'rb')  # 写入文件
    response = FileResponse(file)  # 返回response对象
    response['Content-Type'] = 'application/octet-stream'  # 定义response对象返回类型
    home_cut = str(home).split('/')[-1]  # 定义文件名称和格式
    response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(home_cut))  # 把文件名称写入response对象
    return response


# 告警回执添加
def add_warningreceipt(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取用户及公司
    user = request.session.get('mylogin')
    place = user.myuser.company

    # 设置number为在前段页面固定的
    number = place.comsimplename + datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == 'GET':
        # 查询该告警通知单 在审批流中的状态,如果该通知单为归档状态,则将该通知单添加至data列表中
        data = []   # 已归档的告警通知单
        waring_notice_list = WarningNotice.objects.filter(is_activate=1, place=place)
        for notice in waring_notice_list:
            try:
                if notice.pinstance.cur_node.mynode.node_name == "归档":   # 归档状态
                    data.append(notice)
            except:
                pass  # 未归档


        return render(request, 'warning_re/add_warningreceipt.html',locals())

    elif request.method == 'POST':
        created_at = last_updated_at = datetime.now()
        number = request.POST.get('number')
        result = request.POST.get('result')
        content = request.POST.get('content')
        warningnotice_id = request.POST.get('warning_notice')
        warning_notice_data = WarningNotice.objects.filter(id=warningnotice_id).first()
        enclosure = request.FILES.get('enclosure')
        num = request.POST['num2']

        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)

        all_data = WarningReceipt.objects.create(place=place,
                                                 state='拟定',
                                                 result=result,
                                                 number=number,
                                                 content=content,
                                                 enclosure=enclosure,
                                                 warning_notice=warning_notice_data,
                                                 created_at=created_at,
                                                 last_updated_at=last_updated_at,
                                                 )
        all_data.save()
        my_process = MyProcess.objects.filter(app_name='告警回执', supervision_major=all_data.warning_notice.supervise_major,
                                              is_activate=1, company=place).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='告警回执', is_activate=1, company=place).first()
            if my_process == None:
                messages.info(request, 'Success %s: %s,%s' % ('保存', all_data, '暂无匹配的工作流程,请先去配置流程后再提交！'))
                return HttpResponseRedirect(
                    '/warningre/' + str(all_data.id) + '/detail/?action=detail&menuid=14')
        process = my_process.process
        all_data.created_by = request.session['mylogin']
        all_data.save()
        if num == '1':
            all_data.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", all_data))
            return HttpResponseRedirect(
                '/warningre/' + str(all_data.id) + '/detail2/?action=detail&menuid=14')
        elif num == '2':
            all_data.create_pinstance(process=process, submit=True)
            all_data.created_by = request.user
            all_data.save()
            new_processinstance = all_data.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', all_data))

            return HttpResponseRedirect(
                '/warningre/' + str(all_data.id) + '/detail/?action=detail&menuid=14&pinstance_id=' + str(
                    new_processinstance.id))



# 搜索告警回执单
@csrf_exempt
def warning_rece_search(request):
    # print('aaa')
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    waring_notice_list = WarningNotice.objects.filter(is_activate=1)
    user_list = MyUser.objects.filter(company=place)
    # 获取该登录人的组织机构
    # Department = request.session.get('Department')
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # warning_rece_list = []
    # 获取前端传来的数据
    # receipt_user = request.GET.get('receipt_user','')
    waring_notice = request.GET.get('waring_notice','')
    receipt_content = request.GET.get('receipt_content','')
    receipt_result = request.GET.get('receipt_result','')

    # if receipt_user == '':
    if waring_notice == '':
        warning_rece_list = WarningReceipt.objects.filter(Q(content__icontains=receipt_content),Q(result__icontains=receipt_result),Q(is_activate=1))
    else:
        warning_rece_list = WarningReceipt.objects.filter(Q(warning_notice_id=waring_notice),Q(content__icontains=receipt_content),Q(result__icontains=receipt_result),Q(is_activate=1))

    # else:
    #     if waring_notice == '':
    #         warning_rece_list = WarningReceipt.objects.filter(Q(warning_noticeexetuct_user_id=receipt_user),Q(content__icontains=receipt_content),
    #                                                           Q(result__icontains=receipt_result), Q(is_activate=1))
    #     else:
    #         warning_rece_list = WarningReceipt.objects.filter(Q(warning_notice_exetuct_user_id=receipt_user),Q(warning_notice_id=waring_notice),
    #                                                           Q(content__icontains=receipt_content),
    #                                                           Q(result__icontains=receipt_result), Q(is_activate=1))

    # abnormal = request.POST['abnormal']
    # result = request.POST['result']
    # if len(number) == 0:
    #     number = ''
    # if len(orgid) == 0:
    #     orgid = ""
    # elif len(plan) == 0:
    #     plan = ""
    # elif len(abnormal) == 0:
    #     abnormal = ""
    # elif len(result) == 0:
    #     result = ""
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM warningre_warningreceipt where orgid like '%%%%%s%%%%' and number like '%%%%%s%%%%' and is_activate=1 and plan like '%%%%%s%%%%' and abnormal like '%%%%%s%%%%' and result like '%%%%%s%%%%' " % (
    #         orgid, number, plan, abnormal, result))
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
    #     warningnotice_rece_plan = WarningReceipt.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=warningnotice_rece_plan.orgid) in orgid_list:
    #         warning_rece_list.append(warningnotice_rece_plan)
    # cursor.close()
    # 去重
    data = list(set(warning_rece_list))
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

    return render(request, 'warning_re/show_warningreceipt.html',locals())


# 展示所有告警回执单
def show_warningreceipt(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取到登录的用户及所在公司
    user = request.session.get('mylogin')
    place = user.myuser.company
    waring_notice_list = WarningNotice.objects.filter(is_activate=1)
    user_list = MyUser.objects.filter(company=place)
    warning_data_list =[]
    # if user.is_superuser:
    #     warning_data_list = WarningReceipt.objects.filter(is_activate=1)
    # else:
    warning_data_list = WarningReceipt.objects.filter(is_activate=1,place=place).order_by('-id')

    # 总条数
    total_counts = WarningReceipt.objects.filter(is_activate=1).count()

    # 分页
    paginator = Paginator(warning_data_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        warning_data_list = paginator.page(page)
    except PageNotAnInteger:
        warning_data_list = paginator.page(1)
    except EmptyPage:
        warning_data_list = paginator.page(paginator.num_pages)

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
    return render(request, 'warning_re/show_warningreceipt.html',
                  {'data': warning_data_list,'action':action,'menuid':menuid,'place':place,
                   'user_list':user_list,'waring_notice_list':waring_notice_list,'page_range':page_range,'total_counts':total_counts,'page_last':page_last,'total_page':total_page})


# 展示一个告警详情信息
def show_one_warningreceipt(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    data = WarningReceipt.objects.filter(id=wid).first()
    try:
        file_name = data.enclosure.name.split('/')[1]
    except:
        file_name = ''
    data_sup = WarningNotice.objects.filter(id=data.warning_notice.id).first()
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = data.pinstance
    if processinstance != None:
        return render(request, 'warning_re/show_one_warningreceipt.html', locals())
    else:
        return render(request, 'warning_re/show_one_warningreceipt2.html', locals())



# 编辑一个告警回执单
def one_warningreceipt(request, wid):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power

    # 获取用户及公司
    user = request.session.get('mylogin')
    place = user.myuser.company

    if request.method == 'GET':
        # 查询该告警通知单 在审批流中的状态,如果该通知单为归档状态,则将该通知单添加至data列表中
        waring_data = []  # 已归档的告警通知单
        waring_notice_list = WarningNotice.objects.filter(is_activate=1, place=place)
        for notice in waring_notice_list:
            try:
                if notice.pinstance.cur_node.mynode.node_name == "归档":  # 归档状态
                    waring_data.append(notice)
            except:
                pass  # 未归档
        data = WarningReceipt.objects.filter(id=wid).first()
        data_sup = WarningNotice.objects.filter(id=data.warning_notice.id).first()
        return render(request, 'warning_re/one_warningreceipt.html',locals())
    elif request.method == 'POST':
        created_at = last_updated_at = datetime.now()
        number = request.POST.get('number')
        result = request.POST.get('result')
        content = request.POST.get('content')
        warningnotice_id = request.POST.get('warning_notice')
        warning_notice_data = WarningNotice.objects.filter(id=warningnotice_id).first()
   
        all_data = WarningReceipt.objects.filter(id=wid).first()
        all_data.place=place
        all_data.state='拟定'
        all_data.result=result
        all_data.number=number
        all_data.content=content
        all_data.warning_notice=warning_notice_data
        all_data.created_at=created_at
        all_data.ast_updated_at=last_updated_at
        all_data.save()
        return HttpResponseRedirect('/warningre/list/?action=list&menuid=14')


# 删除告警管理回执单
def del_warningreceipt(request, wid):
    data = WarningReceipt.objects.filter(id=wid).first()
    data.is_activate = 0
    data.save()
    return HttpResponseRedirect('/warningre/list/?action=list&menuid=14')
