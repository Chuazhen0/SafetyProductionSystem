from django.http import HttpResponseRedirect,  FileResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from . import models
from django.utils.http import urlquote
import os
from django.db import connection
from django.db.models import Q
from systemsettings.views import  checkpower
from systemsettings.models import  Department
from mon_plan_sum.myviews import later_five_year
from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance
from django.contrib import messages


# Create your views here.
# 上传附件
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

# 自动查找当前年份前两年，后两年
def before_later_five_year():
    current_year = datetime.now().year
    year_list = [ current_year - 2, current_year - 1,current_year, current_year + 1, current_year + 2]
    return year_list



# 展示列表
def year_plan(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    year_list = before_later_five_year()

    yearplan_list = []
    # if user.is_superuser:
    #     yearplan_list_2 = models.YearPlan.objects.filter(is_activate=1)
    #     # 遍历每一个组织为下属机构的月度计划与总结列表
    #     for mon in yearplan_list_2:
    #         # 加入到list中保存
    #         yearplan_list.append(mon)
    # else:
    yearplan_list_2 = models.YearPlan.objects.filter(is_activate=1, place=place)

    #  总条数
    total_counts = models.YearPlan.objects.filter(is_activate=1)

    # 遍历每一个组织为下属机构的月度计划与总结列表
    for mon in yearplan_list_2:
        # 加入到list中保存
        yearplan_list.append(mon)
    yearplan_list=list(set(yearplan_list))
    # 分页
    paginator = Paginator(yearplan_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        yearplan_list = paginator.page(page)
    except PageNotAnInteger:
        yearplan_list = paginator.page(1)
    except EmptyPage:
        yearplan_list = paginator.page(paginator.num_pages)

    page_last = (int(page) - 1) * 10
    total_page = paginator.num_pages
    total_counts = len(yearplan_list)
    if total_page > 5:
        if page != '':
            page = int(page)
            if page < 5:
                page_range = list(range(1, 6))
            elif page >= 5:
                page_range = list(range(page - 4, page + 1))
    else:
        page_range = list(range(1, total_page + 1))

    return render(request, 'year_plan/year_plan.html',
                  {'year_plan_list': yearplan_list, 'action': action,'year_list':year_list,'page_range':page_range,'total_counts':total_counts,'page_last':page_last,'total_page':total_page})


# 新建
@csrf_exempt
def year_plan_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    year_list = later_five_year()
    now = datetime.now()
    if request.method == 'GET':
        # get 方式访问
        year = datetime.now().year
        return render(request, 'year_plan/year_plan_add.html',locals())

    elif request.method == 'POST':
        desc = request.POST['desc']
        created_at = datetime.now()
        last_updated_at = datetime.now()
        enclosure = request.FILES.get('enclosure')
        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
        last_updated_by = request.session.get('mylogin').myuser
        state = '草稿'
        place = place
        year = request.POST['year']
        num = request.POST['num2']
        new_year_plan = models.YearPlan.objects.create(created_at=created_at,
                                                       last_updated_at=last_updated_at,
                                                       last_updated_by=last_updated_by,
                                                       state=state, year=year,  place=place,
                                                       desc=desc,
                                                       enclosure=enclosure)
        new_year_plan.save()
        

        my_process = MyProcess.objects.filter(app_name='年度计划',is_activate=1, company=place).first()
        if my_process == None:
            messages.info(request, 'Success %s: %s,%s' % ('保存', new_year_plan, '暂无匹配的工作流程,请先去配置流程后再提交！'))
            return HttpResponseRedirect(
                '/yearplan/' + str(new_year_plan.id) + '/detail/?action=detail&menuid=9')

        process = my_process.process

        new_year_plan.created_by = request.session['mylogin']
        new_year_plan.save()
        if num == '1':
            new_year_plan.create_pinstance(process=process)
            new_year_plan.created_by = request.user
            new_year_plan.save()
            messages.info(request, 'Success %s: %s' % ("保存", new_year_plan))
            return HttpResponseRedirect(
                '/yearplan/' + str(new_year_plan.id) + '/detail2/?action=detail&menuid=9')
        elif num == '2':
            new_year_plan.create_pinstance(process=process, submit=True)
            new_year_plan.created_by = request.user
            new_year_plan.save()
            new_processinstance = new_year_plan.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', new_year_plan))

            return HttpResponseRedirect(
                '/yearplan/' + str(new_year_plan.id) + '/detail/?action=detail&menuid=9&pinstance_id=' + str(
                    new_processinstance.id))




# 编辑
@csrf_exempt
def year_plan_edit(request, y_id):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取各专业监督年度总结记录
    year_plan = models.YearPlan.objects.get(id=y_id)
    home = year_plan.enclosure
    home_cut = str(home).split('/')[-1]
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    department = user.myuser.department
    # 找到其所在分公司
    # place = check_place(Department)
    place = user.myuser.company
    # 找到该登录人的组织机构所有下属机构
    orgid = []
    de_company = Department.objects.filter(departname=department)[0].company
    orgid_1 = Department.objects.filter(company=de_company)
    for org in orgid_1:
        orgid.append(org)
    orgid.append(Department)
    year_list = later_five_year()
    now = datetime.now()
    if request.method == 'GET':
        # get 方式访问
        year = datetime.now().year
        last_updated_by = year_plan.last_updated_by
        return render(request, 'year_plan/year_plan_edit.html',locals())

    elif request.method == 'POST':
        desc = request.POST['desc']
        orgid = request.POST['orgid']
        year = request.POST['year']
        last_updated_at = datetime.now()
        enclosure = request.FILES.get('enclosure')
        last_updated_by = request.session.get('mylogin').myuser
        year_plan.desc = desc
        if enclosure == None:
            year_plan.save()
            # pass
        else:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
            year_plan.enclosure = enclosure

        year_plan.last_updated_at = last_updated_at
        year_plan.last_updated_by = last_updated_by
        year_plan.orgid = orgid
        year_plan.year = year
        year_plan.save()
        return HttpResponseRedirect('/yearplan/' + y_id + '/detail/?action=detail&menuid=9')


# 详情
def year_plan_detail(request, y_id):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获监督年度计划记录
    year_plan = models.YearPlan.objects.get(id=y_id)
    try:
        file_name = year_plan.enclosure.name.split('/')[1]
    except:
        file_name = ''
    # home = year_plan.enclosure
    # home_cut = str(home).split('/')[-1]
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = year_plan.pinstance
    if processinstance != None:
        return render(request, 'year_plan/year_plan_detail.html', locals())
    else:
        return render(request, 'year_plan/year_plan_detail2.html', locals())



# 删除
def year_plan_delete(request, y_id):
    # 获取各专业监督年度总结记录
    year_plan = models.YearPlan.objects.get(id=y_id)
    # 修改is_activate的值为0
    year_plan.is_activate = 0
    year_plan.save()
    return HttpResponseRedirect('/yearplan/list/?action=list&menuid=9')

# 监督年度计划汇总
@csrf_exempt
def year_plan_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    place= user.myuser.company
    year_list = before_later_five_year()

    # 获取前端传来的数据
    # orgid = request.POST['orgid']
    desc = request.GET.get('desc','')
    year = request.GET.get('year','')
    if year == '':
        year_plan_list = models.YearPlan.objects.filter(Q(desc__icontains=desc),Q(is_activate=1))
    else:
        year_plan_list = models.YearPlan.objects.filter(Q(year=year),Q(desc__icontains=desc),Q(is_activate=1))


    # state = request.POST['state']
    # if len(orgid) == 0:
    #     orgid = ""
    # if len(desc) == 0:
    #     desc = ""
    # if len(year) == 0:
    #     year = ""
    # if len(state) == 0:
    #     state = ''
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT id FROM yearplan_yearplan where orgid like '%%%%%s%%%%' and state like '%%%%%s%%%%' and is_activate=1 and `year` like '%%%%%s%%%%' and `desc` like '%%%%%s%%%%' " % (
    #         orgid, state, year, desc))
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
    #     year_plan = models.YearPlan.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=year_plan.orgid) in orgid_list:
    #         year_plan_list.append(year_plan)
    # cursor.close()
    # 去重
    year_plan_list = list(set(year_plan_list))
    # 分页
    paginator = Paginator(year_plan_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        year_plan_list = paginator.page(page)
    except PageNotAnInteger:
        year_plan_list = paginator.page(1)
    except EmptyPage:
        year_plan_list = paginator.page(paginator.num_pages)

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
    return render(request, 'year_plan/year_plan.html',locals())