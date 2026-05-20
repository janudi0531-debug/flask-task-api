import uuid
from dataclasses import dataclass, field
from typing import Optional
 
@dataclass
class Task:
    title: str
    description: str = ''
    completed: bool = False
    id: str = field(default_factory = lambda: str(uuid.uuid4()))
 
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
        }
 
class TaskStore:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
 
    def add(self, title: str, description: str = '') -> Task:
        if not title or not title.strip():
            raise ValueError('Title cannot be empty')
        task = Task(title = title.strip(), description = description)
        self._tasks[task.id] = task
        return task
 
    def get_all(self) -> list[Task]:
        return list(self._tasks.values())
 
    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
 
    def update(self, task_id: str, **kwargs) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        if 'title' in kwargs:
            if not kwargs['title'] or not kwargs['title'].strip():
                raise ValueError('Title cannot be empty')
            task.title = kwargs['title'].strip()
        if 'description' in kwargs:
            task.description = kwargs['description']
        if 'completed' in kwargs:
            task.completed = bool(kwargs['completed'])
        return task
 
    def delete(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
 
    def count(self) -> int:
        return len(self._tasks)
 
 
# Module-level store (shared across requests)
store = TaskStore()
