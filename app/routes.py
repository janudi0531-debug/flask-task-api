from flask import Blueprint, jsonify, request
from .models import store
 
tasks_bp = Blueprint('tasks', __name__)
 
@tasks_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'tasks': store.count()})
 
@tasks_bp.route('/tasks', methods = ['GET'])
def get_tasks():
    return jsonify([t.to_dict() for t in store.get_all()])
 
@tasks_bp.route('/tasks', methods = ['POST'])
def create_task():
    data = request.get_json(silent = True) or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400
    try:
        task = store.add(title, data.get('description', ''))
        return jsonify(task.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
 
@tasks_bp.route('/tasks/<task_id>', methods = ['GET'])
def get_task(task_id):
    task = store.get(task_id)
    if not task:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(task.to_dict())
 
@tasks_bp.route('/tasks/<task_id>', methods = ['PUT'])
def update_task(task_id):
    data = request.get_json(silent = True) or {}
    try:
        task = store.update(task_id, **data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    if not task:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(task.to_dict())
 
@tasks_bp.route('/tasks/<task_id>', methods = ['DELETE'])
def delete_task(task_id):
    if store.delete(task_id):
        return '', 204
    return jsonify({'error': 'Not found'}), 404
