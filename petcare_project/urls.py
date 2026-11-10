"""
URL configuration for petcare_project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Redirección raíz a Dashboard
    path("", RedirectView.as_view(url="/api/dashboard/", permanent=False)),

    path("admin/", admin.site.urls),

    # ── App Clínica: API + Vistas de sesión ──────────────────────
    path("api/", include("clinica.urls", namespace="clinica")),

    # ── Browsable API auth (login/logout para DRF browsable) ─────
    path("api-auth/", include("rest_framework.urls")),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
