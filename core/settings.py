import os

from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Check if the .env file exists
if os.path.isfile('.env'):
    load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
# DEBUG = os.getenv('DEBUG', 'False')
# getenv não está funcionando
DEBUG=True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',                            # uses 'django-widget-tweaks' app
    'crispy_forms',                             # uses 'django-crispy-forms' app
    'crispy_bootstrap4',
    'login_required',                           # uses 'django-login-required-middleware' app

    'homepage.apps.HomepageConfig',
    'tabelas.apps.TabelasConfig',
    'processos.apps.ProcessosConfig',
    'simple_history',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'login_required.middleware.LoginRequiredMiddleware',    # middleware used for global login
    'simple_history.middleware.HistoryRequestMiddleware',   # middleware usado para registro de logs
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],  # included 'templates' directory for django to access the html templates
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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': os.getenv('DB_NAME'),
#        'USER': os.getenv('POSTGRES_USER'),
#        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
#        'HOST': os.getenv('DB_HOST'),
#        'PORT': os.getenv('DB_PORT', '5432'),
#    }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.microcredito',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

SIMPLE_HISTORY_ENABLED = True

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = False

DECIMAL_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Diretório onde o Django coletará os arquivos estáticos (usado em produção)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# # Diretórios adicionais para buscar arquivos estáticos (usado no desenvolvimento)
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'homepage/static')
# ]

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MEDIA_URL = '/documentos/'
#
# MEDIA_ROOT = os.path.join(BASE_DIR, 'documentos/')
#

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

CRISPY_TEMPLATE_PACK = 'bootstrap4'                     # bootstrap template crispy-form uses

LOGIN_REDIRECT_URL = 'home'                             # sets the login redirect to the 'home' page after login

LOGIN_URL = 'login'                                     # sets the 'login' page as default when user tries to illegally access profile or other hidden pages

LOGIN_REQUIRED_IGNORE_VIEW_NAMES = [                    # urls ignored by the login_required. Can be accessed KRwith out logging in
    'login',
    'logout',
    'about',

    'password_reset',
    'password_reset_done',
    'password_reset_confirm',
    'password_reset_complete',

]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Configuração para página não encontrada (404)
handler404 = 'processos.views.pagina_nao_encontrada'

# Configuração para erro interno do servidor (500)
handler500 = 'processos.views.erro_servidor'


# Configuração de e-mail para redefinição de senha
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.campos.rj.gov.br'  # Ex: smtp.gmail.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Adicione no .env
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Adicione no .env
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
