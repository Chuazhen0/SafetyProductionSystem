from weekworkplan.models import WeekWorkPlan
from SafetyProductionSystem.settings import CRONJOBS
from django.core.management import call_command


def create_task(myid):  # 生成空的周期工作任务记录
    week_plan= WeekWorkPlan.objects.filter(id=myid).first()
    week_plan.create_task()


'''
    时间设置格式说明
    0   7   *    *   *    
    分  时  日   月   周   
    假如，想每隔2分钟执行以此或者想在每天的6,12,18点执行，可以通过“/”和“，”来设置

'''

def weekworkplan_test():
    weekworkplan_list = WeekWorkPlan.objects.filter(is_activate=1)
    for weekplan in weekworkplan_list:
        new_job = ''
        if weekplan.rate_code == '小时':
            if weekplan.rate_desc == '':
                weekplan.rate_desc = 1
            new_job = ('1 */%s * * *' % (weekplan.rate_desc), 'weekworkplan.cron.create_task', [],{'myid': weekplan.id})
            # new_job = ('*/1 * * * *', 'weekworkplan.cron.create_task', [],{'myid': weekplan.id})

        elif weekplan.rate_code == '天':
            # print('天')
            if weekplan.rate_desc == '':
                weekplan.rate_desc = 1
            new_job = ('0 8 */%s * *' % (weekplan.rate_desc), 'weekworkplan.cron.create_task', [], {'myid': weekplan.id}
                       )
        elif weekplan.rate_code == '周':
            # print('周')
            if weekplan.num2 == '':
                weekplan.num2 = 1
            else:
                pass
            new_job = ('0 8 * * */%s' % (weekplan.rate_desc), 'weekworkplan.cron.create_task', [], {'myid': weekplan.id}
                       )
        elif weekplan.rate_code == '月':
            # print('月')
            if weekplan.num2 == '':
                weekplan.num2 = 1
            new_job = ('0 8 1 */%s *' % (weekplan.rate_desc), 'weekworkplan.cron.create_task', [], {'myid': weekplan.id}
                       )
        elif weekplan.rate_code == '年':
            # print('年')
            if weekplan.num2 == '':
                weekplan.num2 = 1

            new_job = (
                '0 8 1 */%s *' % (int(weekplan.rate_desc) * 12), 'weekworkplan.cron.create_task', [], {'myid': weekplan.id}
            )
        elif weekplan.rate_code == '一次性工作计划':
            new_job = ()

        CRONJOBS.append(new_job)
        # list(set(CRONJOBS))
        # print('添加定期工作任务成功！')
        from django_crontab.management.commands import crontab
    # CRONJOBS[0], CRONJOBS[-1] = CRONJOBS[-1], CRONJOBS[0]
    call_command('crontab', 'add')
    # print('crontab add 完毕！')







