from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
	name: str
	daily_time_available: int
	preferences: list[str] = field(default_factory=list)

	def update_time_available(self, minutes: int) -> None:
		self.daily_time_available = minutes

	def set_preferences(self, preferences: list[str]) -> None:
		self.preferences = preferences


@dataclass
class Pet:
	name: str
	species: str
	age: int

	def update_info(self, name: str, species: str, age: int) -> None:
		self.name = name
		self.species = species
		self.age = age


@dataclass
class Task:
	title: str
	duration_minutes: int
	priority: int
	category: str

	def update(
		self,
		duration_minutes: int | None = None,
		priority: int | None = None,
		category: str | None = None,
	) -> None:
		if duration_minutes is not None:
			self.duration_minutes = duration_minutes
		if priority is not None:
			self.priority = priority
		if category is not None:
			self.category = category


@dataclass
class Scheduler:
	owner: Owner
	pet: Pet
	tasks: list[Task] = field(default_factory=list)
	daily_plan: list[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)

	def edit_task(self, task_index: int, updates: dict) -> None:
		if task_index < 0 or task_index >= len(self.tasks):
			return

		task = self.tasks[task_index]
		task.update(
			duration_minutes=updates.get("duration_minutes"),
			priority=updates.get("priority"),
			category=updates.get("category"),
		)

	def generate_daily_plan(self) -> list[Task]:
		"""Build and return a daily plan from available tasks."""
		raise NotImplementedError

	def explain_plan(self) -> str:
		"""Return a plain-language explanation of the chosen daily plan."""
		raise NotImplementedError
