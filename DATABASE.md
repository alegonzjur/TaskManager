# Estructura de Base de Datos - Task Manager

## Diagrama ER (Entidad-Relación)

```
┌─────────────────┐
│   EMPLOYEES     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ email (UNIQUE)  │
│ position        │
│ is_active       │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────┐
│ TASK_ASSIGNMENTS    │
├─────────────────────┤
│ id (PK)             │
│ employee_id (FK)    │───┐
│ task_id (FK)        │   │
│ start_time          │   │
│ end_time            │   │
│ status              │   │
│ notes               │   │
│ created_at          │   │
│ updated_at          │   │
└─────────────────────┘   │
                          │
                          │ N:1
                          │
                          ▼
                    ┌─────────────┐
                    │    TASKS    │
                    ├─────────────┤
                    │ id (PK)     │
                    │ name (UQ)   │
                    │ description │
                    │ est_duration│
                    │ category    │
                    │ is_active   │
                    │ created_at  │
                    └─────────────┘
```

## Tablas

### 1. EMPLOYEES (Empleados)

Almacena información de los empleados del equipo.

| Campo      | Tipo         | Descripción                          | Restricciones |
|------------|--------------|--------------------------------------|---------------|
| id         | INTEGER      | Identificador único                  | PRIMARY KEY   |
| name       | VARCHAR(100) | Nombre completo del empleado         | NOT NULL      |
| email      | VARCHAR(120) | Correo electrónico                   | UNIQUE, NOT NULL |
| position   | VARCHAR(100) | Puesto o cargo                       | NULL          |
| is_active  | BOOLEAN      | Estado activo/inactivo               | DEFAULT TRUE  |
| created_at | DATETIME     | Fecha de creación del registro       | DEFAULT NOW() |

**Índices:**
- `idx_employees_email` ON email
- `idx_employees_active` ON is_active

**Relaciones:**
- 1:N con task_assignments (un empleado puede tener múltiples asignaciones)

---

### 2. TASKS (Tareas)

Catálogo de tareas preestablecidas disponibles para asignar.

| Campo              | Tipo         | Descripción                          | Restricciones |
|--------------------|--------------|--------------------------------------|---------------|
| id                 | INTEGER      | Identificador único                  | PRIMARY KEY   |
| name               | VARCHAR(200) | Nombre de la tarea                   | UNIQUE, NOT NULL |
| description        | TEXT         | Descripción detallada                | NULL          |
| estimated_duration | INTEGER      | Duración estimada en minutos         | NULL          |
| category           | VARCHAR(50)  | Categoría de la tarea                | NULL          |
| is_active          | BOOLEAN      | Estado activo/inactivo               | DEFAULT TRUE  |
| created_at         | DATETIME     | Fecha de creación del registro       | DEFAULT NOW() |

**Índices:**
- `idx_tasks_name` ON name
- `idx_tasks_category` ON category
- `idx_tasks_active` ON is_active

**Relaciones:**
- 1:N con task_assignments (una tarea puede ser asignada múltiples veces)

---

### 3. TASK_ASSIGNMENTS (Asignaciones)

Registro de asignaciones de tareas a empleados con seguimiento de tiempo.

| Campo       | Tipo         | Descripción                          | Restricciones |
|-------------|--------------|--------------------------------------|---------------|
| id          | INTEGER      | Identificador único                  | PRIMARY KEY   |
| employee_id | INTEGER      | ID del empleado asignado             | FK, NOT NULL  |
| task_id     | INTEGER      | ID de la tarea asignada              | FK, NOT NULL  |
| start_time  | DATETIME     | Fecha/hora de inicio de la tarea     | NOT NULL      |
| end_time    | DATETIME     | Fecha/hora de finalización           | NULL          |
| status      | VARCHAR(20)  | Estado actual                        | DEFAULT 'en_progreso' |
| notes       | TEXT         | Notas adicionales                    | NULL          |
| created_at  | DATETIME     | Fecha de creación del registro       | DEFAULT NOW() |
| updated_at  | DATETIME     | Fecha de última actualización        | DEFAULT NOW() |

**Estados válidos:**
- `en_progreso`: Tarea actualmente en ejecución
- `pausada`: Tarea temporalmente pausada
- `completada`: Tarea finalizada

**Índices:**
- `idx_employee_status` ON (employee_id, status) - Compuesto
- `idx_task_dates` ON (task_id, start_time) - Compuesto
- `idx_assignments_status` ON status
- `idx_assignments_dates` ON (start_time, end_time)
- `idx_assignments_employee_time` ON (employee_id, start_time)

**Foreign Keys:**
- employee_id → employees(id) ON DELETE CASCADE
- task_id → tasks(id) ON DELETE CASCADE

---

## Vistas (Views)

### 1. current_assignments_view

Muestra todas las asignaciones actualmente en progreso con información completa.

```sql
CREATE OR REPLACE VIEW current_assignments_view AS
SELECT 
    ta.id as assignment_id,
    e.id as employee_id,
    e.name as employee_name,
    e.position as employee_position,
    t.id as task_id,
    t.name as task_name,
    t.category as task_category,
    t.estimated_duration,
    ta.start_time,
    ta.status,
    ta.notes,
    EXTRACT(EPOCH FROM (NOW() - ta.start_time))/60 as elapsed_minutes
FROM task_assignments ta
JOIN employees e ON ta.employee_id = e.id
JOIN tasks t ON ta.task_id = t.id
WHERE ta.status = 'en_progreso'
ORDER BY ta.start_time DESC;
```

**Uso:**
```sql
SELECT * FROM current_assignments_view;
```

---

### 2. daily_stats_view

Estadísticas diarias de productividad y actividad.

```sql
CREATE OR REPLACE VIEW daily_stats_view AS
SELECT 
    DATE(ta.start_time) as date,
    COUNT(*) as total_assignments,
    COUNT(CASE WHEN ta.status = 'completada' THEN 1 END) as completed_tasks,
    COUNT(DISTINCT ta.employee_id) as active_employees,
    COUNT(DISTINCT ta.task_id) as unique_tasks,
    AVG(CASE 
        WHEN ta.end_time IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (ta.end_time - ta.start_time))/60 
    END) as avg_duration_minutes
FROM task_assignments ta
GROUP BY DATE(ta.start_time)
ORDER BY date DESC;
```

**Uso:**
```sql
-- Estadísticas de hoy
SELECT * FROM daily_stats_view 
WHERE date = CURRENT_DATE;

-- Estadísticas de la última semana
SELECT * FROM daily_stats_view 
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

---

### 3. employee_productivity_view

Métricas de productividad por empleado.

```sql
CREATE OR REPLACE VIEW employee_productivity_view AS
SELECT 
    e.id as employee_id,
    e.name as employee_name,
    e.position,
    COUNT(ta.id) as total_assignments,
    COUNT(CASE WHEN ta.status = 'completada' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN ta.status = 'en_progreso' THEN 1 END) as in_progress_tasks,
    AVG(CASE 
        WHEN ta.end_time IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (ta.end_time - ta.start_time))/60 
    END) as avg_completion_time_minutes,
    MAX(ta.start_time) as last_assignment_time
FROM employees e
LEFT JOIN task_assignments ta ON e.id = ta.employee_id
WHERE e.is_active = true
GROUP BY e.id, e.name, e.position
ORDER BY completed_tasks DESC;
```

**Uso:**
```sql
-- Ver productividad de todos los empleados
SELECT * FROM employee_productivity_view;

-- Empleado más productivo
SELECT * FROM employee_productivity_view 
ORDER BY completed_tasks DESC 
LIMIT 1;
```

---

## Consultas Útiles

### Obtener tarea actual de un empleado

```sql
SELECT 
    e.name as employee,
    t.name as task,
    ta.start_time,
    ta.notes,
    EXTRACT(EPOCH FROM (NOW() - ta.start_time))/60 as elapsed_minutes
FROM task_assignments ta
JOIN employees e ON ta.employee_id = e.id
JOIN tasks t ON ta.task_id = t.id
WHERE ta.employee_id = ? 
  AND ta.status = 'en_progreso';
```

### Historial de tareas de un empleado

```sql
SELECT 
    t.name as task,
    ta.start_time,
    ta.end_time,
    ta.status,
    CASE 
        WHEN ta.end_time IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (ta.end_time - ta.start_time))/60 
        ELSE NULL 
    END as duration_minutes
FROM task_assignments ta
JOIN tasks t ON ta.task_id = t.id
WHERE ta.employee_id = ?
ORDER BY ta.start_time DESC;
```

### Tareas más frecuentes

```sql
SELECT 
    t.name,
    t.category,
    COUNT(*) as assignment_count,
    AVG(EXTRACT(EPOCH FROM (ta.end_time - ta.start_time))/60) as avg_duration
FROM tasks t
JOIN task_assignments ta ON t.id = ta.task_id
WHERE ta.end_time IS NOT NULL
GROUP BY t.id, t.name, t.category
ORDER BY assignment_count DESC
LIMIT 10;
```

### Reporte de productividad semanal

```sql
SELECT 
    e.name,
    COUNT(CASE WHEN ta.status = 'completada' THEN 1 END) as completed,
    COUNT(CASE WHEN ta.status = 'en_progreso' THEN 1 END) as in_progress,
    SUM(EXTRACT(EPOCH FROM (ta.end_time - ta.start_time))/60) as total_minutes
FROM employees e
LEFT JOIN task_assignments ta ON e.id = ta.employee_id
WHERE ta.start_time >= CURRENT_DATE - INTERVAL '7 days'
  AND e.is_active = true
GROUP BY e.id, e.name
ORDER BY completed DESC;
```

---

## Triggers

### Actualización automática de updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_task_assignments_updated_at 
    BEFORE UPDATE ON task_assignments 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Mantenimiento

### Limpiar asignaciones antiguas

```sql
-- Eliminar asignaciones completadas de hace más de 1 año
DELETE FROM task_assignments 
WHERE status = 'completada' 
  AND end_time < NOW() - INTERVAL '1 year';
```

### Vaciar tablas (con precaución)

```sql
-- Eliminar todas las asignaciones
TRUNCATE task_assignments RESTART IDENTITY CASCADE;

-- Eliminar todos los datos
TRUNCATE employees, tasks, task_assignments RESTART IDENTITY CASCADE;
```

---

## Backup

### Exportar base de datos

```bash
pg_dump -U usuario -d taskmanager_db > backup_$(date +%Y%m%d).sql
```

### Restaurar base de datos

```bash
psql -U usuario -d taskmanager_db < backup_20241124.sql
```