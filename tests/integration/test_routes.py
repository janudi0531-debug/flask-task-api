import pytest
import json
from app import create_app
from app.models import store
 
@pytest.fixture(autouse = True)
def clear_store():
    store._tasks.clear()
    yield
    store._tasks.clear()

@pytest.fixture(scope = 'session')
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
 
def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'
 
def test_get_tasks_empty(client):
    r = client.get('/tasks')
    assert r.status_code == 200
    assert r.get_json() == []
 
def test_create_task(client):
    r = client.post('/tasks', data = json.dumps({'title': 'Test task'}), content_type = 'application/json')
    assert r.status_code == 201
    data = r.get_json()
    assert data['title'] == 'Test task'
    assert 'id' in data
 
def test_create_task_no_title(client):
    r = client.post('/tasks', data = json.dumps({}), content_type = 'application/json')
    assert r.status_code == 400
 
def test_get_task_by_id(client):
    create = client.post('/tasks', data = json.dumps({'title': 'Find me'}), content_type = 'application/json')
    task_id = create.get_json()['id']
    r = client.get(f'/tasks/{task_id}')
    assert r.status_code == 200
    assert r.get_json()['title'] == 'Find me'
 
def test_get_task_not_found(client):
    r = client.get('/tasks/bad-id')
    assert r.status_code == 404
 
def test_update_task(client):
    create = client.post('/tasks', data = json.dumps({'title': 'Original'}), content_type = 'application/json')
    task_id = create.get_json()['id']
    r = client.put(f'/tasks/{task_id}', data = json.dumps({'title': 'Updated', 'completed': True}), content_type = 'application/json')
    assert r.status_code == 200
    assert r.get_json()['title'] == 'Updated'
    assert r.get_json()['completed'] is True
 
def test_delete_task(client):
    create = client.post('/tasks', data = json.dumps({'title': 'Goodbye'}), content_type = 'application/json')
    task_id = create.get_json()['id']
    r = client.delete(f'/tasks/{task_id}')
    assert r.status_code == 204
 
def test_delete_task_not_found(client):
    r = client.delete('/tasks/bad-id')
    assert r.status_code == 404
