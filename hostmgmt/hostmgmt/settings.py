"""
Django settings for PRAVAAH – Hostel Management Module.

Tech Stack: Django · SQLite (dev) / MySQL (production) · Bootstrap 5 · Font Awesome 6
"""

from pathlib import Path
from django.contrib.messages import constants as message_constants

# ── BUILD PATHS ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ── SECURITY ───────────────────────────────────────────────────────────────────
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cswmwxcn%*s1-*^7a^p-dv1h08ps0!f^439&u@gshv2h#u@%p='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# ── APPLICATIONS ───────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'hostel',   # PRAVAAH Hostel Room Allocation Module
]


# ── MIDDLEWARE ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hostmgmt.urls'


# ── TEMPLATES ──────────────────────────────────────────────────────────────────
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
            ],
        },
    },
]

WSGI_APPLICATION = 'hostmgmt.wsgi.application'


# ── DATABASE ───────────────────────────────────────────────────────────────────
#
# ┌─────────────────────────────────────────────────────────────────────────┐
# │  HOW TO SWITCH TO MYSQL                                                 │
# │  ─────────────────────────────────────────────────────────────────────  │
# │  1. Install driver:    pip install mysqlclient                          │
# │  2. Create database:   CREATE DATABASE pravaah_hostel                   │
# │                        CHARACTER SET utf8mb4                            │
# │                        COLLATE utf8mb4_unicode_ci;                      │
# │  3. Fill in your credentials in the MySQL block below                   │
# │  4. Comment out the SQLite block                                        │
# │  5. Uncomment the MySQL block                                           │
# │  6. Run:               python manage.py migrate                         │
# │  7. Seed:              python manage.py seed_rooms                      │
# │                        python manage.py seed_students                   │
# └─────────────────────────────────────────────────────────────────────────┘
#

# ── ACTIVE: SQLite (development / local testing) ──────────────────────────────
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pravaah',
        'USER': 'test',
        'PASSWORD': 'admin@123',
        'HOST': '192.168.0.77',
        'PORT': '3306',
    }
}

# ── READY: MySQL (uncomment to activate) ─────────────────────────────────────
# DATABASES = {
#     'default': {
#         'ENGINE':   'django.db.backends.mysql',
#         'NAME':     'pravaah_hostel',       # Your database name
#         'USER':     'root',                 # Your MySQL username
#         'PASSWORD': 'your_password_here',   # Your MySQL password
#         'HOST':     '127.0.0.1',            # MySQL host
#         'PORT':     '3306',                 # MySQL port (default 3306)
#         'OPTIONS': {
#             'charset':       'utf8mb4',
#             'init_command':  "SET sql_mode='STRICT_TRANS_TABLES'",
#             'connect_timeout': 10,
#         },
#         'TEST': {
#             'NAME': 'pravaah_hostel_test',
#         },
#     }
# }


# ── PASSWORD VALIDATION ────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── INTERNATIONALISATION ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'   # IST (UTC+5:30)
USE_I18N      = True
USE_TZ        = True


# ── STATIC FILES ───────────────────────────────────────────────────────────────
STATIC_URL = '/static/'


# ── MESSAGES — map to PRAVAAH design system classes ───────────────────────────
MESSAGE_TAGS = {
    message_constants.DEBUG:   'info',
    message_constants.INFO:    'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR:   'error',
}


# # ── AUTH ───────────────────────────────────────────────────────────────────────
# LOGIN_URL          = '/admin/login/'
# LOGIN_REDIRECT_URL = '/hostel/'

LOGIN_URL = '/hostel/login/'
LOGIN_REDIRECT_URL = '/hostel/'
LOGOUT_REDIRECT_URL = '/hostel/login/'

# ── DEFAULT AUTO FIELD ─────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── COMMON SERVICES INTEGRATION ────────────────────────────────────────────────
# URL of the Common Services email dispatch endpoint.
# Replace this with the real endpoint URL from the central ERP.
# The hostel module will POST a CSV file to this URL after auto-allocation.
COMMON_SERVICES_EMAIL_URL = 'http://YOUR_COMMON_SERVICES_HOST/api/send-bulk-email/'
