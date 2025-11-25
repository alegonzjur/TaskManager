from datetime import datetime
from app import db


class Employee(db.Model):
    """Modelo para empleados"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con asignaciones de tareas
    task_assignments = db.relationship('TaskAssignment', backref='employee', 
                                      lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'position': self.position,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Modelo para tareas preestablecidas"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    estimated_duration = db.Column(db.Integer)  # Duración estimada en minutos
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con asignaciones
    assignments = db.relationship('TaskAssignment', backref='task', 
                                 lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.name}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TaskAssignment(db.Model):
    """Modelo para asignaciones de tareas a empleados"""
    __tablename__ = 'task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # Control de tiempo
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Estado de la tarea
    status = db.Column(db.String(20), default='en_progreso')  # en_progreso, completada, pausada
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice compuesto para búsquedas eficientes
    __table_args__ = (
        db.Index('idx_employee_status', 'employee_id', 'status'),
        db.Index('idx_task_dates', 'task_id', 'start_time'),
    )
    
    def __repr__(self):
        return f'<TaskAssignment {self.employee_id} - {self.task_id}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'task_id': self.task_id,
            'task_name': self.task.name if self.task else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_duration_minutes(self):
        """Calcula la duración de la tarea en minutos"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return None