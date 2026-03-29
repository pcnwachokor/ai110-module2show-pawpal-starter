import streamlit as st
from pawpal_system import Task, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ Dashboard")
st.markdown("*Your intelligent pet care scheduler*")

st.markdown("---")

with st.container():
    st.subheader("Owner Setup")
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Owner name", value="Jordan")
    with col2:
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

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Manage Pets")
    pet_col1, pet_col2, pet_col3, pet_col4 = st.columns(4)
    with pet_col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with pet_col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pet_col3:
        age = st.number_input("Pet age", min_value=0, max_value=50, value=3)
    with pet_col4:
        st.write("")
        st.write("")
        add_pet_btn = st.button("Add pet", use_container_width=True)

    if add_pet_btn:
        if owner.get_pet(pet_name):
            st.info(f"{pet_name} already exists.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
            st.success(f"Added {pet_name}")
            st.rerun()

with col2:
    st.metric("Total Pets", len(owner.pets))

if owner.pets:
    st.write("**Current Pets:**")
    pet_cols = st.columns(len(owner.pets))
    for idx, pet in enumerate(owner.pets):
        with pet_cols[idx]:
            with st.container(border=True):
                st.write(f"🐾 **{pet.name}**")
                st.caption(f"{pet.species.capitalize()} • {pet.age} years")
                st.metric("Tasks", len(pet.tasks))
else:
    st.info("No pets added yet. Start by adding your first pet!")

st.markdown("---")

st.subheader("Schedule a Task")
tc1, tc2, tc3, tc4, tc5 = st.columns(5)
with tc1:
    task_description = st.text_input("Task description", value="Morning walk")
with tc2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with tc3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with tc4:
    frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly", "as_needed"], index=0)
with tc5:
    selected_pet_name = st.selectbox(
        "Pet",
        options=[pet.name for pet in owner.pets],
        index=0,
        disabled=not owner.pets,
    )

priority_map = {"low": 1, "medium": 2, "high": 3}

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("Add task", use_container_width=True):
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
            st.success(f"Task added for {selected_pet_name}")
            st.rerun()

st.markdown("---")


def _suggest_resolution(conflict: str) -> str:
    """Convert technical conflict warnings into owner-friendly actions."""
    if "Time conflict at" in conflict:
        return "Move one of the overlapping tasks to a different time so care is not double-booked."
    if "Duplicate recurring task" in conflict:
        return "Remove one duplicate task to avoid doing the same care twice by mistake."
    if "exceeds available time" in conflict:
        return "Lower durations, postpone lower-priority tasks, or increase daily available time."
    return "Review this warning and adjust task details before generating the final plan."


def _priority_badge(priority: int) -> str:
    """Return a colored badge for task priority."""
    if priority >= 3:
        return "High"
    elif priority == 2:
        return "Medium"
    else:
        return "Low"




all_tasks = scheduler.retrieve_tasks(include_completed=True)
if all_tasks:
    st.subheader("Task Overview")

    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
    with filter_col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            options=["All pets"] + [pet.name for pet in owner.pets],
            key="task_filter_pet",
        )
    with filter_col2:
        status_filter_label = st.selectbox(
            "Filter by status",
            options=["All", "Pending", "Completed"],
            key="task_filter_status",
        )
    with filter_col3:
        st.metric("Total Tasks", len(all_tasks))

    status_filter = None
    if status_filter_label == "Pending":
        status_filter = False
    elif status_filter_label == "Completed":
        status_filter = True

    filtered_tasks = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        is_completed=status_filter,
    )

    tab_all, tab_time, tab_priority = st.tabs([
        "Filtered Tasks",
        "Sorted by Time",
        "Planning Order",
    ])

    with tab_all:
        if filtered_tasks:
            task_display = []
            for pet, task in filtered_tasks:
                task_display.append({
                    "Pet": f"🐾 {pet}",
                    "Task": task.description,
                    "Duration": f"{task.duration_minutes} min",
                    "Frequency": task.frequency,
                    "Priority": _priority_badge(task.priority),
                    "Due": task.due_date.isoformat(),
                    "Status": "Done" if task.is_completed else "Pending",
                })
            st.dataframe(task_display, use_container_width=True, hide_index=True)
            st.success(f"Showing {len(filtered_tasks)} task(s)")
        else:
            st.warning("No tasks match the selected filters.")

    with tab_time:
        sorted_by_time = scheduler.sort_by_time(tasks=filtered_tasks)
        if sorted_by_time:
            time_display = []
            for pet, task in sorted_by_time:
                time_display.append({
                    "Pet": f"🐾 {pet}",
                    "Task": task.description,
                    "Duration": f"{task.duration_minutes} min",
                    "Frequency": task.frequency,
                    "Priority": _priority_badge(task.priority),
                })
            st.dataframe(time_display, use_container_width=True, hide_index=True)
            st.caption("⏱Chronological order by shortest duration first")
        else:
            st.info("No tasks available for time-based sorting.")

    with tab_priority:
        planning_order = scheduler.organize_tasks(tasks=filtered_tasks)
        if planning_order:
            planning_display = []
            for pet, task in planning_order:
                planning_display.append({
                    "Pet": f"🐾 {pet}",
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Priority": _priority_badge(task.priority),
                    "Duration": f"{task.duration_minutes} min",
                    "Status": "Done" if task.is_completed else "Pending",
                })
            st.dataframe(planning_display, use_container_width=True, hide_index=True)
            st.caption("Planning order: frequency → priority → duration")
        else:
            st.info("No tasks available for planning-order sorting.")

    # Keep conflict warnings highly visible and actionable for pet owners.
    pending_conflicts = scheduler.detect_conflicts()
    if pending_conflicts:
        with st.container(border=True):
            st.warning(f"**{len(pending_conflicts)} Scheduling Warning(s)**")
            st.caption("These warnings do not block schedule generation, but they may cause issues.")
            for conflict in pending_conflicts:
                col_w, col_a = st.columns([1.5, 1])
                with col_w:
                    st.markdown(f"**Warning:** {conflict}")
                with col_a:
                    st.markdown(f"*{_suggest_resolution(conflict)}*")
    else:
        st.success("No scheduling conflicts detected for current pending tasks.")
else:
    st.info("No tasks yet. Add one above to get started!")

st.markdown("---")

pending_tasks = scheduler.retrieve_tasks(include_completed=False)
if pending_tasks:
    st.subheader("Complete a Task")

    task_options = {
        f"{pet_name} - {task.description} (due {task.due_date.isoformat()})": task.task_id
        for pet_name, task in pending_tasks
    }
    col_select, col_btn = st.columns([3, 1])
    with col_select:
        selected_task_label = st.selectbox(
            "Choose a pending task",
            options=list(task_options.keys()),
            key="complete_task_select",
        )
    with col_btn:
        st.write("")
        complete_btn = st.button("Mark Complete", use_container_width=True)

    if complete_btn:
        task_id = task_options[selected_task_label]
        if scheduler.mark_task_completed(task_id):
            st.success("Task marked completed. Recurring tasks advanced to next date.")
            st.rerun()
        else:
            st.error("Could not find the selected task.")

st.divider()

st.subheader("🎯 Build Today's Schedule")
st.caption("Generate an optimized daily plan based on your pets' tasks and available time.")

col_gen, col_info = st.columns([1, 3])
with col_gen:
    if st.button("Generate Schedule", use_container_width=True):
        if not owner.pets:
            st.warning("Add at least one pet first.")
        elif not scheduler.retrieve_tasks(include_completed=False):
            st.warning("Add at least one pending task first.")
        else:
            plan = scheduler.generate_daily_plan()
            if plan:
                with st.container(border=True):
                    st.success("Today's Schedule Generated!")
                    plan_display = []
                    total_time = 0
                    for pet_name, task in plan:
                        total_time += task.duration_minutes
                        plan_display.append({
                            "Pet": f"🐾 {pet_name}",
                            "Task": task.description,
                            "Duration": f"{task.duration_minutes} min",
                            "Frequency": task.frequency,
                            "Priority": _priority_badge(task.priority),
                        })
                    st.dataframe(plan_display, use_container_width=True, hide_index=True)
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Tasks Scheduled", len(plan))
                    with col_m2:
                        st.metric("Total Time", f"{total_time} min")
                    with col_m3:
                        st.metric("Available", f"{owner.daily_time_available} min")
            else:
                st.info("No tasks fit in today's available time.")

            st.markdown("### Plan Explanation")
            with st.container(border=True):
                st.write(scheduler.explain_plan())
