-- ============================================
-- MIGRACIÓN: Sistema de Descansos
-- Permite registrar descansos sin tarea asociada
-- ============================================

-- Permitir task_id NULL para registrar descansos
ALTER TABLE task_assignments ALTER COLUMN task_id DROP NOT NULL;

-- Verificar
SELECT 
    'Migración completada' AS status,
    'task_id ahora permite NULL para descansos' AS nota;

COMMIT;