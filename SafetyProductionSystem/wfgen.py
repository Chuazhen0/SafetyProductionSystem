#!/usr/bin/env python
import inspect
import os
import shutil
import sys

import django
from django.core.management import call_command


def gen():
    from lbworkflow.flowgen import FlowAppGenerator
    from regularworktask.models import RegularWorkTask as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from mon_plan_sum.models import MonPlanSum as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from yearsum.models import YearSum as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from yearplan.models import YearPlan as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from warning.models import WarningNotice as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from warningre.models import WarningReceipt as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)
    from monworkexe.models import MonWorkExe as wf_class
    FlowAppGenerator().gen(wf_class, replace=True)


def rm_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def clean():
    from lbworkflow.flowgen import clean_generated_files
    from lbworkflow.tests.issue.models import Issue
    clean_generated_files(Issue)
    # remove migrations for leave
    from lbworkflow.tests.leave.models import Leave
    folder_path = os.path.dirname(inspect.getfile(Leave))
    path = os.path.join(folder_path, 'migrations')
    rm_folder(path)
    # remove migrations for purchase
    from lbworkflow.tests.purchase.models import Purchase
    clean_generated_files(Purchase)
    folder_path = os.path.dirname(inspect.getfile(Purchase))
    path = os.path.join(folder_path, 'migrations')
    rm_folder(path)


def load_data():
    from lbworkflow.core.datahelper import load_wf_data
    load_wf_data('lbworkflow')
    load_wf_data('regularworktask')
    load_wf_data('mon_plan_sum')
    load_wf_data('yearsum')
    load_wf_data('yearplan')
    load_wf_data('warning')
    load_wf_data('warningre')
    load_wf_data('monworkexe')



if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, BASE_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = "SafetyProductionSystem.settings"
    django.setup()
    if (len(sys.argv)) == 2:
        cmd = sys.argv[1]
        if cmd == 'load_data':
            load_data()
        elif cmd == 'clean':
            clean()
        sys.exit(0)
    gen()

    call_command('makemigrations', 'regularworktask')
    call_command('makemigrations', 'mon_plan_sum')
    call_command('makemigrations', 'yearsum')
    call_command('makemigrations', 'yearplan')
    call_command('makemigrations', 'warning')
    call_command('makemigrations', 'warningre')
    call_command('makemigrations', 'monworkexe')
    call_command('migrate')
    load_data()
