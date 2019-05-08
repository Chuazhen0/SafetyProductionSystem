from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from systemsettings.views import checkpower
from systemsettings.models import Department, User, MyUser, KKS
import os
from django.utils.http import urlquote
import time, datetime
import calendar
from systemsettings.models import SupervisionType, Company, PowerPlants, Job
from problemlog.models import Problemlog
from myform.models import MyForm
from django.db.models import Q
import pymysql
import copy


# 计算当月最后一天
def test(time):
    last_week = calendar.monthcalendar(time.year, time.month)[-1]
    res = []
    for i in last_week:
        if i != 0:
            res.append(i)
    return res[-1]


# 展示报表信息进行填报
def show_user_data(request):
    # action = request.GET.get('action')
    action = 'list'
    # menuid = request.GET.get('menuid')
    menuid = '16'
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    # search_power = '0'
    # for power_msg in power:
    #     if power_msg['key'] == '2':
    #         search_power = '1'
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company

    now_time = datetime.datetime.now()
    first_day = datetime.datetime(now_time.year, now_time.month, 1)
    up_last = first_day - datetime.timedelta(days=1)
    last_month = up_last.strftime('%Y-%m-%d')[:7]
    month_now = now_time.strftime('%Y-%m-%d')[:7]
    ptype_list = SupervisionType.objects.all()

    state_up_power = '0'
    state_check_power = '0'
    state_back_power = '0'
    state_edit_power = '0'
    state_add_power = '0'
    state_plantcheck = '0'
    del_power = '1'
    for power_msg in power:
        if power_msg['key'] == '10':
            state_check_power = '1'
        if power_msg['key'] == '9':
            state_up_power = '1'
        if power_msg['key'] == '11':
            state_back_power = '1'
        if power_msg['key'] == '1':
            state_edit_power = '1'
        if power_msg['key'] == '12':
            state_add_power = '1'
        if power_msg['key'] == '13':
            state_plantcheck = '1'

    if user.is_superuser:
        data = MyForm.objects.filter(~Q(state_num='0')).order_by('-created_at', '-powerplants_id')
        company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
    else:
        if state_check_power == '1':
            company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
        powerplan_id = PowerPlants.objects.get(powname=company).id
        '''
        if state_up_power == '1' and state_check_power == '1' and state_back_power == '1':
            data = MyForm.objects.filter(~Q(state_num='0'),powerplants_id=powerplan_id).order_by('-form_date','-state_num')
        else:
            data = MyForm.objects.filter(powerplants_id=powerplan_id).order_by('-form_date','-state_num')
        # company_list = [company]
        '''
        # print(state_add_power,'state_add_power')
        # print(state_plantcheck,'state_plantcheck===')
        if state_add_power == '1' and state_plantcheck == '0':
            # print(1111)
            data = MyForm.objects.filter(powerplants_id=powerplan_id, create_person=user.myuser).order_by('-created_at',
                                                                                                          '-state_num')
        elif state_add_power == '1' and state_plantcheck == '1':
            # print(2222)
            data = MyForm.objects.filter(~Q(state_num='10') | Q(create_person=user.myuser),
                                         powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
        elif state_plantcheck == '1' and state_add_power == '0':
            # print(3333)
            data = MyForm.objects.filter(~Q(state_num='10'), powerplants_id=powerplan_id).order_by('-created_at',
                                                                                                   '-state_num')
        elif state_back_power == '1' and state_edit_power == '1':
            # print(4444)
            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0')).order_by(
                '-created_at', '-state_num')
        else:
            # print(5555)
            data = []

        company_list = PowerPlants.objects.filter(powname=company.comname)  # 电厂列表（PowerPlants表）

    for row in data:
        create_at = row.created_at.strftime('%Y-%m-%d')
        row.create_at = create_at



    # 分页
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page", "1")
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
    # print(state_up_power,"state_up_power====")
    return render(request, 'myform/form_list.html', locals())


# 添加报表头信息
def add_myform_head(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    powerplan_id = PowerPlants.objects.filter(powname=company).first()

    now_time = datetime.datetime.now()
    first_day = datetime.datetime(now_time.year, now_time.month, 1)
    up_last = first_day - datetime.timedelta(days=1)
    time_pass = up_last.strftime('%Y-%m-%d')
    time_now = now_time.strftime('%Y-%m-%d')

    if request.method == "GET":
        supervision_data = SupervisionType.objects.filter(form_use='1')  # 所有的监督专业
        # 查询出已经创建过的监督专业并从supervision_data中剔除
        # supervision_have = SupervisionType.objects.filter()
        if user.is_superuser:
            power_plan = PowerPlants.objects.all()
            # company_list = Company.objects.all()
        else:
            company_obj = user.myuser.company
            power_plan = PowerPlants.objects.filter(powname=company_obj.comname)
            # company_list = [company]
        # power_plan = PowerPlants.objects.all()
        return render(request, "myform/add_myform_head.html", locals())
    elif request.method == "POST":
        # 获取前端传来的数据
        number = request.POST.get('number')  # 集团名称
        # formname = request.POST.get('formname')  # 状态
        form_state = request.POST.get('form_state')  # 状态
        ptype_id = request.POST.get('ptype')  # 监督专业
        ptype = SupervisionType.objects.filter(id=ptype_id, form_use='1').first()
        exe_job = user.myuser.jobname  # 创建人的岗位
        powerplants_id = request.POST.get('powerplants')  # 电厂名称
        powerplants = PowerPlants.objects.filter(id=powerplants_id).first()
        # company = Company.objects.filter(id=powerplants_id).first()
        created_at = request.POST.get('created_at')  # 创建时间
        year_moon = request.POST.get('year_moon')  # 创建月份
        state_name = '草稿'

        # 判断当前监督专业的报表头是否已经被创建
        myform_obj = MyForm.objects.filter(form_date=year_moon, ptype=ptype, powerplants=powerplants)
        if len(myform_obj) > 0:
            supervision_data = SupervisionType.objects.filter(form_use='1')  # 所有的监督专业
            # 查询出已经创建过的监督专业并从supervision_data中剔除
            # supervision_have = SupervisionType.objects.filter()
            if user.is_superuser:
                power_plan = PowerPlants.objects.all()
                # company_list = Company.objects.all()
            else:
                company_obj = user.myuser.company
                power_plan = PowerPlants.objects.filter(powname=company_obj.comname)
            msg = '%s监督专业的报表已经创建！' % ptype.name
            return render(request, "myform/add_myform_head.html", locals())

        # state_obj = Form_state.objects.create(state_num=10,state_name=state_name, edit_person=user.myuser)

        # 保存到数据库
        qua = MyForm.objects.create(
            number=number,
            # formname=formname,
            ptype=ptype,
            exe_job=exe_job,
            powerplants=powerplants,
            # company=company,
            created_at=created_at,
            create_person=user.myuser,
            form_date=year_moon,
            # state=state_obj,
            state_num=10,
            state_name=state_name,
            edit_person=user.myuser
        )
        qua.save()
        return HttpResponseRedirect('/myform/show_all_form/?action=list&menuid=16')


# 报表头删除
def delete_form(request, form_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # print(form_id)
    form_del = MyForm.objects.filter(id=form_id).first()  # 获取要删除的报表头对象
    # print(form_del)
    form_del.delete()
    return HttpResponseRedirect('/myform/show_all_form/?action=list&menuid=16')


# 进入指标填报的table界面
def show_add_target(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    power_id = request.GET.get('power_id')
    type_id = request.GET.get('type_id')
    time_is = request.GET.get('time_is')
    form_id = request.GET.get('form_id')
    form_state = request.GET.get('form_state')
    # return render(request, 'myform/show_add_insulation_form.html', locals())
    state_up_power = '0'
    state_check_power = '0'
    state_back_power = '0'
    state_add_power = '0'
    state_plantcheck = '0'
    for power_msg in power:
        if power_msg['key'] == '9':
            state_up_power = '1'
    for power_msg in power:
        if power_msg['key'] == '10':
            state_check_power = '1'
    for power_msg in power:
        if power_msg['key'] == '11':
            state_back_power = '1'
        if power_msg['key'] == '12':
            state_add_power = '1'
        if power_msg['key'] == '13':
            state_plantcheck = '1'
    if type_id == '13':  # 绝缘
        return render(request, 'myform/show_add_insulation_form.html', locals())
    elif type_id == '2':  # 金属
        return render(request, 'myform/show_add_metal_form.html', locals())
    elif type_id == '4':  # 热工
        return render(request, 'myform/show_add_hotman_form.html', locals())
    elif type_id == '6':  # 电测
        return render(request, 'myform/show_add_electrictest_form.html', locals())
    elif type_id == '3':  # 节能汽机
        return render(request, 'myform/show_add_conservation_form.html', locals())
    elif type_id == '14':  # 励磁
        return render(request, 'myform/show_add_excitation_form.html', locals())
    elif type_id == '21':  # 震动
        return render(request, 'myform/show_add_shock_form.html', locals())
    elif type_id == '15':  # 锅炉压力容器管理
        return render(request, 'myform/show_add_pressure_form.html', locals())
    elif type_id == '1':  # 特种设备
        return render(request, 'myform/show_add_specialequipment_form.html', locals())
    elif type_id == '16':  # 计量
        return render(request, 'myform/show_add_metering_form.html', locals())
    elif type_id == '17':  # 电压质量
        return render(request, 'myform/show_add_voltagequality_form.html', locals())
    elif type_id == '18':  # 继电保护及安自装置
        return render(request, 'myform/show_add_protection_form.html', locals())
    elif type_id == '7':  # 节能(锅炉)
        return render(request, 'myform/show_add_energysavingboiler_form.html', locals())
    elif type_id == '19':  # 环保
        return render(request, 'myform/show_add_environmentalprotection_form.html', locals())
    elif type_id == '12':  # 化学
        return render(request, 'myform/show_add_chemistry_form.html', locals())


# 展示所有已填报表信息
def show_all_form(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    power2 = checkpower(16, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    state_up_power = '0'
    state_check_power = '0'
    state_back_power = '0'
    state_edit_power = '0'
    state_add_power = '0'
    state_plantcheck = '0'
    for power_msg in power2:
        if power_msg['key'] == '10':
            state_check_power = '1'
        if power_msg['key'] == '9':
            state_up_power = '1'
        if power_msg['key'] == '11':
            state_back_power = '1'
        if power_msg['key'] == '1':
            state_edit_power = '1'
        if power_msg['key'] == '12':
            state_add_power = '1'
        if power_msg['key'] == '13':
            state_plantcheck = '1'

    # if user.is_superuser:
    #     data = MyForm.objects.filter(~Q(state_num='0')).order_by('-created_at', '-powerplants_id')
    #     company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
    # else:
    #     if state_check_power == '1':
    #         company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
    if user.is_superuser:
        data = MyForm.objects.all().order_by('-created_at', '-powerplants_id')
        company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
        # 超级管理员状态下总数
        total_counts = MyForm.objects.all().order_by('-created_at', '-powerplants_id').count()
        summary_data = '汇总表'
    else:
        if state_check_power == '1':
            company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
        powerplan_id = PowerPlants.objects.get(powname=company).id
        # data = MyForm.objects.filter(powerplants_id=powerplan_id).order_by('-id')
        if state_add_power == '1' and state_plantcheck == '0':
            data = MyForm.objects.filter(powerplants_id=powerplan_id, create_person=user.myuser).order_by('-created_at',
                                                                                                          '-state_num')
        elif state_add_power == '1' and state_plantcheck == '1':
            data = MyForm.objects.filter(~Q(state_num='10') | Q(create_person=user.myuser),
                                         powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
        elif state_plantcheck == '1' and state_add_power == '0':
            data = MyForm.objects.filter(~Q(state_num='10'), powerplants_id=powerplan_id).order_by('-created_at',
                                                                                                   '-state_num')
        elif state_back_power == '1' and state_edit_power == '1':
            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0')).order_by(
                '-created_at', '-state_num')
        else:
            data = []

        summary_data = '不显示'
    supervise_list = SupervisionType.objects.all()

    for row in data:
        create_at = row.created_at.strftime('%Y-%m-%d')
        row.create_at = create_at



    # 分页
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page", "1")
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
    return render(request, 'show_form/form_watch_list.html', locals())


# 根据专业进入报表展示table界面
def show_one_form(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    power_id = request.GET.get('power_id')
    type_id = request.GET.get('type_id')
    time_is = request.GET.get('time_is')
    add_list_num = request.GET.get('add_list_num', '')
    if type_id == '13':  # 绝缘
        return render(request, 'show_form/watch_insulation_form.html', locals())
    elif type_id == '2':  # 金属
        return render(request, 'show_form/watch_metal_form.html', locals())
    elif type_id == '4':  # 热工
        return render(request, 'show_form/watch_hotman_form.html', locals())
    elif type_id == '6':  # 电测
        return render(request, 'show_form/watch_electrictest_form.html', locals())
    elif type_id == '3':  # 节能汽机
        return render(request, 'show_form/watch_conservation_form.html', locals())
    elif type_id == '14':  # 励磁
        return render(request, 'show_form/watch_excitation_form.html', locals())
    elif type_id == '21':  # 震动
        return render(request, 'show_form/watch_shock_form.html', locals())
    elif type_id == '15':  # 锅炉压力容器管理
        return render(request, 'show_form/watch_pressure_form.html', locals())
    elif type_id == '1':  # 特种设备
        return render(request, 'show_form/watch_specialequipment_form.html', locals())
    elif type_id == '16':  # 计量
        return render(request, 'show_form/watch_metering_form.html', locals())
    elif type_id == '17':  # 电压质量
        return render(request, 'show_form/watch_voltagequality_form.html', locals())
    elif type_id == '18':  # 继电保护及安自装置
        return render(request, 'show_form/watch_protection_form.html', locals())
    elif type_id == '7':  # 节能(锅炉)
        return render(request, 'show_form/watch_energysavingboiler_form.html', locals())
    elif type_id == '19':  # 环保
        return render(request, 'show_form/watch_environmentalprotection_form.html', locals())
    elif type_id == '12':  # 化学
        return render(request, 'show_form/watch_chemistry_form.html', locals())


# 展示所有汇总报表
def show_all_time(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    return render(request, 'remittance_data/remittance_table_show.html', locals())


# 汇总表显示
def remittance_show(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    data_years = request.GET.get('years')
    data_type = request.GET.get('month')

    db = pymysql.connect(
        host='192.168.104.212',
        port=3306, user='root',
        passwd='root', db='wang1127',
        charset='utf8')

    if '季度' in data_type:

        # 年份
        year = data_years
        # 季度
        quarter_1 = data_type[0]
        cursor = db.cursor()
        try:
            sql1_value = "select pvalues from myform_collect where (write_time=%s or write_time=%s or write_time=%s) and uid=%s"
        except:
            # 直接结束视图函数，返回异常
            print('月报表不存在')

        # data_list = []
        if data_type == '1季度':
            year_quarter1 = year + '-01'
            year_quarter2 = year + '-02'
            year_quarter3 = year + '-03'
            data_list = [year_quarter1, year_quarter2, year_quarter3]
            quarter = data_years + '年1季度'

            # data_list.append()
        elif data_type == '2季度':
            year_quarter1 = year + '-04'
            year_quarter2 = year + '-05'
            year_quarter3 = year + '-06'
            data_list = [year_quarter1, year_quarter2, year_quarter3]
            quarter = data_years + '年2季度'

        elif data_type == '3季度':
            year_quarter1 = year + '-07'
            year_quarter2 = year + '-08'
            year_quarter3 = year + '-09'
            data_list = [year_quarter1, year_quarter2, year_quarter3]
            quarter = data_years + '年3季度'

        else:
            year_quarter1 = year + '-10'
            year_quarter2 = year + '-11'
            year_quarter3 = year + '-12'
            data_list = [year_quarter1, year_quarter2, year_quarter3]
            quarter = data_years + '年4季度'
        # 季汇总数据列表
        quarter_data_list = []

        # 拼接季度字符串,示例：'2019--1':第一季度
        write_time = year + '--' + quarter_1

        # 将季度中三个月份的数据求平均之后存入列表中
        for i in range(1, 204):
            data_list1 = copy.deepcopy(data_list)
            data_list1.append(i)
            # print(data_list1)
            cursor.execute(sql1_value, data_list1)
            data_fetchall = cursor.fetchall()
            if len(data_fetchall) == 0:
                quarter_data_list.append('/')
            else:
                data = []
                for k in range(len(data_fetchall)):
                    data.append(data_fetchall[k][0])
                while '/' in data:
                    data.remove('/')
                nsum = 0
                if len(data) != 0:
                    for j in range(len(data)):
                        nsum += float(data[j])
                        datas = str(nsum / len(data))
                else:
                    datas = '/'
                if len(datas) > 5:
                    quarter_data_list.append(datas[:5])
                else:
                    quarter_data_list.append(datas)
        # print(len(quarter_data_list),quarter_data_list)

        # # 创建季度汇总表
        cursor.execute(
            "create table IF NOT EXISTS myform_collect_quarter(id int primary key auto_increment,write_time varchar(20),uid int,pvalues varchar(20))")
        db.commit()
        sql2_select = "select pvalues from myform_collect_quarter where write_time=%s"
        cursor.execute(sql2_select, [write_time])

        # 查找数据库，判断该季度的汇总数据是否已经存在，存在则更新，不存在则添加
        if cursor.fetchone() is None:
            for i in range(len(quarter_data_list)):
                sql2_collect = "insert into myform_collect_quarter(write_time,uid,pvalues) values(%s,%s,%s)"
                cursor.execute(sql2_collect, [write_time, i + 1, quarter_data_list[i]])
            db.commit()
        else:
            for i in range(len(quarter_data_list)):
                sql2_collect = "update myform_collect_quarter set pvalues=%s where write_time=%s and uid=%s"
                cursor.execute(sql2_collect, [quarter_data_list[i], write_time, i + 1])
            db.commit()
        cursor.close()
        db.close()
        res_id = 32403
        return render(request, 'remittance_data/one_table_show.html', locals())

    elif '月' in data_type:
        # begin_time1 = datetime.datetime.strptime(data_years + '-' + data_type[:2] + '-01', '%Y-%m-%d')
        # end_time1 = datetime.datetime.strptime(data_years + '-' + data_type[:2] + '-' + str(test(begin_time1)),
        #                                        '%Y-%m-%d')
        # query_type = '月'
        quarter = data_years + data_type[0:-1]
        # end_time = end_time1
        # begin_time = begin_time1

        index_target = ['预试计划完成情况列表', '绝缘缺陷消除率', '监督设备部件检验率', '缺陷消除率', '焊口检验率', '主机保护保护投入率投入率合计',
                        '模拟量控制系统投入率合计', '模拟量控制系统完好率合计', '保护投运率', '保护校验数', '保护正确动作率', '电测标准器具检验率',
                        '电测主要仪表检验率', '电测主要仪表调前合格率', '电测关口表检验合格率', '环保监督脱硫设备投运率合计',
                        '环保监督月除尘投运率合计']
        index_point = ['化学给水合格率合计', '化学凝结水合格率合计', '化学炉水合格率合计', '化学蒸汽合格率合计',
                       '化学补给水合格率合计', '化学循环水合格率合计', '化学水汽水质平均合格率合计',
                       '#99化学监督油质质量统计汽轮机油质合格率', '#99化学监督油质质量统计抗燃油油质合格率',
                       '化学氢气质量合格率合计', '环保监督烟尘达标排放率合计', '环保监督废水排放达标率合计']
        index_all = ['预试计划完成情况列表', '绝缘缺陷消除率', '监督设备部件检验率', '缺陷消除率', '焊口检验率', '主机保护保护投入率投入率合计',
                     '模拟量控制系统投入率合计', '模拟量控制系统完好率合计', '化学给水合格率合计', '化学凝结水合格率合计', '化学炉水合格率合计', '化学蒸汽合格率合计',
                     '化学补给水合格率合计', '化学循环水合格率合计', '化学水汽水质平均合格率合计',
                     '#99化学监督油质质量统计汽轮机油质合格率', '#99化学监督油质质量统计抗燃油油质合格率',
                     '化学氢气质量合格率合计', '保护投运率', '保护校验数', '保护正确动作率', '电测标准器具检验率',
                     '电测主要仪表检验率', '电测主要仪表调前合格率', '电测关口表检验合格率', '环保监督脱硫设备投运率合计',
                     '环保监督烟尘达标排放率合计', '环保监督月除尘投运率合计', '环保监督废水排放达标率合计'
                     ]

        write_time = data_years + '-' + data_type[0:-1]
        cursor = db.cursor()
        sql1_target = "select id from myform_target where powerplants_id=%s and `name`=%s"
        sql1_point = "select id from myform_point where powerplants_id=%s and `name`=%s"

        id_list, target_data_list = [], []
        for i in range(1, 7):
            for j in index_all:
                if j in index_target:
                    target_content1 = [i, j]
                    cursor.execute(sql1_target, target_content1)
                    id_list.append({'1': cursor.fetchone()[0]})
                else:
                    point_content1 = [i, j]
                    cursor.execute(sql1_point, point_content1)
                    id_list.append({'2': cursor.fetchone()[0]})

        sql2_target = "select pvalue from myform_targetdata where number_id=%s and write_time>=%s and write_time<=%s order by id desc limit 1"
        sql2_point = "select pvalue from myform_pointdata where number_id=%s and write_time>=%s and write_time<=%s order by id desc limit 1"

        for i in id_list:
            if '1' in i:
                target_content2 = [i['1'], write_time + '-01', write_time + '-31']
                cursor.execute(sql2_target, target_content2)
            else:
                target_content2 = [i['2'], write_time + '-01', write_time + '-31']
                cursor.execute(sql2_point, target_content2)

            try:
                data = cursor.fetchone()[0]
                if data == None:
                    data = '/'
                elif data == '':
                    data = '/'
            except:
                data = '/'
            target_data_list.append(data)

        data_list = []
        for i in range(29):
            content_data = [target_data_list[i], target_data_list[i + 29], target_data_list[i + 58],
                            target_data_list[i + 87], target_data_list[i + 116], target_data_list[i + 145]]
            while '/' in content_data:
                content_data.remove('/')
            nsum = 0
            if len(content_data) != 0:
                for j in range(len(content_data)):
                    nsum += float(content_data[j])
                    data = str(nsum / len(content_data))
            else:
                data = '/'
            if len(data) > 5:
                data_list.append(data[:5])
            else:
                data_list.append(data)

        data_list.extend(target_data_list)
        # 创建汇总表
        cursor.execute(
            "create table IF NOT EXISTS myform_collect(id int primary key auto_increment,write_time varchar(20),uid int,pvalues varchar(20))")
        db.commit()

        sql2_select = "select pvalues from myform_collect where write_time=%s"
        cursor.execute(sql2_select, [write_time])

        # 查找数据库，判断该月份的汇总数据是否已经存在，存在则更新，不存在则添加
        if cursor.fetchone() is None:
            for i in range(len(data_list)):
                sql2_collect = "insert into myform_collect(write_time,uid,pvalues) values(%s,%s,%s)"
                cursor.execute(sql2_collect, [write_time, i + 1, data_list[i]])
            db.commit()
        else:
            for i in range(len(data_list)):
                sql2_collect = "update myform_collect set pvalues=%s where write_time=%s and uid=%s"
                cursor.execute(sql2_collect, [data_list[i], write_time, i + 1])
            db.commit()
        cursor.close()
        db.close()
        res_id = 32396
        return render(request, 'remittance_data/one_table_show.html', locals())
        # return render(request, 'remittance_data/form_sum_show.html', locals())

    elif '半年' in data_type:

        # 年份
        year = data_years
        # 季度
        quarter_1 = data_type
        # 拼接季度字符串,示例：'2019上半年'
        write_time = year + quarter_1
        quarter = write_time
        cursor = db.cursor()
        try:
            sql1_value = "select pvalues from myform_collect where (write_time=%s or write_time=%s or write_time=%s or write_time=%s or write_time=%s or write_time=%s) and uid=%s"
        except:
            # 直接结束视图函数，返回异常
            print('月报表不存在')

        # data_list = []

        if quarter_1 == '上半年':
            year_quarter1 = year + '-01'
            year_quarter2 = year + '-02'
            year_quarter3 = year + '-03'
            year_quarter4 = year + '-04'
            year_quarter5 = year + '-05'
            year_quarter6 = year + '-06'
            data_list = [year_quarter1, year_quarter2, year_quarter3, year_quarter4, year_quarter5, year_quarter6]
            # data_list.append()
        else:
            year_quarter1 = year + '-07'
            year_quarter2 = year + '-08'
            year_quarter3 = year + '-09'
            year_quarter4 = year + '-10'
            year_quarter5 = year + '-11'
            year_quarter6 = year + '-12'
            data_list = [year_quarter1, year_quarter2, year_quarter3, year_quarter4, year_quarter5, year_quarter6]

        # 半年汇总数据列表
        quarter_data_list = []

        # 将半年中六个月份的数据求平均之后存入列表中
        for i in range(1, 204):
            data_list1 = copy.deepcopy(data_list)
            data_list1.append(i)
            # print(data_list1)
            cursor.execute(sql1_value, data_list1)
            data_fetchall = cursor.fetchall()
            if len(data_fetchall) == 0:
                quarter_data_list.append('/')
            else:
                data = []
                for k in range(len(data_fetchall)):
                    data.append(data_fetchall[k][0])
                while '/' in data:
                    data.remove('/')
                nsum = 0
                if len(data) != 0:
                    for j in range(len(data)):
                        nsum += float(data[j])
                        datas = str(nsum / len(data))
                else:
                    datas = '/'
                if len(datas) > 5:
                    quarter_data_list.append(datas[:5])
                else:
                    quarter_data_list.append(datas)
        # print(len(quarter_data_list),quarter_data_list)

        # # 创建半年汇总表
        cursor.execute(
            "create table IF NOT EXISTS myform_collect_harf_quarter(id int primary key auto_increment,write_time varchar(20),uid int,pvalues varchar(20))")
        db.commit()
        sql2_select = "select pvalues from myform_collect_harf_quarter where write_time=%s COLLATE utf8_unicode_ci"
        cursor.execute(sql2_select, [write_time])

        # 查找数据库，判断该半年的汇总数据是否已经存在，存在则更新，不存在则添加
        if cursor.fetchone() is None:
            for i in range(len(quarter_data_list)):
                sql2_collect = "insert into myform_collect_harf_quarter(write_time,uid,pvalues) values(%s,%s,%s)"
                cursor.execute(sql2_collect, [write_time, i + 1, quarter_data_list[i]])
            db.commit()
        else:
            for i in range(len(quarter_data_list)):
                sql2_collect = "update myform_collect_harf_quarter set pvalues=%s where write_time=%s and uid=%s"
                cursor.execute(sql2_collect, [quarter_data_list[i], write_time, i + 1])
            db.commit()
        cursor.close()
        db.close()

        res_id = 32407
        # print('end')
        return render(request, 'remittance_data/one_table_show.html', locals())

    elif data_type == '全年':

        year = data_years
        quarter = year + '年'
        cursor = db.cursor()
        try:
            sql1_value = "select pvalues from myform_collect_quarter where (write_time=%s or write_time=%s or write_time=%s or write_time=%s) and uid=%s"
        except:
            # 直接结束视图函数，返回异常
            print('季度表不存在')

        # data_list = []
        year_quarter1 = year + '--1'
        year_quarter2 = year + '--2'
        year_quarter3 = year + '--3'
        year_quarter4 = year + '--4'
        data_list = [year_quarter1, year_quarter2, year_quarter3, year_quarter4]

        # 季汇总数据列表
        quarter_data_list = []

        # 将四个季度中的数据求平均之后存入列表中
        for i in range(1, 204):
            data_list1 = copy.deepcopy(data_list)
            data_list1.append(i)
            # print(data_list1)
            cursor.execute(sql1_value, data_list1)
            data_fetchall = cursor.fetchall()
            if len(data_fetchall) == 0:
                quarter_data_list.append('/')
            else:
                data = []
                for k in range(len(data_fetchall)):
                    data.append(data_fetchall[k][0])
                while '/' in data:
                    data.remove('/')
                nsum = 0
                if len(data) != 0:
                    for j in range(len(data)):
                        nsum += float(data[j])
                        datas = str(nsum / len(data))
                else:
                    datas = '/'
                if len(datas) > 5:
                    quarter_data_list.append(datas[:5])
                else:
                    quarter_data_list.append(datas)
        # print(len(quarter_data_list),quarter_data_list)

        # 拼接季度字符串,示例：'2019--1':第一季度
        write_time = year
        # # 创建年度汇总表
        cursor.execute(
            "create table IF NOT EXISTS myform_collect_year(id int primary key auto_increment,write_time varchar(20),uid int,pvalues varchar(20))")
        db.commit()
        sql2_select = "select pvalues from myform_collect_year where write_time=%s"
        cursor.execute(sql2_select, [write_time])

        # 查找数据库，判断该年度的汇总数据是否已经存在，存在则更新，不存在则添加
        if cursor.fetchone() is None:
            for i in range(len(quarter_data_list)):
                sql2_collect = "insert into myform_collect_year(write_time,uid,pvalues) values(%s,%s,%s)"
                cursor.execute(sql2_collect, [write_time, i + 1, quarter_data_list[i]])
            db.commit()
        else:
            for i in range(len(quarter_data_list)):
                sql2_collect = "update myform_collect_year set pvalues=%s where write_time=%s and uid=%s"
                cursor.execute(sql2_collect, [quarter_data_list[i], write_time, i + 1])
            db.commit()
        cursor.close()
        db.close()
        res_id = 32404
        return render(request, 'remittance_data/one_table_show.html', locals())


'''
print(list_data)
hnfgs_data = []  # 河南分公司
kffd_data = []  # 开封发电分公司
nyrd_data = []  # 南阳热电有限责任公司
xyyx_data = []  # 新乡豫新发电有限责任公司
zzrq_data = []  # 郑州燃气发电公司
pdsrd_data = []  # 平顶山热电有限公司
pdrd_data = []  # 平东热电
hnfgs_data = list_data[0]
kffd_data = list_data[1]
nyrd_data = list_data[2]
xyyx_data = list_data[3]
zzrq_data = list_data[4]
pdsrd_data = list_data[5]
pdrd_data = list_data[6]
'''


# 分条件查询报表信息add
def form_search(request):
    action = 'list'
    menuid = '16'
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    now_time = datetime.datetime.now()
    first_day = datetime.datetime(now_time.year, now_time.month, 1)
    up_last = first_day - datetime.timedelta(days=1)
    last_month = up_last.strftime('%Y-%m-%d')[:7]
    month_now = now_time.strftime('%Y-%m-%d')[:7]

    state_up_power = '0'
    state_check_power = '0'
    state_back_power = '0'
    state_add_power = '0'
    del_power = '1'
    state_edit_power = '0'
    for power_msg in power:
        if power_msg['key'] == '10':
            state_check_power = '1'
        if power_msg['key'] == '9':
            state_up_power = '1'
        if power_msg['key'] == '11':
            state_back_power = '1'
        if power_msg['key'] == '12':
            state_add_power = '1'
        if power_msg['key'] == '13':
            state_plantcheck = '1'
        if power_msg['key'] == '1':
            state_edit_power = '1'

    # 获取需要查询的信息
    company_id = request.GET.get('company_id', '')
    # crate_time = request.GET.get('crate_time', '')
    crate_moon = request.GET.get('crate_moon', '')
    create_person = request.GET.get('create_person', '')
    create_state_num = request.GET.get('create_state', '')
    ptype = request.GET.get('ptype', '')

    if user.is_superuser or state_check_power == '1':
        company_list = Company.objects.all()
        if company_id == '' and crate_moon == '' and create_person == '' and create_state_num == '' and ptype == '':
            if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0')).order_by(
                    '-created_at', '-state_num')
            else:
                data = MyForm.objects.all().order_by('-created_at', '-powerplants_id')
            for row in data:
                create_at = row.created_at.strftime('%Y-%m-%d')
                row.create_at = create_at
            # 分页
            paginator = Paginator(data, 10)
            # 网页中的page值
            page = request.GET.get("page", "1")
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
            if user.is_superuser or state_check_power == '1':
                company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
            else:
                company_list = PowerPlants.objects.filter(powname=company.comname)  # 电厂列表（PowerPlants表）
            ptype_list = SupervisionType.objects.all()
            return render(request, 'myform/form_list.html', locals())

        if company_id != '':
            if create_state_num == '':
                if create_person == '':
                    if ptype == '':
                        if 25 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 25 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')

                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
            else:
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')

                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon)
                                                         | Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon)
                                                         | Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
        else:
            if create_state_num == '':
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date=crate_moon)).order_by('-created_at',
                                                                                           '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date=crate_moon)).order_by('-created_at',
                                                                                           '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date=crate_moon) | Q(
                                                             ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(
                                Q(form_date=crate_moon) | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                    '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person) | Q(
                                                             form_date=crate_moon)).order_by('-created_at',
                                                                                             '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(
                                Q(create_person__name__icontains=create_person) | Q(form_date=crate_moon)).order_by(
                                '-created_at', '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon)
                                                         | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon)
                                                         | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
            else:
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
    else:
        powerplan_id = PowerPlants.objects.get(powname=company.comname).id
        if create_state_num == '':
            if create_person == '':
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
            else:
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')

        else:
            if create_person == '':
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
            else:
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')

        company_list = [company]
    for row in data:
        create_at = row.created_at.strftime('%Y-%m-%d')
        row.create_at = create_at
    # 分页
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page", "1")
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
    if user.is_superuser or state_check_power == '1':
        company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
    else:

        company_list = PowerPlants.objects.filter(powname=company.comname)  # 电厂列表（PowerPlants表）
    ptype_list = SupervisionType.objects.all()
    return render(request, 'myform/form_list.html', locals())


# 分条件查询报表信息show
def form_search_show(request):
    action = 'list'
    menuid = '17'
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    power2 = checkpower(16, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    company = user.myuser.company
    now_time = datetime.datetime.now()
    first_day = datetime.datetime(now_time.year, now_time.month, 1)
    up_last = first_day - datetime.timedelta(days=1)
    last_month = up_last.strftime('%Y-%m-%d')[:7]
    month_now = now_time.strftime('%Y-%m-%d')[:7]

    state_up_power = '0'
    state_check_power = '0'
    state_back_power = '0'
    state_add_power = '0'
    del_power = '1'
    for power_msg in power2:
        if power_msg['key'] == '10':
            state_check_power = '1'
        if power_msg['key'] == '9':
            state_up_power = '1'
        if power_msg['key'] == '11':
            state_back_power = '1'
        if power_msg['key'] == '12':
            state_add_power = '1'
        if power_msg['key'] == '13':
            state_plantcheck = '1'

    # 获取需要查询的信息
    company_id = request.GET.get('company_id', '')
    # crate_time = request.GET.get('crate_time', '')
    crate_moon = request.GET.get('crate_moon', '')
    create_person = request.GET.get('create_person', '')
    create_state_num = request.GET.get('create_state', '')
    ptype = request.GET.get('ptype', '')

    if user.is_superuser or state_check_power == '1':
        # data = MyForm.objects.all().order_by('-id') __icontains
        company_list = Company.objects.all()
        if company_id == '' and crate_moon == '' and create_person == '' and create_state_num == '' and ptype == '':
            if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0')).order_by(
                    '-created_at', '-state_num')
            else:
                data = MyForm.objects.all().order_by('-created_at', '-powerplants_id')
            for row in data:
                create_at = row.created_at.strftime('%Y-%m-%d')
                row.create_at = create_at
            # 分页
            paginator = Paginator(data, 10)
            # 网页中的page值
            page = request.GET.get("page", "1")
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
            if user.is_superuser or state_check_power == '1':
                company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
            else:
                company_list = PowerPlants.objects.filter(powname=company.comname)  # 电厂列表（PowerPlants表）
            ptype_list = SupervisionType.objects.all()
            return render(request, 'show_form/form_watch_list.html', locals())

        if company_id != '':
            if create_state_num == '':
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')

                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         powerplants__id=company_id).order_by('-created_at',
                                                                                              '-powerplants_id')
            else:
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')

                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon),
                                                         powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon)
                                                         | Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date__icontains=crate_moon)
                                                         | Q(ptype__name__icontains=ptype), powerplants__id=company_id,
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
        else:
            if create_state_num == '':
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date=crate_moon)).order_by('-created_at',
                                                                                           '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date=crate_moon)).order_by('-created_at',
                                                                                           '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date=crate_moon) | Q(
                                                             ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(
                                Q(form_date=crate_moon) | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                    '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person) | Q(
                                                             form_date=crate_moon)).order_by('-created_at',
                                                                                             '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(
                                Q(create_person__name__icontains=create_person) | Q(form_date=crate_moon)).order_by(
                                '-created_at', '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon)
                                                         | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon)
                                                         | Q(ptype__name__icontains=ptype)).order_by('-created_at',
                                                                                                     '-powerplants_id')
            else:
                if create_person == '':
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                else:
                    if ptype == '':
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                    else:
                        if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                            data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                         Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
                        else:
                            data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                         Q(form_date=crate_moon),
                                                         Q(ptype__name__icontains=ptype),
                                                         state_num=create_state_num).order_by('-created_at',
                                                                                              '-powerplants_id')
    else:
        powerplan_id = PowerPlants.objects.get(powname=company.comname).id
        if create_state_num == '':
            if create_person == '':
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
            else:
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype),
                                                     powerplants_id=powerplan_id).order_by('-created_at', '-state_num')

        else:
            if create_person == '':
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
            else:
                if ptype == '':
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                else:
                    if 27 in request.session['role_id'] or 24 in request.session['role_id']:
                        data = MyForm.objects.filter(~Q(state_num='10') & ~Q(state_num='3') & ~Q(state_num='0'),
                                                     Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')
                    else:
                        data = MyForm.objects.filter(Q(create_person__name__icontains=create_person),
                                                     Q(form_date__icontains=crate_moon),
                                                     Q(ptype__name__icontains=ptype), powerplants_id=powerplan_id,
                                                     state_num=create_state_num).order_by('-created_at', '-state_num')

        company_list = [company]
    for row in data:
        create_at = row.created_at.strftime('%Y-%m-%d')
        row.create_at = create_at
    # 分页
    paginator = Paginator(data, 10)
    # 网页中的page值
    page = request.GET.get("page", "1")
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
    if user.is_superuser or state_check_power == '1':
        company_list = PowerPlants.objects.all()  # 电厂列表（PowerPlants表）
    else:

        company_list = PowerPlants.objects.filter(powname=company.comname)  # 电厂列表（PowerPlants表）
    ptype_list = SupervisionType.objects.all()
    return render(request, 'show_form/form_watch_list.html', locals())


# 更改报表状态
def state_change(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user = request.session.get('mylogin')
    form_id = request.GET.get('form_id', '')
    # create_state_num = request.POST.get('create_state')
    form_state = request.GET.get('form_state')
    form_obj = MyForm.objects.filter(id=form_id).first()  # 报表对象
    if form_state == '10':
        form_state = '草稿'
        state_num = '10'
    elif form_state == '0':
        form_state = '电厂未报送'
        state_num = '0'
    elif form_state == '1':
        form_state = '电厂已报送'
        state_num = '1'
    elif form_state == '2':
        form_state = '已审核'
        state_num = '2'
    elif form_state == '3':
        form_state = '已退回'
        state_num = '3'
    else:
        form_state = '草稿'
        state_num = '10'

    # 更改报表状态
    form_obj.state_name = form_state
    form_obj.state_num = state_num
    # print(form_obj.state_name,"==orm_obj.state_name")

    # form_obj.state_num=create_state_num
    #
    # if create_state_num == '0':
    #     state_name = '电厂未报送'
    # elif create_state_num == '1':
    #     state_name = '电厂报送'
    # elif create_state_num == '2':
    #     state_name = '退回'
    # else:
    #     state_name = '电厂未报送'
    # form_obj.state_name=state_name
    form_obj.edit_person = user.myuser
    form_obj.save()
    return HttpResponseRedirect('/myform/show_all_form/?action=list&menuid=16')
