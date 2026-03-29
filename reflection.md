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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
