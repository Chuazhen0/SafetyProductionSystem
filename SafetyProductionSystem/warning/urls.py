from django.conf.urls import url
from . import myviews
app_name = 'warning'


urlpatterns = [
# 查询告警通知
url(r'search/$', myviews.warning_search, name='warning_search'),
# 添加告警通知
url(r'add/$', myviews.add_warningnotice, name='add_warningnotice'),
# 展示告警通知
url(r'list/$', myviews.show_warningnotice, name='show_warningnotice'),
# 编辑一个告警通知详情
url(r'(?P<wid>\d+)/edit/$', myviews.one_warningnotice, name='one_warningnotice'),
# 展示一个告警管理信息
url(r'(?P<wid>\d+)/detail/$', myviews.show_one_warningnotice, name='show_one_warningnotice'),
# 删除告警管理
url(r'(?P<wid>\d+)/delete/$', myviews.del_warningnotice, name='del_warningnotice'),
# 下载附件
url(r'down_file/$', myviews.down_file, name='down_file'),
]