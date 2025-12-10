from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Employee, TaskAssignment
from app.decorators import admin_required
from datetime import datetime

bp = Blueprint('employees', __name__, url_prefix='/employees')


@bp.route('/')
@login_required
def index():
    """Lista de empleados"""
    return render_template('employees/index.html')


@bp.route('/api')
@login_required
def get_employees():
    """API para obtener todos los empleados"""
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    query = Employee.query
    if active_only:
        query = query.filter_by(is_active=True)
    
    employees = query.order_by(Employee.name).all()
    
    # Asegurar que todos los empleados tengan un rol
    for emp in employees:
        if not emp.role:
            emp.role = 'employee'
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return jsonify({
        'employees': [emp.to_dict() for emp in employees]
    })


@bp.route('/api/<int:employee_id>')
@login_required
def get_employee(employee_id):
    """API para obtener un empleado específico"""
    employee = Employee.query.get_or_404(employee_id)
    
    # Asegurar que tenga rol
    if not employee.role:
        employee.role = 'employee'
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    return jsonify(employee.to_dict())


@bp.route('/api', methods=['POST'])
@login_required
@admin_required
def create_employee():
    """API para crear un nuevo empleado con usuario (solo admin)"""
    data = request.get_json()
    
    # Validaciones básicas
    if not data.get('name'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    if not data.get('email'):
        return jsonify({'error': 'El email es obligatorio'}), 400
    
    # Validar email de verificación
    if data.get('email') != data.get('email_confirm'):
        return jsonify({'error': 'Los emails no coinciden'}), 400
    
    # Validar contraseña SOLO si se proporcionó
    password = data.get('password', '').strip()
    password_confirm = data.get('password_confirm', '').strip()
    
    if password or password_confirm:  # Si alguna se proporcionó, validar ambas
        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != password_confirm:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
    
    # Verificar si el email ya existe
    existing = Employee.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({'error': 'Ya existe un empleado con ese email'}), 400
    
    # Validar fecha de nacimiento
    birth_date = None
    if data.get('birth_date'):
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    # Crear empleado
    employee = Employee(
        name=data['name'],
        email=data['email'],
        position=data.get('position', ''),
        birth_date=birth_date,
        role=data.get('role', 'employee'),
        is_active=data.get('is_active', True)
    )
    
    # Establecer contraseña SOLO si se proporcionó
    if password:
        employee.set_password(password)
    
    try:
        db.session.add(employee)
        db.session.commit()
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'employee': employee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    if existing:
        return jsonify({'error': 'Ya existe un empleado con ese email'}), 400
    
    # Crear empleado
    employee = Employee(
        name=data['name'],
        email=data['email'],
        position=data.get('position', ''),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(employee)
        db.session.commit()
        return jsonify({
            'message': 'Empleado creado exitosamente',
            'employee': employee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """API para actualizar un empleado"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    
    # Validaciones
    if 'email' in data and data['email'] != employee.email:
        existing = Employee.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Ya existe un empleado con ese email'}), 400
    
    # Actualizar campos
    if 'name' in data:
        employee.name = data['name']
    if 'email' in data:
        employee.email = data['email']
    if 'position' in data:
        employee.position = data['position']
    if 'is_active' in data:
        employee.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Empleado actualizado exitosamente',
            'employee': employee.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """API para eliminar (desactivar) un empleado"""
    employee = Employee.query.get_or_404(employee_id)
    
    # En lugar de eliminar, desactivamos
    employee.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Empleado desactivado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:employee_id>/history')
def employee_history(employee_id):
    """API para obtener el historial de tareas de un empleado"""
    employee = Employee.query.get_or_404(employee_id)
    
    # Obtener todas las asignaciones del empleado
    assignments = employee.task_assignments.order_by(
        TaskAssignment.start_time.desc()
    ).all()
    
    return jsonify({
        'employee': employee.to_dict(),
        'assignments': [assignment.to_dict() for assignment in assignments]
    })