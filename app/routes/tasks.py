from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Task, TaskAssignment

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/')
def index():
    """Lista de tareas"""
    return render_template('tasks/index.html')


@bp.route('/api')
def get_tasks():
    """API para obtener todas las tareas"""
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    category = request.args.get('category')
    
    query = Task.query
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    tasks = query.order_by(Task.name).all()
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    })


@bp.route('/api/categories')
def get_categories():
    """API para obtener todas las categorías de tareas"""
    categories = db.session.query(Task.category).distinct().filter(
        Task.category.isnot(None),
        Task.is_active == True
    ).all()
    
    return jsonify({
        'categories': [cat[0] for cat in categories if cat[0]]
    })


@bp.route('/api/<int:task_id>')
def get_task(task_id):
    """API para obtener una tarea específica"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@bp.route('/api', methods=['POST'])
def create_task():
    """API para crear una nueva tarea"""
    data = request.get_json()
    
    # Validaciones
    if not data.get('name'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    # Verificar si la tarea ya existe
    existing = Task.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'Ya existe una tarea con ese nombre'}), 400
    
    # Crear tarea
    task = Task(
        name=data['name'],
        description=data.get('description', ''),
        estimated_duration=data.get('estimated_duration'),
        category=data.get('category', ''),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(task)
        db.session.commit()
        return jsonify({
            'message': 'Tarea creada exitosamente',
            'task': task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """API para actualizar una tarea"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    # Validaciones
    if 'name' in data and data['name'] != task.name:
        existing = Task.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Ya existe una tarea con ese nombre'}), 400
    
    # Actualizar campos
    if 'name' in data:
        task.name = data['name']
    if 'description' in data:
        task.description = data['description']
    if 'estimated_duration' in data:
        task.estimated_duration = data['estimated_duration']
    if 'category' in data:
        task.category = data['category']
    if 'is_active' in data:
        task.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tarea actualizada exitosamente',
            'task': task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API para eliminar (desactivar) una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # En lugar de eliminar, desactivamos
    task.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Tarea desactivada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:task_id>/history')
def task_history(task_id):
    """API para obtener el historial de asignaciones de una tarea"""
    task = Task.query.get_or_404(task_id)
    
    # Obtener todas las asignaciones de la tarea
    assignments = task.assignments.order_by(
        TaskAssignment.start_time.desc()
    ).all()
    
    return jsonify({
        'task': task.to_dict(),
        'assignments': [assignment.to_dict() for assignment in assignments]
    })