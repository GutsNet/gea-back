"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
URL configuration for G.E.A. backend.

API versioning: todos los endpoints bajo /api/v1/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# ──────────────────────────────────────────────
# API v1
# ──────────────────────────────────────────────
api_v1_patterns = [
    path("auth/", include("apps.usuarios.urls")),
    path("arboles/", include("apps.arboles.urls")),
    path("reportes/", include("apps.reportes.urls")),
    path("recoleccion/", include("apps.recoleccion.urls")),
    path("solicitudes/", include("apps.solicitudes.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "api-v1"))),
]

# ──────────────────────────────────────────────
# Debug toolbar (solo en desarrollo)
# ──────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
