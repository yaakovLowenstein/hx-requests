"""
Minimal Django settings for the hx_requests test suite.

The test apps live inside ``tests/`` but are installed as top-level apps
(``test_app``, not ``tests.test_app``) so that their app labels match their
import paths. The registry builds module paths from app labels
(``f"{app.label}.hx_requests"``), so dotted app packages would not be
importable.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Make test_app / test_app_two importable as top-level packages.
sys.path.insert(0, str(BASE_DIR))

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = None
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "hx_requests",
    "test_app",
    "test_app_two",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# --- hx_requests settings ---
HX_REQUESTS_USE_HX_MESSAGES = True
HX_REQUESTS_HX_MESSAGES_TEMPLATE = "hx_messages.html"
HX_REQUESTS_MODAL_TEMPLATE = "hx_modal.html"
# Most tests exercise behavior, not auth; the security tests turn this on
# explicitly via override_settings.
HX_REQUESTS_REQUIRE_AUTH = False
