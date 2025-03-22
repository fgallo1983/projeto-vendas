"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_-o34chn75m3*4&4)cg6xw=hp98m6-vq#kbcl*bogn(yqe@n6l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'lokenzzi.pythonanywhere.com',  # Adicione o seu domínio aqui
    '127.0.0.1',  # Mantém localhost para testes locais
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vendas',
    'django_extensions',

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

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [
            "/home/lokenzzi/meuapp/vendas/templates",
        ],
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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = 'static/'

# STATICFILES_DIRS = [BASE_DIR / "static"]

# # Diretório de arquivos estáticos coletados (para produção)
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # Isso será usado quando você rodar 'collectstatic'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# # Diretório onde os arquivos estáticos serão armazenados
# STATIC_URL = '/vendas/static/'
STATIC_URL = '/static/'

# Diretório onde os arquivos estáticos ficam durante o desenvolvimento
STATICFILES_DIRS = [
    # BASE_DIR / 'vendas/static/',  # Altere conforme sua estrutura de pastas
    os.path.join(BASE_DIR, 'meuapp/vendas/static'),  # Substitua 'meuapp' pelo nome do seu app
]



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LOGIN_REDIRECT_URL = '/pagina-vendas/'

AUTH_USER_MODEL = 'vendas.CustomUser'

# Defina os diretórios para arquivos de mídia
MEDIA_URL = '/vendas/media/'
MEDIA_ROOT = BASE_DIR / 'vendas/media'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'atendimentolokenzzi5@gmail.com'  # Seu e-mail
EMAIL_HOST_PASSWORD = 'wbup tfzh ozld rkei'  # Sua senha de e-mail (pode ser a senha de um aplicativo)
DEFAULT_FROM_EMAIL = 'atendimentolokenzzi5@gmail.com'