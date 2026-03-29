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


def test_sorting_correctness_returns_tasks_in_chronological_order():
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


def test_conflict_detection_flags_duplicate_times():
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


def test_recurrence_logic_daily_completion_creates_following_day_task():
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


def test_organize_tasks_orders_by_frequency_priority_and_duration():
    owner = Owner(name="Jordan", daily_time_available=120)
    pet = Pet(name="Mochi", species="dog", age=4)

    pet.add_task(Task(description="Weekly check", duration_minutes=5, frequency="weekly", priority=10))
    pet.add_task(Task(description="Daily low", duration_minutes=20, frequency="daily", priority=1))
    pet.add_task(Task(description="Daily high", duration_minutes=15, frequency="daily", priority=3))
    pet.add_task(Task(description="As needed", duration_minutes=5, frequency="as_needed", priority=10))
    pet.add_task(Task(description="Daily high shorter", duration_minutes=10, frequency="daily", priority=3))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    ordered = scheduler.organize_tasks()

    assert [task.description for _, task in ordered] == [
        "Daily high shorter",
        "Daily high",
        "Daily low",
        "Weekly check",
        "As needed",
    ]


def test_generate_daily_plan_exact_fit_and_one_minute_overflow():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Small", duration_minutes=10, frequency="daily", priority=1))
    pet.add_task(Task(description="Big", duration_minutes=20, frequency="daily", priority=1))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)

    exact_fit_plan = scheduler.generate_daily_plan(max_minutes=30)
    assert [task.description for _, task in exact_fit_plan] == ["Small", "Big"]

    overflow_plan = scheduler.generate_daily_plan(max_minutes=29)
    assert [task.description for _, task in overflow_plan] == ["Small"]
    assert len(scheduler._skipped_reasons) == 1
    assert scheduler._skipped_reasons[0][1].description == "Big"


def test_generate_daily_plan_all_tasks_too_large_tracks_skips():
    owner = Owner(name="Jordan", daily_time_available=30)
    pet = Pet(name="Luna", species="cat", age=2)
    pet.add_task(Task(description="Long task", duration_minutes=40, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_daily_plan()

    assert plan == []
    assert len(scheduler._skipped_reasons) == 1
    assert scheduler._skipped_reasons[0][2] == "not enough remaining time"


def test_expand_recurring_tasks_handles_twice_daily_and_unknown_frequency_once():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    twice_daily = Task(description="Medication", duration_minutes=10, frequency="twice_daily")
    unknown = Task(description="Special", duration_minutes=5, frequency="monthly")
    pet.add_task(twice_daily)
    pet.add_task(unknown)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    tasks = scheduler.retrieve_tasks(include_completed=False)
    expanded = scheduler._expand_recurring_tasks(tasks, reference_date=date(2026, 3, 31))

    assert [task.description for _, task in expanded].count("Medication") == 2
    assert [task.description for _, task in expanded].count("Special") == 1


def test_mark_task_completed_daily_copies_priority_and_scheduled_time_to_next_task():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(
        description="Evening meds",
        duration_minutes=10,
        frequency="daily",
        priority=4,
        scheduled_time="19:30",
    )
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    assert scheduler.mark_task_completed(task.task_id) is True

    next_task = pet.tasks[1]
    assert next_task.priority == 4
    assert next_task.scheduled_time == "19:30"
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_mark_task_completed_on_already_completed_task_does_not_duplicate_next_task():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    task = Task(description="Morning walk", duration_minutes=20, frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    assert scheduler.mark_task_completed(task.task_id) is True
    assert len(pet.tasks) == 2

    # Calling complete again should be idempotent and not create another follow-up.
    assert scheduler.mark_task_completed(task.task_id) is True
    assert len(pet.tasks) == 2


def test_explain_plan_includes_selected_tasks_and_total_time():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Feed", duration_minutes=10, frequency="daily"))
    pet.add_task(Task(description="Walk", duration_minutes=20, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan(max_minutes=30)
    explanation = scheduler.explain_plan()

    assert "Scheduled 2 task(s)" in explanation
    assert "Feed (Mochi)" in explanation
    assert "Walk (Mochi)" in explanation
    assert "Total planned time is 30/60 minutes." in explanation


def test_organize_tasks_keeps_stable_order_when_sort_keys_are_identical():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)

    first = Task(description="Same", duration_minutes=10, frequency="daily", priority=2)
    second = Task(description="Same", duration_minutes=10, frequency="daily", priority=2)
    third = Task(description="Same", duration_minutes=10, frequency="daily", priority=2)
    pet.add_task(first)
    pet.add_task(second)
    pet.add_task(third)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    ordered = scheduler.organize_tasks()

    assert [task.task_id for _, task in ordered] == [first.task_id, second.task_id, third.task_id]


def test_detect_conflicts_duplicate_detection_is_case_insensitive():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Walk", duration_minutes=15, frequency="daily"))
    pet.add_task(Task(description="walk", duration_minutes=20, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert any("Duplicate recurring task" in conflict for conflict in conflicts)


def test_detect_conflicts_finds_same_time_overlap_for_same_pet():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Walk", duration_minutes=20, frequency="daily", scheduled_time="08:00"))
    pet.add_task(Task(description="Feed", duration_minutes=10, frequency="daily", scheduled_time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert any("multiple tasks for Mochi overlap" in conflict for conflict in conflicts)


def test_detect_conflicts_ignores_tasks_without_scheduled_time_for_overlap():
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Walk", duration_minutes=20, frequency="daily"))
    pet.add_task(Task(description="Feed", duration_minutes=10, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert not any("Time conflict at" in conflict for conflict in conflicts)


@pytest.mark.parametrize(
    "invalid_time",
    ["25:00", "08:60", " 08:00", "08:00 "],
)
def test_task_rejects_invalid_scheduled_time_formats(invalid_time):
    with pytest.raises(ValueError, match="scheduled_time must use HH:MM format"):
        Task(description="Feed", duration_minutes=10, frequency="daily", scheduled_time=invalid_time)


def test_task_rejects_non_positive_duration_and_negative_priority():
    with pytest.raises(ValueError, match="duration_minutes must be greater than 0"):
        Task(description="Bad duration", duration_minutes=0, frequency="daily")

    with pytest.raises(ValueError, match="priority must be 0 or greater"):
        Task(description="Bad priority", duration_minutes=10, frequency="daily", priority=-1)
