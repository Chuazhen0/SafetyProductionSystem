from django.shortcuts import render,HttpResponseRedirect
from django.http import JsonResponse
from django.db import connection
from lbworkflow.models import Process,Node,ProcessCategory,App,Transition
from systemsettings.views import checkpower
from SafetyProductionSystem.settings import LBWF_APPS
from systemsettings.models import Job,Department,SupervisionType,Company,MyUser,User,MyGroup
from django.views.decorators.csrf import csrf_exempt
import uuid
from netstructure.models import NetStructure
from netstaff.models import NetStaff
from lbworkflow.core.datahelper import create_node
from lbworkflow.core.datahelper import create_category
from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_transition
from .models import MyProcess,MyNode, TaskHistory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from mon_plan_sum.models import MonPlanSum
from monworkexe.models import MonWorkExe
from regularworkplan.models import RegularWorkPlan, RegularWorkTask
from warning.models import WarningNotice
from warningre.models import WarningReceipt
from yearsum.models import YearSum
from yearplan.models import YearPlan
from weekworkplan.models import WeekWorkPlan
from weekworktask.models import WeekWorkTask
from django.db.models import Q

from lbworkflow.models import Task, ProcessInstance


# Create your views here.
def mywf_list(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    myprocess_list = []
    company_list = Company.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    app_names = LBWF_APPS.keys()

    if request.session['mylogin'].is_superuser == 1:
        myprocess_list_all = MyProcess.objects.all()
        for myprocess in myprocess_list_all:
            if myprocess.process.is_active == 1:
                myprocess_list.append(myprocess)
    else:
        myprocess_list = MyProcess.objects.filter(company=request.session['mylogin'].myuser.company, is_activate=1)
        # 分页
    paginator = Paginator(myprocess_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        myprocess_list = paginator.page(page)
    except PageNotAnInteger:
        myprocess_list = paginator.page(1)
    except EmptyPage:
        myprocess_list = paginator.page(paginator.num_pages)

    total_counts = MyProcess.objects.filter(company=request.session['mylogin'].myuser.company, is_activate=1).count()
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
    return render(request,'myworkflow/mywf_list.html',locals())

def mywf_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    company_list = Company.objects.all()
    supervision_major_list = SupervisionType.objects.all()
    app_names = LBWF_APPS.keys()

    company = request.GET.get('company','')
    supervision_major = request.GET.get('supervision_major','')
    appname = request.GET.get('appname','')
    myprocess_name = request.GET.get('myprocess_name','')

    if company == '':
        if supervision_major == '':
            if appname == '':
                myprocess_list = MyProcess.objects.filter(Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))
            else:
                myprocess_list = MyProcess.objects.filter(Q(app_name=appname),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))

        else:
            if appname == '':
                myprocess_list = MyProcess.objects.filter(Q(supervision_major_id=supervision_major),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))
            else:
                myprocess_list = MyProcess.objects.filter(Q(supervision_major_id=supervision_major),Q(app_name=appname),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))

    else:
        if supervision_major == '':
            if appname == '':
                myprocess_list = MyProcess.objects.filter(Q(company_id=company),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))
            else:
                myprocess_list = MyProcess.objects.filter(Q(company_id=company),Q(app_name=appname),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))

        else:
            if appname == '':
                myprocess_list = MyProcess.objects.filter(Q(company_id=company),Q(supervision_major_id=supervision_major),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))
            else:
                myprocess_list = MyProcess.objects.filter(Q(company_id=company),Q(supervision_major_id=supervision_major),Q(app_name=appname),Q(myprocess_name__icontains=myprocess_name),Q(is_activate=1))



    paginator = Paginator(myprocess_list, 10)
    # 网页中的page值
    page = request.GET.get("page",'1')
    try:
        # 传递HTML当前页对象
        myprocess_list = paginator.page(page)
    except PageNotAnInteger:
        myprocess_list = paginator.page(1)
    except EmptyPage:
        myprocess_list = paginator.page(paginator.num_pages)
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

    return render(request,'myworkflow/mywf_list.html',locals())


def wf_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user_obj = request.session.get('mylogin')

    place = user_obj.myuser.company
    company_list = MyUser.objects.filter(is_activate=1, company=place)

    creater = user_obj.id
    summary = request.GET.get('summary','')
    # if creater == '':
    # creater_number = MyUser.objects.get(id=creater).number
    # creater_1 = User.objects.filter(username=creater_number).first().id
    object_list = ProcessInstance.objects.filter(Q(created_by_id=creater),Q(summary__icontains=summary)).order_by('-id')

    paginator = Paginator(object_list, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    try:
        # 传递HTML当前页对象
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
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

    return render(request,'myworkflow/list_wf_search.html',locals())


def todo_search(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    user_obj = request.session.get('mylogin')
    # object_list = ProcessInstance.objects.filter()
    user = user_obj.id
    # print("222222222222",user)
    summary = request.GET.get('summary','')
    # object_list = ProcessInstance.objects.filter(Q(created_by_id=user),Q(summary__icontains=summary))
    object_1_list = ProcessInstance.objects.filter(Q(summary__icontains=summary))
    object_list = []
    for i in object_1_list:
        object_list.extend(Task.objects.filter(
        Q(user=user) | Q(agent_user=user),
        status='in progress',instance_id=i.id))
    paginator = Paginator(object_list, 10)
    # 网页中的page值
    page = request.GET.get("page", '1')
    try:
        # 传递HTML当前页对象
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
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

    return render(request,'myworkflow/todo_search.html',locals())



@csrf_exempt
def mywf_add(request):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    app_names = LBWF_APPS.keys()
    user = request.session['mylogin']
    place = request.session['mylogin'].myuser.company
    # job_list =['生技部主任','监督专责','执行人']
    node_name_list2 = {'放弃':'Given up','拒绝':'Rejected','草稿':'Draft','归档':'Completed'}
    supervision_major_list = SupervisionType.objects.all()
    if user.is_superuser:
        company_list = Company.objects.all()
    else:
        company_list = Company.objects.filter(comname=place.comname)
    first_node_list = ['Draft']
    next_node_list = ['Completed']
    app_object_list = RegularWorkPlan.objects.filter(place=place,is_activate=1)

    if request.method == 'GET':
        return render(request,'myworkflow/mywf_add.html',locals())
    elif request.method == 'POST':
        companyname = request.POST['companyname']  # 公司名称
        company = Company.objects.filter(comname=companyname).first()
        appname_key = request.POST['appname']
        appname = LBWF_APPS.get(appname_key)  # 获取app名称
        myprocess_name = request.POST['myprocess_name']
        supervision_major = request.POST['supervision_major']  # 监督专业
        mynum = request.POST['mynum']  # 判断是否新增节点
        app_object_id = request.POST['app_object_id']  # 获取定期工作策划编码
        netstructure = NetStructure.objects.filter(place=company, is_activate=1).first()   # 获取网络结构信息
        # print(NetStructure.objects.filter(place=company, is_activate=1),"=======111111")
        '''
        category = create_category('5f31d065-00cc-0100-beea-641f0a670010', '月度工作执行')
        process = create_process('monworkexe', 'Monworkexe', category=category)
        create_node('5f31d065-00a0-0100-beea-641f0a670010', process, 'Draft', status='拟定')
        create_node('5f31d065-00a0-0100-beea-641f0a670050', process, 'A1', operators='[cgl]')
        create_transition('5f31d065-00e0-0100-beea-641f0a670010', process, 'Draft,', 'A1') 
        '''
        category_list = ProcessCategory.objects.filter(is_active=1)
        mycategory=''
        category_namelist=[]
        for category in category_list:
            category_namelist.append(category.name)
        if appname_key in category_namelist:
            mycategory=ProcessCategory.objects.filter(name=appname_key).first()
        else:
            mycategory= create_category(uuid.uuid1(), appname_key)  #
        num=datetime.now().strftime("%Y%m%d%H%M%S")
        process = create_process(appname+num, appname.capitalize(), category=mycategory) # 创建process
        company = Company.objects.filter(comname=companyname).first()
        new_process=''
        if supervision_major == '0':
            new_process = MyProcess.objects.create(company=company,
                                                   myprocess_name=myprocess_name, process=process,
                                                   app_name=appname_key,app_object_id=app_object_id)  # 创建myprocess
        else:
            supervision_major = SupervisionType.objects.filter(name=supervision_major).first()
            new_process = MyProcess.objects.create(company=company,supervision_major=supervision_major,myprocess_name=myprocess_name,process=process,app_name=appname_key,app_object_id=app_object_id)  # 创建myprocess
        app = App.objects.filter(name=appname).first()
        node1=create_node(uuid.uuid1(), process, 'Draft', status='draft')
        node1.can_edit=1
        mynode = MyNode.objects.create(node_name='拟定', resource='无', myprocess=new_process,node=node1)
        node2=create_node(uuid.uuid1(), process, 'Given up', status='given up')
        mynode = MyNode.objects.create(node_name='放弃', resource='无', myprocess=new_process, node=node2)
        node3=create_node(uuid.uuid1(), process, 'Rejected', status='rejected')
        mynode = MyNode.objects.create(node_name='拒绝', resource='无', myprocess=new_process, node=node3)
        node4=create_node(uuid.uuid1(), process, 'Completed', status='completed')
        mynode = MyNode.objects.create(node_name='归档', resource='无', myprocess=new_process, node=node4)


        if mynum == '1': # 如果前端用户提交了节点信息
            node_name = request.POST['node_name']  # 节点名称
            job_name = request.POST['job_name']  # 岗位名称
            resource = request.POST['choice']  # 流程流转类型
            can_give_up = request.POST['can_give_up']  # 可以放弃
            can_edit = request.POST['can_edit']  # 可以编辑
            if resource == '0':
                resource = '监督网络'
                # 1为生技部主任  2.监督专责  3.执行人
                job_name = ''  # 工作流审批人变量
                person_name = request.POST.get('person_name', '')  # 审批人帐号
                job_name = person_name
                '''
                print(job_name,"====2=====22===")
                job = NetStaff.objects.filter(net_name=job_name,netstructure=netstructure).first()
                if job != None:
                    job = job.id
                userdata=[]
                cursor = connection.cursor()
                # 从角色，用户及其中间表中取他们相对应的关系
                cursor.execute(
                    "select myuser_id from netstaff_netstaff_user where netstaff_id = '%s' " % job)
                for row in cursor.fetchall():
                    usertable = {
                        'user': row[0],
                    }
                    userdata.append(usertable)
                cursor.close()
                myuser_list = userdata
                job_name = ''
                for user in myuser_list:
                    new_user = MyUser.objects.filter(id=user['user']).first()
                    job_name += new_user.user.username + ','
                job_name = job_name[:-1]
                '''
            elif resource == '1':
                resource = '行政岗位'
                '''
                # job = Job.objects.filter(jobname=job_name,company=company).first()
                job = Department.objects.filter(departname=job_name,company=company).first()
                # myuser_list = MyUser.objects.filter(jobname=job)
                myuser_list = MyUser.objects.filter(department=job)
                job_name=''
                for user in myuser_list:
                    job_name += user.user.username+','
                job_name = job_name[:-1]'''

                job_name = ''  # 工作流审批人变量
                person_name = request.POST.get('person_name', '')  # 审批人
                job_name = person_name
            elif resource == '2':
                resource = '审批人'
                '''
                job_name = MyUser.objects.filter(name=job_name).first().user.username
                '''
                job_name = ''  # 工作流审批人变量
                person_name = request.POST.get('person_name', '')  # 审批人帐号
                job_name = person_name

            if resource == '3':   # 如果选择是责任组
                resource = '责任组'
                job_name = ''  # 工作流审批人变量
                duty_group_id = request.POST.get('duty_group_name', '')  # 责任组id
                # 获取该责任组的下属人员
                duty_group_obj = MyGroup.objects.filter(id=duty_group_id).first()   # 责任组对象
                duty_user_obj_list = duty_group_obj.duty_user.all()  # 责任人员列表
                operators_job_str = ''
                for duty_user_obj in duty_user_obj_list:
                    operators_job_str += '[%s],' % duty_user_obj.number   # 形成工作流模块需要的数据形式   [xxx],[xxxx],[xxxx]
                operators_job_str = operators_job_str[:-1]   # 去除字符串最后的逗号

                node = create_node(uuid.uuid1(), process, node_name, operators='%s' % operators_job_str)
                node.can_edit = can_edit
                node.can_give_up = can_give_up

                mynode = MyNode.objects.create(node_name=node_name, resource=resource, myprocess=new_process,operators_job='%s' % operators_job_str, node=node)
                mynode.save()
            else:
                node = create_node(uuid.uuid1(), process, node_name, operators='[%s]' % job_name)
                node.can_edit = can_edit
                node.can_give_up = can_give_up
                mynode = MyNode.objects.create(node_name=node_name,resource=resource,myprocess=new_process,operators_job='[%s]'%job_name,node=node)
                mynode.save()
            # 保存信息到transition表
            create_transition(uuid.uuid1(), process, 'Draft',node_name)
            create_transition(uuid.uuid1(), process, node_name,'Completed')
            # print("33333")
        elif mynum == '0': # 未提交节点信息，只提交工作流程
            # print("44444")
            pass
        return HttpResponseRedirect('/wf/'+str(new_process.id)+'/mywf_detail/?action=new&menuid=47')


@csrf_exempt
def mywf_detail(request,p_id):
    action = request.GET.get('action')
    action = 'new'
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    job_list = ['生技部主任', '监督专责', '执行人']
    myprocess = MyProcess.objects.get(id=p_id)
    mynode_list = []
    node_list = MyNode.objects.filter(myprocess=myprocess).exclude(operators_job=' ')
    transition_list = Transition.objects.filter(is_active=1,process=myprocess.process) # 节点连接
    for mynode in node_list:
        if mynode.node.is_active == 1:
            user_data = MyUser.objects.filter(number=mynode.operators_job[1:-1]).first()
            # mynode.operators_job = user_data.jobname.jobname
            # mynode.operators_job = Job.objects.filter()
            mynode_list.append(mynode)
    return render(request, 'myworkflow/mywf_detail2.html', locals())
def mywf_delete(request,p_id):
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    myprocess = MyProcess.objects.filter(id=p_id).first()
    myprocess.is_activate = 0    # 删除myprocess表中的信息
    myprocess.save()
    myprocess.process.is_active=0   # 删除process表中的信息
    myprocess.process.save()
    node_list = Node.objects.filter(process=myprocess.process,is_active=1)
    for node in node_list:
        node.is_active=0
        node.save()
    mynode_list = MyNode.objects.filter(myprocess=myprocess)
    for mynode in mynode_list:
        mynode.node.is_active=0
        mynode.node.save()
    return HttpResponseRedirect('/wf/mywf_list/?action=list&menuid=47')

# 根据用户选项（监督网络结构/行政岗位/指定人）返回选择数据列表
@csrf_exempt
def mywf_checkjob(request):
    num = request.POST['num']
    companyname = request.POST['company']
    company = Company.objects.filter(comname=companyname)
    if num == '1': # 行政岗位
        job_list=[]
        job_list2 = Department.objects.filter(company=company[0])
        for job in job_list2:
            job_list.append(job.departname)
        return JsonResponse({"job_list":list(job_list)})
    elif num == '0': # 监督网络结构
        # 找到监督网络结构
        #netstructure_list_obj1 = NetStructure.objects.filter(place=company, is_activate=1)   # 对应电厂监督网络对象列表
        netstructure_list_obj = NetStructure.objects.filter(is_activate=1,place__comname=companyname)   # 对应电厂监督网络对象列表
        netstructure_list = []
        # print(netstructure_list_obj1,"=======netstructure_list_obj")
        for net in netstructure_list_obj:
            net_dict = {'net_num': net.number,
                        'net_desc': net.desc}
            netstructure_list.append(net_dict)
        job_list=['生技部主任','监督专责','执行人']
        job_list = [{'job_num':'1','job_name':'生技部主任'},
                    {'job_num':'2','job_name':'监督专责'},
                    {'job_num':'3','job_name':'执行人'}]
        re_msg = [netstructure_list, job_list]
        return JsonResponse({"re_msg": re_msg})
    elif num =='2':# 指定人
        user_list_obj = MyUser.objects.filter(company=company[0],is_activate=1)
        user_list=[]
        '''
        for myuser in myuser_list:
                job_list.append(myuser.name)'''
        for user in user_list_obj:
            user_dic = {'user_num': user.number,  # 用户帐号，用于保存至工作流引擎
                        'user_name': user.name}  # 用户名，显示用
            user_list.append(user_dic)

        return JsonResponse({"user_list":user_list})
    elif num =='3':   # 责任组
        duty_group_list_obj = MyGroup.objects.filter(place=company[0])
        duty_group_list=[]
        for duty_group in duty_group_list_obj:
            duty_group_dic = {'duty_group_id': duty_group.id,  # 责任组id
                              'duty_group_name': duty_group.name}   # 责任组名
            duty_group_list.append(duty_group_dic)
        #print(duty_group_list)
        return JsonResponse({"duty_group_list": duty_group_list})



# 根据岗位/部门查询对应用户列表返回
@csrf_exempt
def mywf_get_user_list(request):
    # 获取部门名称
    department = request.POST['department']
    # 获取部门所属电厂
    companyname = request.POST['company']
    company = Company.objects.filter(comname=companyname)  # 电厂对象
    # 获取用户对象列表
    job_list = ['1', '2', '3']
    if department in job_list:   # 监督专业下的岗位
        # 查询当前监督网络中的相关用户
        net_num= request.POST['net_num']
        # 获取监网络结构信息
        net_msg = NetStructure.objects.filter(number=net_num).first()  # 网络结构信息表
        netstaff_obj_list = NetStaff.objects.filter(netstructure=net_msg,net_name=department)  # 网络人员维护
        # 查询网络人员对应的用户
        user_list = []  # 用户列表
        for netstaff in netstaff_obj_list:  # 循环网络人员对象
            cursor = connection.cursor()
            # 从角色，用户及其中间表中取他们相对应的关系
            cursor.execute(
                "select myuser_id from netstaff_netstaff_user where netstaff_id = '%s' " % netstaff.id)
            user_id_list = cursor.fetchall()   # 用户id列表
            for user in user_id_list:
                new_user = MyUser.objects.filter(id=user[0]).first()
                user_dic = {'user_num': new_user.number,  # 用户帐号，用于保存至工作流引擎
                            'user_name': new_user.name}  # 用户名，显示用
                if user_dic in user_list:
                    pass
                else:
                    user_list.append(user_dic)
        return JsonResponse({"user_list": user_list})


    else:   # 部门名称
        user_list_obj = MyUser.objects.filter(company=company[0],is_activate=1,department__departname=department)
        user_list = []
        for user in user_list_obj:
            user_dic = {'user_num': user.number,   # 用户帐号，用于保存至工作流引擎
                        'user_name': user.name}    # 用户名，显示用
            user_list.append(user_dic)
        return JsonResponse({"user_list": user_list})



@csrf_exempt
def node_add(request,pp_id):
    user = request.session['mylogin']
    myprocess = MyProcess.objects.filter(id=pp_id).first()
    mynum  = request.POST['mynum']
    # print(myprocess.company,'myprocess.company')
    netstructure = NetStructure.objects.filter(place=myprocess.company,is_activate=1).first()  # 查询网络结构信息
    if mynum == '1':  # 如果前端用户提交了节点信息
        node_name = request.POST['node_name']  # 节点名称
        job_name = request.POST['job_name']  # 岗位名称
        resource = request.POST['choice']  # 流程流转类型
        can_give_up = request.POST['can_give_up']  #
        can_edit = request.POST['can_edit']  #
        if resource == '0':
            resource = '监督网络'
            job_name = ''  # 工作流审批人变量
            person_name = request.POST.get('person_name', '')  # 审批人帐号
            job_name = person_name
            '''
            # 1为生技部主任  2.监督专责  3.执行人
            if job_name == '生技部主任':
                job_name = 1
            if job_name == '监督专责':
                job_name = 2
            if job_name == '执行人':
                job_name = 3
            # print(job_name)
            # print(netstructure)
            # print(NetStructure.objects.filter(place=myprocess.company,is_activate=1))
            job = NetStaff.objects.filter(net_name=job_name, netstructure=netstructure).first()  # 查询网络人员
            # print(job,"==========2222222")
            if job != None:
                job = job.id
            userdata = []
            cursor = connection.cursor()
            # 从角色，用户及其中间表中取他们相对应的关系
            cursor.execute(
                "select myuser_id from netstaff_netstaff_user where netstaff_id = '%s' " % job)
            for row in cursor.fetchall():
                usertable = {
                    'user': row[0],
                }
                userdata.append(usertable)
            cursor.close()
            myuser_list = userdata
            job_name = ''
            for user in myuser_list:
                new_user = MyUser.objects.filter(id=user['user']).first()
                job_name += new_user.user.username + ','
            job_name = job_name[:-1]
            '''
        elif resource == '1':
            resource = '行政岗位'
            job_name = ''  # 工作流审批人变量
            person_name = request.POST.get('person_name', '')  # 审批人
            job_name = person_name
        elif resource == '2':
            resource = '审批人'
            '''
            job_name = MyUser.objects.filter(name=job_name).first().user.username
            '''
            job_name = ''  # 工作流审批人变量
            person_name = request.POST.get('person_name', '')  # 审批人
            job_name = person_name
        if resource == '3':  # 如果选择是责任组
            resource = '责任组'
            job_name = ''  # 工作流审批人变量
            duty_group_id = request.POST.get('duty_group_name', '')  # 责任组id
            # 获取该责任组的下属人员
            duty_group_obj = MyGroup.objects.filter(id=duty_group_id).first()  # 责任组对象
            duty_user_obj_list = duty_group_obj.duty_user.all()  # 责任人员列表
            operators_job_str = ''
            for duty_user_obj in duty_user_obj_list:
                operators_job_str += '[%s],' % duty_user_obj.number  # 形成工作流模块需要的数据形式   [xxx],[xxxx],[xxxx]
            operators_job_str = operators_job_str[:-1]  # 去除字符串最后的逗号

            node = create_node(uuid.uuid1(), myprocess.process, node_name, operators='%s' % operators_job_str)
            node.can_edit = can_edit
            node.can_give_up = can_give_up

            mynode = MyNode.objects.create(node_name=node_name, resource=resource, myprocess=myprocess,operators_job='%s' % operators_job_str, node=node)
            mynode.save()
        else:
            node = create_node(uuid.uuid1(), myprocess.process, node_name, operators='[%s]'%job_name)
            node.can_edit = can_edit
            node.can_give_up = can_give_up
            mynode = MyNode.objects.create(node_name=node_name, resource=resource, myprocess=myprocess,operators_job='[%s]'%job_name, node=node)
            mynode.save()
        mytransition_list  = Transition.objects.filter(is_active=1,process=myprocess.process)
        # if mytransition_list == None:
        if len(mytransition_list) == 0:
            create_transition(uuid.uuid1(), myprocess.process, 'Draft', node_name)   # 草稿
            create_transition(uuid.uuid1(), myprocess.process, node_name, 'Completed')   # 完成
        else:
            for transition in mytransition_list:
                if transition.output_node.name=='Completed':    # 如果最后一个节点‘完成’节点
                    transition.output_node = node    # 将最后一个节点变成新增加的节点
                    transition.save()   # 保存节点
                    create_transition(uuid.uuid1(), myprocess.process, node_name, 'Completed' )   # 创建新的‘完成’节点


    elif mynum == '0':  # 未提交节点信息，只提交工作流程
        pass
    return HttpResponseRedirect('/wf/' + str(myprocess.id) + '/mywf_detail/?action=new&menuid=47')

def node_delete(request,node_id):
    node_obj = MyNode.objects.filter(id=node_id).first()
    myprocess = node_obj.myprocess  # 获取节点所属的工作流对象

    # 找到当前节点，从transition表中删除该节点编号，将上一节点的下一个节点改为当前节点的下一各节点
    # 查询过度表中结束节点id为要删除的节点id的信息    过度信息1
    cursor = connection.cursor()
    cursor.execute(
        "select id,input_node_id from lbworkflow_transition where output_node_id = '%s' " % node_id)
    node_msg = cursor.fetchall()  # 过度表中结束节点id为要删除的节点id的信息
    node_msg_id = node_msg[0][0]   # 该过度信息的id
    node_msg_in = node_msg[0][1]   # 该过度信息的上一个节点id

    # 查询结束节点为node_msg_in的过度信息    过度信息2
    cursor.execute(
        "select id,output_node_id from lbworkflow_transition where input_node_id = '%s' " % node_id)
    node_msg2 = cursor.fetchall()
    node_msg2_id = node_msg2[0][0]
    node_msg2_out = node_msg2[0][1]

    # 将过度信息1删除，并将过度信息1的开始节点id保存到过度信息2的开始节点信息
    cursor.execute(
        "update lbworkflow_transition set is_active = 0 where id = '%s' " % (node_msg_id))
    cursor.execute(
        "update lbworkflow_transition set input_node_id = '%s' where id = '%s' " % (node_msg_in, node_msg2_id))


    # 删除节点信息
    mynode_obj = MyNode.objects.filter(id=node_id).first()  # 获取自建节点表对象
    mynode_obj.is_activate = 0  # 修改为不活动状态
    mynode_obj.save()
    mynode_obj.node.is_active = 0  # 修改为不活动状态
    mynode_obj.node.save()

    return HttpResponseRedirect('/wf/' + str(myprocess.id) + '/mywf_detail/?action=new&menuid=47')


@csrf_exempt
def node_edit(request,node_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 根据节点id先查询出mynode表中的数据，修改相关值，再查询关联的node表，修改node表中的数据
    # 用户可以编辑节点名称和操作人
    mynode_obj = MyNode.objects.filter(id=node_id).first()  # 获取自建节点表对象
    myprocess = mynode_obj.myprocess  # 获取节点所属的工作流对象
    if request.method == 'GET':
        # 查询出对应节点的相关信息
        node_person = MyUser.objects.filter(number=mynode_obj.operators_job[1:-1]).first()  # 获取节点审批人对象
        return render(request, 'myworkflow/mywf_node_edit.html', {"mynode_obj":mynode_obj,
                                                                  "action": action,
                                                                  "menuid": menuid,
                                                                  "myprocess": myprocess,
                                                                  "node_person": node_person})
    elif request.method == 'POST':
        node_name = request.POST.get('node_name', '')  # 获取前端节点名称
        mynode_obj = MyNode.objects.filter(id=node_id).first()  # 获取自建节点表对象
        resource = request.POST.get('choice','')  # 流程流转类型

        if resource == '3':  # 如果选择是责任组
            duty_group_id = request.POST.get('duty_group_name', '')  # 责任组id
            # 获取该责任组的下属人员
            duty_group_obj = MyGroup.objects.filter(id=duty_group_id).first()  # 责任组对象
            duty_user_obj_list = duty_group_obj.duty_user.all()  # 责任人员列表
            operators_job_str = ''
            for duty_user_obj in duty_user_obj_list:
                operators_job_str += '[%s],' % duty_user_obj.number  # 形成工作流模块需要的数据形式   [xxx],[xxxx],[xxxx]
            operators_job_str = operators_job_str[:-1]  # 去除字符串最后的逗号
            mynode_obj.node_name = node_name  # 修改mynode表中的节点名
            mynode_obj.operators_job = "%s" % operators_job_str  # 修改mynode表中的节点审批人
            mynode_obj.save()
            mynode_obj.node.name = node_name  # 修改node表中的节点名
            mynode_obj.node.operators = "%s" % operators_job_str  # 修改node表中的节点审批人
        else:
            node_person = request.POST.get('person_name', '')  # 获取前端节点名称

            mynode_obj.node_name = node_name  # 修改mynode表中的节点名
            mynode_obj.operators_job = "[%s]" % node_person # 修改mynode表中的节点审批人
            mynode_obj.save()
            mynode_obj.node.name = node_name   # 修改node表中的节点名
            mynode_obj.node.operators = "[%s]" % node_person  # 修改node表中的节点审批人
        mynode_obj.node.save()


        return HttpResponseRedirect('/wf/' + str(myprocess.id) + '/mywf_detail/?action=new&menuid=47')


def ajax_search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', None)
        if keyword:
            count = RegularWorkPlan.objects.filter(work_content__contains=keyword).count()
            data = {'count': count, }
            return JsonResponse(data)


# 工作流历史记录
def wf_history(request,process_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取审批记录对象
    history_obj_list = TaskHistory.objects.filter(process_id=process_id)
    list1 = []
    if history_obj_list:
        for re in history_obj_list:
            list1.append(re.node_name)
    process = ProcessInstance.objects.filter(id=process_id)
    # 根据process_id 查出ProcessInstance
    list3 = []
    if process:
        res_node = Node.objects.filter(process_id=process[0].process_id,status="in progress")
        # 查出相关联的节点
        list2 = []
        for res in res_node:
            list2.append(res.name)
        res_node = [his for his in list2 if his not in list1]
        # res_node 查出所有未审批的节点名
        list3 = []
        for res in res_node:
            node = Node.objects.get(process_id=process[0].process_id,name=res)
            list3.append({"name":node.name,"operators":node.operators,"type":'未审批'})
    return render(request, 'myworkflow/wf_history.html', {"action": action,'list3':list3,
                                                          "menuid": menuid,
                                                          "history_obj_list": history_obj_list})

def todo_history(request,process_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # 获取审批记录对象
    history_obj_list = TaskHistory.objects.filter(process_id=process_id)
    return render(request, 'myworkflow/wf_history.html', {"action": action,
                                                          "menuid": menuid,
                                                          "history_obj_list": history_obj_list})


# 根据流程id查询对应的任务完成情况描述信息
@csrf_exempt
def get_complete_desc(request):
    proins_id = request.POST.get('proins_id','0')   # 获取流程id
    processinstance_obj = ProcessInstance.objects.filter(id=proins_id).first()
    process_type = str(processinstance_obj.process)  # 流程类型  Monworkexe:月度工作执行
    # print(process_type,"====")
    if process_type == 'Monworkexe':  # 月度工作执行
        complete_desc_obj = MonWorkExe.objects.filter(pinstance_id=proins_id).first()
        re_dic = {'complete_desc': complete_desc_obj.execute_desc}   # 查询对应的完成描述信息
    elif process_type == 'Mon_plan_sum':  # 月度计划
        # complete_desc_obj = MonPlanSum.objects.filter(pinstance_id=proins_id).first()
        # re_dic = {'complete_desc': complete_desc_obj.desc}  # 查询对应的完成描述信息
        re_dic = {'complete_desc': '无'}  # 查询对应的完成描述信息  计划类无完成情况描述
    elif process_type == 'Warning':  # 告警通知
        #complete_desc_obj = WarningNotice.objects.filter(pinstance_id=proins_id).first()
        # re_dic = {'complete_desc': complete_desc_obj.title}  # 查询对应的完成描述信息
        re_dic = {'complete_desc': '无'}  # 查询对应的完成描述信息 计划类无完成情况描述
    elif process_type == 'Warningre':  # 告警回执
        complete_desc_obj = WarningReceipt.objects.filter(pinstance_id=proins_id).first()
        re_dic = {'complete_desc': complete_desc_obj.result}  # 查询对应的完成描述信息
    elif process_type == 'Yearsum':  # 年度总结
        # complete_desc_obj = YearSum.objects.filter(pinstance_id=proins_id).first()
        # re_dic = {'complete_desc': complete_desc_obj.result}  # 查询对应的完成描述信息
        re_dic = {'complete_desc': '无'}  # 查询对应的完成描述信息 年度总结类无完成情况描述
    elif process_type == 'Yearplan':  # 年度计划
        re_dic = {'complete_desc': '无'}  # 查询对应的完成描述信息 年度计划类无完成情况描述
    elif process_type == 'Weekworktask':  # 周期检测
        complete_desc_obj = WeekWorkTask.objects.filter(pinstance_id=proins_id).first()
        re_dic = {'complete_desc': complete_desc_obj.result}  # 查询对应的完成描述信息
    else:  # 定期工作
        complete_desc_obj = RegularWorkTask.objects.filter(pinstance_id=proins_id).first()
        re_dic = {'complete_desc': complete_desc_obj.result}   # 查询对应的完成描述信息
    return JsonResponse(re_dic)

# 根据用户帐号查询用户名
@csrf_exempt
def get_username(request):
    user_num_list = request.POST.get('user_num','')   # 获取用户帐号
    # print(user_num_list)
    if ', ' in user_num_list:
        user_num_list = user_num_list.split(', ')
    else:
        user_num_list = user_num_list.split(',')
    # 查询用户名
    try:
        user_obj_name = ''
        for user_num in user_num_list:
            user_obj = MyUser.objects.filter(number=user_num.strip()).first()
            user_obj_name += "%s," % user_obj.name
    except:
        user_obj_name = '无'
    re_dic = {'username': user_obj_name[:-1]}
    # print(re_dic)
    return JsonResponse(re_dic)


# 进入审批详情页，查看工作内容，进行通过或驳回操作
def wf_approval(request, task_id, pro_ins_id):
    action = request.GET.get('action')
    menuid = request.GET.get('menuid')
    power = checkpower(menuid, request.session['mylogin'], request.session['role_id'])
    request.session['powerdata'] = power
    # transition_name = 'Agree'
    task_list = Task.objects.filter(id=task_id)  # 获取流程信息
    # 获取定期工作内容和完成情况
    processinstance_obj = ProcessInstance.objects.filter(id=pro_ins_id).first()
    process_type = str(processinstance_obj.process)  # 流程类型  Monworkexe:月度工作执行
    if process_type == 'Monworkexe':  # 月度工作执行
        mon_work_exe_obj = MonWorkExe.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '1'
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              # "transition_name": transition_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "mon_work": mon_work_exe_obj,
                                                                              "process_type_code": process_type_code})
    elif process_type == 'Mon_plan_sum':
        mon_plan_sum_obj = MonPlanSum.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '2'  # 月度计划
        try:
            file_name = mon_plan_sum_obj.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "file_name": file_name,
                                                                              # "transition_name": transition_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "mon_plan_sum": mon_plan_sum_obj,
                                                                              "process_type_code": process_type_code})

    elif process_type == 'Warning':
        warning_notice = WarningNotice.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '3'  # 告警通知
        try:
            file_name = warning_notice.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "processinstance": processinstance_obj,
                                                                              "file_name": file_name,
                                                                              "data": warning_notice,
                                                                              "process_type_code": process_type_code})

    elif process_type == 'Warningre':
        warning_receipt = WarningReceipt.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '4'  # 告警回执
        try:
            file_name = warning_receipt.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "file_name": file_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "data": warning_receipt,
                                                                              "process_type_code": process_type_code})
    elif process_type == 'Yearsum':  # 年度总结
        yearsum_obj = YearSum.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '5'  # 年度总结
        try:
            file_name = yearsum_obj.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "file_name": file_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "year_sum": yearsum_obj,
                                                                              "process_type_code": process_type_code})

    elif process_type == 'Yearplan':  # 年度计划
        yearplan_obj = YearPlan.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '6'  # 年度计划
        try:
            file_name = yearplan_obj.enclosure.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "file_name": file_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "year_plan": yearplan_obj,
                                                                              "process_type_code": process_type_code})
    elif process_type == 'Weekworktask':  # 周期检测计划
        weekworktask_obj = WeekWorkTask.objects.filter(pinstance_id=pro_ins_id).first()
        process_type_code = '7'  # 周期检测计划
        try:
            week_plan_file_name = weekworktask_obj.plan.enclosure.name.split('/')[1]   # 周期检测计划附件名
            week_task_file_name = weekworktask_obj.enclosure.name.split('/')[1]   # 周期检测计划完成情况名
        except:
            week_plan_file_name = ''
            week_task_file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "week_plan_file_name": week_plan_file_name,
                                                                              "week_task_file_name": week_task_file_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "weekworktask_obj": weekworktask_obj,
                                                                              "process_type_code": process_type_code})

    else:
        process_type_code = '10'  # 定期工作  Regularworkplan
        regular_work_task_obj = RegularWorkTask.objects.filter(pinstance_id=processinstance_obj.id).first()  # 工作任务对象
        # work_result = regular_work_task_obj.result   # 工作完成情况
        # regular_work_plan_obj = regular_work_task_obj.regularwork   # 获取定期工作内容
        try:
            file_name = regular_work_task_obj.enclosure_file.name.split('/')[1]
        except:
            file_name = ''
        return render(request, 'myworkflow/mywf_batch_detail_approval.html', {"action": action,
                                                                              "task_list": task_list,
                                                                              "file_name": file_name,
                                                                              # "transition_name": transition_name,
                                                                              "processinstance": processinstance_obj,
                                                                              "regularworktask": regular_work_task_obj,
                                                                              "process_type_code": process_type_code})