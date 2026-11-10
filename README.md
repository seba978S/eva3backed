# 🐾 PetCare — Sistema de Gestión Veterinaria y Fichas Médicas

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2%20LTS-darkgreen?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.14%2B-red?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

Sistema web integral y API RESTful diseñado para clínicas veterinarias, permitiendo la administración eficiente de tutores, pacientes (mascotas), jornadas y disponibilidad de médicos veterinarios, agendamiento de citas con prevención de solapamientos horarios, expedientes clínicos digitales y control de vacunación con semáforo preventivo.

---

## 📌 Problemática y Solución

### Problemática
En los centros de atención veterinaria tradicionales, la gestión manual o desarticulada genera:
1. **Solapamiento de citas médicas**: Múltiples pacientes citados al mismo profesional en el mismo bloque horario.
2. **Pérdida o dispersión del historial clínico**: Dificultad para acceder rápidamente a diagnósticos previos, tratamientos aplicados, recetas o exámenes emitidos.
3. **Abandono o retraso en esquemas de vacunación**: Falta de seguimiento preventivo que pone en riesgo la salud animal y la salud pública (enfermedades zoonóticas como la rabia).

### Solución Implementada
**PetCare** centraliza toda la operación en una plataforma unificada:
- **Motor anti-colisión horaria**: Validación estricta a nivel de modelo de base de datos y serializador de API para impedir reservas simultáneas.
- **Expediente digital único por paciente**: Historial cronológico con diagnósticos, prescripciones, exámenes y tratamientos.
- **Sistema de alertas inteligentes de vacunación**: Detección automática en tiempo real de vacunas vencidas, próximas a vencer (≤ 7 días) o aplicadas mediante semáforo visual.
- **Arquitectura desacoplada y responsiva**: Frontend interactivo que consume endpoints asíncronos vía Fetch API con protección de sesiones y CSRF.

---

## 🏗️ Arquitectura Tecnológica

- **Backend**: Python 3 con Django 4.2 LTS.
- **API REST**: Django REST Framework (DRF) con filtros avanzados (`django-filter`), ordenamiento y serializadores anidados.
- **Base de Datos**: PostgreSQL para entornos de producción (AWS EC2) y SQLite conmutador para pruebas locales ágiles vía variable de entorno `USE_SQLITE`.
- **Frontend**: Django Templates + Bootstrap 5.3 + Bootstrap Icons + JavaScript Vanilla (Fetch API asíncrono con manejo de CSRF).
- **Seguridad**: Autenticación por sesiones de Django, permisos `IsAuthenticated` en todos los endpoints de API y decoradores `@login_required` en vistas web.
- **Administración**: Django Admin personalizado con inlines anidados, búsquedas y filtros por jerarquías temporales.

---

## 📂 Estructura del Proyecto

```text
eva3backed/
├── clinica/                          # Aplicación principal
│   ├── management/commands/          # Comandos personalizados
│   │   └── seed_petcare.py           # Generador de datos de prueba
│   ├── migrations/                   # Migraciones de base de datos
│   ├── templates/clinica/            # Plantillas HTML
│   │   ├── base.html                 # Layout principal con sidebar responsivo
│   │   ├── login.html                # Pantalla de inicio de sesión
│   │   └── dashboard.html            # Panel unificado SPA (4 módulos)
│   ├── admin.py                      # Configuración avanzada de Django Admin
│   ├── models.py                     # Modelos relacionales y reglas de negocio
│   ├── serializers.py                # Serializadores DRF con validaciones
│   ├── urls.py                       # Rutas de API y autenticación
│   └── views.py                      # ViewSets, endpoints y vistas web
├── petcare_project/                  # Configuración raíz de Django
│   ├── asgi.py
│   ├── settings.py                   # Ajustes generales y variables .env
│   ├── urls.py                       # Enrutador principal
│   └── wsgi.py
├── media/                            # Archivos multimedia de usuarios
├── static/                           # Archivos estáticos personalizados
├── .env                              # Variables de entorno activas
├── .env.example                      # Plantilla de variables de entorno
├── manage.py                         # Utilidad CLI de Django
├── prompts_ia.md                     # Registro detallado de prompts de IA
├── README.md                         # Documentación técnica
└── requirements.txt                  # Dependencias del proyecto
```

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio y acceder a la carpeta
```bash
git clone <URL_DEL_REPOSITORIO>
cd eva3backed
```

### 2. Crear y activar entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (`.env`)
El proyecto incluye un archivo de plantilla [`.env.example`](file:///c:/Users/arria/OneDrive/Desktop/eva3backed/.env.example). Crea tu archivo `.env` a partir de la plantilla:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

El archivo `.env` viene configurado con soporte completo para PostgreSQL y opción de fallback local:
```ini
USE_SQLITE=True

# Configuración PostgreSQL (para AWS EC2 o producción)
DB_NAME=petcare_db
DB_USER=petcare_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=*
```

### 5. Aplicar migraciones
```bash
python manage.py makemigrations clinica
python manage.py migrate
```

---

## 🧪 Carga de Datos de Demostración (`seed_petcare`)

Ejecuta el comando personalizado para poblar la base de datos con información realista (veterinarios, tutores, pacientes, citas, historiales y recordatorios):

```bash
# Poblar o actualizar datos de prueba
python manage.py seed_petcare

# Para limpiar la base de datos y cargar desde cero
python manage.py seed_petcare --clear
```

### 🔑 Credenciales de Acceso de Prueba

| Usuario | Contraseña | Rol | Acceso |
|---------|------------|-----|--------|
| `admin` | `admin1234` | Superusuario / Director Médico | Panel Web (`/api/dashboard/`) y Admin (`/admin/`) |
| `recepcion` | `recepcion123` | Personal Administrativo / Staff | Panel Web (`/api/dashboard/`) y Admin (`/admin/`) |

---

## 🚀 Ejecución del Servidor

Inicia el servidor de desarrollo local:
```bash
python manage.py runserver
```

Una vez iniciado, accede desde tu navegador web:
- **Aplicación Web Principal / Dashboard**: [http://localhost:8000/](http://localhost:8000/) (redirige automáticamente al Dashboard o Login).
- **Panel Django Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **API Browsable DRF**: [http://localhost:8000/api/](http://localhost:8000/api/)

---

## 🌐 Endpoints Principales de la API REST

Todos los endpoints requieren autenticación de sesión:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET / POST` | `/api/tutores/` | Listado y registro de tutores |
| `GET / PUT / DELETE` | `/api/tutores/{id}/` | Detalle, edición o eliminación de tutor |
| `GET / POST` | `/api/mascotas/` | Listado y registro de mascotas |
| `GET` | `/api/mascotas/{id}/historial/` | **Expediente completo** (fichas clínicas y vacunas) |
| `GET` | `/api/veterinarios/{id}/disponibilidad/?fecha=YYYY-MM-DD` | **Bloques horarios de 30 min** (disponibles/ocupados) |
| `GET / POST` | `/api/citas/` | Citas con validación anti-solapamiento |
| `PATCH` | `/api/citas/{id}/` | Cambio rápido de estado (`Confirmada`, `Atendida`, `Cancelada`) |
| `GET / POST` | `/api/fichas-clinicas/` | Registro de atenciones médicas y recetas |
| `GET` | `/api/recordatorios-vacuna/alertas/` | **Alertas clasificadas**: vencidas, próximas a vencer y pendientes |
| `PATCH` | `/api/recordatorios-vacuna/{id}/` | Marcar vacuna o control periódico como aplicado |
| `GET` | `/api/stats/` | Métricas generales para las tarjetas del panel |

---

## ☁️ Despliegue en AWS EC2 (Producción)

### Información de Instancia Cloud
- **Proveedor:** Amazon Web Services (AWS)
- **Servicio:** Elastic Compute Cloud (EC2)
- **Sistema Operativo:** Ubuntu Server 22.04 LTS
- **Servidor Web / Proxy Inverso:** Nginx
- **Servidor WSGI:** Gunicorn con Systemd
- **Motor de Base de Datos:** PostgreSQL

### 🌐 IP Pública / Enlace de Producción
> **Dirección IP Pública EC2:** `[CONFIGURAR TRAS LANZAR INSTANCIA EN AWS]`  
> **Ejemplo:** `http://54.xxx.xxx.xxx/`  
> *(Actualizar esta sección una vez completada la instancia en la consola de AWS)*

---

## 👥 Autores y Evaluación
- **Asignatura:** Desarrollo Backend / Aplicaciones Web Avanzadas
- **Evaluación:** Evaluación 3 (EVA 3)
- **Año:** 2026

