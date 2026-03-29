import streamlit as st
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")
daily_time = st.number_input("Daily time available (minutes)", min_value=1, max_value=480, value=60)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, daily_time_available=int(daily_time))
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# Keep owner values in sync with current form fields.
owner.name = owner_name
owner.update_time_available(int(daily_time))

st.markdown("### Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Pet age", min_value=0, max_value=50, value=3)

if st.button("Add pet"):
    if owner.get_pet(pet_name):
        st.info(f"{pet_name} already exists.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        st.success(f"Added pet: {pet_name}")

if owner.pets:
    st.write("Current pets:")
    st.table([
        {"name": pet.name, "species": pet.species, "age": pet.age, "tasks": len(pet.tasks)}
        for pet in owner.pets
    ])
else:
    st.info("No pets added yet.")

st.markdown("### Schedule a Task")
col1, col2, col3, col4 = st.columns(4)
with col1:
    task_description = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly", "as_needed"], index=0)

priority_map = {"low": 1, "medium": 2, "high": 3}

selected_pet_name = st.selectbox(
    "Assign task to pet",
    options=[pet.name for pet in owner.pets],
    index=0,
    disabled=not owner.pets,
)

if st.button("Add task"):
    if not owner.pets:
        st.warning("Add a pet before adding tasks.")
    else:
        scheduler.add_task_to_pet(
            selected_pet_name,
            Task(
                description=task_description,
                duration_minutes=int(duration),
                frequency=frequency,
                priority=priority_map[priority_label],
            ),
        )
        st.success(f"Added task for {selected_pet_name}")

all_tasks = scheduler.retrieve_tasks(include_completed=True)
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "pet": pet,
            "description": task.description,
            "duration_minutes": task.duration_minutes,
            "frequency": task.frequency,
            "due_date": task.due_date.isoformat(),
            "priority": task.priority,
            "completed": task.is_completed,
        }
        for pet, task in all_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

pending_tasks = scheduler.retrieve_tasks(include_completed=False)
if pending_tasks:
    st.markdown("### Complete a Task")

    task_options = {
        f"{pet_name} - {task.description} (due {task.due_date.isoformat()})": task.task_id
        for pet_name, task in pending_tasks
    }
    selected_task_label = st.selectbox(
        "Choose a pending task",
        options=list(task_options.keys()),
        key="complete_task_select",
    )

    if st.button("Mark selected task completed"):
        task_id = task_options[selected_task_label]
        if scheduler.mark_task_completed(task_id):
            st.success("Task marked completed. Recurring tasks were advanced to their next due date.")
            st.rerun()
        else:
            st.error("Could not find the selected task.")

st.divider()

st.subheader("Build Schedule")
st.caption("Build and display today's schedule using your Scheduler class.")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one pet first.")
    elif not scheduler.retrieve_tasks(include_completed=False):
        st.warning("Add at least one pending task first.")
    else:
        plan = scheduler.generate_daily_plan()
        if plan:
            st.success("Today's Schedule")
            st.table([
                {
                    "pet": pet_name,
                    "task": task.description,
                    "duration_minutes": task.duration_minutes,
                    "frequency": task.frequency,
                    "priority": task.priority,
                }
                for pet_name, task in plan
            ])
        else:
            st.info("No tasks fit in today's available time.")

        st.markdown("### Plan Explanation")
        st.write(scheduler.explain_plan())
