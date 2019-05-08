from regularworkplan.models import RegularWorkPlan
from SafetyProductionSystem.settings import CRONJOBS
from django.core.management import call_command
from weekworkplan.cron import weekworkplan_test


def create_task(myid):  # 生成空的定期工作任务记录
    regular_plan= RegularWorkPlan.objects.filter(id=myid).first()
    regular_plan.create_task()


def test():
    regularworkplan_list = RegularWorkPlan.objects.filter(is_activate=1)
    for regularplan in regularworkplan_list:
        # print(regularplan.id)
        new_job = ''
        if regularplan.weekend_desc == '小时':
            # print('小时')
            if regularplan.num2 == '':
                regularplan.num2 = 1
            new_job = ('%s */%s * * *' % (regularplan.num2, regularplan.num1), 'regularworkplan.cron.create_task', [],{'myid': regularplan.id})
            # new_job = ('*/1 * * * *', 'regularworkplan.cron.create_task', [],{'myid': regularplan.id})

        elif regularplan.weekend_desc == '天':
            # print('天')
            if regularplan.num2 == '':
                regularplan.num2 = 1
            new_job = ('0 %s */%s * *' % (regularplan.num2, regularplan.num1), 'regularworkplan.cron.create_task', [], {'myid': regularplan.id}
                       )
        elif regularplan.weekend_desc == '周':
            # print('周')
            if regularplan.num2 == '':
                regularplan.num2 = 1
            else:
                pass
            new_job = ('0 0 * * */%s,%s' % (regularplan.num1, regularplan.num2), 'regularworkplan.cron.create_task', [], {'myid': regularplan.id}
                       )
        elif regularplan.weekend_desc == '月':
            # print('月')
            if regularplan.num2 == '':
                regularplan.num2 = 1
            new_job = ('0 0 * */%s,%s *' % (regularplan.num1, regularplan.num2), 'regularworkplan.cron.create_task', [], {'myid': regularplan.id}
                       )
        elif regularplan.weekend_desc == '年':
            # print('年')
            if regularplan.num2 == '':
                regularplan.num2 = 1

            new_job = (
                '0 0 * */%s,%s *' % (int(regularplan.num1) * 12, regularplan.num2), 'regularworkplan.cron.create_task', [], {'myid': regularplan.id}
            )
        elif regularplan.weekend_desc == '一次性工作计划':
            new_job = ()

        CRONJOBS.append(new_job)
        # list(set(CRONJOBS))
        # print('添加定期工作任务成功！')
        from django_crontab.management.commands import crontab
    # CRONJOBS[0], CRONJOBS[-1] = CRONJOBS[-1], CRONJOBS[0]
    call_command('crontab', 'add')
    # print('crontab add 完毕！')
    weekworkplan_test()







