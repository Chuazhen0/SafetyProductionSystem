from lbworkflow.core.datahelper import create_node
from lbworkflow.core.datahelper import create_category
from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_transition


def load_data():
    load_weekworktask()
def load_weekworktask():
    #  拟定--------cgl---------cry--------归档
    """ load_[wf_code] """
    category = create_category('5f31d065-00cc-0190-beea-641f0a670010', '周期检测任务')
    process = create_process('weekworktask', 'Weekworktask', category=category)
    create_node('5f31d065-00a0-0190-beea-641f0a670010', process, 'Draft', status='拟定')
    create_node('5f31d065-00a0-0190-beea-641f0a670020', process, 'Given up', status='放弃')
    create_node('5f31d065-00a0-0190-beea-641f0a670030', process, 'Rejected', status='拒绝')
    create_node('5f31d065-00a0-0190-beea-641f0a670040', process, 'Completed', status='归档')
    create_node('5f31d065-00a0-0190-beea-641f0a670050', process, 'A1', operators='[cgl]')
    create_node('5f31d065-00a0-0190-beea-641f0a670060', process, 'A2', operators='[lyh]')
    create_transition('5f31d065-00e0-0190-beea-641f0a670010', process, 'Draft,', 'A1')
    create_transition('5f31d065-00e0-0190-beea-641f0a670020', process, 'A1,', 'A2')
    create_transition('5f31d065-00e0-0190-beea-641f0a670030', process, 'A2,', 'Completed')


