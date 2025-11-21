import os
from pathlib import Path

# БАЗОВЫЕ ПУТИ
BASE_DIR = Path(__file__).resolve().parent.parent

# СЕКРЕТ
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')

# В РАЗРАБОТКЕ держим True, в продакшн ставь False
DEBUG = True

# Разрешённые хосты — без схемы. Подставь свой конкретный ngrok-хост, если хочешь.
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # шаблон для поддоменов ngrok (пример который ты привёл)
    '.ngrok-free.dev',
    # конкрентный адрес (оставь если он у тебя стабилен)
    'cirrostrative-unshared-kelley.ngrok-free.dev',
]

# Установленные приложения — добавил cinema и опционально crispy_forms
INSTALLED_APPS = [
    'daphne',                       # если используешь daphne для ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',                     # Channels (ASGI)
    'cinema',                       # твоё приложение кинотеатра
    'crispy_forms',                 # опционально
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корни URL (подставь своё)
ROOT_URLCONF = 'cinema_project.urls'

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
            ],
        },
    },
]

# ASGI приложение (Channels)
ASGI_APPLICATION = 'cinema_project.asgi.application'

# БД (по умолчанию sqlite — оставить для разработки)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей (пусто для dev)
AUTH_PASSWORD_VALIDATORS = []

# Локализация — установил Asia/Bishkek согласно твоей локали
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'     # для collectstatic (prod)
STATICFILES_DIRS = [BASE_DIR / 'static']   # локальные dev static

# Медиа (постеры, pdf билеты)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels — InMemory для dev. Для реального использования перейди на Redis.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# CSRF trusted origins — важно: схему (http/https) + хост, без слеша в конце
# ngrok может проксировать и http, и https — поэтому добавлены оба варианта.
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
    'https://*.ngrok-free.dev',
    'http://*.ngrok-free.dev',
    'https://cirrostrative-unshared-kelley.ngrok-free.dev',
    'http://cirrostrative-unshared-kelley.ngrok-free.dev',
]

# Когда ngrok выставляет HTTPS, полезно доверять proxy-заголовку X-Forwarded-Proto
# чтобы Django правильно понимал, что соединение по HTTPS.
# Это безопасно для dev/тестирования при использовании ngrok.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# EMAIL: для разработки удобно выводить в консоль. Для реальной почты заменяй настройки.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Пример SMTP (раскомментируй/замени данные для продакшна):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'your@example.com'
# EMAIL_HOST_PASSWORD = 'yourpassword'
# EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Cinema <no-reply@example.com>'

# Дополнительные удобства для dev
INTERNAL_IPS = ['127.0.0.1']

# Примечание:
# - Если ngrok даёт динамический поддомен, можно временно добавить ALLOWED_HOSTS = ['*']
#   но это не безопасно на проде.
# - После изменения ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS перезапусти Django и ngrok.
