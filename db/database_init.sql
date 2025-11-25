-- Script de inicialización de la base de datos Task Manager
-- PostgreSQL

-- Crear la base de datos (ejecutar como superusuario)
-- DROP DATABASE IF EXISTS taskmanager_db;
-- CREATE DATABASE taskmanager_db;

-- Conectar a la base de datos
\c taskmanager_db;

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto

-- Las tablas serán creadas automáticamente por Flask-Migrate
-- Este script es principalmente para referencia y configuración inicial

-- Función para actualizar el campo updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Nota: Los triggers se crearán después de que Flask-Migrate cree las tablas
-- o puedes ejecutar estas líneas después de 'flask db upgrade':

/*
CREATE TRIGGER update_task_assignments_updated_at 
    BEFORE UPDATE ON task_assignments 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
*/

-- Crear índices adicionales para mejorar el rendimiento
-- (Flask-Migrate ya crea algunos, estos son opcionales adicionales)

/*
CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_active ON employees(is_active);
CREATE INDEX IF NOT EXISTS idx_tasks_name ON tasks(name);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_tasks_active ON tasks(is_active);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_assignments_dates ON task_assignments(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_assignments_employee_time ON task_assignments(employee_id, start_time);
*/

-- Vista útil para consultas rápidas de asignaciones actuales
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

-- Vista para estadísticas diarias
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

-- Vista para productividad por empleado
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

-- Comentarios en las tablas (para documentación)
COMMENT ON TABLE employees IS 'Tabla de empleados del equipo';
COMMENT ON TABLE tasks IS 'Catálogo de tareas preestablecidas';
COMMENT ON TABLE task_assignments IS 'Registro de asignaciones de tareas a empleados';

-- Configuración de permisos (ajustar según tus necesidades)
-- GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO tu_usuario;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tu_usuario;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tu_usuario;