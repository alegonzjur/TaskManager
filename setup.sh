#!/bin/bash

# Script de configuración inicial para Task Manager
# Este script facilita la instalación y configuración del proyecto

set -e  # Salir si hay algún error

echo "================================================"
echo "Task Manager - Script de Configuración Inicial"
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    print_error "Por favor, ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# 1. Verificar Python
print_info "Verificando instalación de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 no está instalado. Por favor, instálalo primero."
    exit 1
fi

# 2. Verificar PostgreSQL
print_info "Verificando instalación de PostgreSQL..."
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | cut -d " " -f 3)
    print_success "PostgreSQL $PSQL_VERSION encontrado"
else
    print_warning "PostgreSQL no está instalado o no está en el PATH"
    print_info "Por favor, instala PostgreSQL antes de continuar"
fi

# 3. Verificar/activar entorno virtual
print_info "Verificando entorno virtual..."
if [ -d "taskmanager" ]; then
    print_success "Entorno virtual 'taskmanager' encontrado"
    
    # Activar entorno virtual
    if [ -f "taskmanager/bin/activate" ]; then
        source taskmanager/bin/activate
        print_success "Entorno virtual activado"
    else
        print_error "No se pudo activar el entorno virtual"
        exit 1
    fi
else
    print_warning "Entorno virtual no encontrado"
    print_info "Creando entorno virtual 'taskmanager'..."
    python3 -m venv taskmanager
    source taskmanager/bin/activate
    print_success "Entorno virtual creado y activado"
fi

# 4. Instalar dependencias
print_info "Instalando dependencias de Python..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Dependencias instaladas"

# 5. Configurar archivo .env
if [ ! -f ".env" ]; then
    print_info "Configurando archivo .env..."
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
    print_warning "IMPORTANTE: Edita el archivo .env con tus credenciales de base de datos"
    echo ""
    print_info "Debes configurar:"
    echo "  - DATABASE_URL: URL de conexión a PostgreSQL"
    echo "  - SECRET_KEY: Clave secreta para Flask"
    echo ""
else
    print_success "Archivo .env ya existe"
fi

# 6. Configurar base de datos
echo ""
print_info "¿Deseas configurar la base de datos PostgreSQL ahora? (s/n)"
read -r SETUP_DB

if [ "$SETUP_DB" = "s" ] || [ "$SETUP_DB" = "S" ]; then
    echo ""
    print_info "Ingresa el nombre de usuario de PostgreSQL (por defecto: postgres):"
    read -r DB_USER
    DB_USER=${DB_USER:-postgres}
    
    print_info "Creando base de datos taskmanager_db..."
    
    # Intentar crear la base de datos
    if psql -U "$DB_USER" -c "CREATE DATABASE taskmanager_db;" 2>/dev/null; then
        print_success "Base de datos taskmanager_db creada"
    else
        print_warning "La base de datos ya existe o hubo un error"
    fi
    
    # Preguntar si desea ejecutar el script SQL
    print_info "¿Deseas ejecutar el script de inicialización SQL? (s/n)"
    read -r RUN_SQL
    
    if [ "$RUN_SQL" = "s" ] || [ "$RUN_SQL" = "S" ]; then
        if [ -f "database_init.sql" ]; then
            psql -U "$DB_USER" -d taskmanager_db -f database_init.sql
            print_success "Script SQL ejecutado"
        else
            print_error "No se encontró database_init.sql"
        fi
    fi
fi

# 7. Inicializar migraciones
echo ""
print_info "¿Deseas inicializar las migraciones de Flask-Migrate? (s/n)"
read -r INIT_MIGRATIONS

if [ "$INIT_MIGRATIONS" = "s" ] || [ "$INIT_MIGRATIONS" = "S" ]; then
    export FLASK_APP=run.py
    
    if [ ! -d "migrations" ]; then
        print_info "Inicializando Flask-Migrate..."
        flask db init
        print_success "Flask-Migrate inicializado"
    else
        print_success "Flask-Migrate ya está inicializado"
    fi
    
    print_info "Creando migración inicial..."
    flask db migrate -m "Initial migration"
    print_success "Migración creada"
    
    print_info "Aplicando migraciones a la base de datos..."
    flask db upgrade
    print_success "Migraciones aplicadas"
    
    # 8. Poblar con datos de ejemplo
    print_info "¿Deseas poblar la base de datos con datos de ejemplo? (s/n)"
    read -r INIT_DATA
    
    if [ "$INIT_DATA" = "s" ] || [ "$INIT_DATA" = "S" ]; then
        print_info "Poblando base de datos..."
        flask init-db
        print_success "Datos de ejemplo creados"
    fi
fi

# Resumen final
echo ""
echo "================================================"
print_success "Configuración completada!"
echo "================================================"
echo ""
print_info "Para iniciar la aplicación, ejecuta:"
echo "  python run.py"
echo ""
print_info "O usando Flask CLI:"
echo "  flask run"
echo ""
print_info "La aplicación estará disponible en: http://localhost:5000"
echo ""
print_warning "Recuerda revisar y actualizar el archivo .env con tus credenciales"
echo ""