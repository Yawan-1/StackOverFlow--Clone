from pathlib import Path
import os
import django_heroku
from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=dei9kx=^q))zm#z-(_cwdii75e-4bsf5_7suo9ll&besz088u'
# from django.conf import settings
settings.configure()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'adminactions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # App
    'profile',
    # App
    'users',
    # App
    'qa',
    # App
    'notification',
    # App
    'review',
    # App
    'tagbadge',
    # App
    'help',
    'taggit',
    'crispy_forms',
    'martor',
    'simple_history',
    # 'background_task',
    'review.templatetags',
    'tagbadge.tb_templatetags',
    'online_users',
    # 'debug_toolbar',
    'tools',
]

MAX_ATTEMPTS = 1


CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'simple_history.middleware.HistoryRequestMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #add whitenoise
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'online_users.middleware.OnlineNowMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR,"templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'review.context_processors.reviewAnswer_cp',
                'review.context_processors.returnTrue',
                'review.context_processors.reviewQuestion_cp',
                'review.context_processors.returnTrue_or_False',
                'review.context_processors.reviewLateAnswer_cp',
                'review.context_processors.returnLateReview_True_or_False',
                'review.context_processors.reviewClosedQuestions',
                'review.context_processors.returnTrue_or_FalseClosedQuestions',
                'review.context_processors.reviewReOpenQuestion_sVotes',
                'review.context_processors.returnTrue_or_FalseUnCloseQuestion_s',
                'review.context_processors.reviewEditedPosts',
                'review.context_processors.returnTrue_or_FalseEditPosts',
                'review.context_processors.reviewLowQualityPosts',
                'review.context_processors.returnTrue_or_FalseLowPosts',
                'review.context_processors.reviewFlagPosts',
                'review.context_processors.returnTrue_or_FalseFlagPosts',
                'review.context_processors.reviewFlagComments',
                'review.context_processors.returnTrue_or_FalseFlagComments',
                'notification.context_processors.privNotificationViewer',
                'notification.context_processors.notificationViewer',
                'profile.context_processors.top_questions',
                'profile.context_processors.count_all_bounties',

            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# DATABASES

"""
If you don't want to use postgresql then remove comment of sqlite's configuration and
comment in the postgresql configuration
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'POSTGRESQL_NAME',
#         'USER': 'POSTGRESQL_USER',
#         'PASSWORD': 'POSTGRESQL_PASSWORD',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "example"
    }
}
CACHE_TTL = 60 * 15

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# os.path.join(BASE_DIR, "static", "static")

#MY SETTINGS FOR LOGIN.
LOGIN_URL = 'users:login_request'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
#     os.path.join(BASE_DIR, 'media'),
# ]

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Martor Configuration
MARTOR_THEME = 'bootstrap'  # semantic
MARTOR_ENABLE_LABEL = True
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',        # to enable/disable emoji icons.
    'imgur': 'true',        # to enable/disable imgur/custom uploader.
    'mention': 'true',      # to enable/disable mention
    'jquery': 'true',       # to include/revoke jquery (require for admin default django)
    'living': 'true',      # to enable/disable live updates in preview
    'spellcheck': 'true',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',         # to enable/disable hljs highlighting in preview
}
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'image-upload', 'emoji',
    'direct-mention', 'toggle-maximize', 'help'
]

MARTOR_MARKDOWN_BASE_MENTION_URL = getattr(
    settings, 'MARTOR_MARKDOWN_BASE_MENTION_URL',
    'http://127.0.0.1:8000/pageOnlyWithUser/'
)


CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"


# INTERNAL_IPS = [
#     '127.0.0.1',
# ]

# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.history.HistoryPanel',
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     'debug_toolbar.panels.profiling.ProfilingPanel',
# ]

django_heroku.settings(locals())
