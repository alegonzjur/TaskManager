# Task Manager - Guía de Inicio Rápido

## 📦 Proyecto Completado

Se ha creado exitosamente la estructura completa de la aplicación de asignación de tareas con Flask y PostgreSQL.

## 📁 Estructura del Proyecto

```
taskmanager/
├── app/                           # Aplicación Flask
│   ├── __init__.py               # Factory de aplicación
│   ├── models/                   # Modelos de base de datos
│   │   └── __init__.py          # Employee, Task, TaskAssignment
│   ├── routes/                   # Blueprints (rutas/endpoints)
│   │   ├── __init__.py
│   │   ├── main.py              # Dashboard y rutas principales
│   │   ├── employees.py         # CRUD de empleados
│   │   ├── tasks.py             # CRUD de tareas
│   │   └── assignments.py       # Gestión de asignaciones
│   ├── templates/                # Plantillas HTML
│   │   ├── base.html            # Template base
│   │   ├── index.html           # Página principal
│   │   ├── dashboard.html       # Dashboard
│   │   ├── employees/           # Vistas de empleados
│   │   │   └── index.html
│   │   ├── tasks/               # Vistas de tareas
│   │   │   └── index.html
│   │   └── assignments/         # Vistas de asignaciones
│   │       └── index.html
│   └── static/                   # Archivos estáticos
│       ├── css/
│       │   └── style.css        # Estilos personalizados
│       └── js/
│           └── main.js          # JavaScript principal
├── config/                       # Configuración
│   ├── __init__.py
│   └── config.py                # Configuraciones por entorno
├── migrations/                   # Migraciones de BD (se crean con Flask-Migrate)
├── instance/                     # Archivos de instancia
├── database_init.sql            # Script SQL de inicialización
├── requirements.txt             # Dependencias Python
├── .env.example                 # Ejemplo de variables de entorno
├── .gitignore                   # Archivos ignorados por Git
├── setup.sh                     # Script de instalación automatizada
├── run.py                       # Punto de entrada
├── README.md                    # Documentación principal
└── DATABASE.md                  # Documentación de BD
```

## 🚀 Instalación y Configuración

### Opción 1: Script Automatizado (Recomendado)

```bash
# Hacer ejecutable el script
chmod +x setup.sh

# Ejecutar el script de configuración
./setup.sh
```

El script te guiará a través de:
1. ✓ Verificación de Python y PostgreSQL
2. ✓ Creación/activación del entorno virtual
3. ✓ Instalación de dependencias
4. ✓ Configuración de .env
5. ✓ Creación de base de datos
6. ✓ Inicialización de migraciones
7. ✓ Población con datos de ejemplo

### Opción 2: Instalación Manual

#### Paso 1: Entorno Virtual

```bash
# Activar tu entorno virtual existente
source taskmanager/bin/activate  # Linux/Mac
# o
taskmanager\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 2: Configurar PostgreSQL

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear la base de datos
CREATE DATABASE taskmanager_db;

# (Opcional) Crear usuario
CREATE USER tu_usuario WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO tu_usuario;

\q
```

#### Paso 3: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Configurar en `.env`:
```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/taskmanager_db
SECRET_KEY=tu_clave_secreta_aleatoria_aqui
FLASK_ENV=development
```

#### Paso 4: Inicializar Base de Datos

```bash
# Configurar variable de entorno
export FLASK_APP=run.py

# Inicializar Flask-Migrate
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade

# (Opcional) Poblar con datos de ejemplo
flask init-db
```

## ▶️ Ejecutar la Aplicación

```bash
# Método 1: Python directo
python run.py

# Método 2: Flask CLI
flask run

# Método 3: Con puerto personalizado
flask run --port=8000
```

La aplicación estará disponible en: **http://localhost:5000**

## 🎯 Funcionalidades Implementadas

### ✅ Backend Completo

- **Modelos de Base de Datos**:
  - Employee (Empleados)
  - Task (Tareas preestablecidas)
  - TaskAssignment (Asignaciones con historial)

- **API RESTful Completa**:
  - Empleados: CRUD + historial
  - Tareas: CRUD + gestión de categorías
  - Asignaciones: crear, pausar, reanudar, completar

- **Características**:
  - Seguimiento de tiempo en tiempo real
  - Historial completo de asignaciones
  - Estados de tarea (en progreso, pausada, completada)
  - Validaciones de negocio
  - Índices de BD optimizados
  - Vistas SQL para consultas rápidas

### ✅ Frontend Base

- **Interfaz Web**:
  - Dashboard con estadísticas
  - Gestión de empleados
  - Gestión de tareas
  - Gestión de asignaciones
  - Actualización en tiempo real (30s)

- **Tecnologías Frontend**:
  - Bootstrap 5
  - Font Awesome
  - Axios (AJAX)
  - JavaScript vanilla

## 📊 Base de Datos

### Tablas Principales

1. **employees** - Información de empleados
2. **tasks** - Catálogo de tareas
3. **task_assignments** - Registro de asignaciones

### Vistas SQL

- `current_assignments_view` - Asignaciones actuales
- `daily_stats_view` - Estadísticas diarias
- `employee_productivity_view` - Productividad por empleado

Consulta `DATABASE.md` para documentación completa.

## 🔌 API Endpoints

### Empleados
- `GET /employees/api` - Listar empleados
- `POST /employees/api` - Crear empleado
- `GET /employees/api/<id>` - Obtener empleado
- `PUT /employees/api/<id>` - Actualizar empleado
- `DELETE /employees/api/<id>` - Desactivar empleado
- `GET /employees/api/<id>/history` - Historial

### Tareas
- `GET /tasks/api` - Listar tareas
- `POST /tasks/api` - Crear tarea
- `GET /tasks/api/<id>` - Obtener tarea
- `PUT /tasks/api/<id>` - Actualizar tarea
- `DELETE /tasks/api/<id>` - Desactivar tarea
- `GET /tasks/api/categories` - Listar categorías

### Asignaciones
- `GET /assignments/api` - Listar asignaciones (con filtros)
- `POST /assignments/api` - Crear asignación
- `PUT /assignments/api/<id>/complete` - Completar
- `PUT /assignments/api/<id>/pause` - Pausar
- `PUT /assignments/api/<id>/resume` - Reanudar
- `GET /assignments/api/current` - Asignaciones actuales

### Dashboard
- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/current-assignments` - Asignaciones en progreso

## 📝 Ejemplos de Uso

### Crear un Empleado

```bash
curl -X POST http://localhost:5000/employees/api \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ana García",
    "email": "ana@empresa.com",
    "position": "Desarrolladora"
  }'
```

### Crear una Tarea

```bash
curl -X POST http://localhost:5000/tasks/api \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Desarrollo Frontend",
    "description": "Implementar componentes React",
    "estimated_duration": 240,
    "category": "Desarrollo"
  }'
```

### Asignar Tarea

```bash
curl -X POST http://localhost:5000/assignments/api \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "task_id": 1,
    "notes": "Trabajando en el módulo de autenticación"
  }'
```

### Completar Tarea

```bash
curl -X PUT http://localhost:5000/assignments/api/1/complete \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Tarea completada exitosamente"
  }'
```

## 🔧 Comandos Útiles

```bash
# Ver migraciones
flask db history

# Crear nueva migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Poblar BD con datos de ejemplo
flask init-db

# Consola interactiva de Python con contexto de app
flask shell
```

## 🐛 Solución de Problemas

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql
```

### Error "ModuleNotFoundError"

```bash
# Asegurarse de estar en el entorno virtual
source taskmanager/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de migraciones

```bash
# Eliminar carpeta migrations y reiniciar
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📈 Próximos Pasos

1. **Autenticación**: Implementar login de usuarios
2. **Permisos**: Sistema de roles y permisos
3. **Reportes**: Gráficos y exportación de datos
4. **Notificaciones**: Alertas en tiempo real
5. **API Avanzada**: Paginación, filtros avanzados
6. **Testing**: Tests unitarios e integración
7. **Docker**: Containerización de la aplicación
8. **CI/CD**: Pipeline de despliegue automático

## 📚 Documentación

- `README.md` - Documentación principal y uso
- `DATABASE.md` - Esquema y consultas de BD
- Este archivo - Inicio rápido

## 💡 Tips

- Usa `flask shell` para explorar modelos interactivamente
- Revisa las vistas SQL en `database_init.sql` para consultas optimizadas
- El frontend usa polling cada 30s - considera WebSockets para producción
- Los datos de ejemplo incluyen 4 empleados y 8 tareas

## 🎉 ¡Listo!

Tu aplicación de Task Manager está lista para usar. 

**Accede a**: http://localhost:5000
