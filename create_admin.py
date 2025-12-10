"""
Script para crear el usuario administrador inicial
Ejecutar: python create_admin.py
"""
import sys
import os
from datetime import date

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTANTE: Cargar variables de entorno ANTES de importar la app
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Employee

def create_admin():
    """Crear usuario administrador inicial"""
    
    # Verificar que las variables de entorno se cargaron
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: No se encontró DATABASE_URL en las variables de entorno")
        print("Asegúrate de tener un archivo .env con la configuración de la base de datos")
        print("\nEjemplo de .env:")
        print("DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/taskmanager_db")
        return
    
    print(f"📊 Conectando a la base de datos...")
    print(f"   URL: {db_url.split('@')[1] if '@' in db_url else 'No configurada'}")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si ya existe un admin
            existing_admin = Employee.query.filter_by(role='admin').first()
            
            if existing_admin:
                print(f"✅ Ya existe un administrador: {existing_admin.name} ({existing_admin.email})")
                return
        except Exception as e:
            print(f"\n❌ Error al conectar con la base de datos:")
            print(f"   {str(e)}")
            print("\n🔍 Verifica:")
            print("   1. PostgreSQL está corriendo")
            print("   2. La base de datos 'taskmanager_db' existe")
            print("   3. Las credenciales en .env son correctas")
            print("   4. Has aplicado las migraciones (flask db upgrade)")
            return
        
        # Datos del administrador
        print("=" * 60)
        print("CREAR USUARIO ADMINISTRADOR INICIAL")
        print("=" * 60)
        
        name = input("Nombre completo: ").strip()
        if not name:
            print("❌ El nombre es obligatorio")
            return
        
        email = input("Email: ").strip()
        if not email:
            print("❌ El email es obligatorio")
            return
        
        # Verificar si el email ya existe
        existing_email = Employee.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Ya existe un usuario con el email {email}")
            return
        
        password = input("Contraseña (mínimo 8 caracteres): ").strip()
        if len(password) < 8:
            print("❌ La contraseña debe tener al menos 8 caracteres")
            return
        
        password_confirm = input("Confirmar contraseña: ").strip()
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden")
            return
        
        birth_date_str = input("Fecha de nacimiento (YYYY-MM-DD) [opcional]: ").strip()
        birth_date_obj = None
        if birth_date_str:
            try:
                birth_date_obj = date.fromisoformat(birth_date_str)
            except ValueError:
                print("⚠️  Formato de fecha inválido, se omitirá")
        
        # Crear administrador
        admin = Employee(
            name=name,
            email=email,
            position='Administrador del Sistema',
            birth_date=birth_date_obj,
            role='admin',
            is_active=True
        )
        
        admin.set_password(password)
        
        try:
            db.session.add(admin)
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ ¡Administrador creado exitosamente!")
            print("=" * 60)
            print(f"Nombre: {admin.name}")
            print(f"Email: {admin.email}")
            print(f"Rol: Administrador")
            print("\nYa puedes iniciar sesión en la aplicación con estas credenciales.")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al crear administrador: {str(e)}")


if __name__ == '__main__':
    create_admin()