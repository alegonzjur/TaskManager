-- Script de inicialización de base de datos PostgreSQL para Task Manager
-- Ejecutar como superusuario de PostgreSQL (postgres)

-- Crear usuario si no existe
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'taskuser') THEN
      
      CREATE USER taskuser WITH PASSWORD 'taskpassword';
   END IF;
END
$do$;

-- Crear base de datos si no existe
SELECT 'CREATE DATABASE taskmanager'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'taskmanager')\gexec

-- Conectar a la base de datos
\c taskmanager

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;

-- Otorgar privilegios en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO taskuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO taskuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO taskuser;

-- Configurar privilegios por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO taskuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO taskuser;

-- Mensaje de confirmación
\echo '✓ Base de datos taskmanager creada correctamente'
\echo '✓ Usuario taskuser configurado'
\echo ''
\echo 'Credenciales:'
\echo '  Base de datos: taskmanager'
\echo '  Usuario: taskuser'
\echo '  Password: taskpassword'
\echo '  Host: localhost'
\echo '  Puerto: 5432'
\echo ''
\echo 'Cadena de conexión:'
\echo '  postgresql://taskuser:taskpassword@localhost:5432/taskmanager'