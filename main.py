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
		Task(description="Morning walk", duration_minutes=25, frequency="daily", priority=3),
	)
	scheduler.add_task_to_pet(
		"Mochi",
		Task(description="Breakfast feeding", duration_minutes=10, frequency="daily", priority=2),
	)
	scheduler.add_task_to_pet(
		"Luna",
		Task(description="Litter cleaning", duration_minutes=15, frequency="daily", priority=2),
	)

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
