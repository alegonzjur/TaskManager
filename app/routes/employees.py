from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Employee, TaskAssignment

bp = Blueprint('employees', __name__, url_prefix='/employees')


@bp.route('/')
def index():
    """Lista de empleados"""
    return render_template('employees/index.html')


@bp.route('/api')
def get_employees():
    """API para obtener todos los empleados"""
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    query = Employee.query
    if active_only:
        query = query.filter_by(is_active=True)
    
    employees = query.order_by(Employee.name).all()
    
    return jsonify({
        'employees': [emp.to_dict() for emp in employees]
    })


@bp.route('/api/<int:employee_id>')
def get_employee(employee_id):
    """API para obtener un empleado específico"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())


@bp.route('/api', methods=['POST'])
def create_employee():
    """API para crear un nuevo empleado"""
    data = request.get_json()
    
    # Validaciones
    if not data.get('name'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    if not data.get('email'):
        return jsonify({'error': 'El email es obligatorio'}), 400
    
    # Verificar si el email ya existe
    existing = Employee.query.filter_by(email=data['email']).first()
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