# heycg_project/settings.py
"""
Django settings for heycg_project project.
"""

import os
import dj_database_url
from pathlib import Path

# ===== O N G E Z A  H I Z I =====
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
load_dotenv()  # Inasoma .env file

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-!q(u41=*%5qcd9qs-+nmm+gu9eb1z#zs*bxy-6qxw!yqpu5r&=')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ===== MUHIMU: Ongeza hii =====
ALLOWED_HOSTS = ['*']  # Kwa Render, au weka domain yako

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # ===== O N G E Z A  H I Z I =====
    'cloudinary_storage',  # Hii lazima iwe kabla ya cloudinary
    'cloudinary',
    
    'crispy_forms',
    'crispy_bootstrap5',
    'tinymce',
    'whitenoise.runserver_nostatic',
    'website',
    'accounts',
    'members',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'heycg_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'members.context_processors.admin_notification_link',
            ],
        },
    },
]

WSGI_APPLICATION = 'heycg_project.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===== STATIC FILES =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# ===== M E D I A   F I L E S   -   C L O U D I N A R Y =====
# ============================================================

# ===== CLOUDINARY CONFIGURATION =====
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True  # Inatumia HTTPS
)

# ===== MEDIA FILES STORAGE =====
# Sasa picha zote zinaenda Cloudinary, si filesystem tena!
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Media URL - hii ni URL ya picha kutoka Cloudinary
MEDIA_URL = '/media/'

# Hii haihitajiki tena, lakini tuweke tu
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===== OLD MEDIA SETTINGS - ZIMEONDOLEWA! =====
# if DEBUG:
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# else:
#     MEDIA_URL = '/static/media/'
#     MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

# ============================================================

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'members:dashboard'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF and Session settings
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.onrender.com',
]

CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# Admin Customization
ADMIN_SITE_HEADER = "HEYCG Membership Portal"
ADMIN_SITE_TITLE = "HEYCG Admin"
ADMIN_INDEX_TITLE = "Welcome to HEYCG Membership Portal Administration"

# Pagination
BLOG_PAGINATION = 6
EVENTS_PAGINATION = 9
GALLERY_PAGINATION = 12
LOGOUT_REDIRECT_URL = '/'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'youngcharitygeneration20@gmail.com'
EMAIL_HOST_PASSWORD = 'gmlbncgncxvbbmum'
DEFAULT_FROM_EMAIL = 'HEYCG <youngcharitygeneration20@gmail.com>'
EMAIL_TIMEOUT = 30
EMAIL_USE_LOCALTIME = True

# TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'menubar': 'file edit view insert format tools table help',
    'toolbar': 'undo redo | bold italic underline | formatselect | bullist numlist | outdent indent | removeformat | code | image media',
    'plugins': 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount',
}