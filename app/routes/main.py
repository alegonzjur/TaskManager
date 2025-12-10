from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models import Employee, Task, TaskAssignment
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """Página principal - Dashboard"""
    return render_template('index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Vista del dashboard con información general"""
    return render_template('dashboard.html')


@bp.route('/test-api')
@login_required
def test_api():
    """Página de prueba de API"""
    return render_template('test_api.html')


@bp.route('/api/dashboard/stats')
def dashboard_stats():
    """API para obtener estadísticas del dashboard"""
    
    # Contar empleados activos
    active_employees = Employee.query.filter_by(is_active=True).count()
    
    # Contar tareas disponibles
    available_tasks = Task.query.filter_by(is_active=True).count()
    
    # Contar asignaciones en progreso
    active_assignments = TaskAssignment.query.filter_by(status='en_progreso').count()
    
    # Asignaciones completadas hoy
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = TaskAssignment.query.filter(
        TaskAssignment.status == 'completada',
        TaskAssignment.end_time >= today_start
    ).count()
    
    return jsonify({
        'active_employees': active_employees,
        'available_tasks': available_tasks,
        'active_assignments': active_assignments,
        'completed_today': completed_today
    })


@bp.route('/api/current-assignments')
def current_assignments():
    """API para obtener las asignaciones actuales de todos los empleados"""
    
    # Obtener asignaciones en progreso
    assignments = TaskAssignment.query.filter_by(status='en_progreso').all()
    
    return jsonify({
        'assignments': [assignment.to_dict() for assignment in assignments]
    })