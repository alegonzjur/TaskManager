from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con asignaciones
    assignments = db.relationship('TaskAssignment', backref='employee', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Establece el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def get_current_task(self):
        """Obtiene la tarea actual del usuario"""
        return TaskAssignment.query.filter_by(
            user_id=self.id,
            completed=False
        ).order_by(TaskAssignment.started_at.desc()).first()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """Modelo de Tarea"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relación con asignaciones
    assignments = db.relationship('TaskAssignment', backref='task', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.name}>'


class TaskAssignment(db.Model):
    """Modelo de Asignación de Tarea"""
    __tablename__ = 'task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    def complete(self):
        """Marca la tarea como completada"""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def duration_minutes(self):
        """Calcula la duración en minutos"""
        if self.completed and self.completed_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds() / 60, 1)
        return None
    
    def __repr__(self):
        return f'<TaskAssignment {self.id}: User {self.user_id} - Task {self.task_id}>'


@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario para Flask-Login"""
    return User.query.get(int(user_id))