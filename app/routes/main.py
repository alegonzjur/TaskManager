from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import User, Task, TaskAssignment
from sqlalchemy import func

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """Vista principal - Dashboard del equipo"""
    # Obtener todos los usuarios activos
    users = User.query.filter_by(is_active=True).all()
    
    # Obtener tareas activas
    active_tasks = Task.query.filter_by(is_active=True).all()
    
    # Preparar datos para el dashboard
    team_status = []
    for user in users:
        current_task = user.get_current_task()
        team_status.append({
            'user': user,
            'current_task': current_task
        })
    
    return render_template('main/index.html', 
                         team_status=team_status,
                         active_tasks=active_tasks)


@bp.route('/history')
@login_required
def history():
    """Vista del historial de tareas"""
    # Obtener historial completo ordenado por fecha
    assignments = TaskAssignment.query.filter_by(completed=True)\
        .order_by(TaskAssignment.completed_at.desc())\
        .limit(100)\
        .all()
    
    return render_template('main/history.html', assignments=assignments)


@bp.route('/my-tasks')
@login_required
def my_tasks():
    """Vista de mis tareas"""
    # Tareas actuales del usuario
    current_task = current_user.get_current_task()
    
    # Historial personal
    my_history = TaskAssignment.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(TaskAssignment.completed_at.desc()).limit(20).all()
    
    # Estadísticas personales
    total_completed = TaskAssignment.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).count()
    
    return render_template('main/my_tasks.html',
                         current_task=current_task,
                         my_history=my_history,
                         total_completed=total_completed)