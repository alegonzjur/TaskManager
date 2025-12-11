-- ============================================
-- MIGRACIÓN: Sistema de Fichaje (Attendance)
-- ============================================

-- Crear tabla de fichajes (attendance)
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Tiempos de entrada y salida
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    
    -- Ubicación y notas
    location VARCHAR(20) NOT NULL CHECK (location IN ('office', 'home')),
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_out_after_check_in CHECK (check_out IS NULL OR check_out > check_in)
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_attendance_employee_id ON attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_check_in ON attendance(check_in);
CREATE INDEX IF NOT EXISTS idx_attendance_check_out ON attendance(check_out);
CREATE INDEX IF NOT EXISTS idx_attendance_active ON attendance(employee_id, check_out) WHERE check_out IS NULL;

-- Comentarios descriptivos
COMMENT ON TABLE attendance IS 'Registro de fichajes de entrada y salida de empleados';
COMMENT ON COLUMN attendance.check_in IS 'Hora de entrada (fichaje)';
COMMENT ON COLUMN attendance.check_out IS 'Hora de salida (NULL si aún está fichado)';
COMMENT ON COLUMN attendance.location IS 'Ubicación: office (oficina) o home (casa/teletrabajo)';
COMMENT ON COLUMN attendance.notes IS 'Notas opcionales del empleado';

-- Verificar que se creó correctamente
SELECT 
    'Tabla attendance creada correctamente' AS status,
    COUNT(*) AS total_records
FROM attendance;

COMMIT;