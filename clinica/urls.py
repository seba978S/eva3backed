"""
Configuración de URLs de la app Clínica PetCare.

Registra todos los ViewSets bajo /api/ usando un DefaultRouter
y las vistas de autenticación por sesión.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# ── DRF Router ───────────────────────────────────────────────────
router = DefaultRouter()
router.register(r"tutores", views.TutorViewSet, basename="tutor")
router.register(r"mascotas", views.MascotaViewSet, basename="mascota")
router.register(r"veterinarios", views.VeterinarioViewSet, basename="veterinario")
router.register(r"citas", views.CitaViewSet, basename="cita")
router.register(r"fichas-clinicas", views.FichaClinicaViewSet, basename="fichaclinica")
router.register(
    r"recordatorios-vacuna",
    views.RecordatorioVacunaViewSet,
    basename="recordatoriovacuna",
)
router.register(
    r"inventario-vacunas",
    views.InventarioVacunaViewSet,
    basename="inventariovacuna",
)

app_name = "clinica"

urlpatterns = [
    # ── API REST ─────────────────────────────────────────────────
    path("", include(router.urls)),

    # ── Autenticación por sesión ─────────────────────────────────
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ── Dashboard y Stats ────────────────────────────────────────
    path("stats/", views.stats_view, name="stats"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
