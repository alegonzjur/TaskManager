"""
Script para verificar empleados en la base de datos
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Employee

app = create_app()

with app.app_context():
    print("=" * 60)
    print("VERIFICACIÓN DE EMPLEADOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    # Contar empleados
    total = Employee.query.count()
    activos = Employee.query.filter_by(is_active=True).count()
    admins = Employee.query.filter_by(role='admin').count()
    
    print(f"\n📊 Estadísticas:")
    print(f"   Total empleados: {total}")
    print(f"   Activos: {activos}")
    print(f"   Administradores: {admins}")
    
    if total == 0:
        print("\n⚠️  No hay empleados en la base de datos")
        print("   Ejecuta: python create_admin.py")
    else:
        print(f"\n👥 Lista de empleados:")
        print("-" * 60)
        
        employees = Employee.query.all()
        for emp in employees:
            status = "✅ Activo" if emp.is_active else "❌ Inactivo"
            has_pwd = "🔑 Con contraseña" if emp.password_hash else "🔓 Sin contraseña"
            role_icon = "👑" if emp.role == 'admin' else "👤"
            
            print(f"{role_icon} {emp.name}")
            print(f"   Email: {emp.email}")
            print(f"   Rol: {emp.role or 'Sin rol'}")
            print(f"   Estado: {status}")
            print(f"   Acceso: {has_pwd}")
            print(f"   ID: {emp.id}")
            print()
    
    print("=" * 60)