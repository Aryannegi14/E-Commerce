from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d-8ap6f8za!tn0gp1oqer=-flf5_wrt=b2_=_tte_*m&go=^m1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Change to a more restrictive list in production

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default Django session backend
SESSION_COOKIE_NAME = 'sessionid'  # Use the default session cookie name for simplicity
SESSION_COOKIE_AGE = 3600  # Set session timeout to 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Session doesn't expire when browser is closed
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False   # Set to True in production if using HTTPS

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',  # Ensure this is present
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Default middleware to handle sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Email settings for sending OTPs or notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aryannegiofficial@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'qrfi ulza amyl vaad'  # Replace with your app-specific password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ROOT_URLCONF = 'e_commerce.urls'
# settings.py

TIME_ZONE = 'Asia/Kolkata'  # Set this to your local time zone
USE_TZ = True  # Ensure this is set to True to use timezone-aware datetimes

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # This is for project-level templates
        'APP_DIRS': True,  # This allows looking inside app-level templates
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



WSGI_APPLICATION = 'e_commerce.wsgi.application'

# Database settings (SQLite in development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation settings (use default validators)
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

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aryannegiofficial@gmail.com'
EMAIL_HOST_PASSWORD = 'lusc tamt pemm eyjc'  # Replace with your email password
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

