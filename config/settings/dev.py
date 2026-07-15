"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Django development settings for G.E.A. backend.

Usa SQLite por defecto para desarrollo rápido.
"""

from .base import *  # noqa: F401, F403

# ──────────────────────────────────────────────
# Debug
# ──────────────────────────────────────────────
DEBUG = True

# ──────────────────────────────────────────────
# Database — SQLite for quick local development
# ──────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ──────────────────────────────────────────────
# Django Debug Toolbar
# ──────────────────────────────────────────────
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# ──────────────────────────────────────────────
# CORS — allow all in dev
# ──────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ──────────────────────────────────────────────
# DRF — add browsable API in dev
# ──────────────────────────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [  # noqa: F405
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# ──────────────────────────────────────────────
# Email — console backend
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
