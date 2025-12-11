from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# Tabla intermedia para tareas asignables a empleados específicos
task_allowed_employees = db.Table('task_allowed_employees',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Attendance(db.Model):
    """Modelo para registro de fichajes (entrada/salida)"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Tiempos
    check_in = db.Column(db.DateTime, nullable=False)  # Hora de entrada
    check_out = db.Column(db.DateTime)  # Hora de salida (null si está fichado)
    
    # Ubicación y notas
    location = db.Column(db.String(20), nullable=False)  # 'office' o 'home'
    notes = db.Column(db.Text)  # Notas opcionales
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con empleado
    employee = db.relationship('Employee', backref=db.backref('attendances', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Attendance {self.employee.name if self.employee else "Unknown"} - {self.check_in}>'
    
    def get_duration_minutes(self):
        """Calcula la duración del fichaje en minutos"""
        if not self.check_out:
            # Si aún está fichado, calcular hasta ahora
            duration = datetime.utcnow() - self.check_in
        else:
            duration = self.check_out - self.check_in
        return int(duration.total_seconds() / 60)
    
    def get_duration_formatted(self):
        """Retorna duración formateada como HH:MM"""
        minutes = self.get_duration_minutes()
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def is_active(self):
        """Verifica si el fichaje está activo (sin salida)"""
        return self.check_out is None
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        def to_iso_utc(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.isoformat() + 'Z'
            return dt.isoformat()
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'check_in': to_iso_utc(self.check_in),
            'check_out': to_iso_utc(self.check_out),
            'location': self.location,
            'location_display': 'Oficina' if self.location == 'office' else 'Casa (Teletrabajo)',
            'notes': self.notes,
            'duration_minutes': self.get_duration_minutes(),
            'duration_formatted': self.get_duration_formatted(),
            'is_active': self.is_active(),
            'created_at': to_iso_utc(self.created_at),
            'updated_at': to_iso_utc(self.updated_at)
        }


class Employee(db.Model):
    """Modelo para empleados con autenticación"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    position = db.Column(db.String(100))
    
    # Campos de autenticación
    password_hash = db.Column(db.String(255))
    birth_date = db.Column(db.Date)  # Fecha de nacimiento
    role = db.Column(db.String(20), default='employee')  # 'admin' o 'employee'
    
    # Estado y metadata
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con asignaciones de tareas
    task_assignments = db.relationship('TaskAssignment', backref='employee', 
                                      lazy='dynamic', cascade='all, delete-orphan')
    
    # Relación con tareas permitidas
    allowed_tasks = db.relationship('Task', secondary=task_allowed_employees,
                                   back_populates='allowed_employees')
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == 'admin'
    
    # Métodos requeridos por Flask-Login
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def to_dict(self, include_sensitive=False):
        """Convierte el objeto a diccionario"""
        def to_iso_utc(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.isoformat() + 'Z'
            return dt.isoformat()
        
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'position': self.position,
            'is_active': self.is_active,
            'role': self.role,
            'created_at': to_iso_utc(self.created_at)
        }
        
        if include_sensitive:
            data['birth_date'] = self.birth_date.isoformat() if self.birth_date else None
            data['last_login'] = to_iso_utc(self.last_login)
            data['has_password'] = bool(self.password_hash)
        
        return data


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
        def to_iso_utc(dt):
            if dt is None:
                return None
            if dt.tzinfo is None:
                return dt.isoformat() + 'Z'
            return dt.isoformat()
        
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'category': self.category,
            'is_active': self.is_active,
            'assigned_to_all': self.assigned_to_all,
            'created_at': to_iso_utc(self.created_at)
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
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # NULL para descansos
    
    # Control de tiempo
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    pause_time = db.Column(db.DateTime)  # Momento en que se pausó
    total_paused_duration = db.Column(db.Integer, default=0)  # Minutos totales pausados
    
    # Estado de la tarea
    status = db.Column(db.String(20), default='en_progreso')  # en_progreso, completada, detenida, descanso
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
        # Función auxiliar para convertir datetime a ISO con 'Z' (UTC)
        def to_iso_utc(dt):
            if dt is None:
                return None
            # Si no tiene timezone, asumimos que es UTC
            if dt.tzinfo is None:
                return dt.isoformat() + 'Z'
            return dt.isoformat()
        
        # Determinar si es un descanso
        is_break = self.status == 'descanso' or self.task_id is None
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'task_id': self.task_id,
            'task_name': '☕ Descanso' if is_break else (self.task.name if self.task else None),
            'is_break': is_break,
            'start_time': to_iso_utc(self.start_time),
            'end_time': to_iso_utc(self.end_time),
            'pause_time': to_iso_utc(self.pause_time),
            'total_paused_duration': self.total_paused_duration or 0,
            'status': self.status,
            'notes': self.notes,
            'created_at': to_iso_utc(self.created_at),
            'updated_at': to_iso_utc(self.updated_at)
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