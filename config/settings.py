# config/settings.py
#
# Django settings for QVS.
#
# Every value that differs between the local .venv, CI and the Docker image is read
# from the environment. That is what makes D-002's claim true - migrating from SQLite
# to PostgreSQL is a configuration change - and it is what keeps REQ-N-002 (no secret
# committed) enforceable rather than aspirational.

import os
import secrets
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# BASE_DIR is the repository root, derived from this file's location. The absolute
# path appears nowhere in the repository, for the same reason tools\ derives it from
# $PSScriptRoot - D-013.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment ------------------------------------------------------------------

# Default is development. Production must opt in by setting QVS_DEBUG=0, so a missing
# environment variable can never silently produce a debug-mode container.
DEBUG = os.environ.get("QVS_DEBUG", "1") == "1"

# REQ-N-002: no secret, key or credential is committed. There is deliberately no
# hard-coded fallback key in this file - not even a "dev only" one, because a
# committed placeholder is exactly the string that ends up in production.
#
# In development an ephemeral key is generated per process. The cost is that sessions
# do not survive a server restart, which nothing in this project depends on. Outside
# development a missing key is fatal and says so at start-up rather than at first use.
SECRET_KEY = os.environ.get("QVS_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "QVS_SECRET_KEY must be set when QVS_DEBUG is not 1. "
            "See .env.example for the variables this project reads."
        )
    SECRET_KEY = secrets.token_urlsafe(50)

# D-003: the HMAC key that signs qualification records. Same rule as SECRET_KEY, but
# with no development fallback at all - a signature produced under an ephemeral key
# would verify inside one process and fail in the next, which is worse than an error.
# Read lazily by the signing code so that management commands unrelated to signing
# still run without it.
QVS_SIGNING_KEY = os.environ.get("QVS_SIGNING_KEY", "")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("QVS_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# --- Applications -----------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "qualifications",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # A project-level templates directory for base.html and anything shared.
        # App template directories stay enabled so each app keeps its own pages.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ---------------------------------------------------------------------

# D-002: SQLite, with the file location read from the environment so the container
# can point it at a mounted volume without a settings change.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("QVS_DATABASE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentication ---------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    # Expanded across three lines because that is how `ruff format` wants it. The
    # dotted path still exceeds the 88-character line length even when expanded,
    # which is why config/settings.py carries an E501 per-file ignore in
    # pyproject.toml - the formatter cannot split a string literal.
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# REQ-F-004: unauthenticated users cannot register or edit records. These are where
# the redirect lands; the login and logout routes themselves are wired in config/urls.
LOGIN_URL = "login"

# Was "/", which routes nowhere - the qualifications app is mounted at the root but
# defines no index, so a successful login landed on a 404. Pointed at the register
# view, which is the only thing an authenticated user can currently do. A real landing
# page belongs with REQ-F-009 search and REQ-F-010 record detail, not here.
LOGIN_REDIRECT_URL = "qualifications:register"
LOGOUT_REDIRECT_URL = "login"

# --- Internationalisation ---------------------------------------------------------

LANGUAGE_CODE = "en-us"

# UTC, not Africa/Harare. REQ-F-007 writes an audit event for every verification
# attempt, and an audit trail whose timestamps shift with a server's local zone is not
# evidence. Display can be localised later; storage stays UTC.
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files -----------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
