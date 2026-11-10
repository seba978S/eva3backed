"""
Comando de gestión: seed_petcare
Carga datos de demostración completos en la base de datos.

Uso:
    python manage.py seed_petcare
    python manage.py seed_petcare --clear   # Limpia datos previos antes de crear
"""

from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clinica.models import (
    Tutor, Mascota, Veterinario, Cita, FichaClinica, RecordatorioVacuna, InventarioVacuna,
)


class Command(BaseCommand):
    help = "Carga datos de demostración para PetCare (usuarios, veterinarios, tutores, mascotas, citas, fichas, vacunas)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina todos los datos de la app clínica antes de crear los nuevos.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Limpiando datos existentes…")
            InventarioVacuna.objects.all().delete()
            RecordatorioVacuna.objects.all().delete()
            FichaClinica.objects.all().delete()
            Cita.objects.all().delete()
            Mascota.objects.all().delete()
            Tutor.objects.all().delete()
            Veterinario.objects.all().delete()
            self.stdout.write(self.style.WARNING("  ✓ Datos eliminados"))

        hoy = date.today()

        # ══════════════════════════════════════════════════════════
        #  USUARIOS
        # ══════════════════════════════════════════════════════════
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@petcare.cl",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Administrador",
            },
        )
        admin_user.set_password("admin1234")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"  ✓ Superusuario: admin / admin1234 {'(creado)' if created else '(actualizado)'}"))

        recep_user, created = User.objects.get_or_create(
            username="recepcion",
            defaults={
                "email": "recepcion@petcare.cl",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Camila",
                "last_name": "Reyes",
            },
        )
        recep_user.set_password("recepcion123")
        recep_user.is_staff = True
        recep_user.is_superuser = True
        recep_user.save()
        self.stdout.write(self.style.SUCCESS(f"  ✓ Recepcionista (Superuser): recepcion / recepcion123 {'(creado)' if created else '(actualizado)'}"))

        # ══════════════════════════════════════════════════════════
        #  VETERINARIOS
        # ══════════════════════════════════════════════════════════
        vet1, _ = Veterinario.objects.get_or_create(
            nombre_completo="Ana Torres",
            defaults={
                "especialidad": "Medicina General",
                "telefono": "+56 9 8765 4321",
                "email": "ana.torres@petcare.cl",
                "horario_inicio": time(8, 0),
                "horario_fin": time(18, 0),
                "activo": True,
            },
        )
        vet2, _ = Veterinario.objects.get_or_create(
            nombre_completo="Carlos Méndez",
            defaults={
                "especialidad": "Cirugía Veterinaria",
                "telefono": "+56 9 7654 3210",
                "email": "carlos.mendez@petcare.cl",
                "horario_inicio": time(9, 0),
                "horario_fin": time(17, 0),
                "activo": True,
            },
        )
        vet3, _ = Veterinario.objects.get_or_create(
            nombre_completo="Patricia Soto",
            defaults={
                "especialidad": "Dermatología y Alergias",
                "telefono": "+56 9 6543 2109",
                "email": "patricia.soto@petcare.cl",
                "horario_inicio": time(10, 0),
                "horario_fin": time(19, 0),
                "activo": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("  ✓ 3 veterinarios creados"))

        # ══════════════════════════════════════════════════════════
        #  TUTORES
        # ══════════════════════════════════════════════════════════
        t1, _ = Tutor.objects.get_or_create(
            rut_dni="12.345.678-9",
            defaults={
                "nombre_completo": "María González Paredes",
                "telefono": "+56 9 1234 5678",
                "email": "maria.gonzalez@mail.cl",
                "direccion": "Av. Providencia 1234, Santiago",
            },
        )
        t2, _ = Tutor.objects.get_or_create(
            rut_dni="98.765.432-1",
            defaults={
                "nombre_completo": "Juan Pérez Morales",
                "telefono": "+56 9 2345 6789",
                "email": "juan.perez@mail.cl",
                "direccion": "Los Leones 567, Providencia",
            },
        )
        t3, _ = Tutor.objects.get_or_create(
            rut_dni="15.678.901-2",
            defaults={
                "nombre_completo": "Catalina Muñoz Rivera",
                "telefono": "+56 9 3456 7890",
                "email": "catalina.munoz@mail.cl",
                "direccion": "Manuel Montt 890, Ñuñoa",
            },
        )
        t4, _ = Tutor.objects.get_or_create(
            rut_dni="11.222.333-4",
            defaults={
                "nombre_completo": "Roberto Silva Fuentes",
                "telefono": "+56 9 4567 8901",
                "email": "roberto.silva@mail.cl",
                "direccion": "Irarrázaval 2345, Ñuñoa",
            },
        )
        self.stdout.write(self.style.SUCCESS("  ✓ 4 tutores creados"))

        # ══════════════════════════════════════════════════════════
        #  MASCOTAS
        # ══════════════════════════════════════════════════════════
        m1, _ = Mascota.objects.get_or_create(
            tutor=t1, nombre="Firulais",
            defaults={"especie": "Perro", "raza": "Labrador Retriever",
                       "fecha_nacimiento": date(2020, 3, 15), "peso": 28.5,
                       "sexo": "M", "observaciones": "Alérgico al pollo."},
        )
        m2, _ = Mascota.objects.get_or_create(
            tutor=t1, nombre="Michi",
            defaults={"especie": "Gato", "raza": "Siamés",
                       "fecha_nacimiento": date(2021, 7, 22), "peso": 4.2,
                       "sexo": "H", "observaciones": "Muy juguetona."},
        )
        m3, _ = Mascota.objects.get_or_create(
            tutor=t2, nombre="Rocky",
            defaults={"especie": "Perro", "raza": "Pastor Alemán",
                       "fecha_nacimiento": date(2019, 1, 10), "peso": 35.0,
                       "sexo": "M", "observaciones": "Displasia de cadera leve."},
        )
        m4, _ = Mascota.objects.get_or_create(
            tutor=t3, nombre="Luna",
            defaults={"especie": "Gato", "raza": "Persa",
                       "fecha_nacimiento": date(2022, 11, 5), "peso": 3.8,
                       "sexo": "H", "observaciones": ""},
        )
        m5, _ = Mascota.objects.get_or_create(
            tutor=t4, nombre="Thor",
            defaults={"especie": "Perro", "raza": "Bulldog Francés",
                       "fecha_nacimiento": date(2023, 4, 18), "peso": 12.1,
                       "sexo": "M", "observaciones": "Tendencia a dermatitis."},
        )
        m6, _ = Mascota.objects.get_or_create(
            tutor=t3, nombre="Coco",
            defaults={"especie": "Exótico", "raza": "Tortuga de Orejas Rojas",
                       "fecha_nacimiento": date(2018, 6, 1), "peso": 1.5,
                       "sexo": "H", "observaciones": "Requiere terrario con temperatura controlada."},
        )
        self.stdout.write(self.style.SUCCESS("  ✓ 6 mascotas creadas"))

        # ══════════════════════════════════════════════════════════
        #  CITAS
        # ══════════════════════════════════════════════════════════
        citas_data = [
            # Citas de hoy
            (m1, vet1, hoy, time(9, 0), time(9, 30), "Control general de rutina", "Confirmada"),
            (m3, vet1, hoy, time(10, 0), time(10, 30), "Revisión displasia de cadera", "Pendiente"),
            (m5, vet3, hoy, time(11, 0), time(11, 30), "Evaluación dermatitis", "Pendiente"),
            # Citas de mañana
            (m2, vet1, hoy + timedelta(days=1), time(8, 30), time(9, 0), "Vacunación anual", "Pendiente"),
            (m4, vet2, hoy + timedelta(days=1), time(10, 0), time(10, 30), "Esterilización programada", "Confirmada"),
            (m6, vet1, hoy + timedelta(days=1), time(14, 0), time(14, 30), "Revisión de caparazón", "Pendiente"),
            # Citas pasadas (atendidas)
            (m1, vet1, hoy - timedelta(days=7), time(9, 0), time(9, 30), "Vacunación antirrábica", "Atendida"),
            (m3, vet2, hoy - timedelta(days=14), time(11, 0), time(12, 0), "Cirugía menor — extracción de tumor benigno", "Atendida"),
            (m5, vet3, hoy - timedelta(days=5), time(10, 0), time(10, 30), "Primera evaluación dermatológica", "Atendida"),
            # Cita cancelada
            (m2, vet1, hoy - timedelta(days=3), time(15, 0), time(15, 30), "Desparasitación", "Cancelada"),
        ]
        for mascota, vet, fecha, hi, hf, motivo, estado in citas_data:
            Cita.objects.get_or_create(
                mascota=mascota,
                veterinario=vet,
                fecha=fecha,
                hora_inicio=hi,
                defaults={"hora_fin": hf, "motivo": motivo, "estado": estado},
            )
        self.stdout.write(self.style.SUCCESS("  ✓ 10 citas creadas"))

        # ══════════════════════════════════════════════════════════
        #  FICHAS CLÍNICAS
        # ══════════════════════════════════════════════════════════
        f1, _ = FichaClinica.objects.get_or_create(
            mascota=m1, veterinario=vet1,
            diagnostico="Paciente en buen estado general",
            defaults={
                "anamnesis": "Tutor reporta buen apetito y actividad normal. Sin vómitos ni diarrea.",
                "tratamiento": "Continuar con dieta hipoalergénica. Próximo control en 6 meses.",
                "receta_medica": "Omega 3 cápsulas — 1 diaria con alimento por 30 días.",
                "examenes_solicitados": "Hemograma completo, perfil bioquímico",
                "resultados_examenes": "Hemograma: valores dentro de rango normal. Perfil bioquímico: sin alteraciones.",
                "costo_atencion": 25000,
                "pagado": True,
            },
        )
        f2, _ = FichaClinica.objects.get_or_create(
            mascota=m3, veterinario=vet2,
            diagnostico="Tumor benigno subcutáneo en región costal derecha",
            defaults={
                "anamnesis": "Tutor notó bulto en costado derecho hace 2 semanas, crecimiento lento.",
                "tratamiento": "Extracción quirúrgica exitosa. Biopsia enviada a laboratorio.",
                "receta_medica": "Meloxicam 0.1 mg/kg cada 24h por 5 días.\nAmoxicilina 22 mg/kg cada 12h por 7 días.\nUsar collar isabelino por 10 días.",
                "examenes_solicitados": "Biopsia de tejido extirpado",
                "resultados_examenes": "Biopsia: lipoma benigno, bordes limpios. Sin indicación de malignidad.",
                "costo_atencion": 95000,
                "pagado": True,
            },
        )
        f3, _ = FichaClinica.objects.get_or_create(
            mascota=m5, veterinario=vet3,
            diagnostico="Dermatitis atópica canina leve a moderada",
            defaults={
                "anamnesis": "Prurito intenso en zona ventral y patas. Rascado constante hace 3 semanas.",
                "tratamiento": "Baños medicados con clorhexidina 2 veces/semana. Dieta de eliminación por 8 semanas.",
                "receta_medica": "Apoquel (oclacitinib) 0.4 mg/kg cada 12h por 14 días, luego cada 24h.\nShampoo Malaseb — baños cada 3 días por 2 semanas.",
                "examenes_solicitados": "Raspado cutáneo, cultivo fúngico, citología de piel",
                "resultados_examenes": "Raspado: negativo para ácaros. Citología: inflamación leve, sin infección bacteriana secundaria.",
                "costo_atencion": 35000,
                "pagado": True,
            },
        )
        f4, _ = FichaClinica.objects.get_or_create(
            mascota=m2, veterinario=vet1,
            diagnostico="Paciente sana, apta para vacunación",
            defaults={
                "anamnesis": "Gata indoor, sin contacto con otros animales. Apetito y comportamiento normal.",
                "tratamiento": "Se aplica vacuna triple felina. Próxima dosis en 1 año.",
                "receta_medica": "No requiere medicación.",
                "examenes_solicitados": "",
                "resultados_examenes": "",
                "costo_atencion": 20000,
                "pagado": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("  ✓ 4 fichas clínicas creadas"))

        # ══════════════════════════════════════════════════════════
        #  RECORDATORIOS DE VACUNAS / CONTROLES
        # ══════════════════════════════════════════════════════════
        recordatorios_data = [
            # Vacunas vencidas
            (m1, "Vacuna", "Refuerzo Antirrábica", hoy - timedelta(days=15), None, "Pendiente",
             "Refuerzo anual pendiente."),
            (m3, "Vacuna", "Séxtuple Canina", hoy - timedelta(days=10), None, "Pendiente",
             "Vacuna vencida, reprogramar urgente."),
            # Próximas a vencer (≤ 7 días)
            (m5, "Control Periódico", "Control Dermatológico", hoy + timedelta(days=3), None, "Pendiente",
             "Seguimiento de dermatitis atópica."),
            (m2, "Vacuna", "Triple Felina", hoy + timedelta(days=5), None, "Pendiente",
             "Dosis de refuerzo anual."),
            (m6, "Control Periódico", "Revisión de Caparazón", hoy + timedelta(days=2), None, "Pendiente",
             "Control semestral de caparazón y estado general."),
            # Aplicadas
            (m1, "Vacuna", "Antirrábica 2025", hoy - timedelta(days=365), hoy - timedelta(days=365), "Aplicada",
             "Aplicada en control de rutina."),
            (m3, "Vacuna", "Antirrábica 2025", hoy - timedelta(days=200), hoy - timedelta(days=200), "Aplicada",
             "Aplicada sin inconvenientes."),
            (m4, "Vacuna", "Triple Felina 2025", hoy - timedelta(days=120), hoy - timedelta(days=120), "Aplicada",
             "Primera dosis aplicada."),
            # Pendientes futuras
            (m4, "Vacuna", "Refuerzo Triple Felina", hoy + timedelta(days=30), None, "Pendiente",
             "Segunda dosis programada."),
            (m1, "Control Periódico", "Control Semestral", hoy + timedelta(days=60), None, "Pendiente",
             "Control general cada 6 meses."),
        ]
        for mascota, tipo, nombre, f_prog, f_aplic, estado, notas in recordatorios_data:
            RecordatorioVacuna.objects.get_or_create(
                mascota=mascota,
                nombre=nombre,
                defaults={
                    "tipo": tipo,
                    "fecha_programada": f_prog,
                    "fecha_aplicacion": f_aplic,
                    "estado": estado,
                    "notas": notas,
                },
            )
        self.stdout.write(self.style.SUCCESS("  ✓ 10 recordatorios de vacuna creados"))

        # ══════════════════════════════════════════════════════════
        #  INVENTARIO DE VACUNAS Y VENTAS (Módulo Administrador)
        # ══════════════════════════════════════════════════════════
        inventario_data = [
            ("Antirrábica Canina / Felina", 18, 12, 18000, 5),
            ("Séxtuple Canina (DHPPI+L)", 14, 8, 22000, 5),
            ("Triple Felina (FVRCP)", 12, 6, 20000, 5),
            ("Parvovirus / Coronavirus Canino", 4, 11, 19000, 5),  # Bajo stock
            ("Leucemia Felina (FeLV)", 10, 4, 25000, 5),
            ("KC Kennel Cough (Tos de las Perreras)", 8, 5, 16000, 4),
        ]
        for nom, stock, aplicadas, precio, min_stock in inventario_data:
            InventarioVacuna.objects.get_or_create(
                nombre=nom,
                defaults={
                    "dosis_disponibles": stock,
                    "dosis_aplicadas": aplicadas,
                    "precio_unitario": precio,
                    "stock_minimo": min_stock,
                },
            )
        self.stdout.write(self.style.SUCCESS("  ✓ 6 ítems de inventario de vacunas creados"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("═" * 50))
        self.stdout.write(self.style.SUCCESS(" 🐾 PetCare — Datos de demostración cargados"))
        self.stdout.write(self.style.SUCCESS("═" * 50))
        self.stdout.write(f"  Usuarios:        admin / admin1234  |  recepcion / recepcion123")
        self.stdout.write(f"  Veterinarios:    {Veterinario.objects.count()}")
        self.stdout.write(f"  Tutores:         {Tutor.objects.count()}")
        self.stdout.write(f"  Mascotas:        {Mascota.objects.count()}")
        self.stdout.write(f"  Citas:           {Cita.objects.count()}")
        self.stdout.write(f"  Fichas clínicas: {FichaClinica.objects.count()}")
        self.stdout.write(f"  Recordatorios:   {RecordatorioVacuna.objects.count()}")
        self.stdout.write(f"  Stock Vacunas:   {sum(v.dosis_disponibles for v in InventarioVacuna.objects.all())} dosis disponibles")
        self.stdout.write("")

