from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
	owner = Owner(name="Jordan", daily_time_available=60)

	dog = Pet(name="Mochi", species="dog", age=4)
	cat = Pet(name="Luna", species="cat", age=2)

	owner.add_pet(dog)
	owner.add_pet(cat)

	scheduler = Scheduler(owner=owner)

	scheduler.add_task_to_pet(
		"Mochi",
		Task(
			description="Morning walk",
			duration_minutes=25,
			frequency="daily",
			scheduled_time="08:00",
			priority=3,
		),
	)
	scheduler.add_task_to_pet(
		"Mochi",
		Task(description="Quick refill water", duration_minutes=5, frequency="daily", priority=1),
	)
	scheduler.add_task_to_pet(
		"Luna",
		Task(
			description="Litter cleaning",
			duration_minutes=15,
			frequency="daily",
			scheduled_time="08:00",
			priority=2,
		),
	)
	scheduler.add_task_to_pet(
		"Luna",
		Task(description="Weekly brushing", duration_minutes=30, frequency="weekly", priority=2),
	)
	scheduler.add_task_to_pet(
		"Mochi",
		Task(
			description="Old medication reminder",
			duration_minutes=8,
			frequency="daily",
			priority=1,
			is_completed=True,
		),
	)

	print("All Tasks Sorted by Time (Shortest First)")
	for pet_name, task in scheduler.sort_by_time(tasks=scheduler.filter_tasks()):
		status = "completed" if task.is_completed else "pending"
		print(
			f"- {task.description} for {pet_name} "
			f"({task.duration_minutes} min, {task.frequency}, {status})"
		)

	print()
	print("Filtered Tasks (Mochi Only)")
	for pet_name, task in scheduler.filter_tasks(pet_name="Mochi"):
		status = "completed" if task.is_completed else "pending"
		print(
			f"- {task.description} for {pet_name} "
			f"({task.duration_minutes} min, {task.frequency}, {status})"
		)

	print()
	print("Filtered Tasks (Completed Only)")
	for pet_name, task in scheduler.filter_tasks(is_completed=True):
		print(
			f"- {task.description} for {pet_name} "
			f"({task.duration_minutes} min, {task.frequency}, completed)"
		)

	print()
	print("Conflict Warnings")
	conflicts = scheduler.detect_conflicts()
	if conflicts:
		for warning in conflicts:
			print(f"- WARNING: {warning}")
	else:
		print("- No conflicts detected.")

	print()

	plan = scheduler.generate_daily_plan()

	print("Today's Schedule")
	for pet_name, task in plan:
		print(
			f"- {task.description} for {pet_name} "
			f"({task.duration_minutes} min, {task.frequency}, priority {task.priority})"
		)

	print()
	print(scheduler.explain_plan())


if __name__ == "__main__":
	main()
