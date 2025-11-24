# Guía de Instalación de PostgreSQL en Mac

## Opción 1: Usando Homebrew (Recomendado)

### 1. Instalar Homebrew (si no lo tienes)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instalar PostgreSQL
```bash
brew install postgresql@16
```

### 3. Iniciar PostgreSQL
```bash
# Iniciar ahora
brew services start postgresql@16

# O iniciar solo una vez
pg_ctl -D /opt/homebrew/var/postgresql@16 start
```

### 4. Crear base de datos y usuario
```bash
# Acceder a PostgreSQL
psql postgres

# Dentro de psql, ejecutar:
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'taskpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;

# Salir
\q
```

## Opción 2: Usando Postgres.app (Interfaz Gráfica)

### 1. Descargar Postgres.app
Descarga desde: https://postgresapp.com/

### 2. Instalar y abrir
- Arrastra Postgres.app a Aplicaciones
- Abre la aplicación
- Haz clic en "Initialize" para crear un nuevo servidor

### 3. Configurar PATH (añadir a ~/.zshrc o ~/.bash_profile)
```bash
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
```

### 4. Crear base de datos
```bash
# Abrir terminal y ejecutar:
psql

# Crear base de datos y usuario
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'taskpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;

# Salir
\q
```

## Verificar Instalación

```bash
# Verificar versión
psql --version

# Verificar que el servicio está corriendo
pg_isready

# Conectar a la base de datos
psql -U taskuser -d taskmanager
```

## Configuración en Task Manager

Una vez instalado PostgreSQL, edita el archivo `.env`:

```
DATABASE_URL=postgresql://taskuser:taskpassword@localhost:5432/taskmanager
```

## Comandos Útiles

```bash
# Ver bases de datos
psql -l

# Conectar a una base de datos
psql -U taskuser -d taskmanager

# Comandos dentro de psql:
\l          # Listar bases de datos
\dt         # Listar tablas
\d+ tabla   # Describir tabla
\q          # Salir

# Detener PostgreSQL
brew services stop postgresql@16
```

## Solución de Problemas

### Error: "psql: command not found"
Añade PostgreSQL a tu PATH en ~/.zshrc:
```bash
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
```

### Error: "Connection refused"
Verifica que PostgreSQL está corriendo:
```bash
brew services list
```

Si no está activo:
```bash
brew services start postgresql@16
```

### Error: "FATAL: role does not exist"
Crea el usuario manualmente:
```bash
psql postgres
CREATE USER taskuser WITH PASSWORD 'taskpassword';
```

## Alternativa: SQLite (Solo para desarrollo/pruebas)

Si prefieres no instalar PostgreSQL para pruebas iniciales, puedes usar SQLite modificando `.env`:

```
DATABASE_URL=sqlite:///app.db
```

**Nota:** SQLite es más simple pero tiene limitaciones. PostgreSQL es recomendado para producción.