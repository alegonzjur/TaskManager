"""
Script de diagnóstico para verificar la configuración
Ejecutar: python check_config.py
"""
import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN - TASK MANAGER")
print("=" * 70)

# 1. Verificar archivo .env
print("\n1️⃣  Verificando archivo .env...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"   ✅ Archivo .env encontrado: {env_path}")
    load_dotenv()
else:
    print(f"   ❌ Archivo .env NO encontrado en: {env_path}")
    print("   Crea un archivo .env con la configuración de la base de datos")
    sys.exit(1)

# 2. Verificar variables de entorno
print("\n2️⃣  Verificando variables de entorno...")
db_url = os.environ.get('DATABASE_URL')
secret_key = os.environ.get('SECRET_KEY')
flask_env = os.environ.get('FLASK_ENV', 'production')

if db_url:
    # Ocultar contraseña en la salida
    if '@' in db_url:
        safe_url = db_url.split('://')[0] + '://' + db_url.split('@')[1]
        print(f"   ✅ DATABASE_URL: {safe_url}")
    else:
        print(f"   ⚠️  DATABASE_URL: {db_url} (formato incorrecto)")
else:
    print("   ❌ DATABASE_URL no configurada")
    sys.exit(1)

if secret_key:
    print(f"   ✅ SECRET_KEY: {'*' * len(secret_key[:10])}... (oculta)")
else:
    print("   ⚠️  SECRET_KEY no configurada (se usará una por defecto)")

print(f"   ✅ FLASK_ENV: {flask_env}")

# 3. Verificar conexión a PostgreSQL
print("\n3️⃣  Verificando conexión a PostgreSQL...")
try:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parsear URL
    result = urlparse(db_url)
    
    print(f"   📊 Host: {result.hostname}")
    print(f"   📊 Puerto: {result.port or 5432}")
    print(f"   📊 Base de datos: {result.path[1:]}")
    print(f"   📊 Usuario: {result.username}")
    
    # Intentar conexión
    print("   🔌 Intentando conectar...")
    conn = psycopg2.connect(
        host=result.hostname,
        port=result.port or 5432,
        database=result.path[1:],
        user=result.username,
        password=result.password
    )
    print("   ✅ Conexión exitosa a PostgreSQL")
    
    # Verificar si existen las tablas
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('employees', 'tasks', 'task_assignments', 'task_allowed_employees')
    """)
    tables = cursor.fetchall()
    
    print(f"\n4️⃣  Verificando tablas en la base de datos...")
    expected_tables = ['employees', 'tasks', 'task_assignments', 'task_allowed_employees']
    found_tables = [t[0] for t in tables]
    
    for table in expected_tables:
        if table in found_tables:
            print(f"   ✅ Tabla '{table}' existe")
        else:
            print(f"   ❌ Tabla '{table}' NO existe")
    
    if len(found_tables) < len(expected_tables):
        print("\n   ⚠️  Faltan tablas. Ejecuta las migraciones:")
        print("   flask db upgrade")
    
    # Verificar columnas de autenticación
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'employees' 
        AND column_name IN ('password_hash', 'role', 'birth_date', 'last_login')
    """)
    auth_columns = [c[0] for c in cursor.fetchall()]
    
    print(f"\n5️⃣  Verificando columnas de autenticación...")
    expected_columns = ['password_hash', 'role', 'birth_date', 'last_login']
    for col in expected_columns:
        if col in auth_columns:
            print(f"   ✅ Columna '{col}' existe")
        else:
            print(f"   ❌ Columna '{col}' NO existe")
    
    if len(auth_columns) < len(expected_columns):
        print("\n   ⚠️  Faltan columnas de autenticación. Ejecuta:")
        print("   flask db migrate -m 'Add authentication'")
        print("   flask db upgrade")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("   ❌ psycopg2 no está instalado")
    print("   Instala: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error de conexión: {str(e)}")
    print("\n   🔍 Posibles causas:")
    print("   - PostgreSQL no está corriendo")
    print("   - Credenciales incorrectas en .env")
    print("   - La base de datos no existe")
    sys.exit(1)

# 6. Verificar Flask y dependencias
print(f"\n6️⃣  Verificando dependencias...")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__}")
except ImportError:
    print("   ❌ Flask no instalado")

try:
    import flask_login
    print(f"   ✅ Flask-Login instalado")
except ImportError:
    print("   ❌ Flask-Login no instalado (pip install Flask-Login)")

try:
    import flask_sqlalchemy
    print(f"   ✅ Flask-SQLAlchemy instalado")
except ImportError:
    print("   ❌ Flask-SQLAlchemy no instalado")

try:
    import flask_migrate
    print(f"   ✅ Flask-Migrate instalado")
except ImportError:
    print("   ❌ Flask-Migrate no instalado")

print("\n" + "=" * 70)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 70)
print("\n💡 Próximos pasos:")
print("   1. Si faltan tablas/columnas: flask db upgrade")
print("   2. Crear admin: python create_admin.py")
print("   3. Iniciar app: python run.py")