"""
Django settings for project - Production Ready
Django 5.2.8
"""
import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path
from decouple import config
import os
from datetime import timedelta

# ==================================================
# Base
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG=True
#DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# ==================================================
# Applications
# ==================================================

INSTALLED_APPS =[ 
    'accounts',
    'jazzmin',
    'adminsortable2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Third party
    'compressor',
    'django_celery_results',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',

    # Local
    'utils',
    'products',
    'orders',
    'cart',
    'home',
    'support',
    'api',
]


# ==================================================
# Middleware
# ==================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.CheckUserActiveMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ==================================================
#  Cache 
# ==================================================

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://:pgnh3kDHsI0cOzlJvtM@127.0.0.1:49169/0",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# ==================================================
# URLs / Templates
# ==================================================

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.theme_processor',
                'accounts.context_processors.pending_users_count',
                'cart.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# ==================================================
# Database (PostgreSQL Docker)
# ==================================================


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'elwsamst_alwesam_store',
        'USER': 'elwsamst_alwesam_user',
        'PASSWORD': '3]qi04F*#6{k3]qi04F*#6{k3]qi04F*#6{k',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4'"
        },
    }
}
# ==================================================
# Auth
# ==================================================

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==================================================
# Internationalization
# ==================================================

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'

USE_I18N = True
USE_TZ = True

# ==================================================
# Static / Media
# ==================================================
STATIC_URL = '/static/'

# المسار النهائي لكل ملفات static بعد جمعها
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # هذه إضافة مهمة
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
    if not DEBUG else
    'django.contrib.staticfiles.storage.StaticFilesStorage'
)

COMPRESS_ENABLED = False
# ==================================================
# Email
# ==================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default='Alwesam Talabat <info@elwsam.com>'
)




# ==================================================
# REST Framework
# ==================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ==================================================
# JWT
# ==================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',

]


# ==================================================
# Swagger
# ==================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'E-Commerce API',
    'DESCRIPTION': 'REST API for wholesale e-commerce system',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}










# ==================================================
# Logging (Final Production Setup)
# ==================================================

import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = BASE_DIR / "logs"
(LOG_DIR / "django").mkdir(parents=True, exist_ok=True)
(LOG_DIR / "celery").mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} | {name}:{lineno} | {message}",
            "style": "{",
        },
    },

    "handlers": {
        # Console (for docker logs)
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },

        # Django errors
        "django_error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django/error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "level": "ERROR",
            "formatter": "default",
        },

        # Django warnings
        "django_warning_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django/warning.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "level": "WARNING",
            "formatter": "default",
        },

        # Application logic (your code)
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django/app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "level": "INFO",
            "formatter": "default",
        },

        # Celery
        "celery_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "celery/worker.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "level": "INFO",
            "formatter": "default",
        },
    },

    "loggers": {
        # Django internal
        "django": {
            "handlers": ["console", "django_warning_file"],
            "level": "WARNING",
            "propagate": True,
        },

        "django.request": {
            "handlers": ["django_error_file"],
            "level": "ERROR",
            "propagate": False,
        },

        "django.db.backends": {
            "handlers": ["django_error_file"],
            "level": "ERROR",
            "propagate": False,
        },

        # Your project apps (auto-detected via __name__)
        "": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
        },

        # Celery
        "celery": {
            "handlers": ["console", "celery_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
