"""
Django test settings for G.E.A. backend.

SQLite in-memory + password hasher rápido para tests veloces.
"""

from .base import *  # noqa: F401, F403

# ──────────────────────────────────────────────
# Database — SQLite in-memory
# ──────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ──────────────────────────────────────────────
# Faster password hashing for tests
# ──────────────────────────────────────────────
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ──────────────────────────────────────────────
# Media — use temp dir
# ──────────────────────────────────────────────
MEDIA_ROOT = BASE_DIR / "test_media"  # noqa: F405

# ──────────────────────────────────────────────
# Disable throttling in tests
# ──────────────────────────────────────────────
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405
