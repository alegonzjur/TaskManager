from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Attendance, Employee
from app.decorators import admin_required
from datetime import datetime, date, timedelta

bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@bp.route('/')
@login_required
def index():
    """Vista principal de fichaje"""
    return render_template('attendance/index.html')


@bp.route('/api/check-in', methods=['POST'])
@login_required
def check_in():
    """Registrar entrada (fichaje)"""
    data = request.get_json()
    
    # Determinar qué empleado va a fichar
    employee_id = data.get('employee_id')
    
    # Si no es admin, solo puede fichar para sí mismo
    if not current_user.is_admin():
        employee_id = current_user.id
    else:
        # Admin puede fichar por cualquiera
        if not employee_id:
            employee_id = current_user.id
    
    # Verificar que el empleado existe
    employee = Employee.query.get_or_404(employee_id)
    
    # Verificar si ya tiene un fichaje activo hoy
    active_attendance = Attendance.query.filter_by(
        employee_id=employee_id,
        check_out=None
    ).first()
    
    if active_attendance:
        return jsonify({
            'error': f'{employee.name} ya tiene un fichaje activo desde las {active_attendance.check_in.strftime("%H:%M")}'
        }), 400
    
    # Validar ubicación
    location = data.get('location', 'office')
    if location not in ['office', 'home']:
        return jsonify({'error': 'Ubicación inválida'}), 400
    
    # Crear nuevo fichaje
    attendance = Attendance(
        employee_id=employee_id,
        check_in=datetime.utcnow(),
        location=location,
        notes=data.get('notes', '')
    )
    
    try:
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': f'Entrada registrada para {employee.name}',
            'attendance': attendance.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/check-out', methods=['POST'])
@login_required
def check_out():
    """Registrar salida"""
    data = request.get_json()
    
    # Determinar qué empleado va a fichar salida
    employee_id = data.get('employee_id')
    
    if not current_user.is_admin():
        employee_id = current_user.id
    else:
        if not employee_id:
            employee_id = current_user.id
    
    # Buscar fichaje activo
    attendance = Attendance.query.filter_by(
        employee_id=employee_id,
        check_out=None
    ).first()
    
    if not attendance:
        return jsonify({'error': 'No hay fichaje activo para registrar salida'}), 400
    
    # Registrar salida
    attendance.check_out = datetime.utcnow()
    attendance.notes = data.get('notes', attendance.notes)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Salida registrada correctamente',
            'attendance': attendance.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/current')
@login_required
def get_current_attendance():
    """Obtener fichaje activo del usuario actual"""
    employee_id = request.args.get('employee_id', type=int)
    
    # Si no es admin, solo puede ver el suyo
    if not current_user.is_admin():
        employee_id = current_user.id
    else:
        if not employee_id:
            employee_id = current_user.id
    
    attendance = Attendance.query.filter_by(
        employee_id=employee_id,
        check_out=None
    ).first()
    
    return jsonify({
        'attendance': attendance.to_dict() if attendance else None
    })


@bp.route('/api/today')
@login_required
def get_today_attendances():
    """Obtener todos los fichajes de hoy"""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # Si no es admin, solo ver los suyos
    if current_user.is_admin():
        attendances = Attendance.query.filter(
            Attendance.check_in >= start_of_day,
            Attendance.check_in <= end_of_day
        ).order_by(Attendance.check_in.desc()).all()
    else:
        attendances = Attendance.query.filter(
            Attendance.employee_id == current_user.id,
            Attendance.check_in >= start_of_day,
            Attendance.check_in <= end_of_day
        ).order_by(Attendance.check_in.desc()).all()
    
    return jsonify({
        'attendances': [a.to_dict() for a in attendances]
    })


@bp.route('/api/history')
@login_required
def get_attendance_history():
    """Obtener historial de fichajes"""
    employee_id = request.args.get('employee_id', type=int)
    days = request.args.get('days', 7, type=int)  # Últimos 7 días por defecto
    
    # Si no es admin, solo puede ver el suyo
    if not current_user.is_admin():
        employee_id = current_user.id
    
    # Calcular fecha de inicio
    start_date = datetime.now() - timedelta(days=days)
    
    # Query base
    query = Attendance.query.filter(Attendance.check_in >= start_date)
    
    # Filtrar por empleado si se especifica
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    
    attendances = query.order_by(Attendance.check_in.desc()).all()
    
    return jsonify({
        'attendances': [a.to_dict() for a in attendances]
    })


@bp.route('/api/stats/today')
@login_required
def get_today_stats():
    """Obtener estadísticas de fichajes de hoy"""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Total de empleados activos
    total_employees = Employee.query.filter_by(is_active=True).count()
    
    # Empleados que han fichado hoy
    checked_in_today = db.session.query(Attendance.employee_id).filter(
        Attendance.check_in >= start_of_day
    ).distinct().count()
    
    # Empleados actualmente en el trabajo
    currently_working = Attendance.query.filter(
        Attendance.check_in >= start_of_day,
        Attendance.check_out.is_(None)
    ).count()
    
    # Empleados en oficina vs casa
    in_office = Attendance.query.filter(
        Attendance.check_in >= start_of_day,
        Attendance.check_out.is_(None),
        Attendance.location == 'office'
    ).count()
    
    in_home = Attendance.query.filter(
        Attendance.check_in >= start_of_day,
        Attendance.check_out.is_(None),
        Attendance.location == 'home'
    ).count()
    
    return jsonify({
        'total_employees': total_employees,
        'checked_in_today': checked_in_today,
        'currently_working': currently_working,
        'in_office': in_office,
        'in_home': in_home,
        'not_checked_in': total_employees - checked_in_today
    })