# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Core actions
    User should be able to:
    - add pet and owner info
    - add and modify tasks/constraints
    - generate a plan based on those tasks/constraints

- Briefly describe your initial UML design.
    My initial UML design has an Owner, Pet, Task, and Scheduler class.
    The system follows the scenario fairly well, complexity will be added where I see fit.
- What classes did you include, and what responsibilities did you assign to each?
    My initial UML design has an Owner, Pet, Task, and Scheduler class. 
    Owner is responsible for contianing the owners name, the time they are available, and a list of their preferences. They can also update time available and set their preferences.
    Pet, has their name, pet species, and age of pet, You can also update this information with a seter. 
    Task has a title, duration, priority, and category, you can also update this with a setter.
    Scheduler is the most complex class, it has owner and pet objects, a list of task objects/daily plans, add and edit methods for tasks, plan generation method, and a explain plan tostring method.


**b. Design changes**

- Did your design change during implementation?
    Yes
- If yes, describe at least one change and why you made it.
    Scheduling logic was implemented, tasks sorted by owner preference match, then priority, then shorter duration
    No task and no fit edge cases are handled
    removed silent failures
    includes skipped task reasonsimp

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    The scheduler considers available daily time, task frequency (daily/twice_daily/weekly/as_needed), task priority, task duration, completion status, and lightweight time conflicts (same scheduled clock time). It also keeps track of skipped tasks when they do not fit in the remaining time budget.
- How did you decide which constraints mattered most?
    I prioritized constraints that most directly affect whether a task can realistically happen today. Time budget comes first because it is a hard limit. After that, recurring frequency and task priority are used to keep consistent pet care tasks at the top, then shorter duration helps fit more tasks into limited time. Conflict detection is treated as a warning so planning remains usable instead of failing.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    Time conflicts are exact match only
- Why is that tradeoff reasonable for this scenario?
    It optimizies for simplicity and reliability since this app is very minimal/early stage. It also mkaes
    the logic easy to read and maintain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    I used AI tools for all aspects, system design, helping me brainstorm, debugging issues, and refactoring components to fit design needs.
- What kinds of prompts or questions were most helpful?
    Having AI explain what current functionality does, screenshots of issues in the app help with context as well.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
    I had to reprompt for the Mermaid code and UML diagrams a few times to get it
    to where I wanted.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    I tested task creation and retrieval, filtering by pet and completion status, sorting by duration and planning priority, recurring expansion (daily/twice_daily/weekly), conflict warnings, and daily plan generation within the available time limit. I also tested completing tasks and confirming recurring daily/weekly tasks generate the next due instance.
- Why were these tests important?
    These tests are important because they validate  correctness and user trust. The scheduler is only useful if it consistently picks tasks in the expected order, respects time constraints, and clearly reports conflicts instead of failing silently. Testing recurring behavior and completion flow also prevents long-term care routines from breaking over time.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    I am fairly confident that the scheduler works correctly for the intended scope. The core planning path, recurrence handling, filtering/sorting, and warning generation are implemented and covered by tests for expected behavior and common edge cases.
- What edge cases would you test next if you had more time?
    Next I would test very large task lists for performance, multiple weekly tasks across different days, and more complex scheduling overlap logic.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    I am pretty satisfied with the logic.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    I'd put more time into the UI, make the experience a bit more appealing to look at for the user.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    AI is an incredibly powerful planning tool. I can run my thought process or decisions choices through it, and it can give me the pros and cons of my approach, make suggestions I never thought of, and apply my designs quicker than I could maually.
