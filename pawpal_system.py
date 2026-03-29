from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


FREQUENCY_ORDER = {
	"daily": 0,
	"twice_daily": 0,
	"weekly": 1,
	"as_needed": 2,
}


@dataclass
class Task:
	description: str
	duration_minutes: int
	frequency: str = "daily"
	is_completed: bool = False
	priority: int = 1
	task_id: str = field(default_factory=lambda: uuid4().hex[:8])

	def __post_init__(self) -> None:
		"""Validate task values and normalize the frequency string."""
		if self.duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than 0")
		if self.priority < 0:
			raise ValueError("priority must be 0 or greater")
		self.frequency = self.frequency.lower()

	def update(
		self,
		description: str | None = None,
		duration_minutes: int | None = None,
		frequency: str | None = None,
		is_completed: bool | None = None,
		priority: int | None = None,
	) -> None:
		"""Update task fields while enforcing basic validation rules."""
		if description is not None:
			self.description = description
		if duration_minutes is not None:
			if duration_minutes <= 0:
				raise ValueError("duration_minutes must be greater than 0")
			self.duration_minutes = duration_minutes
		if frequency is not None:
			self.frequency = frequency.lower()
		if is_completed is not None:
			self.is_completed = is_completed
		if priority is not None:
			if priority < 0:
				raise ValueError("priority must be 0 or greater")
			self.priority = priority

	def mark_completed(self) -> None:
		"""Mark this task as completed."""
		self.is_completed = True

	def mark_incomplete(self) -> None:
		"""Mark this task as not completed."""
		self.is_completed = False


@dataclass
class Pet:
	name: str
	species: str
	age: int
	tasks: list[Task] = field(default_factory=list)

	def update_info(self, name: str, species: str, age: int) -> None:
		"""Update this pet's basic profile information."""
		self.name = name
		self.species = species
		self.age = age

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet's task list."""
		self.tasks.append(task)

	def get_task(self, task_id: str) -> Task | None:
		"""Return a task by id for this pet, if it exists."""
		return next((task for task in self.tasks if task.task_id == task_id), None)

	def remove_task(self, task_id: str) -> bool:
		"""Remove a task by id and return whether removal succeeded."""
		for index, task in enumerate(self.tasks):
			if task.task_id == task_id:
				del self.tasks[index]
				return True
		return False

	def get_pending_tasks(self) -> list[Task]:
		"""Return only tasks that are not yet completed."""
		return [task for task in self.tasks if not task.is_completed]


@dataclass
class Owner:
	name: str
	pets: list[Pet] = field(default_factory=list)
	daily_time_available: int = 60

	def update_time_available(self, minutes: int) -> None:
		"""Set the owner's daily time budget for scheduling."""
		if minutes <= 0:
			raise ValueError("daily_time_available must be greater than 0")
		self.daily_time_available = minutes

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner's pet list."""
		self.pets.append(pet)

	def get_pet(self, pet_name: str) -> Pet | None:
		"""Return a pet by name using a case-insensitive match."""
		return next(
			(pet for pet in self.pets if pet.name.lower() == pet_name.lower()),
			None,
		)

	def remove_pet(self, pet_name: str) -> bool:
		"""Remove a pet by name and return whether removal succeeded."""
		for index, pet in enumerate(self.pets):
			if pet.name.lower() == pet_name.lower():
				del self.pets[index]
				return True
		return False

	def get_all_tasks(self, include_completed: bool = True) -> list[Task]:
		"""Return all tasks across pets, with optional completion filtering."""
		all_tasks: list[Task] = []
		for pet in self.pets:
			if include_completed:
				all_tasks.extend(pet.tasks)
			else:
				all_tasks.extend(pet.get_pending_tasks())
		return all_tasks


@dataclass
class Scheduler:
	owner: Owner
	daily_plan: list[tuple[str, Task]] = field(default_factory=list)
	_skipped_reasons: list[tuple[str, Task, str]] = field(default_factory=list, repr=False)

	def retrieve_tasks(self, include_completed: bool = False) -> list[tuple[str, Task]]:
		"""Collect tasks across all pets with optional completed inclusion."""
		tasks: list[tuple[str, Task]] = []
		for pet in self.owner.pets:
			for task in pet.tasks:
				if include_completed or not task.is_completed:
					tasks.append((pet.name, task))
		return tasks

	def organize_tasks(
		self,
		tasks: list[tuple[str, Task]] | None = None,
	) -> list[tuple[str, Task]]:
		"""Sort tasks by completion, frequency, priority, duration, and description."""
		items = tasks if tasks is not None else self.retrieve_tasks(include_completed=False)
		return sorted(
			items,
			key=lambda item: (
				item[1].is_completed,
				FREQUENCY_ORDER.get(item[1].frequency, 3),
				-item[1].priority,
				item[1].duration_minutes,
				item[1].description.lower(),
			),
		)

	def add_task_to_pet(self, pet_name: str, task: Task) -> None:
		"""Add a task to a specific pet by name."""
		pet = self.owner.get_pet(pet_name)
		if pet is None:
			raise KeyError(f"Pet '{pet_name}' was not found")
		pet.add_task(task)

	def edit_task(self, task_id: str, updates: dict[str, int | str | bool]) -> None:
		"""Update a task by id using a validated updates payload."""
		if not updates:
			raise ValueError("updates cannot be empty")

		allowed_keys = {
			"description",
			"duration_minutes",
			"frequency",
			"is_completed",
			"priority",
		}
		invalid_keys = set(updates) - allowed_keys
		if invalid_keys:
			raise ValueError(f"Unsupported update keys: {sorted(invalid_keys)}")

		task = self.get_task_by_id(task_id)
		if task is None:
			raise KeyError(f"Task with id '{task_id}' was not found")

		task.update(
			description=updates.get("description"),
			duration_minutes=updates.get("duration_minutes"),
			frequency=updates.get("frequency"),
			is_completed=updates.get("is_completed"),
			priority=updates.get("priority"),
		)

	def get_task_by_id(self, task_id: str) -> Task | None:
		"""Find and return a task by id across all pets."""
		for _, task in self.retrieve_tasks(include_completed=True):
			if task.task_id == task_id:
				return task
		return None

	def mark_task_completed(self, task_id: str) -> bool:
		"""Mark a task completed by id and return whether it was found."""
		task = self.get_task_by_id(task_id)
		if task is None:
			return False
		task.mark_completed()
		return True

	def generate_daily_plan(self, max_minutes: int | None = None) -> list[tuple[str, Task]]:
		"""Build a daily plan across all pets within the available time budget."""
		available_minutes = max_minutes if max_minutes is not None else self.owner.daily_time_available
		if available_minutes <= 0:
			raise ValueError("available minutes must be greater than 0")

		remaining_minutes = available_minutes
		sorted_tasks = self.organize_tasks()

		self.daily_plan = []
		self._skipped_reasons = []

		for pet_name, task in sorted_tasks:
			if task.duration_minutes <= remaining_minutes:
				self.daily_plan.append((pet_name, task))
				remaining_minutes -= task.duration_minutes
			else:
				self._skipped_reasons.append((pet_name, task, "not enough remaining time"))

		return self.daily_plan

	def explain_plan(self) -> str:
		"""Return a plain-language explanation of the generated daily plan."""
		all_tasks = self.retrieve_tasks(include_completed=True)
		if not all_tasks:
			return "No tasks were provided, so no plan was generated."

		if not self.daily_plan:
			return "No tasks fit within the available time, so the plan is empty."

		total_scheduled = sum(task.duration_minutes for _, task in self.daily_plan)
		available = self.owner.daily_time_available

		selected_titles = ", ".join(
			f"{task.description} ({pet_name})" for pet_name, task in self.daily_plan
		)
		explanation_parts = [
			f"Scheduled {len(self.daily_plan)} task(s): {selected_titles}.",
			f"Total planned time is {total_scheduled}/{available} minutes.",
			"Tasks were prioritized by frequency, then priority, then shorter duration.",
		]

		if self._skipped_reasons:
			skipped_text = "; ".join(
				f"{task.description} ({pet_name}: {reason})"
				for pet_name, task, reason in self._skipped_reasons
			)
			explanation_parts.append(f"Skipped: {skipped_text}.")

		return " ".join(explanation_parts)
