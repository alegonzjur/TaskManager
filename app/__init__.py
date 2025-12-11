import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Cargar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Asegurar que el directorio instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Employee
        return Employee.query.get(int(user_id))
    
    # Importar modelos
    from app.models import Employee, Task, TaskAssignment
    
    # Registrar blueprints
    from app.routes import main, employees, tasks, assignments, auth, attendance
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(assignments.bp)
    app.register_blueprint(attendance.bp)
    
    # Comando personalizado para inicializar la BD con datos de ejemplo
    @app.cli.command()
    def init_db():
        """Inicializa la base de datos con datos de ejemplo"""
        db.create_all()
        
        # Verificar si ya hay datos
        if Employee.query.first() is None:
            # Crear empleados de ejemplo
            employees_data = [
                {'name': 'Ana García', 'email': 'ana.garcia@empresa.com', 'position': 'Desarrolladora Senior'},
                {'name': 'Carlos Ruiz', 'email': 'carlos.ruiz@empresa.com', 'position': 'Desarrollador'},
                {'name': 'María López', 'email': 'maria.lopez@empresa.com', 'position': 'Diseñadora UX/UI'},
                {'name': 'Juan Martínez', 'email': 'juan.martinez@empresa.com', 'position': 'Project Manager'},
            ]
            
            for emp_data in employees_data:
                employee = Employee(**emp_data)
                db.session.add(employee)
            
            # Crear tareas de ejemplo
            tasks_data = [
                {'name': 'Desarrollo Frontend', 'description': 'Implementar componentes de interfaz', 
                 'estimated_duration': 240, 'category': 'Desarrollo'},
                {'name': 'Desarrollo Backend', 'description': 'Crear APIs y lógica de negocio', 
                 'estimated_duration': 300, 'category': 'Desarrollo'},
                {'name': 'Diseño UI', 'description': 'Crear mockups y prototipos', 
                 'estimated_duration': 180, 'category': 'Diseño'},
                {'name': 'Testing', 'description': 'Pruebas funcionales y de integración', 
                 'estimated_duration': 120, 'category': 'QA'},
                {'name': 'Reunión de Equipo', 'description': 'Daily standup meeting', 
                 'estimated_duration': 30, 'category': 'Gestión'},
                {'name': 'Documentación', 'description': 'Actualizar documentación técnica', 
                 'estimated_duration': 90, 'category': 'Documentación'},
                {'name': 'Code Review', 'description': 'Revisión de código de compañeros', 
                 'estimated_duration': 60, 'category': 'Desarrollo'},
                {'name': 'Investigación', 'description': 'Investigar nuevas tecnologías o soluciones', 
                 'estimated_duration': 120, 'category': 'Investigación'},
            ]
            
            for task_data in tasks_data:
                task = Task(**task_data)
                db.session.add(task)
            
            db.session.commit()
            print('Base de datos inicializada con datos de ejemplo')
        else:
            print('La base de datos ya contiene datos')
    
    return app