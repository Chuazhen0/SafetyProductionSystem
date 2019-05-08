import os

import pymysql
pymysql.install_as_MySQLdb()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'va-&%0w8ekgz^&5!lypcl*fgpcs8*a*@y$6k61*7z7vrio6f=n'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # tests.settings
    'crispy_forms',
    'django_crontab',
    'lbattachment',
    'lbadminlte',
    'lbutils',
    'compressor',
    'djangobower',
    'el_pagination',
    'lbworkflow',# 工作流
    'lbworkflow.tests.leave',
    'lbworkflow.tests.purchase',
    'lbworkflow.tests.issue',
    'SafetyProductionSystem',
    'stronghold',
    'impersonate',
    'systemsettings',  # 系统设置
    'crm',  # 分页
    'netstructure',# 网络结构信息
    'netstaff',# 网络人员信息
    'staff_qua',# 监督网络人员资质信息
    'mon_plan_sum',# 月度工作计划与总结
    'monworkexe',# 月度工作执行
    'yearplan',# 年度计划
    'yearsum',# 年度总结
    'regularworktask',# 定期工作任务
    'regularworkplan',# 定期工作标准
    'warning',# 告警通知单
    'warningre',# 告警回执单
    'standard',# 指标管理
    'qua25',# 资质管理
    'quatype',# 资质类别管理
    'weekworkplan',# 周期检测计划
    'weekworktask',# 周期检测任务
    'myworkflow',# 自定义工作流app
    'problemlog',# 问题管理
    'myform',# 报表管理


]
# django2.0
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]
ROOT_URLCONF = 'SafetyProductionSystem.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "template")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
WSGI_APPLICATION = 'SafetyProductionSystem.wsgi.application'

DATABASES = {
    'default': {

        'HOST':'47.92.26.15',
        'PASSWORD':'wak123',
        # 'PASSWORD':'root',
        # 'HOST':'192.168.104.212',
        # 'HOST':'192.168.104.231',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wang1127',
        #'NAME': '0823',
        'USER': 'root',
        #'USER': 'test',
        'CONN_MAX_AGE': 600,
        'PORT':3333,


    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
                            ]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
SESSION_PERMISSION_URL_KEY = 'cool'
SESSION_MENU_KEY = 'awesome'
ALL_MENU_KEY = 'k1'
PERMISSION_MENU_KEY = 'k2'
LOGIN_URL = '/systemsettings/login/'
REGEX_URL = r'^{url}$'  # url作严格匹配
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
IMPERSONATE_REDIRECT_URL = '/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL_ = '/media/'
MEDIA_URL = MEDIA_URL_
STATIC_ROOT = os.path.join(BASE_DIR, 'collectedstatic')
STRONGHOLD_PUBLIC_URLS = [
    r'^/admin/',
]
###########################tests.settings整合到项目中#################################33
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# 设置session过期时间
SESSION_COOKIE_AGE = 60*60*12
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 工作流 apps
LBWF_APPS = {
    # 'leave': 'lbworkflow.tests.leave',
    # 'purchase': 'lbworkflow.tests.purchase',
    # 'issue':'lbworkflow.tests.issue',
    # '定期工作任务':'regularworktask',
    '定期工作策划':'regularworkplan',
    '月度计划':'mon_plan_sum',
    '月度工作执行':'monworkexe',
    '年度计划':'yearplan',
    '年度总结':'yearsum',
    '告警通知':'warning',
    '告警回执':'warningre',
    '周期检测计划':'weekworkplan',
}
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# bower
STATICFILES_FINDERS += (('djangobower.finders.BowerFinder'),)
BOWER_COMPONENTS_ROOT = BASE_DIR
BOWER_INSTALLED_APPS = (
    'admin-lte#2.3.11',
    'font-awesome#4.7.0',
    'ionicons#2.0.1',
    'modernizr',
    # POLYFILLS: javascript fallback solutions for older browsers.
    # CSS3 selectors for IE 6-8.
    'selectivizr',
    # min/max width media queries for IE 6-8.
    'respond',
    # CSS3 styles for IE 6-8.
    'pie',
    # HTML5 tag support for IE 6-8.
    'html5shiv',
    'masonry#4.1.1',
    'blueimp-file-upload#9.12.5',
    'flatpickr-calendar#2.5.6',
)

# django-compressor
STATICFILES_FINDERS += (('compressor.finders.CompressorFinder'),)
COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'sass {infile} {outfile}'),
    ('text/x-scss', 'sass --scss {infile} {outfile}'),
)

LBWF_APPS.update({
    '周期检测任务':'weekworktask',
})
CRONJOBS = [
    ('* * * * *', 'regularworkplan.cron.test'),
]
