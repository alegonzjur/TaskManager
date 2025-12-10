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
def get_assignment(assignment_id):
    """API para obtener una asignación específica"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    return jsonify(assignment.to_dict())


@bp.route('/api', methods=['POST'])
def create_assignment():
    """API para crear una nueva asignación (iniciar tarea)"""
    data = request.get_json()
    
    # Validaciones
    if not data.get('employee_id'):
        return jsonify({'error': 'El ID del empleado es obligatorio'}), 400
    
    if not data.get('task_id'):
        return jsonify({'error': 'El ID de la tarea es obligatorio'}), 400
    
    # Verificar que el empleado y la tarea existen y están activos
    employee = Employee.query.get(data['employee_id'])
    if not employee or not employee.is_active:
        return jsonify({'error': 'Empleado no encontrado o inactivo'}), 404
    
    task = Task.query.get(data['task_id'])
    if not task or not task.is_active:
        return jsonify({'error': 'Tarea no encontrada o inactiva'}), 404
    
    # Verificar si el empleado ya tiene una tarea en progreso
    active_assignment = TaskAssignment.query.filter_by(
        employee_id=data['employee_id'],
        status='en_progreso'
    ).first()
    
    if active_assignment:
        return jsonify({
            'error': 'El empleado ya tiene una tarea en progreso',
            'active_assignment': active_assignment.to_dict()
        }), 400
    
    # Crear asignación
    assignment = TaskAssignment(
        employee_id=data['employee_id'],
        task_id=data['task_id'],
        start_time=datetime.utcnow(),
        status='en_progreso',
        notes=data.get('notes', '')
    )
    
    try:
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            'message': 'Tarea asignada exitosamente',
            'assignment': assignment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>/complete', methods=['PUT'])
def complete_assignment(assignment_id):
    """API para completar una asignación"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    if assignment.status == 'completada':
        return jsonify({'error': 'La tarea ya está completada'}), 400
    
    data = request.get_json() or {}
    
    assignment.end_time = datetime.utcnow()
    assignment.status = 'completada'
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tarea completada exitosamente',
            'assignment': assignment.to_dict(),
            'duration_minutes': assignment.get_duration_minutes()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>/pause', methods=['PUT'])
def pause_assignment(assignment_id):
    """API para pausar una asignación"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    if assignment.status != 'en_progreso':
        return jsonify({'error': 'Solo se pueden pausar tareas en progreso'}), 400
    
    data = request.get_json() or {}
    
    # Guardar el momento de la pausa
    assignment.pause_time = datetime.utcnow()
    assignment.status = 'pausada'
    
    if 'notes' in data:
        assignment.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tarea pausada exitosamente',
            'assignment': assignment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>/resume', methods=['PUT'])
def resume_assignment(assignment_id):
    """API para reanudar una asignación pausada"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    if assignment.status != 'pausada':
        return jsonify({'error': 'Solo se pueden reanudar tareas pausadas'}), 400
    
    # Verificar si el empleado ya tiene otra tarea en progreso
    active_assignment = TaskAssignment.query.filter(
        TaskAssignment.employee_id == assignment.employee_id,
        TaskAssignment.status == 'en_progreso',
        TaskAssignment.id != assignment_id
    ).first()
    
    if active_assignment:
        return jsonify({
            'error': 'El empleado ya tiene otra tarea en progreso',
            'active_assignment': active_assignment.to_dict()
        }), 400
    
    # Calcular tiempo que estuvo pausada
    if assignment.pause_time:
        pause_duration = datetime.utcnow() - assignment.pause_time
        pause_minutes = int(pause_duration.total_seconds() / 60)
        
        # Acumular al tiempo total pausado
        assignment.total_paused_duration = (assignment.total_paused_duration or 0) + pause_minutes
    
    assignment.status = 'en_progreso'
    assignment.pause_time = None  # Limpiar tiempo de pausa
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tarea reanudada exitosamente',
            'assignment': assignment.to_dict(),
            'total_paused_minutes': assignment.total_paused_duration
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:assignment_id>', methods=['PUT'])
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
def get_current_assignments():
    """API para obtener todas las asignaciones actuales (en progreso)"""
    assignments = TaskAssignment.query.filter_by(status='en_progreso').all()
    
    return jsonify({
        'assignments': [assignment.to_dict() for assignment in assignments],
        'count': len(assignments)
    })


@bp.route('/api/employee/<int:employee_id>/current')
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