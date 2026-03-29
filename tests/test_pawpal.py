import pytest
from pawpal_system import Task, Pet


def test_task_complete():
    """Verify that calling mark_completed() changes the task's status."""
    task = Task(description="Feed the dog", duration_minutes=10, frequency="daily")

    assert task.is_completed is False

    task.mark_completed()

    assert task.is_completed is True


def test_task_addition_increases_pet_task_count():
    """Verify that adding a task to a Pet increases the pet's task count."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    initial_count = len(pet.tasks)

    task = Task(description="Walk the dog", duration_minutes=20, frequency="daily")
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
