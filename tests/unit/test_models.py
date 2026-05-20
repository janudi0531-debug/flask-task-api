import pytest
from app.models import Task, TaskStore
 
def test_task_creation():
    t = Task(title = 'Buy groceries')
    assert t.title == 'Buy groceries'
    assert t.completed is False
    assert t.id is not None
 
def test_task_to_dict():
    t = Task(title = 'Test', description = 'Desc')
    d = t.to_dict()
    assert d['title'] == 'Test'
    assert d['description'] == 'Desc'
    assert 'id' in d
 
def test_store_add_task():
    s = TaskStore()
    task = s.add('Walk dog')
    assert task.title == 'Walk dog'
    assert s.count() == 1
 
def test_store_add_empty_title_raises():
    s = TaskStore()
    with pytest.raises(ValueError):
        s.add('')
 
def test_store_add_whitespace_title_raises():
    s = TaskStore()
    with pytest.raises(ValueError):
        s.add('   ')
 
def test_store_get_all():
    s = TaskStore()
    s.add('Task 1')
    s.add('Task 2')
    assert len(s.get_all()) == 2
 
def test_store_get_by_id():
    s = TaskStore()
    task = s.add('Fetch this')
    found = s.get(task.id)
    assert found is not None
    assert found.title == 'Fetch this'
 
def test_store_get_missing_id():
    s = TaskStore()
    assert s.get('nonexistent-id') is None
 
def test_store_update():
    s = TaskStore()
    task = s.add('Old title')
    updated = s.update(task.id, title = 'New title', completed = True)
    assert updated.title == 'New title'
    assert updated.completed is True
 
def test_store_update_missing():
    s = TaskStore()
    result = s.update('bad-id', title = 'X')
    assert result is None
 
def test_store_delete():
    s = TaskStore()
    task = s.add('Delete me')
    assert s.delete(task.id) is True
    assert s.count() == 0
 
def test_store_delete_missing():
    s = TaskStore()
    assert s.delete('bad-id') is False
