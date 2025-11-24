from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Task, TaskAssignment, User

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/assign/<int:task_id>', methods=['POST'])
@login_required
def assign_task(task_id):
    """Asignar una tarea al usuario actual"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar si ya tiene una tarea activa
    current_task = current_user.get_current_task()
    if current_task:
        flash('Ya tienes una tarea activa. Complétala primero.', 'warning')
        return redirect(url_for('main.index'))
    
    # Crear nueva asignación
    assignment = TaskAssignment(
        user_id=current_user.id,
        task_id=task.id
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    flash(f'Tarea "{task.name}" asignada correctamente', 'success')
    return redirect(url_for('main.index'))


@bp.route('/complete/<int:assignment_id>', methods=['POST'])
@login_required
def complete_task(assignment_id):
    """Completar una tarea asignada"""
    assignment = TaskAssignment.query.get_or_404(assignment_id)
    
    # Verificar que la tarea pertenece al usuario actual
    if assignment.user_id != current_user.id and not current_user.is_admin:
        flash('No tienes permisos para completar esta tarea', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener notas si las hay
    notes = request.form.get('notes', '')
    
    # Completar la tarea
    assignment.complete()
    assignment.notes = notes
    
    db.session.commit()
    
    flash('Tarea completada correctamente', 'success')
    return redirect(url_for('main.index'))


@bp.route('/manage')
@login_required
def manage_tasks():
    """Vista para gestionar tareas (solo admins)"""
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    tasks = Task.query.all()
    return render_template('tasks/manage.html', tasks=tasks)


@bp.route('/create', methods=['POST'])
@login_required
def create_task():
    """Crear una nueva tarea (solo admins)"""
    if not current_user.is_admin:
        flash('No tienes permisos para crear tareas', 'error')
        return redirect(url_for('main.index'))
    
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    if not name:
        flash('El nombre de la tarea es obligatorio', 'error')
        return redirect(url_for('tasks.manage_tasks'))
    
    task = Task(
        name=name,
        description=description,
        created_by=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    flash(f'Tarea "{name}" creada correctamente', 'success')
    return redirect(url_for('tasks.manage_tasks'))


@bp.route('/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Activar/desactivar una tarea (solo admins)"""
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    
    task = Task.query.get_or_404(task_id)
    task.is_active = not task.is_active
    
    db.session.commit()
    
    status = 'activada' if task.is_active else 'desactivada'
    return jsonify({'success': True, 'message': f'Tarea {status}', 'is_active': task.is_active})


@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """Eliminar una tarea (solo admins)"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar tareas', 'error')
        return redirect(url_for('main.index'))
    
    task = Task.query.get_or_404(task_id)
    
    # Verificar si tiene asignaciones
    if task.assignments.count() > 0:
        flash('No se puede eliminar una tarea con historial de asignaciones', 'error')
        return redirect(url_for('tasks.manage_tasks'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Tarea eliminada correctamente', 'success')
    return redirect(url_for('tasks.manage_tasks'))