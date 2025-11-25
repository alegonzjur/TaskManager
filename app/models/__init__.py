from datetime import datetime
from app import db


# Tabla intermedia para tareas asignables a empleados específicos
task_allowed_employees = db.Table('task_allowed_employees',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


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
    
    # Relación con tareas permitidas
    allowed_tasks = db.relationship('Task', secondary=task_allowed_employees,
                                   back_populates='allowed_employees')
    
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
    assigned_to_all = db.Column(db.Boolean, default=True)  # True = todos pueden verla
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con asignaciones
    assignments = db.relationship('TaskAssignment', backref='task', 
                                 lazy='dynamic', cascade='all, delete-orphan')
    
    # Relación con empleados permitidos
    allowed_employees = db.relationship('Employee', secondary=task_allowed_employees,
                                       back_populates='allowed_tasks')
    
    def __repr__(self):
        return f'<Task {self.name}>'
    
    def to_dict(self, include_employees=False):
        """Convierte el objeto a diccionario"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'category': self.category,
            'is_active': self.is_active,
            'assigned_to_all': self.assigned_to_all,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_employees:
            data['allowed_employee_ids'] = [emp.id for emp in self.allowed_employees]
        
        return data
    
    def is_available_for_employee(self, employee_id):
        """Verifica si la tarea está disponible para un empleado específico"""
        if self.assigned_to_all:
            return True
        return any(emp.id == employee_id for emp in self.allowed_employees)


class TaskAssignment(db.Model):
    """Modelo para asignaciones de tareas a empleados"""
    __tablename__ = 'task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # Control de tiempo
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    pause_time = db.Column(db.DateTime)  # Momento en que se pausó
    total_paused_duration = db.Column(db.Integer, default=0)  # Minutos totales pausados
    
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
            'pause_time': self.pause_time.isoformat() if self.pause_time else None,
            'total_paused_duration': self.total_paused_duration,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_duration_minutes(self):
        """Calcula la duración de la tarea en minutos (excluyendo pausas)"""
        if self.end_time:
            duration = self.end_time - self.start_time
            total_minutes = int(duration.total_seconds() / 60)
            # Restar tiempo pausado
            return total_minutes - (self.total_paused_duration or 0)
        return None
    
    def get_elapsed_minutes(self):
        """Calcula el tiempo transcurrido actual (excluyendo pausas)"""
        if self.status == 'pausada' and self.pause_time:
            # Si está pausada, calcular hasta el momento de la pausa
            duration = self.pause_time - self.start_time
        else:
            # Si está en progreso, calcular hasta ahora
            duration = datetime.utcnow() - self.start_time
        
        total_minutes = int(duration.total_seconds() / 60)
        return total_minutes - (self.total_paused_duration or 0)