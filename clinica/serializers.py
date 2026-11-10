"""
Serializers de Django REST Framework para la app Clínica PetCare.

Incluyen campos de solo lectura adicionales para consumo del frontend
y validaciones de reglas de negocio (solapamiento de citas, horario
de disponibilidad del veterinario).
"""

from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

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
#  TUTOR
# ═══════════════════════════════════════════════════════════════════
class TutorSerializer(serializers.ModelSerializer):
    cantidad_mascotas = serializers.SerializerMethodField()

    class Meta:
        model = Tutor
        fields = [
            "id",
            "nombre_completo",
            "rut_dni",
            "telefono",
            "email",
            "direccion",
            "fecha_registro",
            "cantidad_mascotas",
        ]
        read_only_fields = ["id", "fecha_registro", "cantidad_mascotas"]

    def get_cantidad_mascotas(self, obj) -> int:
        return obj.mascotas.count()


# ═══════════════════════════════════════════════════════════════════
#  MASCOTA
# ═══════════════════════════════════════════════════════════════════
class MascotaSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(
        source="tutor.nombre_completo", read_only=True
    )

    class Meta:
        model = Mascota
        fields = [
            "id",
            "tutor",
            "tutor_nombre",
            "nombre",
            "especie",
            "raza",
            "fecha_nacimiento",
            "peso",
            "sexo",
            "observaciones",
        ]
        read_only_fields = ["id", "tutor_nombre"]


# ═══════════════════════════════════════════════════════════════════
#  VETERINARIO
# ═══════════════════════════════════════════════════════════════════
class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = [
            "id",
            "user",
            "nombre_completo",
            "especialidad",
            "telefono",
            "email",
            "horario_inicio",
            "horario_fin",
            "activo",
        ]
        read_only_fields = ["id"]


# ═══════════════════════════════════════════════════════════════════
#  CITA  (con validación de solapamiento y horario)
# ═══════════════════════════════════════════════════════════════════
class CitaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(
        source="mascota.nombre", read_only=True
    )
    veterinario_nombre = serializers.CharField(
        source="veterinario.nombre_completo", read_only=True
    )
    tutor_nombre = serializers.CharField(
        source="mascota.tutor.nombre_completo", read_only=True
    )

    class Meta:
        model = Cita
        fields = [
            "id",
            "mascota",
            "mascota_nombre",
            "veterinario",
            "veterinario_nombre",
            "tutor_nombre",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "motivo",
            "estado",
        ]
        read_only_fields = [
            "id",
            "mascota_nombre",
            "veterinario_nombre",
            "tutor_nombre",
        ]

    # ── Validaciones de negocio ──────────────────────────────────
    def validate(self, attrs):
        """
        1) hora_fin > hora_inicio.
        2) La cita debe estar dentro del horario de jornada del veterinario.
        3) No debe existir solapamiento con otra cita activa del mismo
           veterinario en la misma fecha.
        """
        hora_inicio = attrs.get("hora_inicio", getattr(self.instance, "hora_inicio", None))
        hora_fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))
        fecha = attrs.get("fecha", getattr(self.instance, "fecha", None))
        veterinario = attrs.get("veterinario", getattr(self.instance, "veterinario", None))
        estado = attrs.get("estado", getattr(self.instance, "estado", Cita.Estado.PENDIENTE))

        # 1) Validar que hora_fin sea posterior a hora_inicio
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError(
                {"hora_fin": "La hora de fin debe ser posterior a la hora de inicio."}
            )

        # 2) Validar horario de jornada del veterinario
        if veterinario and hora_inicio and hora_fin:
            if veterinario.horario_inicio and hora_inicio < veterinario.horario_inicio:
                raise serializers.ValidationError(
                    {
                        "hora_inicio": (
                            f"La hora de inicio ({hora_inicio:%H:%M}) es anterior "
                            f"al inicio de jornada del Dr(a). "
                            f"{veterinario.nombre_completo} "
                            f"({veterinario.horario_inicio:%H:%M})."
                        )
                    }
                )
            if veterinario.horario_fin and hora_fin > veterinario.horario_fin:
                raise serializers.ValidationError(
                    {
                        "hora_fin": (
                            f"La hora de fin ({hora_fin:%H:%M}) excede el fin "
                            f"de jornada del Dr(a). "
                            f"{veterinario.nombre_completo} "
                            f"({veterinario.horario_fin:%H:%M})."
                        )
                    }
                )

        # 3) Validar solapamiento — solo para estados activos
        if estado in Cita.ESTADOS_ACTIVOS and veterinario and fecha:
            solapadas = Cita.objects.filter(
                veterinario=veterinario,
                fecha=fecha,
                estado__in=Cita.ESTADOS_ACTIVOS,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            if self.instance and self.instance.pk:
                solapadas = solapadas.exclude(pk=self.instance.pk)

            if solapadas.exists():
                conflicto = solapadas.first()
                raise serializers.ValidationError(
                    {
                        "hora_inicio": (
                            f"Conflicto de horario: el/la Dr(a). "
                            f"{veterinario.nombre_completo} ya tiene una cita "
                            f"programada el {fecha} de "
                            f"{conflicto.hora_inicio:%H:%M} a "
                            f"{conflicto.hora_fin:%H:%M}. "
                            f"Por favor, elija otro bloque horario."
                        )
                    }
                )

        return attrs


# ═══════════════════════════════════════════════════════════════════
#  FICHA CLÍNICA
# ═══════════════════════════════════════════════════════════════════
class FichaClinicaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(
        source="mascota.nombre", read_only=True
    )
    veterinario_nombre = serializers.CharField(
        source="veterinario.nombre_completo", read_only=True
    )
    cita_detalle = serializers.SerializerMethodField()

    class Meta:
        model = FichaClinica
        fields = [
            "id",
            "mascota",
            "mascota_nombre",
            "veterinario",
            "veterinario_nombre",
            "cita",
            "cita_detalle",
            "fecha_atencion",
            "anamnesis",
            "diagnostico",
            "tratamiento",
            "receta_medica",
            "examenes_solicitados",
            "resultados_examenes",
            "costo_atencion",
            "pagado",
        ]
        read_only_fields = [
            "id",
            "mascota_nombre",
            "veterinario_nombre",
            "cita_detalle",
            "fecha_atencion",
        ]

    def get_cita_detalle(self, obj) -> dict | None:
        if obj.cita:
            return {
                "id": obj.cita.id,
                "fecha": str(obj.cita.fecha),
                "hora_inicio": str(obj.cita.hora_inicio),
                "hora_fin": str(obj.cita.hora_fin),
                "motivo": obj.cita.motivo,
                "estado": obj.cita.estado,
            }
        return None


# ═══════════════════════════════════════════════════════════════════
#  RECORDATORIO DE VACUNA
# ═══════════════════════════════════════════════════════════════════
class RecordatorioVacunaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(
        source="mascota.nombre", read_only=True
    )
    estado_calculado = serializers.CharField(
        read_only=True,
        help_text="Estado real calculado según la fecha actual.",
    )
    esta_vencida = serializers.BooleanField(read_only=True)
    proxima_a_vencer = serializers.BooleanField(read_only=True)

    class Meta:
        model = RecordatorioVacuna
        fields = [
            "id",
            "mascota",
            "mascota_nombre",
            "tipo",
            "nombre",
            "fecha_programada",
            "fecha_aplicacion",
            "estado",
            "estado_calculado",
            "esta_vencida",
            "proxima_a_vencer",
            "notas",
        ]
        read_only_fields = [
            "id",
            "mascota_nombre",
            "estado_calculado",
            "esta_vencida",
            "proxima_a_vencer",
        ]


# ═══════════════════════════════════════════════════════════════════
#  SERIALIZERS ANIDADOS (para endpoints de historial)
# ═══════════════════════════════════════════════════════════════════
class HistorialFichaSerializer(serializers.ModelSerializer):
    """Versión resumida de FichaClinica para el historial de mascota."""
    veterinario_nombre = serializers.CharField(
        source="veterinario.nombre_completo", read_only=True
    )

    class Meta:
        model = FichaClinica
        fields = [
            "id",
            "veterinario_nombre",
            "fecha_atencion",
            "anamnesis",
            "diagnostico",
            "tratamiento",
            "receta_medica",
            "examenes_solicitados",
            "resultados_examenes",
        ]


class HistorialMascotaSerializer(serializers.ModelSerializer):
    """Serializer completo de historial: datos de la mascota + fichas + vacunas."""
    tutor_nombre = serializers.CharField(
        source="tutor.nombre_completo", read_only=True
    )
    fichas_clinicas = HistorialFichaSerializer(many=True, read_only=True)
    recordatorios_vacuna = RecordatorioVacunaSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Mascota
        fields = [
            "id",
            "nombre",
            "especie",
            "raza",
            "fecha_nacimiento",
            "peso",
            "sexo",
            "tutor",
            "tutor_nombre",
            "observaciones",
            "fichas_clinicas",
            "recordatorios_vacuna",
        ]


# ═══════════════════════════════════════════════════════════════════
#  INVENTARIO DE VACUNAS
# ═══════════════════════════════════════════════════════════════════
class InventarioVacunaSerializer(serializers.ModelSerializer):
    bajo_stock = serializers.BooleanField(read_only=True)
    total_vendido = serializers.FloatField(read_only=True)

    class Meta:
        model = InventarioVacuna
        fields = [
            "id",
            "nombre",
            "dosis_disponibles",
            "dosis_aplicadas",
            "precio_unitario",
            "stock_minimo",
            "bajo_stock",
            "total_vendido",
        ]
        read_only_fields = ["id", "bajo_stock", "total_vendido"]
