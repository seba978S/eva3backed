"""
Vistas de la app Clínica PetCare.

Incluye:
- ModelViewSets para CRUD completo de las 6 entidades.
- Endpoints personalizados (@action) para disponibilidad, historial y alertas.
- Vistas de Login / Logout basadas en sesiones de Django.
"""

from datetime import datetime, date, timedelta, time

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, redirect
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Tutor,
    Mascota,
    Veterinario,
    Cita,
    FichaClinica,
    RecordatorioVacuna,
    InventarioVacuna,
)
from .serializers import (
    TutorSerializer,
    MascotaSerializer,
    VeterinarioSerializer,
    CitaSerializer,
    FichaClinicaSerializer,
    RecordatorioVacunaSerializer,
    HistorialMascotaSerializer,
    InventarioVacunaSerializer,
)


# ═══════════════════════════════════════════════════════════════════
#  VIEWSETS — API REST
# ═══════════════════════════════════════════════════════════════════

class TutorViewSet(viewsets.ModelViewSet):
    """CRUD completo de Tutores."""
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["rut_dni"]
    search_fields = ["nombre_completo", "rut_dni", "email", "telefono"]
    ordering_fields = ["nombre_completo", "fecha_registro"]
    ordering = ["nombre_completo"]


class MascotaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Mascotas con endpoint personalizado de historial clínico.
    """
    queryset = Mascota.objects.select_related("tutor").all()
    serializer_class = MascotaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["tutor", "especie", "sexo"]
    search_fields = ["nombre", "raza", "tutor__nombre_completo"]
    ordering_fields = ["nombre", "fecha_nacimiento"]
    ordering = ["nombre"]

    @action(detail=True, methods=["get"], url_path="historial")
    def historial(self, request, pk=None):
        """
        GET /api/mascotas/{id}/historial/

        Devuelve el historial clínico completo de la mascota:
        datos generales, todas las fichas clínicas (diagnósticos,
        tratamientos, recetas, exámenes) y recordatorios de vacunas.
        """
        mascota = self.get_object()
        # Pre-cargar relaciones para evitar N+1
        mascota_qs = Mascota.objects.prefetch_related(
            "fichas_clinicas__veterinario",
            "recordatorios_vacuna",
        ).get(pk=mascota.pk)

        serializer = HistorialMascotaSerializer(mascota_qs)
        return Response(serializer.data)


class VeterinarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de Veterinarios con endpoint de disponibilidad horaria.
    """
    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["activo", "especialidad"]
    search_fields = ["nombre_completo", "especialidad", "email"]
    ordering_fields = ["nombre_completo"]
    ordering = ["nombre_completo"]

    @action(detail=True, methods=["get"], url_path="disponibilidad")
    def disponibilidad(self, request, pk=None):
        """
        GET /api/veterinarios/{id}/disponibilidad/?fecha=YYYY-MM-DD

        Devuelve los bloques horarios ocupados y disponibles
        del veterinario para la fecha solicitada.

        Divide la jornada en bloques de 30 minutos y marca cada
        uno como 'disponible' u 'ocupado'.
        """
        veterinario = self.get_object()

        # ── Parámetro de fecha ───────────────────────────────────
        fecha_str = request.query_params.get("fecha")
        if not fecha_str:
            return Response(
                {"error": "Debe proporcionar el parámetro '?fecha=YYYY-MM-DD'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            fecha_consulta = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Horario de jornada ───────────────────────────────────
        inicio_jornada = veterinario.horario_inicio or time(8, 0)
        fin_jornada = veterinario.horario_fin or time(18, 0)

        # ── Citas activas del día ────────────────────────────────
        citas_del_dia = Cita.objects.filter(
            veterinario=veterinario,
            fecha=fecha_consulta,
            estado__in=Cita.ESTADOS_ACTIVOS,
        ).order_by("hora_inicio")

        citas_ocupadas = [
            {
                "cita_id": c.id,
                "hora_inicio": c.hora_inicio.strftime("%H:%M"),
                "hora_fin": c.hora_fin.strftime("%H:%M"),
                "mascota": c.mascota.nombre,
                "motivo": c.motivo,
                "estado": c.estado,
            }
            for c in citas_del_dia
        ]

        # ── Generar bloques de 30 min ────────────────────────────
        bloques = []
        bloque_actual = datetime.combine(fecha_consulta, inicio_jornada)
        fin = datetime.combine(fecha_consulta, fin_jornada)
        intervalo = timedelta(minutes=30)

        while bloque_actual + intervalo <= fin:
            bloque_inicio = bloque_actual.time()
            bloque_fin = (bloque_actual + intervalo).time()

            # ¿Hay alguna cita activa que solape este bloque?
            ocupado = citas_del_dia.filter(
                hora_inicio__lt=bloque_fin,
                hora_fin__gt=bloque_inicio,
            ).exists()

            bloques.append(
                {
                    "hora_inicio": bloque_inicio.strftime("%H:%M"),
                    "hora_fin": bloque_fin.strftime("%H:%M"),
                    "estado": "ocupado" if ocupado else "disponible",
                }
            )
            bloque_actual += intervalo

        return Response(
            {
                "veterinario": veterinario.nombre_completo,
                "fecha": fecha_str,
                "jornada": {
                    "inicio": inicio_jornada.strftime("%H:%M"),
                    "fin": fin_jornada.strftime("%H:%M"),
                },
                "citas_ocupadas": citas_ocupadas,
                "bloques": bloques,
            }
        )


class CitaViewSet(viewsets.ModelViewSet):
    """CRUD de Citas con validación de solapamiento vía serializer."""
    queryset = Cita.objects.select_related(
        "mascota", "mascota__tutor", "veterinario"
    ).all()
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["mascota", "veterinario", "fecha", "estado"]
    search_fields = [
        "mascota__nombre",
        "veterinario__nombre_completo",
        "motivo",
    ]
    ordering_fields = ["fecha", "hora_inicio", "estado"]
    ordering = ["-fecha", "hora_inicio"]


class FichaClinicaViewSet(viewsets.ModelViewSet):
    """CRUD de Fichas Clínicas."""
    queryset = FichaClinica.objects.select_related(
        "mascota", "veterinario", "cita"
    ).all()
    serializer_class = FichaClinicaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["mascota", "veterinario"]
    search_fields = [
        "mascota__nombre",
        "veterinario__nombre_completo",
        "diagnostico",
        "anamnesis",
    ]
    ordering_fields = ["fecha_atencion"]
    ordering = ["-fecha_atencion"]


class RecordatorioVacunaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Recordatorios de Vacuna con endpoint de alertas.
    """
    queryset = RecordatorioVacuna.objects.select_related("mascota").all()
    serializer_class = RecordatorioVacunaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["mascota", "tipo", "estado"]
    search_fields = ["nombre", "mascota__nombre"]
    ordering_fields = ["fecha_programada"]
    ordering = ["fecha_programada"]

    @action(detail=False, methods=["get"], url_path="alertas")
    def alertas(self, request):
        """
        GET /api/recordatorios-vacuna/alertas/

        Devuelve los recordatorios que necesitan atención:
        - Vencidos (fecha programada ya pasó, sin aplicación).
        - Próximos a vencer (≤ 7 días).
        - Pendientes explícitamente marcados.

        Excluye los ya aplicados.
        """
        hoy = date.today()
        limite = hoy + timedelta(days=7)

        recordatorios = RecordatorioVacuna.objects.select_related("mascota").filter(
            fecha_aplicacion__isnull=True,  # Sin aplicar
        ).filter(
            Q(fecha_programada__lt=hoy)          # Vencidos
            | Q(fecha_programada__lte=limite)     # Próximos a vencer (≤ 7 días)
        ).order_by("fecha_programada")

        serializer = self.get_serializer(recordatorios, many=True)

        # Agrupar para mayor claridad en la respuesta
        vencidos = []
        proximos = []
        pendientes = []
        for item in serializer.data:
            estado_calc = item.get("estado_calculado", "")
            if estado_calc == "Vencida":
                vencidos.append(item)
            elif estado_calc == "Próxima a vencer":
                proximos.append(item)
            else:
                pendientes.append(item)

        return Response(
            {
                "resumen": {
                    "total_alertas": len(serializer.data),
                    "vencidos": len(vencidos),
                    "proximos_a_vencer": len(proximos),
                    "pendientes": len(pendientes),
                },
                "vencidos": vencidos,
                "proximos_a_vencer": proximos,
                "pendientes": pendientes,
            }
        )


class InventarioVacunaViewSet(viewsets.ModelViewSet):
    """CRUD de Inventario de Vacunas con acción para reabastecer stock."""
    queryset = InventarioVacuna.objects.all()
    serializer_class = InventarioVacunaSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ["nombre", "dosis_disponibles"]
    ordering = ["nombre"]

    @action(detail=True, methods=["post"], url_path="reabastecer")
    def reabastecer(self, request, pk=None):
        vacuna = self.get_object()
        try:
            cantidad = int(request.data.get("cantidad", 10))
        except (ValueError, TypeError):
            cantidad = 10
        vacuna.dosis_disponibles += cantidad
        vacuna.save()
        return Response({
            "mensaje": f"Se agregaron {cantidad} dosis a {vacuna.nombre}.",
            "dosis_disponibles": vacuna.dosis_disponibles,
            "total_vendido": vacuna.total_vendido,
        })


# ═══════════════════════════════════════════════════════════════════
#  VISTAS DE AUTENTICACIÓN (Login / Logout por sesión)
# ═══════════════════════════════════════════════════════════════════

def login_view(request):
    """
    Vista de inicio de sesión basada en sesiones de Django.
    GET  → renderiza el formulario.
    POST → autentica y redirige al dashboard (o a ?next=...).
    """
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "/api/dashboard/")
            return redirect(next_url)
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, "clinica/login.html", {"error": error})


@login_required
def logout_view(request):
    """Cierra la sesión del usuario y redirige al login."""
    logout(request)
    return redirect("clinica:login")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats_view(request):
    """
    Retorna las estadísticas principales adaptadas al rol del usuario.
    - Administrador: Métricas operativas + Métricas financieras (ventas) y stock de vacunas.
    - Recepción: Métricas operativas diarias (citas hoy, tutores, pacientes).
    """
    hoy = date.today()
    limite = hoy + timedelta(days=7)

    # Identificar si es administrador
    is_admin = (request.user.username == "admin") or (request.user.is_superuser and request.user.username != "recepcion")

    # Métricas operativas
    total_tutores = Tutor.objects.count()
    total_mascotas = Mascota.objects.count()
    total_veterinarios = Veterinario.objects.count()
    citas_hoy = Cita.objects.filter(fecha=hoy, estado__in=Cita.ESTADOS_ACTIVOS).count()
    fichas_registradas = FichaClinica.objects.count()
    alertas_vacunas = RecordatorioVacuna.objects.filter(
        fecha_aplicacion__isnull=True,
        fecha_programada__lte=limite,
    ).count()

    # Métricas financieras y stock (para Administrador)
    ventas_consultas_agg = FichaClinica.objects.filter(pagado=True).aggregate(total=Sum("costo_atencion"))
    ventas_consultas = ventas_consultas_agg["total"] or 0

    vacunas_qs = InventarioVacuna.objects.all()
    vacunas_stock_total = sum(v.dosis_disponibles for v in vacunas_qs)
    vacunas_aplicadas_total = sum(v.dosis_aplicadas for v in vacunas_qs)
    ventas_vacunas = sum(v.total_vendido for v in vacunas_qs)
    ventas_totales = float(ventas_consultas) + float(ventas_vacunas)
    vacunas_bajo_stock = sum(1 for v in vacunas_qs if v.bajo_stock)

    inventario_data = InventarioVacunaSerializer(vacunas_qs, many=True).data

    data = {
        "is_admin": is_admin,
        "usuario": request.user.username,
        "nombre_usuario": request.user.get_full_name() or request.user.username,
        "rol_nombre": "Director / Administrador General" if is_admin else "Recepción & Admisión",
        "total_tutores": total_tutores,
        "total_mascotas": total_mascotas,
        "total_veterinarios": total_veterinarios,
        "citas_hoy": citas_hoy,
        "fichas_registradas": fichas_registradas,
        "alertas_vacunas": alertas_vacunas,
        # Finanzas y stock (exclusivo admin)
        "ventas_totales": ventas_totales,
        "ventas_consultas": float(ventas_consultas),
        "ventas_vacunas": float(ventas_vacunas),
        "vacunas_stock_total": vacunas_stock_total,
        "vacunas_aplicadas_total": vacunas_aplicadas_total,
        "vacunas_bajo_stock": vacunas_bajo_stock,
        "inventario_vacunas": inventario_data,
    }
    return Response(data)


@login_required
def dashboard_view(request):
    """
    Vista protegida de ejemplo (dashboard).
    Requiere autenticación — redirige al login si no hay sesión activa.
    """
    hoy = date.today()
    limite = hoy + timedelta(days=7)

    context = {
        "total_tutores": Tutor.objects.count(),
        "total_mascotas": Mascota.objects.count(),
        "citas_hoy": Cita.objects.filter(
            fecha=hoy, estado__in=Cita.ESTADOS_ACTIVOS
        ).count(),
        "alertas_vacunas": RecordatorioVacuna.objects.filter(
            fecha_aplicacion__isnull=True,
            fecha_programada__lte=limite,
        ).count(),
    }
    return render(request, "clinica/dashboard.html", context)
