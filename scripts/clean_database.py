"""
Script para limpiar todos los datos de la base de datos
ADVERTENCIA: Esto borrará TODOS los registros
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Employee, Task, TaskAssignment

app = create_app()

with app.app_context():
    print("=" * 60)
    print("⚠️  LIMPIEZA DE BASE DE DATOS")
    print("=" * 60)
    
    # Contar registros actuales
    employees_count = Employee.query.count()
    tasks_count = Task.query.count()
    assignments_count = TaskAssignment.query.count()
    
    print(f"\n📊 Registros actuales:")
    print(f"   Empleados: {employees_count}")
    print(f"   Tareas: {tasks_count}")
    print(f"   Asignaciones: {assignments_count}")
    
    if employees_count == 0 and tasks_count == 0 and assignments_count == 0:
        print("\n✅ La base de datos ya está vacía")
        exit(0)
    
    print("\n⚠️  ADVERTENCIA:")
    print("   Esto borrará TODOS los datos (empleados, tareas, asignaciones)")
    print("   La estructura de las tablas se mantendrá")
    
    confirm = input("\n¿Estás seguro? Escribe 'SI' para confirmar: ").strip()
    
    if confirm != 'SI':
        print("\n❌ Operación cancelada")
        exit(0)
    
    print("\n🗑️  Borrando datos...")
    
    try:
        # Borrar en orden (por las foreign keys)
        deleted_assignments = TaskAssignment.query.delete()
        print(f"   ✅ {deleted_assignments} asignaciones eliminadas")
        
        # Limpiar tabla intermedia task_allowed_employees
        from app.models import task_allowed_employees
        db.session.execute(task_allowed_employees.delete())
        print(f"   ✅ Relaciones tarea-empleado eliminadas")
        
        deleted_tasks = Task.query.delete()
        print(f"   ✅ {deleted_tasks} tareas eliminadas")
        
        deleted_employees = Employee.query.delete()
        print(f"   ✅ {deleted_employees} empleados eliminados")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ BASE DE DATOS LIMPIADA EXITOSAMENTE")
        print("=" * 60)
        print("\n💡 Próximos pasos:")
        print("   1. Crear admin: python create_admin.py")
        print("   2. Iniciar app: python run.py")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al limpiar: {str(e)}")