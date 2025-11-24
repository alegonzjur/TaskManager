#!/usr/bin/env python3
"""
Script para verificar la conexión a PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Error: DATABASE_URL no está configurada en .env")
        return False
    
    print(f"🔍 Probando conexión a PostgreSQL...")
    print(f"   URL: {database_url.replace(database_url.split('@')[0].split('//')[1], '***')}")
    print()
    
    try:
        # Parsear la URL
        # postgresql://user:password@host:port/database
        from urllib.parse import urlparse
        result = urlparse(database_url)
        
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Intentar conexión
        connection = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        
        # Obtener información
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
        
        # Obtener lista de tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("✅ Conexión exitosa!")
        print()
        print("📊 Información de la base de datos:")
        print(f"   PostgreSQL: {version.split(',')[0]}")
        print(f"   Base de datos: {current_db}")
        print(f"   Usuario: {current_user}")
        print(f"   Host: {hostname}:{port}")
        print()
        
        if tables:
            print("📋 Tablas encontradas:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"   • {table[0]}: {count} registros")
        else:
            print("⚠️  No hay tablas creadas todavía")
            print("   Ejecuta: python run.py init-db")
        
        cursor.close()
        connection.close()
        
        print()
        print("✅ Verificación completada exitosamente")
        return True
        
    except OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print()
        print("Posibles soluciones:")
        print("1. Verifica que PostgreSQL esté corriendo: pg_isready")
        print("2. Verifica las credenciales en .env")
        print("3. Ejecuta el script de setup: ./setup_postgres.sh")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)