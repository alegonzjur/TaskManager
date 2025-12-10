from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Employee
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('auth/login.html')
        
        # Buscar empleado por email
        employee = Employee.query.filter_by(email=email).first()
        
        # Verificar credenciales
        if employee and employee.check_password(password):
            if not employee.is_active:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
                return render_template('auth/login.html')
            
            # Login exitoso
            login_user(employee, remember=remember)
            
            # Actualizar último login
            employee.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            
            flash(f'¡Bienvenido, {employee.name}!', 'success')
            return redirect(next_page)
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/api/current-user')
@login_required
def current_user_info():
    """API para obtener información del usuario actual"""
    return jsonify({
        'user': current_user.to_dict(include_sensitive=True)
    })