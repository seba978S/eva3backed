# Registro de Prompts de Inteligencia Artificial — Proyecto PetCare

Este documento registra la bitácora metodológica de ingeniería de prompts utilizada para el diseño, desarrollo, validación y despliegue del sistema **PetCare (Sistema de Gestión de Citas y Fichas Médicas para Veterinaria)** con Django, Django REST Framework, PostgreSQL y Bootstrap 5.

---

## 1. Fase 1: Arquitectura Base, Modelo Relacional y Reglas de Negocio Críticas

### 1.1. Contexto y Rol
> **Rol asignado a la IA:** Desarrollador Fullstack Senior experto en Python, Django y PostgreSQL.

### 1.2. Prompt Ejecutado
```markdown
Actúa como un desarrollador Fullstack Senior experto en Python, Django y Django REST Framework (DRF). 
Vamos a construir desde cero el proyecto "petcare_project" y una app principal llamada "clinica" 
(Sistema de Gestión de Citas y Fichas Médicas para Veterinaria).

Requerimientos técnicos:
1. Configuración desacoplada en settings.py y requirements.txt con python-dotenv.
   - Conexión a PostgreSQL mediante variables (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).
   - Mecanismo de fallback local con SQLite si USE_SQLITE=True.
   - Configuración de internacionalización (América/Santiago, español chileno es-cl), archivos estáticos y media.
2. Modelado de datos relacional (clinica/models.py):
   - Tutor: nombre completo, RUT/DNI (único), teléfono, email, dirección, fecha_registro auto.
   - Mascota: relación ForeignKey con Tutor, nombre, especie (Perro, Gato, Exótico, Otro), raza, fecha_nacimiento, peso en kg, sexo (Macho/Hembra), observaciones.
   - Veterinario: relación OneToOne opcional con User de Django, nombre completo, especialidad, teléfono, email, horarios de jornada (inicio/fin) y estado activo.
   - Cita: relación con Mascota y Veterinario, fecha, hora_inicio, hora_fin, motivo, estado (Pendiente, Confirmada, Atendida, Cancelada).
     * REGLA DE NEGOCIO CRÍTICA: Implementar validación en clean() y save() (full_clean) para impedir el solapamiento de citas. Un profesional no puede tener dos citas activas en el mismo rango de fecha y hora. Excluir la propia cita en caso de actualización (pk existente).
   - FichaClinica: relación con Mascota, Veterinario y Cita (opcional), fecha_atencion auto_now_add, anamnesis, diagnóstico, tratamiento, receta médica, exámenes solicitados y resultados de exámenes.
   - RecordatorioVacuna: relación con Mascota, tipo (Vacuna / Control Periódico), nombre, fecha_programada, fecha_aplicacion nullable, estado y notas. Propiedad calculada que determine automáticamente si está 'Aplicada', 'Vencida' o 'Próxima a vencer (<= 7 días)' con respecto a la fecha actual.
```

### 1.3. Criterios de Validación Obtenidos
- Generación de migraciones limpias (`0001_initial.py`).
- Implementación de la fórmula de colisión temporal en Django ORM:
  ```python
  solapadas = Cita.objects.filter(
      veterinario=self.veterinario,
      fecha=self.fecha,
      estado__in=self.ESTADOS_ACTIVOS,
      hora_inicio__lt=self.hora_fin,
      hora_fin__gt=self.hora_inicio,
  )
  ```
- Compatibilidad garantizada para SQLite local y PostgreSQL en producción (AWS EC2).

---

## 2. Fase 2: Serializadores, ViewSets en DRF y Django Admin Avanzado

### 2.1. Contexto y Rol
> **Rol asignado a la IA:** Especialista en API RESTful con Django REST Framework y Seguridad.

### 2.2. Prompt Ejecutado
```markdown
Construye la capa de API REST con DRF y el panel de administración avanzado para PetCare:

1. Serializadores (clinica/serializers.py):
   - ModelSerializers para Tutor, Mascota, Veterinario, Cita, FichaClinica y RecordatorioVacuna.
   - Campos de sólo lectura útiles para frontend (tutor_nombre, mascota_nombre, veterinario_nombre, cantidad_mascotas, estado_calculado, proxima_a_vencer, esta_vencida).
   - En CitaSerializer, replicar y reforzar la validación de solapamiento y validación de que la cita se encuentre dentro de la jornada laboral del veterinario, respondiendo errores claros en formato JSON con código HTTP 400.
   - Serializadores anidados para el expediente médico completo de cada paciente (HistorialMascotaSerializer).

2. ViewSets y Endpoints Personalizados (@action en clinica/views.py y clinica/urls.py):
   - ModelViewSet para las 6 entidades con DefaultRouter bajo prefijo /api/.
   - Endpoint GET /api/veterinarios/{id}/disponibilidad/?fecha=YYYY-MM-DD: calcular la jornada completa del profesional dividida en bloques de 30 minutos indicando si cada bloque está 'disponible' u 'ocupado'.
   - Endpoint GET /api/mascotas/{id}/historial/: retornar ficha médica completa, tratamientos, diagnósticos, recetas, exámenes y vacunas históricas en un solo payload.
   - Endpoint GET /api/recordatorios-vacuna/alertas/: filtrar y agrupar en 'vencidos', 'proximos_a_vencer' y 'pendientes'.
   - Endpoint GET /api/stats/: métricas globales del sistema para alimentar el dashboard en tiempo real.

3. Django Admin Avanzado (clinica/admin.py):
   - Configurar site_header = "PetCare - Administración Clínica".
   - ModelAdmin con list_display, search_fields, list_filter, ordering y date_hierarchy.
   - Inlines tabulares: MascotaInline dentro de Tutor, CitaInline, FichaClinicaInline y RecordatorioVacunaInline dentro de Mascota.
```

### 2.3. Criterios de Validación Obtenidos
- Validación cruzada entre Serializer y Model (doble barrera de seguridad).
- Endpoints probados mediante suite de pruebas automatizadas con Django Test Client.
- Respuestas en formato JSON estándar con paginación, filtros y ordenamiento.

---

## 3. Fase 3: Frontend Responsivo, Consumo Asíncrono Fetch API y Comando Seed

### 3.1. Contexto y Rol
> **Rol asignado a la IA:** Desarrollador Frontend UI/UX con Bootstrap 5 y JavaScript moderno.

### 3.2. Prompt Ejecutado
```markdown
Crea el frontend web integrado y un comando seed para demostración en vivo de PetCare:

1. Estructura de Plantillas (Django Templates + Bootstrap 5 + Bootstrap Icons):
   - base.html: Layout con Sidebar lateral responsivo en tonos verde esmeralda (#1a7a4c, #14352a) y acentos turquesa, conmutador de navegación dinámica por pestañas (SPA), reloj en tiempo real, perfil de usuario autenticado y enlaces al Admin y Logout.
   - login.html: Interfaz centrada, moderna, con validación de credenciales y mensajes de alerta.
   - dashboard.html:
     * Tarjetas de resumen estadístico dinámicas (Mascotas, Citas Hoy, Fichas, Alertas de Vacunas).
     * Módulo 1 (Tutores y Mascotas): Tabla con búsqueda reactiva, visualización de mascotas vinculadas y modales interactivos para altas, bajas y modificaciones mediante Fetch API.
     * Módulo 2 (Calendario y Agendamiento): Visualizador de cuadrícula de bloques horarios de 30 minutos (disponibles/ocupados), formulario de reserva interactivo con detección de colisiones de horario y cambio rápido de estados (Confirmada, Atendida, Cancelada).
     * Módulo 3 (Ficha Clínica Digital): Buscador en tiempo real de pacientes y visualizador del expediente clínico completo con registro de nuevas atenciones.
     * Módulo 4 (Recordatorios de Vacunación): Semáforo visual (Rojo: Vencida, Amarillo: Próxima a vencer, Verde: Aplicada) con botón de acción rápida para marcar como "Aplicada".

2. Comando de Gestión Seed (clinica/management/commands/seed_petcare.py):
   - Permitir flag --clear para reiniciar datos.
   - Generar superusuario admin (admin1234), recepcionista (recepcion123), 3 veterinarios con distintas especialidades y horarios, 4 tutores, 6 mascotas de diversas especies, 10 citas en distintos estados, 4 fichas clínicas con prescripciones y 10 recordatorios de vacunas.
```

### 3.3. Criterios de Validación Obtenidos
- CSRF Token gestionado dinámicamente en cada petición `POST`, `PUT`, `PATCH` y `DELETE` vía JavaScript.
- Sistema de feedback visual inmediato mediante componentes Toast de Bootstrap.
- Ejecución limpia del comando `python manage.py seed_petcare --clear`.

---

## 4. Fase 4: Despliegue en la Nube (AWS EC2 + Gunicorn + Nginx + PostgreSQL)

*(Sección preparada para la etapa de despliegue en servidor en la nube)*

### 4.1. Prompt para Aprovisionamiento de Instancia Ubuntu 22.04 LTS en AWS EC2
```markdown
Genera el script de aprovisionamiento en Bash para una instancia AWS EC2 Ubuntu 22.04 LTS:
1. Actualización de paquetes del sistema (apt update && apt upgrade -y).
2. Instalación de dependencias: Python 3, python3-pip, python3-venv, postgresql, postgresql-contrib, libpq-dev, nginx, git, curl.
3. Creación de base de datos PostgreSQL 'petcare_db', usuario 'petcare_user' y permisos necesarios.
4. Clonación del repositorio, configuración de entorno virtual (.venv) e instalación de requirements.txt.
5. Configuración del archivo .env de producción con USE_SQLITE=False, SECRET_KEY segura, DEBUG=False y ALLOWED_HOSTS con la IP pública de EC2.
6. Ejecución de migraciones y comando collectstatic.
```

### 4.2. Prompt para Servicio Systemd (Gunicorn) y Proxy Inverso (Nginx)
```markdown
Genera los archivos de configuración de producción:
1. /etc/systemd/system/gunicorn.service:
   - Configuración de socket Unix y workers proporcionales a los vCPUs de la instancia t2.micro / t3.micro.
   - Ejecución bajo el usuario ubuntu con reinicio automático.
2. /etc/nginx/sites-available/petcare:
   - Proxy_pass hacia el socket de Gunicorn.
   - Bloques 'location /static/' y 'location /media/' con directivas de caché optimizadas.
   - Configuración de tamaño máximo de subida de archivos (client_max_body_size 20M).
```

### 4.3. Scripts de Despliegue Automatizado
- **IP Pública AWS EC2:** `[PENDIENTE DE ASIGNACIÓN TRAS LANZAR INSTANCIA]`
- **DNS / Subdominio:** `[OPCIONAL]`
- **Comando de Verificación de Estado:**
  ```bash
  sudo systemctl status gunicorn
  sudo systemctl status nginx
  ```

