from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import TaskAssignment, Employee, Task
from datetime import datetime
from sqlalchemy import and_, or_

bp = Blueprint('assignments', __name__, url_prefix='/assignments')


@bp.route('/')
@login_required
def index():
    """Vista de asignaciones"""
    return render_template('assignments/index.html')


@bp.route('/api')
@login_required
def get_assignments():
    """API para obtener asignaciones con filtros opcionales"""
    employee_id = request.args.get('employee_id', type=int)
    task_id = request.args.get('task_id', type=int)
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = TaskAssignment.query
    
    # Aplicar filtros
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(TaskAssignment.start_time >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(TaskAssignment.start_time <= end_dt)
        except ValueError:
            pass
    
    assignments = query.order_by(TaskAssignment.start_time.desc()).all()
    
    return jsonify({
        'assignments': [assignment.to_dict() for assignment in assignments]
    })


@bp.route('/api/<int:assignment_id>')
@login_required
def get_assignment(assignment_id):
    """API para obtener una asignación específica"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    return jsonify(assignment.to_dict())


@bp.route('/api', methods=['POST'])
@login_required
def create_assignment():
    """API para crear una nueva asignación (iniciar tarea o descanso)"""
    data = request.get_json()
    
    # Validaciones
    if not data.get('employee_id'):
        return jsonify({'error': 'El ID del empleado es obligatorio'}), 400
    
    # Verificar si es un descanso
    is_break = data.get('is_break', False)
    
    if not is_break and not data.get('task_id'):
        return jsonify({'error': 'El ID de la tarea es obligatorio'}), 400
    
    # Verificar que el empleado existe y está activo
    employee = Employee.query.get(data['employee_id'])
    if not employee or not employee.is_active:
        return jsonify({'error': 'Empleado no encontrado o inactivo'}), 404
    
    # Verificar si el empleado ya tiene una tarea en progreso o descanso
    active_assignment = TaskAssignment.query.filter_by(
        employee_id=data['employee_id'],
        status='en_progreso'
    ).first()
    
    active_break = TaskAssignment.query.filter_by(
        employee_id=data['employee_id'],
        status='descanso'
    ).first()
    
    if active_assignment:
        return jsonify({
            'error': 'El empleado ya tiene una tarea en progreso',
            'active_assignment': active_assignment.to_dict()
        }), 400
    
    if active_break:
        return jsonify({
            'error': 'El empleado ya está en descanso',
            'active_assignment': active_break.to_dict()
        }), 400
    
    # Crear asignación
    if is_break:
        # Crear registro de descanso (sin task_id)
        assignment = TaskAssignment(
            employee_id=data['employee_id'],
            task_id=None,
            start_time=datetime.utcnow(),
            status='descanso',
            notes=data.get('notes', '☕ Descanso')
        )
        message = '☕ Descanso iniciado'
    else:
        # Verificar que la tarea existe y está activa
        task = Task.query.get(data['task_id'])
        if not task or not task.is_active:
            return jsonify({'error': 'Tarea no encontrada o inactiva'}), 404
        
        assignment = TaskAssignment(
            employee_id=data['employee_id'],
            task_id=data['task_id'],
            start_time=datetime.utcnow(),
            status='en_progreso',
            notes=data.get('notes', '')
        )
        message = f'Tarea iniciada: {task.name}'
    
    try:
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            'message': message,
            'assignment': assignment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>/complete', methods=['PUT'])
@login_required
def complete_assignment(assignment_id):
    """API para completar una asignación (marcarla como terminada)"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    # Puede completarse desde 'en_progreso', 'pausada', o 'detenida' (legacy)
    if assignment.status == 'completada':
        return jsonify({'error': 'La tarea ya está completada'}), 400
    
    # Solo el empleado asignado o admin pueden completar
    if not current_user.is_admin() and assignment.employee_id != current_user.id:
        return jsonify({'error': 'No tienes permiso para completar esta tarea'}), 403
    
    data = request.get_json() or {}
    
    # Si aún no tiene end_time (viene de en_progreso), ponerlo ahora
    if not assignment.end_time:
        assignment.end_time = datetime.utcnow()
    
    assignment.status = 'completada'
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': '¡Tarea completada exitosamente!',
            'assignment': assignment.to_dict(),
            'duration_minutes': assignment.get_duration_minutes()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>/stop', methods=['PUT'])
@login_required
def stop_assignment(assignment_id):
    """API para detener una asignación temporalmente (descanso o tarea)"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    # Permitir detener tanto tareas en progreso como descansos
    if assignment.status not in ['en_progreso', 'descanso']:
        return jsonify({'error': 'Solo se pueden detener tareas en progreso o descansos activos'}), 400
    
    data = request.get_json() or {}
    
    # Detener sin completar (para descanso o cambiar de tarea)
    assignment.end_time = datetime.utcnow()
    assignment.status = 'pausada'  # Cambiado de 'detenida' a 'pausada'
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tarea/descanso detenido. Puedes iniciar otra tarea.',
            'assignment': assignment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@bp.route('/api/<int:assignment_id>', methods=['PUT'])
@login_required
def update_assignment(assignment_id):
    """API para actualizar notas de una asignación"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    data = request.get_json()
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Asignación actualizada exitosamente',
            'assignment': assignment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>', methods=['DELETE'])
@login_required
def delete_assignment(assignment_id):
    """API para eliminar una asignación"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    try:
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'message': 'Asignación eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/current')
@login_required
def get_current_assignments():
    """API para obtener todas las asignaciones actuales (en progreso y descansos)"""
    assignments = TaskAssignment.query.filter(
        TaskAssignment.status.in_(['en_progreso', 'descanso'])
    ).all()
    
    return jsonify({
        'assignments': [assignment.to_dict() for assignment in assignments],
        'count': len(assignments)
    })


@bp.route('/api/employee/<int:employee_id>/current')
@login_required
def get_employee_current_assignment(employee_id):
    """API para obtener la asignación actual de un empleado"""
    employee = Employee.query.get_or_404(employee_id)
    
    assignment = TaskAssignment.query.filter_by(
        employee_id=employee_id,
        status='en_progreso'
    ).first()
    
    if assignment:
        return jsonify({
            'assignment': assignment.to_dict()
        })
    else:
        return jsonify({
            'assignment': None,
            'message': 'El empleado no tiene tareas en progreso'
        })