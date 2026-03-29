from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
	due_date: date = field(default_factory=date.today)
	scheduled_time: str | None = None
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
		if self.scheduled_time is not None:
			self._validate_time(self.scheduled_time)

	@staticmethod
	def _validate_time(time_value: str) -> None:
		"""Validate time using 24-hour HH:MM format."""
		try:
			datetime.strptime(time_value, "%H:%M")
		except ValueError as exc:
			raise ValueError("scheduled_time must use HH:MM format") from exc

	def update(
		self,
		description: str | None = None,
		duration_minutes: int | None = None,
		frequency: str | None = None,
		due_date: date | None = None,
		scheduled_time: str | None = None,
		is_completed: bool | None = None,
		priority: int | None = None,
	) -> None:
		"""Update task fields while enforcing basic validation rules."""
		if description is not None:
			self.description = description

		if duration_minutes is not None:
			self._validate_duration(duration_minutes)
			self.duration_minutes = duration_minutes

		if frequency is not None:
			self.frequency = frequency.lower()

		if due_date is not None:
			self.due_date = due_date

		if scheduled_time is not None:
			self._validate_time(scheduled_time)
			self.scheduled_time = scheduled_time

		if is_completed is not None:
			self.is_completed = is_completed

		if priority is not None:
			self._validate_priority(priority)
			self.priority = priority

	@staticmethod
	def _validate_duration(duration_minutes: int) -> None:
		"""Validate task duration."""
		if duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than 0")

	@staticmethod
	def _validate_priority(priority: int) -> None:
		"""Validate task priority."""
		if priority < 0:
			raise ValueError("priority must be 0 or greater")

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
	_conflicts: list[str] = field(default_factory=list, repr=False)

	def retrieve_tasks(
		self,
		include_completed: bool = False,
		pet_name: str | None = None,
		is_completed: bool | None = None,
	) -> list[tuple[str, Task]]:
		"""Collect tasks with optional filtering by pet and completion state."""
		tasks: list[tuple[str, Task]] = []
		pet_filter = pet_name.lower() if pet_name is not None else None
		for pet in self.owner.pets:
			if pet_filter is not None and pet.name.lower() != pet_filter:
				continue
			for task in pet.tasks:
				if not include_completed and task.is_completed:
					continue
				if is_completed is not None and task.is_completed != is_completed:
					continue
				tasks.append((pet.name, task))
		return tasks

	def sort_by_time(
		self,
		tasks: list[tuple[str, Task]] | None = None,
		ascending: bool = True,
	) -> list[tuple[str, Task]]:
		"""Sort tasks by duration, then description, for deterministic time-based ordering."""
		items = tasks if tasks is not None else self.retrieve_tasks(include_completed=False)
		ordered = sorted(items, key=lambda item: (item[1].duration_minutes, item[1].description.lower()))
		if ascending:
			return ordered
		return list(reversed(ordered))

	def filter_tasks(
		self,
		pet_name: str | None = None,
		is_completed: bool | None = None,
	) -> list[tuple[str, Task]]:
		"""Filter tasks by pet name, completion state, or both."""
		return self.retrieve_tasks(
			include_completed=True,
			pet_name=pet_name,
			is_completed=is_completed,
		)

	def _expand_recurring_tasks(
		self,
		tasks: list[tuple[str, Task]],
		reference_date: date | None = None,
	) -> list[tuple[str, Task]]:
		"""Expand recurring tasks into today's list (twice-daily duplicated, weekly on Monday)."""
		day = reference_date if reference_date is not None else date.today()
		expanded: list[tuple[str, Task]] = []

		for pet_name, task in tasks:
			if task.frequency == "twice_daily":
				expanded.append((pet_name, task))
				expanded.append((pet_name, task))
			elif task.frequency == "weekly":
				# Use Monday as the weekly scheduling anchor.
				if day.weekday() == 0:
					expanded.append((pet_name, task))
			elif task.frequency in {"daily", "as_needed"}:
				expanded.append((pet_name, task))
			else:
				expanded.append((pet_name, task))

		return expanded

	def detect_conflicts(
		self,
		max_minutes: int | None = None,
		reference_date: date | None = None,
	) -> list[str]:
		"""Return non-fatal warnings for time budget pressure, duplicates, and same-time collisions."""
		available_minutes = max_minutes if max_minutes is not None else self.owner.daily_time_available
		tasks = self.retrieve_tasks(include_completed=False)
		expanded = self._expand_recurring_tasks(tasks, reference_date=reference_date)
		conflicts: list[str] = []
		conflicts.extend(self._time_budget_conflicts(expanded, available_minutes))
		conflicts.extend(self._duplicate_task_conflicts(tasks))
		conflicts.extend(self._scheduled_time_conflicts(tasks))

		self._conflicts = conflicts
		return conflicts

	def _time_budget_conflicts(
		self,
		expanded_tasks: list[tuple[str, Task]],
		available_minutes: int,
	) -> list[str]:
		"""Detect conflicts where required time exceeds available time."""
		total_required = sum(task.duration_minutes for _, task in expanded_tasks)
		if total_required <= available_minutes:
			return []
		return [
			f"Total required time ({total_required} minutes) exceeds available time ({available_minutes} minutes)."
		]

	def _duplicate_task_conflicts(self, tasks: list[tuple[str, Task]]) -> list[str]:
		"""Detect duplicate recurring task definitions for the same pet."""
		conflicts: list[str] = []
		seen: set[tuple[str, str, str]] = set()
		for pet_name, task in tasks:
			key = (pet_name.lower(), task.description.strip().lower(), task.frequency)
			if key in seen:
				conflicts.append(
					f"Duplicate recurring task for {pet_name}: '{task.description}' ({task.frequency})."
				)
			else:
				seen.add(key)
		return conflicts

	def _scheduled_time_conflicts(self, tasks: list[tuple[str, Task]]) -> list[str]:
		"""Detect exact scheduled-time matches; this intentionally does not compute interval overlap."""
		conflicts: list[str] = []
		time_buckets: dict[str, list[tuple[str, Task]]] = {}
		for pet_name, task in tasks:
			if task.scheduled_time is None:
				continue
			time_buckets.setdefault(task.scheduled_time, []).append((pet_name, task))

		for scheduled_time, items in time_buckets.items():
			if len(items) < 2:
				continue

			pet_names = {pet_name for pet_name, _ in items}
			task_names = ", ".join(f"{task.description} ({pet_name})" for pet_name, task in items)
			if len(pet_names) == 1:
				only_pet = next(iter(pet_names))
				conflicts.append(
					f"Time conflict at {scheduled_time}: multiple tasks for {only_pet} overlap ({task_names})."
				)
			else:
				conflicts.append(
					f"Time conflict at {scheduled_time}: tasks overlap across pets ({task_names})."
				)
		return conflicts

	def organize_tasks(
		self,
		tasks: list[tuple[str, Task]] | None = None,
	) -> list[tuple[str, Task]]:
		"""Order tasks by completion, then frequency, then priority, then shorter duration."""
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

	def _find_pet_for_task(self, task_id: str) -> tuple[Pet, Task] | None:
		"""Return the pet and task pair for a given task id."""
		for pet in self.owner.pets:
			for task in pet.tasks:
				if task.task_id == task_id:
					return pet, task
		return None

	def _build_next_recurring_task(self, task: Task, completed_on: date | None = None) -> Task | None:
		"""Create a follow-up task for daily/weekly items with the next due date and same time."""
		if task.frequency not in {"daily", "weekly"}:
			return None

		reference_day = completed_on if completed_on is not None else date.today()
		if task.frequency == "daily":
			next_due_date = reference_day + timedelta(days=1)
		else:
			next_due_date = reference_day + timedelta(days=7)

		return Task(
			description=task.description,
			duration_minutes=task.duration_minutes,
			frequency=task.frequency,
			due_date=next_due_date,
			scheduled_time=task.scheduled_time,
			priority=task.priority,
		)

	def mark_task_completed(self, task_id: str) -> bool:
		"""Mark a task completed by id and return whether it was found."""
		found = self._find_pet_for_task(task_id)
		if found is None:
			return False

		pet, task = found
		if task.is_completed:
			return True

		task.mark_completed()

		next_task = self._build_next_recurring_task(task, completed_on=date.today())
		if next_task is not None:
			pet.add_task(next_task)

		return True

	def generate_daily_plan(self, max_minutes: int | None = None) -> list[tuple[str, Task]]:
		"""Generate a capped plan using recurring expansion, priority ordering, and time-budget checks."""
		available_minutes = max_minutes if max_minutes is not None else self.owner.daily_time_available
		if available_minutes <= 0:
			raise ValueError("available minutes must be greater than 0")

		remaining_minutes = available_minutes
		base_tasks = self.retrieve_tasks(include_completed=False)
		expanded_tasks = self._expand_recurring_tasks(base_tasks)
		sorted_tasks = self.organize_tasks(expanded_tasks)
		self.detect_conflicts(max_minutes=available_minutes)

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

		if self._conflicts:
			explanation_parts.append("Conflicts: " + " ".join(self._conflicts))

		return " ".join(explanation_parts)
