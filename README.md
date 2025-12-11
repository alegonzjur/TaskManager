# Task Manager - Sistema de Asignación de Tareas

Sistema de gestión y asignación de tareas para equipos pequeños con capacidad de crecimiento. Permite realizar seguimiento en tiempo real de qué tarea está realizando cada empleado, mantiene un historial completo y permite la gestión dinámica de tareas.

## Características

- ✅ Gestión de empleados (crear, editar, desactivar)
- ✅ Catálogo de tareas preestablecidas (con opción de añadir nuevas)
- ✅ Asignación de tareas a empleados
- ✅ Seguimiento en tiempo real del estado de cada empleado
- ✅ Historial completo de asignaciones
- ✅ Estados de tarea: en progreso, pausada, completada
- ✅ Cálculo automático de duración de tareas
- ✅ API RESTful completa
- ✅ Base de datos PostgreSQL con índices optimizados
- ✅ Vistas SQL para consultas rápidas

## Tecnologías

- **Backend**: Flask 3.0
- **Base de datos**: PostgreSQL
- **ORM**: SQLAlchemy con Flask-SQLAlchemy
- **Migraciones**: Flask-Migrate (Alembic)
- **Python**: 3.8+

## Estructura del Proyecto

```
taskmanager/
├── app/
│   ├── __init__.py           # Factory de aplicación Flask
│   ├── models/
│   │   └── __init__.py       # Modelos de BD (Employee, Task, TaskAssignment)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py           # Rutas principales y dashboard
│   │   ├── employees.py      # CRUD de empleados
│   │   ├── tasks.py          # CRUD de tareas
│   │   └── assignments.py    # Gestión de asignaciones
│   ├── templates/            # Templates HTML (por implementar)
│   └── static/               # Archivos estáticos CSS/JS
│       ├── css/
│       └── js/
├── config/
│   ├── __init__.py
│   └── config.py             # Configuración de la aplicación
├── migrations/               # Migraciones de base de datos
├── instance/                 # Archivos de instancia (no versionados)
├── database_init.sql         # Script SQL de inicialización
├── requirements.txt          # Dependencias Python
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
├── run.py                   # Punto de entrada de la aplicación
└── README.md
```

## Instalación

### 1. Prerrequisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Virtualenv (recomendado)

### 2. Clonar y configurar el entorno virtual

```bash
# Activar tu entorno virtual
source taskmanager/bin/activate  # En Linux/Mac
# o
taskmanager\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar PostgreSQL

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear la base de datos
CREATE DATABASE taskmanager_db;

# Crear usuario (opcional)
CREATE USER tu_usuario WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO tu_usuario;

# Salir
\q
```

Alternativamente, puedes ejecutar el script SQL proporcionado:

```bash
psql -U postgres -f database_init.sql
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Actualiza el archivo `.env` con tus datos:

```
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@localhost:5432/taskmanager_db
SECRET_KEY=genera_una_clave_secreta_aleatoria
FLASK_ENV=development
```

### 5. Inicializar la base de datos

```bash
# Inicializar migraciones
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade

# Poblar con datos de ejemplo (opcional)
flask init-db
```

## Uso

### Iniciar la aplicación

```bash
# Modo desarrollo
python run.py

# O usando Flask CLI
flask run
```

La aplicación estará disponible en `http://localhost:5000`

### API Endpoints

#### Empleados

- `GET /employees/api` - Listar todos los empleados
- `GET /employees/api/<id>` - Obtener un empleado
- `POST /employees/api` - Crear empleado
- `PUT /employees/api/<id>` - Actualizar empleado
- `DELETE /employees/api/<id>` - Desactivar empleado
- `GET /employees/api/<id>/history` - Historial de tareas del empleado

**Ejemplo de creación de empleado:**
```json
POST /employees/api
{
  "name": "Juan Pérez",
  "email": "juan.perez@empresa.com",
  "position": "Desarrollador"
}
```

#### Tareas

- `GET /tasks/api` - Listar todas las tareas
- `GET /tasks/api/<id>` - Obtener una tarea
- `POST /tasks/api` - Crear tarea
- `PUT /tasks/api/<id>` - Actualizar tarea
- `DELETE /tasks/api/<id>` - Desactivar tarea
- `GET /tasks/api/categories` - Listar categorías
- `GET /tasks/api/<id>/history` - Historial de la tarea

**Ejemplo de creación de tarea:**
```json
POST /tasks/api
{
  "name": "Desarrollo Frontend",
  "description": "Implementar componentes React",
  "estimated_duration": 240,
  "category": "Desarrollo"
}
```

#### Asignaciones

- `GET /assignments/api` - Listar asignaciones (con filtros)
- `GET /assignments/api/<id>` - Obtener una asignación
- `POST /assignments/api` - Crear asignación (iniciar tarea)
- `PUT /assignments/api/<id>/complete` - Completar tarea
- `PUT /assignments/api/<id>/pause` - Pausar tarea
- `PUT /assignments/api/<id>/resume` - Reanudar tarea
- `PUT /assignments/api/<id>` - Actualizar notas
- `DELETE /assignments/api/<id>` - Eliminar asignación
- `GET /assignments/api/current` - Asignaciones actuales (en progreso)
- `GET /assignments/api/employee/<id>/current` - Tarea actual del empleado

**Ejemplo de iniciar una tarea:**
```json
POST /assignments/api
{
  "employee_id": 1,
  "task_id": 2,
  "notes": "Trabajando en el módulo de autenticación"
}
```

**Ejemplo de completar una tarea:**
```json
PUT /assignments/api/5/complete
{
  "notes": "Tarea completada exitosamente"
}
```

#### Dashboard

- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/current-assignments` - Asignaciones actuales

### Filtros disponibles

Las asignaciones pueden filtrarse usando query parameters:

```
GET /assignments/api?employee_id=1&status=completada
GET /assignments/api?start_date=2024-01-01&end_date=2024-01-31
GET /assignments/api?task_id=3
```

## Modelos de Datos

### Employee (Empleado)
- `id`: ID único
- `name`: Nombre del empleado
- `email`: Email (único)
- `position`: Puesto de trabajo
- `is_active`: Estado activo/inactivo
- `created_at`: Fecha de creación

### Task (Tarea)
- `id`: ID único
- `name`: Nombre de la tarea (único)
- `description`: Descripción detallada
- `estimated_duration`: Duración estimada en minutos
- `category`: Categoría de la tarea
- `is_active`: Estado activo/inactivo
- `created_at`: Fecha de creación

### TaskAssignment (Asignación)
- `id`: ID único
- `employee_id`: FK al empleado
- `task_id`: FK a la tarea
- `start_time`: Hora de inicio
- `end_time`: Hora de finalización (null si está en progreso)
- `status`: Estado (en_progreso, pausada, completada)
- `notes`: Notas adicionales
- `created_at`: Fecha de creación
- `updated_at`: Última actualización

## Vistas SQL Útiles

El script `database_init.sql` crea varias vistas útiles:

- `current_assignments_view`: Asignaciones actuales con información completa
- `daily_stats_view`: Estadísticas diarias de productividad
- `employee_productivity_view`: Métricas por empleado

Puedes consultarlas directamente:

```sql
SELECT * FROM current_assignments_view;
SELECT * FROM employee_productivity_view WHERE employee_id = 1;
```

## Comandos Flask CLI

```bash
# Inicializar BD con datos de ejemplo
flask init-db

# Crear migraciones
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade
```

## Desarrollo Futuro

Próximas características planificadas:

- [ ] Interfaz web (templates HTML + JavaScript)
- [ ] Autenticación y autorización de usuarios
- [ ] Reportes y gráficos de productividad
- [ ] Notificaciones en tiempo real
- [ ] Exportación de datos (CSV, PDF)
- [ ] API de integración con herramientas externas
- [ ] App móvil

## Contribución

Este proyecto está en desarrollo activo. Para contribuir:

1. Crea un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## Licencia



## Contacto

