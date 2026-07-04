# heycg_project/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== SECURITY =====
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-!q(u41=*%5qcd9qs-+nmm+gu9eb1z#zs*bxy-6qxw!yqpu5r&=')

# ===== MUHIMU: PythonAnywhere inahitaji DEBUG=False kwa production =====
DEBUG = False

ALLOWED_HOSTS = ['*', '.pythonanywhere.com']

# ===== INSTALLED APPS =====
INSTALLED_APPS = [
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap5',
    'tinymce',
    'whitenoise.runserver_nostatic',
    'website',
    'accounts',
    'members',
]

# ===== MIDDLEWARE =====
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

# ===== DATABASE - SQLITE KWA PYTHONANYWHERE =====
# ONDOA dj_database_url - haihitajiki kwa SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===== PASSWORD VALIDATION =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# ===== CLOUDINARY CONFIGURATION =====
# ============================================================

CLOUDINARY_CLOUD_NAME = 'diqw9vxni'
CLOUDINARY_API_KEY = '214443295411688'
CLOUDINARY_API_SECRET = 'f5ywn0NI6Ww9vshruM9KmfqeRFY'

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

# ===== MEDIA FILES STORAGE =====
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================================

# ===== INTERNATIONALIZATION =====
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================
# ===== STATIC FILES =====
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# ===== CRISPY FORMS =====
# ============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ===== LOGIN =====
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'members:dashboard'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== CSRF =====
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
    'https://*.pythonanywhere.com',
]

CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# ===== ADMIN =====
ADMIN_SITE_HEADER = "HEYCG Membership Portal"
ADMIN_SITE_TITLE = "HEYCG Admin"
ADMIN_INDEX_TITLE = "Welcome to HEYCG Membership Portal Administration"

# ===== PAGINATION =====
BLOG_PAGINATION = 6
EVENTS_PAGINATION = 9
GALLERY_PAGINATION = 12
LOGOUT_REDIRECT_URL = '/'

# ===== EMAIL =====
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'youngcharitygeneration20@gmail.com'
EMAIL_HOST_PASSWORD = 'gmlbncgncxvbbmum'
DEFAULT_FROM_EMAIL = 'HEYCG <youngcharitygeneration20@gmail.com>'
EMAIL_TIMEOUT = 30
EMAIL_USE_LOCALTIME = True

# ===== TINYMCE =====
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'menubar': 'file edit view insert format tools table help',
    'toolbar': 'undo redo | bold italic underline | formatselect | bullist numlist | outdent indent | removeformat | code | image media',
    'plugins': 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount',
}