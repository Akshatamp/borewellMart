import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

DEBUG = True

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])
# HTTPS / SSL Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.VisitorTrackingMiddleware',
    'core.middleware.VendorAccessMiddleware',
]

ROOT_URLCONF = 'borewellmart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.services_context',
                'core.context_processors.notification_context',
                'core.context_processors.base_template_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'borewellmart.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise configuration - serve media files in development and production
if not DEBUG:
    # In production, configure WhiteNoise to serve media files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# CORS Configuration for Razorpay
CORS_ALLOWED_ORIGINS = [
    "https://api.razorpay.com",
    "https://lumberjack.razorpay.com",
    "https://rzp.io",
]
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=DEBUG, cast=bool)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your-email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-app-password')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='BorewellMart <noreply@borewellmart.com>')
EMAIL_SUBJECT_PREFIX = '[BorewellMart] '

# Front-end URL for email links (e.g., 'http://localhost:8000' in dev)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:8000')

# WhatsApp Cloud API settings
WHATSAPP_CLOUD_API_URL = config('WHATSAPP_CLOUD_API_URL', default='https://graph.facebook.com/v17.0')
WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
WHATSAPP_BUSINESS_ACCOUNT_ID = config('WHATSAPP_BUSINESS_ACCOUNT_ID', default='')
WHATSAPP_CLOUD_TOKEN = config('WHATSAPP_CLOUD_TOKEN', default='')
WHATSAPP_TEMPLATE_NAME = config('WHATSAPP_TEMPLATE_NAME', default='service_enquiry')
WHATSAPP_TEMPLATE_LANGUAGE = config('WHATSAPP_TEMPLATE_LANGUAGE', default='en_US')

# Twilio SMS settings
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_FROM_NUMBER = config('TWILIO_FROM_NUMBER', default='')

from decouple import config

# Razorpay Settings
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# Amounts in paise
REGISTRATION_AMOUNT = config(
    'REGISTRATION_AMOUNT',
    default=99900,
    cast=int
)


RAZORPAY_CURRENCY = config(
    'RAZORPAY_CURRENCY',
    default='INR'
)

RAZORPAY_WEBHOOK_SECRET = config(
    'RAZORPAY_WEBHOOK_SECRET',
    default=''
)
RAZORPAY_VENDOR_REGISTRATION_AMOUNT = 99900  # ₹999.00 in paise

# Whitenoise configuration for serving media files
# This allows Whitenoise to serve media files in both development and production
WHITENOISE_MEDIA_ROOTS = [MEDIA_ROOT]
WHITENOISE_MEDIA_PREFIX = MEDIA_URL
