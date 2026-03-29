import pytest
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_retrieve_tasks_can_filter_by_pet_and_status():
    owner = Owner(name="Jordan", daily_time_available=60)
    dog = Pet(name="Mochi", species="dog", age=4)
    cat = Pet(name="Luna", species="cat", age=2)

    dog_task = Task(description="Morning walk", duration_minutes=20, frequency="daily")
    cat_task = Task(description="Litter cleaning", duration_minutes=10, frequency="daily")
    cat_task.mark_completed()

    dog.add_task(dog_task)
    cat.add_task(cat_task)
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner=owner)

    dog_pending = scheduler.retrieve_tasks(pet_name="Mochi", is_completed=False)
    assert len(dog_pending) == 1
    assert dog_pending[0][0] == "Mochi"
    assert dog_pending[0][1].description == "Morning walk"

    cat_completed = scheduler.retrieve_tasks(include_completed=True, pet_name="Luna", is_completed=True)
    assert len(cat_completed) == 1
    assert cat_completed[0][1].description == "Litter cleaning"


def test_sort_by_time_orders_by_duration():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Long walk", duration_minutes=30, frequency="daily"))
    pet.add_task(Task(description="Quick feed", duration_minutes=5, frequency="daily"))
    pet.add_task(Task(description="Brush coat", duration_minutes=10, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [task.description for _, task in sorted_tasks] == ["Quick feed", "Brush coat", "Long walk"]


def test_generate_daily_plan_expands_twice_daily_tasks():
    owner = Owner(name="Jordan", daily_time_available=40)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Medication", duration_minutes=10, frequency="twice_daily", priority=3))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_daily_plan()

    assert len(plan) == 2
    assert all(task.description == "Medication" for _, task in plan)


def test_weekly_tasks_only_scheduled_on_monday():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Luna", species="cat", age=2)
    pet.add_task(Task(description="Nail trim", duration_minutes=15, frequency="weekly"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    tasks = scheduler.retrieve_tasks(include_completed=False)

    monday = date(2026, 3, 30)  # Monday
    tuesday = date(2026, 3, 31)  # Tuesday

    assert len(scheduler._expand_recurring_tasks(tasks, reference_date=monday)) == 1
    assert len(scheduler._expand_recurring_tasks(tasks, reference_date=tuesday)) == 0


def test_detect_conflicts_finds_time_overflow_and_duplicates():
    owner = Owner(name="Jordan", daily_time_available=20)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Walk", duration_minutes=15, frequency="daily"))
    pet.add_task(Task(description="Walk", duration_minutes=15, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert any("exceeds available time" in conflict for conflict in conflicts)
    assert any("Duplicate recurring task" in conflict for conflict in conflicts)


def test_detect_conflicts_finds_same_time_overlap_warning():
    owner = Owner(name="Jordan", daily_time_available=60)
    dog = Pet(name="Mochi", species="dog", age=4)
    cat = Pet(name="Luna", species="cat", age=2)

    dog.add_task(
        Task(description="Walk", duration_minutes=20, frequency="daily", scheduled_time="08:00")
    )
    cat.add_task(
        Task(description="Feed", duration_minutes=10, frequency="daily", scheduled_time="08:00")
    )
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert any("Time conflict at 08:00" in conflict for conflict in conflicts)


def test_mark_task_completed_creates_next_daily_occurrence():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(description="Morning walk", duration_minutes=20, frequency="daily", priority=2)
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    completed = scheduler.mark_task_completed(task.task_id)

    assert completed is True
    assert len(pet.tasks) == 2
    assert pet.tasks[0].is_completed is True
    assert pet.tasks[1].description == "Morning walk"
    assert pet.tasks[1].frequency == "daily"
    assert pet.tasks[1].priority == 2
    assert pet.tasks[1].is_completed is False
    assert pet.tasks[1].task_id != pet.tasks[0].task_id
    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)


def test_mark_task_completed_creates_next_weekly_occurrence():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Luna", species="cat", age=2)
    task = Task(description="Weekly grooming", duration_minutes=15, frequency="weekly", priority=1)
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    completed = scheduler.mark_task_completed(task.task_id)

    assert completed is True
    assert len(pet.tasks) == 2
    assert pet.tasks[1].description == "Weekly grooming"
    assert pet.tasks[1].frequency == "weekly"
    assert pet.tasks[1].is_completed is False
    assert pet.tasks[1].due_date == date.today() + timedelta(days=7)


def test_mark_task_completed_does_not_create_next_for_as_needed():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(description="One-off vet call", duration_minutes=10, frequency="as_needed")
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    completed = scheduler.mark_task_completed(task.task_id)

    assert completed is True
    assert len(pet.tasks) == 1
    assert pet.tasks[0].is_completed is True
