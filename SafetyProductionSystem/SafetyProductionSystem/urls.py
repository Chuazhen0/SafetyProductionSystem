"""SafetyProductionSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include
from django.contrib import admin
from systemsettings import views
from django.conf.urls import url
from django.views.static import serve
from . import settings

urlpatterns = [
    url(r'^$', views.mylogin,name='login'),  # 系统设置-登录
    url(r'^admin/', admin.site.urls),
    url(r'^netstructure/', include('netstructure.urls')),  # 网络结构信息
    url(r'^netstaff/', include('netstaff.urls')),  # 网络结构信息
    url(r'^staff_qua/', include('staff_qua.urls')),  # 监督网络结构人员资质信息
    url(r'^mon_plan_sum/', include('mon_plan_sum.urls')),  # 月度计划与总结
    url(r'^monworkexe/', include('monworkexe.urls')),  # 月度工作执行
    url(r'^yearplan/', include('yearplan.urls')),  # 年度计划
    url(r'^yearsum/', include('yearsum.urls')),  # 年度总结
    url(r'^warning/', include('warning.urls')),  # 告警通知单
    url(r'^warningre/', include('warningre.urls')),  # 告警回执单
    url(r'^standard/', include('standard.urls')),  # 指标管理
    url(r'^systemsettings/', include('systemsettings.urls')),  # 系统设置
    url(r'^weekworkplan/', include('weekworkplan.urls')),  # 周期检测计划
    url(r'^weekworktask/', include('weekworktask.urls')),  # 周期检测任务
    url(r'^qua25/', include('qua25.urls')),  # 25项反措--资质管理
    url(r'^quatype/', include('quatype.urls')),  # 资质类型管理
    url(r'^regularworkplan/', include('regularworkplan.urls')),  # 定期工作标准
    url(r'^regularworktask/', include('regularworktask.urls')),  # 定期工作任务
    #######################################工作流##############################################
    # url(r'^wf/list/', RedirectView.as_view(url='/wf/list/'), name='home'),
    url(r'^wf/', include('myworkflow.urls')),
    url(r'^attachment/', include('lbattachment.urls')),
    url(r'^myform/', include('myform.urls')),
    url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

