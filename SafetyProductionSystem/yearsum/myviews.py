from django.http import HttpResponseRedirect, JsonResponse,FileResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from . import models
import os
from django.db import connection
from django.utils.http import urlquote
from systemsettings.views import  checkpower
from django.db.models import Q
from mon_plan_sum.myviews import later_five_year

from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance
from django.contrib import messages

# Create your views here.
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
def year_sum(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    year_list = before_later_five_year()

    yearsum_list = []
    # if user.is_superuser:
    #     # 找到该登录人的组织机构所有下属机构
    #     yearsum_list_2 = models.YearSum.objects.filter(is_activate=1)
    #     # 遍历每一个组织为下属机构的月度计划与总结列表
    #     for mon in yearsum_list_2:
    #         # 加入到list中保存
    #         yearsum_list.append(mon)
    # else:
    # 找到该登录人的组织机构所有下属机构
    yearsum_list_2 = models.YearSum.objects.filter(is_activate=1, place=place)
    total_counts = models.YearSum.objects.filter(is_activate=1).count()
    # 遍历每一个组织为下属机构的月度计划与总结列表
    for mon in yearsum_list_2:
        # 加入到list中保存
        yearsum_list.append(mon)
    # 去重
    yearsum_list = list(set(yearsum_list))
    # 分页
    paginator = Paginator(yearsum_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        yearsum_list = paginator.page(page)
    except PageNotAnInteger:
        yearsum_list = paginator.page(1)
    except EmptyPage:
        yearsum_list = paginator.page(paginator.num_pages)
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

    return render(request, 'year_sum/year_sum.html',
                  {'year_sum_list': yearsum_list, 'action': action,'year_list':year_list,'page_range':page_range,'page_last':page_last,'total_counts':total_counts,'total_page':total_page})


# 新建
@csrf_exempt
def year_sum_add(request):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    place = user.myuser.company
    year_list = later_five_year()
    if request.method == 'GET':
        # get 方式访问
        year = datetime.now().year
        return render(request, 'year_sum/year_sum_add.html',
                      {'year': year, 'action': action, 'now': datetime.now(), 'year_list': year_list, 'place': place})

    elif request.method == 'POST':
        sum_desc = request.POST['sum_desc']
        sum_type = request.POST['sum_type']
        created_at = datetime.now()
        last_updated_at = datetime.now()
        enclosure = request.FILES.get('enclosure')
        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
        created_by = request.session.get('mylogin').myuser
        last_updated_by = request.session.get('mylogin').myuser
        state = '新建'
        place = place
        year = request.POST['year']
        new_year_sum = models.YearSum.objects.create(
            created_at=created_at,
           sum_type=sum_type,
            last_updated_at=last_updated_at,
            last_updated_by=last_updated_by, state=state, year=year,
            place=place, sum_desc=sum_desc,
            enclosure=enclosure)
        new_year_sum.save()
        
        num = request.POST['num2']
        my_process = MyProcess.objects.filter(app_name='年度总结', is_activate=1, company=place).first()
        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            messages.info(request, 'Success %s: %s,%s' % ('保存', new_year_sum, '暂无匹配的工作流程,请先去配置流程后再提交！'))
            return HttpResponseRedirect(
                '/yearsum/' + str(new_year_sum.id) + '/detail/?action=detail&menuid=10')

        process = my_process.process

        new_year_sum.created_by = request.session['mylogin']
        new_year_sum.save()
        if num == '1':
            new_year_sum.create_pinstance(process=process)
            new_year_sum.created_by = request.user
            new_year_sum.save()
            messages.info(request, 'Success %s: %s' % ("保存", new_year_sum))
            return HttpResponseRedirect(
                '/yearsum/' + str(new_year_sum.id) + '/detail2/?action=detail&menuid=10')
        elif num == '2':
            new_year_sum.create_pinstance(process=process, submit=True)
            new_year_sum.created_by = request.user
            new_year_sum.save()
            new_processinstance = new_year_sum.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', new_year_sum))

            return HttpResponseRedirect(
                '/yearsum/' + str(new_year_sum.id) + '/detail/?action=detail&menuid=10&pinstance_id=' + str(
                    new_processinstance.id))



# 编辑
@csrf_exempt
def year_sum_edit(request, y_id):
    # if request.method == 'GET':
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取监督年度总结记录
    year_sum = models.YearSum.objects.get(id=y_id)
    home = year_sum.enclosure
    home_cut = str(home).split('/')[-1]
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    Department = user.myuser.Department
    # 找到其所在分公司
    place = check_place(Department)
    # 找到该登录人的组织机构所有下属机构
    orgid = []
    orgid_1 = Department.objects.filter(parent=Department)
    for org in orgid_1:
        orgid.append(org)

    orgid.append(Department)
    year_list = later_five_year()
    if request.method == 'GET':
        # get 方式访问
        year = datetime.now().year
        return render(request, 'year_sum/year_sum_edit.html',
                      {"year_sum": year_sum, 'year': year,
                       'now': datetime.now(), 'action': action,
                       'orgid': orgid, 'place': place, 'year_list': year_list,
                       'home_cut': home_cut})

    elif request.method == 'POST':
        sum_desc = request.POST['sum_desc']
        sum_type = request.POST['sum_type']
        year = request.POST['year']
        orgid = request.POST['orgid']
        last_updated_at = datetime.now()
        enclosure = request.FILES.get('enclosure')
        if enclosure == None:
            pass
        else:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
            year_sum.enclosure = enclosure
        last_updated_by = request.session.get('mylogin')
        year_sum.sum_desc = sum_desc
        year_sum.sum_type = sum_type
        year_sum.year = year
        year_sum.orgid = request.POST['orgid']
        year_sum.last_updated_at = last_updated_at
        year_sum.last_updated_by = last_updated_by.myuser
        year_sum.save()
        return HttpResponseRedirect('/yearsum/' + y_id + '/detail/?action=detail&menuid=10')


# 详情
def year_sum_detail(request, y_id):
  
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获监督年度总结记录
    year_sum = models.YearSum.objects.get(id=y_id)
    try:
        file_name = year_sum.enclosure.name.split('/')[1]
    except:
        file_name = ''
    # home = year_sum.enclosure
    # home_cut = str(home).split('/')[-1]
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = year_sum.pinstance
    if processinstance != None:
        return render(request, 'year_sum/year_sum_detail.html', locals())
    else:
        return render(request, 'year_sum/year_sum_detail2.html', locals())



# 删除
def year_sum_delete(request, y_id):
    # 获取各专业监督年度总结记录
    year_sum = models.YearSum.objects.get(id=y_id)
    # 修改is_activate的值为0
    year_sum.is_activate = 0
    year_sum.save()
    return HttpResponseRedirect('/yearsum/list/?action=list&menuid=10')


# ajax 搜索
@csrf_exempt
def sum_check(request):
    word = request.POST['word']
    # 从数据库中匹配
    # queryset 对象序列化[{}]
    year_sum_list = serializers.serialize("json",
                                          models.YearSum.objects.filter(sum_desc__icontains=word).filter(
                                              is_activate=1))
    year_sum_list = eval(year_sum_list)  # 字符串转化为json数据
    # 定义num，用来记录个数
    num = 0
    for i in range(0, len(year_sum_list)):
        num += 1

    return JsonResponse({'list': year_sum_list, 'num': num})


# 监督年度总结汇总查询
@csrf_exempt
def year_sum_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    year_list = before_later_five_year()

    # 获取该登录人的组织机构
    # Department = user.myuser.Department
    # 定义一个空的列表,用户保存最终要展示的所有符合要求的数据记录
    # 找到该登录人的组织机构所有下属机构
    # orgid_list = Department.objects.filter(parent=Department)
    # orgid_list = list(orgid_list)
    # orgid_list.append(Department)
    # 定义空的列表，用于保存筛选好的数据
    # 获取前端传来的数据
    # orgid = request.POST['orgid']
    # sum_type = request.POST['sum_type']
    desc = request.GET.get('desc','')
    year = request.GET.get('year','')

    if year == '':
        year_sum_list = models.YearSum.objects.filter(Q(sum_desc__icontains=desc),Q(is_activate=1))

    else:
        year_sum_list = models.YearSum.objects.filter(Q(year=year),Q(sum_desc__icontains=desc),Q(is_activate=1))


    # state = request.POST['state']
    # if len(orgid) == 0:
    #     orgid = ""
    # if len(desc) == 0:
    #     desc = ""
    # if len(year) == 0:
    #     year = ""
    # if len(sum_type) == 0:
    #     sum_type = ""
    # if len(state) == 0:
    #     state = ''
    # cursor = connection.cursor()
    #
    # cursor.execute(
    #     "SELECT id FROM yearsum_yearsum where orgid like '%%%%%s%%%%' and state like '%%%%%s%%%%' and is_activate=1 and `sum_desc` like '%%%%%s%%%%' and `sum_type` like '%%%%%s%%%%' and `year` like '%%%%%s%%%%' " % (
    #         orgid, state, desc, sum_type, year,))
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
    #     year_sum = models.YearSum.objects.get(id=id)
    #     # 判断该数据对象的组织机构是否属于当前组织机构或下属机构
    #     if Department.objects.get(name=year_sum.orgid) in orgid_list:
    #         year_sum_list.append(year_sum)
    # cursor.close()
    # 去重
    year_sum_list = list(set(year_sum_list))
    # 分页
    paginator = Paginator(year_sum_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        year_sum_list = paginator.page(page)
    except PageNotAnInteger:
        year_sum_list = paginator.page(1)
    except EmptyPage:
        year_sum_list = paginator.page(paginator.num_pages)

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

    return render(request, 'year_sum/year_sum.html',locals())