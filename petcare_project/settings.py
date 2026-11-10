"""
Django settings for petcare_project.

Configurado para desarrollo local con SQLite (fallback) y listo
para despliegue en AWS EC2 con PostgreSQL.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ───────────────────────────── Paths ──────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / ".env")

# ───────────────────────────── Core ───────────────────────────────
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-cambia-esto-en-produccion-abc123xyz",
)

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ───────────────────────── Applications ───────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "django_filters",
    # Local apps
    "clinica",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "petcare_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "petcare_project.wsgi.application"

# ──────────────────────── Base de datos ───────────────────────────
# Configuración de base de datos relacional (PostgreSQL / SQLite fallback):
# - Por defecto soporta PostgreSQL según la rúbrica de la evaluación.
# - Parámetros leídos desde variables de entorno con os.environ y valores seguros para desarrollo:
#     ENGINE: 'django.db.backends.postgresql'
#     NAME, USER, PASSWORD, HOST, PORT
# - Mecanismo de respaldo (fallback) a SQLite solo si USE_SQLITE=True está presente en el entorno.
USE_SQLITE = os.environ.get("USE_SQLITE", "False").lower() in ("true", "1", "yes")

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "petcare_db"),
            "USER": os.environ.get("DB_USER", "petcare_user"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "petcare_password"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# Soporte opcional para DATABASE_URL vía dj-database-url si está instalado y configurado
if not USE_SQLITE and os.environ.get("DATABASE_URL"):
    try:
        import dj_database_url
        DATABASES["default"] = dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
        )
    except ImportError:
        pass

# ──────────────────── Password validation ─────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─────────────────────── Internationalization ─────────────────────
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# ─────────────────────── Static files ─────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─────────────────────── Media files ──────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─────────────────────── Default PK ───────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────── Django REST Framework ────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DATE_FORMAT": "%d/%m/%Y",
    "DATETIME_FORMAT": "%d/%m/%Y %H:%M",
}

# ─────────────────── Autenticación / Sesiones ─────────────────────
LOGIN_URL = "/api/login/"
LOGIN_REDIRECT_URL = "/api/dashboard/"
LOGOUT_REDIRECT_URL = "/api/login/"
