"""
Configuración del Django Admin para PetCare.
Panel de administración avanzado con inlines, filtros y búsquedas.
"""

from django.contrib import admin
from .models import (
    Tutor,
    Mascota,
    Veterinario,
    Cita,
    FichaClinica,
    RecordatorioVacuna,
    InventarioVacuna,
)


# ═══════════════════════════════════════════════════════════════════
#  Personalización global del sitio Admin
# ═══════════════════════════════════════════════════════════════════
admin.site.site_header = "PetCare - Administración Clínica"
admin.site.site_title = "PetCare Admin"
admin.site.index_title = "Panel de Gestión Veterinaria"


# ═══════════════════════════════════════════════════════════════════
#  INLINES
# ═══════════════════════════════════════════════════════════════════
class MascotaInline(admin.TabularInline):
    """Muestra las mascotas dentro de la vista del Tutor."""
    model = Mascota
    extra = 1
    fields = ("nombre", "especie", "raza", "sexo", "peso", "fecha_nacimiento")
    show_change_link = True


class FichaClinicaInline(admin.StackedInline):
    """Muestra las fichas clínicas dentro de la vista de Mascota."""
    model = FichaClinica
    extra = 0
    fields = (
        "veterinario",
        "cita",
        "fecha_atencion",
        "anamnesis",
        "diagnostico",
        "tratamiento",
        "receta_medica",
        "examenes_solicitados",
        "resultados_examenes",
    )
    readonly_fields = ("fecha_atencion",)
    show_change_link = True


class RecordatorioVacunaInline(admin.TabularInline):
    """Muestra los recordatorios de vacuna dentro de la vista de Mascota."""
    model = RecordatorioVacuna
    extra = 0
    fields = (
        "tipo",
        "nombre",
        "fecha_programada",
        "fecha_aplicacion",
        "estado",
        "estado_actual",
    )
    readonly_fields = ("estado_actual",)
    show_change_link = True

    @admin.display(description="Estado calculado")
    def estado_actual(self, obj):
        return obj.estado_calculado if obj.pk else "—"


class CitaInline(admin.TabularInline):
    """Muestra las citas dentro de la vista de Mascota."""
    model = Cita
    extra = 0
    fields = (
        "veterinario",
        "fecha",
        "hora_inicio",
        "hora_fin",
        "motivo",
        "estado",
    )
    show_change_link = True


# ═══════════════════════════════════════════════════════════════════
#  MODEL ADMINS
# ═══════════════════════════════════════════════════════════════════

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "rut_dni", "telefono", "email", "fecha_registro")
    search_fields = ("nombre_completo", "rut_dni", "email", "telefono")
    list_filter = ("fecha_registro",)
    ordering = ("nombre_completo",)
    date_hierarchy = "fecha_registro"
    inlines = [MascotaInline]


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "especie",
        "raza",
        "sexo",
        "peso",
        "tutor",
        "fecha_nacimiento",
    )
    search_fields = ("nombre", "raza", "tutor__nombre_completo")
    list_filter = ("especie", "sexo")
    ordering = ("nombre",)
    inlines = [CitaInline, FichaClinicaInline, RecordatorioVacunaInline]


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "especialidad",
        "telefono",
        "email",
        "horario_inicio",
        "horario_fin",
        "activo",
    )
    search_fields = ("nombre_completo", "especialidad", "email")
    list_filter = ("activo", "especialidad")
    ordering = ("nombre_completo",)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "hora_inicio",
        "hora_fin",
        "mascota",
        "veterinario",
        "motivo_corto",
        "estado",
    )
    search_fields = (
        "mascota__nombre",
        "veterinario__nombre_completo",
        "motivo",
    )
    list_filter = ("estado", "fecha", "veterinario")
    ordering = ("-fecha", "hora_inicio")
    date_hierarchy = "fecha"

    @admin.display(description="Motivo")
    def motivo_corto(self, obj):
        """Muestra los primeros 60 caracteres del motivo."""
        if obj.motivo:
            return obj.motivo[:60] + ("…" if len(obj.motivo) > 60 else "")
        return "—"


@admin.register(FichaClinica)
class FichaClinicaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mascota",
        "veterinario",
        "fecha_atencion",
        "costo_atencion",
        "pagado",
        "diagnostico_corto",
    )
    search_fields = (
        "mascota__nombre",
        "veterinario__nombre_completo",
        "diagnostico",
        "anamnesis",
    )
    list_filter = ("veterinario", "fecha_atencion", "pagado")
    ordering = ("-fecha_atencion",)
    date_hierarchy = "fecha_atencion"
    readonly_fields = ("fecha_atencion",)

    @admin.display(description="Diagnóstico")
    def diagnostico_corto(self, obj):
        if obj.diagnostico:
            return obj.diagnostico[:80] + ("…" if len(obj.diagnostico) > 80 else "")
        return "—"


@admin.register(RecordatorioVacuna)
class RecordatorioVacunaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "mascota",
        "fecha_programada",
        "fecha_aplicacion",
        "estado",
        "estado_actual",
    )
    search_fields = ("nombre", "mascota__nombre")
    list_filter = ("tipo", "estado", "fecha_programada")
    ordering = ("fecha_programada",)
    date_hierarchy = "fecha_programada"

    @admin.display(description="Estado calculado")
    def estado_actual(self, obj):
        return obj.estado_calculado


@admin.register(InventarioVacuna)
class InventarioVacunaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "dosis_disponibles",
        "dosis_aplicadas",
        "precio_unitario",
        "total_vendido_formato",
        "bajo_stock_badge",
    )
    search_fields = ("nombre",)
    list_filter = ("stock_minimo",)
    ordering = ("nombre",)

    @admin.display(description="Total Vendido ($)")
    def total_vendido_formato(self, obj):
        return f"${obj.total_vendido:,.0f}"

    @admin.display(description="Alerta Stock")
    def bajo_stock_badge(self, obj):
        return "⚠️ Bajo Stock" if obj.bajo_stock else "✅ Normal"
