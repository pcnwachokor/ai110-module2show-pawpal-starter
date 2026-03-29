# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

- Time-based sorting and filtering by pet and completion status.
- Recurring task support that expands daily/twice-daily/weekly behavior at planning time.
- Auto-regeneration of recurring tasks when completed:
	- Daily tasks create a new task due the next day.
	- Weekly tasks create a new task due in 7 days.
- Lightweight conflict detection warnings (non-fatal):
	- Not enough available time for all expanded tasks.
	- Duplicate recurring definitions for the same pet.
	- Exact same-time collisions across tasks.

## Features

- **Task Recurrence**: Expands daily/twice-daily/weekly/as-needed tasks for planning
- **Smart Sorting**: Organizes tasks by completion status → frequency → priority → duration
- **Time Budget**: Greedy scheduling that fits tasks within available time; tracks skipped tasks
- **Conflict Detection**: Warns about time budget overages, duplicate tasks, and scheduled time collisions
- **Auto-Regeneration**: Creating follow-up daily/weekly tasks when recurring tasks are completed
- **Input Validation**: Enforces duration > 0, priority ≥ 0, and HH:MM time format
- **Flexible Filtering**: Retrieve tasks by pet, completion status, or task ID
- **Plan Explanation**: `explain_plan()` provides natural language reasoning for selected tasks
- **Case-Insensitive Matching**: Pet lookups accept any capitalization (Fluffy, fluffy, FLUFFY)

## Demo

<a href="/PawPal_App.png" target="_blank"><img src='/PawpPal_App.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

## Testing PawPal+
```bash
python -m pytest
```
Confidence Level: 5 

## Getting started

### Setup

```bash 
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
