"""
Modelos del dominio de la Clínica Veterinaria PetCare.
"""

from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# ═══════════════════════════════════════════════════════════════════
#  TUTOR (dueño de la mascota)
# ═══════════════════════════════════════════════════════════════════
class Tutor(models.Model):
    nombre_completo = models.CharField("Nombre completo", max_length=200)
    rut_dni = models.CharField(
        "RUT / DNI",
        max_length=20,
        unique=True,
        help_text="Identificador único del tutor (ej. 12.345.678-9).",
    )
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo electrónico", blank=True)
    direccion = models.CharField("Dirección", max_length=300, blank=True)
    fecha_registro = models.DateField("Fecha de registro", auto_now_add=True)

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut_dni})"


# ═══════════════════════════════════════════════════════════════════
#  MASCOTA
# ═══════════════════════════════════════════════════════════════════
class Mascota(models.Model):
    class Especie(models.TextChoices):
        PERRO = "Perro", "Perro"
        GATO = "Gato", "Gato"
        EXOTICO = "Exótico", "Exótico"
        OTRO = "Otro", "Otro"

    class Sexo(models.TextChoices):
        MACHO = "M", "Macho"
        HEMBRA = "H", "Hembra"

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="mascotas",
        verbose_name="Tutor",
    )
    nombre = models.CharField("Nombre", max_length=100)
    especie = models.CharField(
        "Especie",
        max_length=10,
        choices=Especie.choices,
        default=Especie.PERRO,
    )
    raza = models.CharField("Raza", max_length=100, blank=True)
    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)
    peso = models.DecimalField(
        "Peso (kg)",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    sexo = models.CharField(
        "Sexo",
        max_length=1,
        choices=Sexo.choices,
        default=Sexo.MACHO,
    )
    observaciones = models.TextField("Observaciones", blank=True)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()}) — {self.tutor.nombre_completo}"


# ═══════════════════════════════════════════════════════════════════
#  VETERINARIO
# ═══════════════════════════════════════════════════════════════════
class Veterinario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="veterinario",
        verbose_name="Usuario del sistema",
        help_text="Relación opcional con un usuario de Django para acceso al sistema.",
    )
    nombre_completo = models.CharField("Nombre completo", max_length=200)
    especialidad = models.CharField("Especialidad", max_length=150, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Correo electrónico", blank=True)
    horario_inicio = models.TimeField(
        "Hora inicio jornada",
        null=True,
        blank=True,
        help_text="Ej. 08:00",
    )
    horario_fin = models.TimeField(
        "Hora fin jornada",
        null=True,
        blank=True,
        help_text="Ej. 18:00",
    )
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Veterinario"
        verbose_name_plural = "Veterinarios"
        ordering = ["nombre_completo"]

    def __str__(self):
        estado = "✓" if self.activo else "✗"
        return f"[{estado}] Dr(a). {self.nombre_completo}"


# ═══════════════════════════════════════════════════════════════════
#  CITA
# ═══════════════════════════════════════════════════════════════════
class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        CONFIRMADA = "Confirmada", "Confirmada"
        ATENDIDA = "Atendida", "Atendida"
        CANCELADA = "Cancelada", "Cancelada"

    # Los estados que ocupan el horario del veterinario (se usan para
    # la validación de solapamiento).
    ESTADOS_ACTIVOS = [Estado.PENDIENTE, Estado.CONFIRMADA, Estado.ATENDIDA]

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Mascota",
    )
    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Veterinario",
    )
    fecha = models.DateField("Fecha")
    hora_inicio = models.TimeField("Hora de inicio")
    hora_fin = models.TimeField("Hora de fin")
    motivo = models.TextField("Motivo de la consulta", blank=True)
    estado = models.CharField(
        "Estado",
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["fecha", "hora_inicio"]

    def __str__(self):
        return (
            f"Cita {self.fecha} {self.hora_inicio}–{self.hora_fin} | "
            f"{self.mascota.nombre} → Dr(a). {self.veterinario.nombre_completo} "
            f"[{self.estado}]"
        )

    # ── Regla de negocio: anti-solapamiento ──────────────────────
    def clean(self):
        """
        Impide que un veterinario tenga dos citas activas solapadas
        en la misma fecha y bloque horario.

        Dos citas se solapan si:
            cita_existente.hora_inicio < self.hora_fin
            AND
            cita_existente.hora_fin > self.hora_inicio
        """
        super().clean()

        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                {"hora_fin": "La hora de fin debe ser posterior a la hora de inicio."}
            )

        # Solo validar solapamiento si la cita está en un estado activo.
        if self.estado in self.ESTADOS_ACTIVOS:
            solapadas = Cita.objects.filter(
                veterinario=self.veterinario,
                fecha=self.fecha,
                estado__in=self.ESTADOS_ACTIVOS,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            )
            # Excluir la propia cita (para ediciones).
            if self.pk:
                solapadas = solapadas.exclude(pk=self.pk)

            if solapadas.exists():
                cita_conflicto = solapadas.first()
                raise ValidationError(
                    f"El/la Dr(a). {self.veterinario.nombre_completo} ya tiene una "
                    f"cita activa el {self.fecha} entre "
                    f"{cita_conflicto.hora_inicio} y {cita_conflicto.hora_fin}. "
                    f"No se permite solapamiento de horarios."
                )

    def save(self, *args, **kwargs):
        """Ejecuta clean() antes de guardar para garantizar la regla de negocio."""
        self.full_clean()
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════
#  FICHA CLÍNICA
# ═══════════════════════════════════════════════════════════════════
class FichaClinica(models.Model):
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="fichas_clinicas",
        verbose_name="Mascota",
    )
    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fichas_clinicas",
        verbose_name="Veterinario",
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fichas_clinicas",
        verbose_name="Cita asociada",
        help_text="Opcional. Vincula esta ficha con una cita específica.",
    )
    fecha_atencion = models.DateTimeField("Fecha de atención", auto_now_add=True)
    anamnesis = models.TextField(
        "Anamnesis",
        blank=True,
        help_text="Antecedentes y síntomas reportados por el tutor.",
    )
    diagnostico = models.TextField("Diagnóstico", blank=True)
    tratamiento = models.TextField("Tratamiento", blank=True)
    receta_medica = models.TextField("Receta médica", blank=True)
    examenes_solicitados = models.TextField("Exámenes solicitados", blank=True)
    resultados_examenes = models.TextField("Resultados de exámenes", blank=True)
    costo_atencion = models.DecimalField(
        "Costo de atención ($)",
        max_digits=10,
        decimal_places=0,
        default=25000,
        help_text="Valor cobrado por la consulta médica o procedimiento.",
    )
    pagado = models.BooleanField("Pagado", default=True)

    class Meta:
        verbose_name = "Ficha Clínica"
        verbose_name_plural = "Fichas Clínicas"
        ordering = ["-fecha_atencion"]

    def __str__(self):
        return (
            f"Ficha #{self.pk} — {self.mascota.nombre} "
            f"({self.fecha_atencion:%d/%m/%Y})"
        )


# ═══════════════════════════════════════════════════════════════════
#  RECORDATORIO DE VACUNA / CONTROL PERIÓDICO
# ═══════════════════════════════════════════════════════════════════
class RecordatorioVacuna(models.Model):
    class Tipo(models.TextChoices):
        VACUNA = "Vacuna", "Vacuna"
        CONTROL = "Control Periódico", "Control Periódico"

    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        APLICADA = "Aplicada", "Aplicada"
        VENCIDA = "Vencida", "Vencida"

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="recordatorios_vacuna",
        verbose_name="Mascota",
    )
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.VACUNA,
    )
    nombre = models.CharField(
        "Nombre de vacuna / control",
        max_length=200,
    )
    fecha_programada = models.DateField("Fecha programada")
    fecha_aplicacion = models.DateField(
        "Fecha de aplicación",
        null=True,
        blank=True,
    )
    estado = models.CharField(
        "Estado",
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    notas = models.TextField("Notas", blank=True)

    class Meta:
        verbose_name = "Recordatorio de vacuna"
        verbose_name_plural = "Recordatorios de vacunas"
        ordering = ["fecha_programada"]

    def __str__(self):
        return (
            f"{self.get_tipo_display()}: {self.nombre} — "
            f"{self.mascota.nombre} ({self.estado_calculado})"
        )

    # ── Propiedades calculadas ───────────────────────────────────
    @property
    def estado_calculado(self) -> str:
        """
        Devuelve el estado real basándose en la fecha actual:
        - 'Aplicada' si ya se registró fecha_aplicacion.
        - 'Vencida' si la fecha programada ya pasó sin aplicación.
        - 'Próxima a vencer' si faltan ≤ 7 días.
        - 'Pendiente' en caso contrario.
        """
        if self.fecha_aplicacion:
            return "Aplicada"

        hoy = date.today()
        if self.fecha_programada < hoy:
            return "Vencida"
        if self.fecha_programada <= hoy + timedelta(days=7):
            return "Próxima a vencer"
        return "Pendiente"

    @property
    def esta_vencida(self) -> bool:
        return self.estado_calculado == "Vencida"

    @property
    def proxima_a_vencer(self) -> bool:
        return self.estado_calculado == "Próxima a vencer"


# ═══════════════════════════════════════════════════════════════════
#  INVENTARIO DE VACUNAS / INSUMOS Y VENTAS
# ═══════════════════════════════════════════════════════════════════
class InventarioVacuna(models.Model):
    nombre = models.CharField("Nombre de vacuna", max_length=150, unique=True)
    dosis_disponibles = models.PositiveIntegerField("Dosis en stock", default=20)
    dosis_aplicadas = models.PositiveIntegerField("Dosis vendidas / aplicadas", default=0)
    precio_unitario = models.DecimalField(
        "Precio por dosis ($)",
        max_digits=10,
        decimal_places=0,
        default=15000,
        help_text="Valor cobrado al tutor por la aplicación.",
    )
    stock_minimo = models.PositiveIntegerField("Stock mínimo de alerta", default=5)

    class Meta:
        verbose_name = "Inventario de Vacuna"
        verbose_name_plural = "Inventario de Vacunas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (Stock: {self.dosis_disponibles} dosis | ${self.precio_unitario:,.0f})"

    @property
    def bajo_stock(self) -> bool:
        return self.dosis_disponibles <= self.stock_minimo

    @property
    def total_vendido(self) -> float:
        return float(self.dosis_aplicadas * self.precio_unitario)
