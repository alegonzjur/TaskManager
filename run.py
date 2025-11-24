#!/usr/bin/env python3
"""
Archivo principal para ejecutar la aplicación Flask
"""
import os
from app import create_app, db
from app.models import User, Task, TaskAssignment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Proporciona contexto para Flask shell"""
    return {
        'db': db,
        'User': User,
        'Task': Task,
        'TaskAssignment': TaskAssignment
    }


@app.cli.command()
def init_db():
    """Inicializa la base de datos con datos de prueba"""
    print("Creando tablas...")
    db.create_all()
    
    print("Verificando si ya existen datos...")
    if User.query.first() is not None:
        print("La base de datos ya tiene datos. Saltando inicialización.")
        return
    
    print("Creando usuario administrador...")
    admin = User(
        username='admin',
        email='admin@taskmanager.com',
        full_name='Administrador',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    print("Creando usuarios de prueba...")
    users_data = [
        ('juan', 'juan@empresa.com', 'Juan García', 'pass123'),
        ('maria', 'maria@empresa.com', 'María López', 'pass123'),
        ('carlos', 'carlos@empresa.com', 'Carlos Rodríguez', 'pass123'),
        ('ana', 'ana@empresa.com', 'Ana Martínez', 'pass123'),
    ]
    
    users = []
    for username, email, full_name, password in users_data:
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        users.append(user)
    
    print("Creando tareas de ejemplo...")
    tasks_data = [
        ('Atención al cliente', 'Responder consultas y resolver incidencias de clientes'),
        ('Revisión de inventario', 'Verificar stock y actualizar sistema'),
        ('Preparación de pedidos', 'Empaquetar y etiquetar pedidos para envío'),
        ('Control de calidad', 'Inspeccionar productos y documentar resultados'),
        ('Actualización de base de datos', 'Introducir nuevos registros y actualizar información'),
        ('Reunión de equipo', 'Participar en reunión semanal del equipo'),
        ('Formación', 'Completar módulos de formación online'),
        ('Limpieza y mantenimiento', 'Mantener área de trabajo ordenada y limpia'),
    ]
    
    for name, description in tasks_data:
        task = Task(name=name, description=description, created_by=admin.id)
        db.session.add(task)
    
    db.session.commit()
    print("✓ Base de datos inicializada correctamente!")
    print("\nCredenciales de acceso:")
    print("  Admin: admin / admin123")
    print("  Usuarios: juan, maria, carlos, ana / pass123")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)