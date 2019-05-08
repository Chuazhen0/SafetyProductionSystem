from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from systemsettings.views import  checkpower
from systemsettings.models import MyUser
from . import models
import os
from django.db.models import Q
from django.utils.http import urlquote
from django.http import FileResponse
from django.db import connection

from systemsettings.models import SupervisionType
from datetime import datetime
from django.contrib import messages
from myworkflow.models import MyProcess
from lbworkflow.models import ProcessInstance

# Create your views here.
#  大文件上传
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
    home = request.GET.get('data', 0)  # 获取文件数据库路径
    file = open(home, 'rb')  # 写入文件
    response = FileResponse(file)  # 返回response对象
    response['Content-Type'] = 'application/octet-stream'  # 定义response对象返回类型
    home_cut = str(home).split('/')[-1]  # 定义文件名称和格式
    response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(home_cut))  # 把文件名称写入response对象
    return response
# 2.自动查找当前年份以后的5年
def later_five_year():
    current_year = datetime.now().year
    year_list = [current_year, current_year + 1, current_year + 2, current_year + 3, current_year + 4]
    return year_list
# 自动查找当前年份前两年，后两年
def before_later_five_year():
    current_year = datetime.now().year
    year_list = [ current_year - 2, current_year - 1,current_year, current_year + 1, current_year + 2]
    return year_list


# 公用函数
# 3.自动查找当前年份月份
def monthes():
    mon_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    return mon_list


# 公用函数
# 4.自动查找当前年份前后10年
# 1.月度计划
# 展示列表
def mon_plan_sum(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    supervision_major_list = SupervisionType.objects.all()
    year_list = before_later_five_year()
    month_list = monthes()
    mon_plan_sum_list=[]
    if user.is_superuser:
        mon_plan_sum_list_qur = models.MonPlanSum.objects.filter(is_activate=1)
        # 总共显示多少条数据
        total_counts = models.MonPlanSum.objects.filter(is_activate=1).count()

    else:
        mon_plan_sum_list_qur = models.MonPlanSum.objects.filter(is_activate=1, place=place)
        total_counts = models.MonPlanSum.objects.filter(is_activate=1, place=place).count()

    for mon in mon_plan_sum_list_qur:
        mon_plan_sum_list.append(mon)
    mon_plan_sum_list = list(set(mon_plan_sum_list))
    paginator = Paginator(mon_plan_sum_list, 10)
    page = request.GET.get("page",'1')
    try:
        mon_plan_sum_list = paginator.page(page)
    except PageNotAnInteger:
        mon_plan_sum_list = paginator.page(1)
    except EmptyPage:
        mon_plan_sum_list = paginator.page(paginator.num_pages)

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
    return render(request, 'monworkplan/mon_plan_sum.html',locals())


# 增加月度计划
@csrf_exempt
def mon_plan_sum_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    place = user.myuser.company
    number = place.comsimplename+datetime.now().strftime("%Y%m%d%H%M%S")
    smallnumber = number+datetime.now().strftime("%S")
    exe_user_list = MyUser.objects.filter(is_activate=1,company=place)
    if request.method == 'GET':
        # get 方式访问
        # 将监督类型列表查询
        supervision_major_list = SupervisionType.objects.all()
        year_list = later_five_year()
        month_list = monthes()
        year = datetime.now().year
        month = datetime.now().month+1
        now = datetime.now()
        return render(request, 'monworkplan/mon_plan_sum_add.html',locals())

    elif request.method == 'POST':
        supervision_major = request.POST['supervision_major']
        supervision_major =SupervisionType.objects.get(name=supervision_major)
        desc = request.POST['desc']
        created_at = datetime.now()
        last_updated_at = datetime.now()
        enclosure = request.FILES.get('enclosure')
        if enclosure is not None:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
        last_updated_by = request.session.get('mylogin').myuser
        state = '拟定'
        year = request.POST['year']
        month = request.POST['month']
        smallnumber = request.POST.getlist('smallnumber')
        content = request.POST.getlist('content')
        exe_users = request.POST.getlist('exe_user')
        finish_time = request.POST.getlist('finish_time')
        num = request.POST['num2']
        new_plan_sum = models.MonPlanSum.objects.create(supervision_major=supervision_major, number=number,
                                                        created_at=created_at,
                                                        last_updated_at=last_updated_at,
                                                        last_updated_by=last_updated_by, state=state, year=year,
                                                        month=month, place=place, desc=desc,
                                                        enclosure=enclosure)
        new_plan_sum.save()
        for i in range(0,len(smallnumber)):
            new_small_data = models.SmallDatas.objects.create(finish_time=finish_time[i],smallnumber=smallnumber[i],content=content[i],exe_user=MyUser.objects.get(id=exe_users[i]),monplansum=new_plan_sum)
            new_small_data.save()


        my_process = MyProcess.objects.filter(app_name='月度计划', supervision_major=new_plan_sum.supervision_major,
                                              is_activate=1, company=place).first()

        if my_process == None:  # 如果监督专业和指定number的标准的myprocess没有找到，就找未指定监督专业，但是指定number的
            my_process = MyProcess.objects.filter(app_name='月度计划', is_activate=1, company=place).first()
            if my_process == None:
                messages.info(request, 'Success %s: %s,%s' % ('保存', new_plan_sum,'暂无匹配的工作流程,请先去配置流程后再提交！'))
                return HttpResponseRedirect(
                    '/mon_plan_sum/' + str(new_plan_sum.id) + '/detail/?action=detail&menuid=7')
        process = my_process.process

        new_plan_sum.created_by = request.session['mylogin']
        new_plan_sum.save()
        if num == '1':
            new_plan_sum.create_pinstance(process=process)
            messages.info(request, 'Success %s: %s' % ("保存", new_plan_sum))
            return HttpResponseRedirect(
                '/mon_plan_sum/' + str(new_plan_sum.id) + '/detail2/?action=detail&menuid=7')
        elif num == '2':
            new_plan_sum.create_pinstance(process=process, submit=True)
            new_plan_sum.created_by = request.user
            new_plan_sum.save()
            new_processinstance = new_plan_sum.pinstance
            messages.info(request, 'Success %s: %s' % ('提交', new_plan_sum))

            return HttpResponseRedirect(
                '/mon_plan_sum/' + str(new_plan_sum.id) + '/detail/?action=detail&menuid=7&pinstance_id=' + str(
                    new_processinstance.id))





# 删除月度计划
def mon_plan_sum_delete(request, m_id):
    mon_plan_sum = models.MonPlanSum.objects.get(id=m_id)
    mon_plan_sum.is_activate = 0
    smalldata_list = models.SmallDatas.objects.filter(monplansum=mon_plan_sum)
    for a in smalldata_list:
        a.is_activate=0
        a.save()
    mon_plan_sum.save()
    return HttpResponseRedirect('/mon_plan_sum/list/?action=list&menuid=7')


# 查看月度计划详情
def mon_plan_sum_detail(request, m_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    mon_plan_sum = models.MonPlanSum.objects.get(id=m_id)
    try:
        file_name = mon_plan_sum.enclosure.name.split('/')[1]
    except:
        file_name = ''
    smalldata_list = models.SmallDatas.objects.filter(monplansum=mon_plan_sum)
    # home = mon_plan_sum.enclosure
    # home_cut = str(home).split('/')[-1]
    processinstance = ProcessInstance.objects.filter(id=request.GET.get('pinstance_id')).first()
    processinstance = mon_plan_sum.pinstance
    if processinstance != None:
        return render(request, 'monworkplan/mon_plan_sum_detail.html', locals())
    else:
        return render(request, 'monworkplan/mon_plan_sum_detail2.html', locals())



# 编辑月度计划
@csrf_exempt
def mon_plan_sum_edit(request, m_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取登录人信息
    user = request.session.get('mylogin')
    # 获取该登录人的组织机构
    department = user.myuser.department
    # 找到其所在分公司
    # place = check_place(department)
    place = user.myuser.company
    # 找到该登录人的组织机构所有下属机构

    mon_plan_sum = models.MonPlanSum.objects.get(id=m_id)

    home = mon_plan_sum.enclosure
    home_cut = str(home).split('/')[-1]
    year_list = later_five_year()
    month_list = monthes()
    # 根据id获取对象
    if request.method == 'GET':
        last_updated_by = mon_plan_sum.last_updated_by
        now = datetime.now()
        supervision_major_list = SupervisionType.objects.all()

        return render(request, 'monworkplan/mon_plan_sum_edit.html',locals())
    elif request.method == 'POST':
        supervision_major = request.POST['supervision_major']
        if supervision_major == None:
            supervision_major = mon_plan_sum.supervision_major
        else:
            supervision_major = SupervisionType.objects.get(name=supervision_major)
        desc = request.POST['desc']
        orgid = request.POST['orgid']
        year = request.POST['year']
        month = request.POST['month']
        last_updated_at = datetime.now()
        last_updated_by = request.session.get('mylogin').myuser
        mon_plan_sum.supervision_major = supervision_major
        mon_plan_sum.orgid = orgid
        mon_plan_sum.desc = desc
        mon_plan_sum.month = month
        mon_plan_sum.year = year
        mon_plan_sum.last_updated_at = last_updated_at
        mon_plan_sum.last_updated_by = last_updated_by
        enclosure = request.FILES.get('enclosure')
        if enclosure == None:
            mon_plan_sum.save()
            # pass
        else:
            enclosure.name = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + str(enclosure.name)
            mon_plan_sum.enclosure = enclosure
        mon_plan_sum.save()
        return HttpResponseRedirect('/mon_plan_sum/' + m_id + '/detail/?action=detail&menuid=7')

@csrf_exempt
def mon_plan_sum_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    department = user.myuser.department
    # place = check_place(department)
    place = user.myuser.company
    supervision_major_list = SupervisionType.objects.all()
    year_list = before_later_five_year()
    month_list = monthes()
    mon_plan_sum_list = []
    Supervision_type = request.GET.get('Supervision_type','')
    year = request.GET.get('year','')
    month = request.GET.get('month','')
    describe = request.GET.get('describe','')

    if Supervision_type == '':
        if year == '':
            if month == '':
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(desc__icontains=describe),Q(is_activate=1))
            else:
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(month=month),Q(desc__icontains=describe),Q(is_activate=1))

        else:
            if month == '':
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(year=year),Q(desc__icontains=describe),Q(is_activate=1))

            else:
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(year=year),Q(month=month),Q(desc__icontains=describe),Q(is_activate=1))

    else:
        if year == '':
            if month == '':
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(supervision_major_id=Supervision_type),Q(desc__icontains=describe),Q(is_activate=1))

            else:
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(supervision_major_id=Supervision_type),Q(month=month),Q(desc__icontains=describe),Q(is_activate=1))

        else:
            if month == '':
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(supervision_major_id=Supervision_type),Q(year=year),Q(desc__icontains=describe),Q(is_activate=1))

            else:
                mon_plan_sum_list = models.MonPlanSum.objects.filter(Q(supervision_major_id=Supervision_type),Q(year=year),Q(month=month),Q(desc__icontains=describe),Q(is_activate=1))



    # if len(supervision_major) == 0:
    #     supervision_major = ''
    # else:
    #     supervision_major_obj = SupervisionType.objects.filter(
    #         Q(supervision_major__icontains=supervision_major)).first()
    #     if supervision_major_obj == None:
    #         supervision_major = '#'
    #     else:
    #         supervision_major = supervision_major_obj.id
    # if len(desc) == 0:
    #     desc = ""
    # if len(year) == 0:
    #     year = ""
    # if len(month) == 0:
    #     month = ""
    # if len(state) == 0:
    #     state = ''
    # cursor = connection.cursor()
    #
    # cursor.execute(
    #     "SELECT id FROM mon_plan_sum_monplansum where  state like '%%%%%s%%%%' and is_activate=1 and `desc` like '%%%%%s%%%%' and `month`like '%%%%%s%%%%' and `year` like '%%%%%s%%%%' and supervision_major_id like '%%%%%s%%%%' " % (
    #         state, desc, month, year, supervision_major))
    # # id 列表
    # data = list(cursor.fetchall())
    # id_list = []
    # for row in data:
    #     # 将id取出，存入列表
    #     id_list.append(row[0])
    #
    # for id in id_list:
    #     mon_plan_sum = models.MonPlanSum.objects.filter(id=id,place=place).first()
    #     mon_plan_sum_list.append(mon_plan_sum)
    # cursor.close()
    mon_plan_sum_list = list(set(mon_plan_sum_list))
    paginator = Paginator(mon_plan_sum_list, 10, 2)
    page = request.GET.get("page",'1')
    try:
        mon_plan_sum_list = paginator.page(page)
    except PageNotAnInteger:
        mon_plan_sum_list = paginator.page(1)
    except EmptyPage:
        mon_plan_sum_list = paginator.page(paginator.num_pages)
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

    return render(request, 'monworkplan/mon_plan_sum.html',
                  {'mon_plan_sum_list': mon_plan_sum_list, 'action': action,
                   'menu_list': request.session['menudata'],'supervision_major_list':supervision_major_list,
                   'year_list':year_list,'month_list':month_list,'page_range':page_range,'Supervision_type':Supervision_type,
                   'year':year,'month':month,'describe':describe})
