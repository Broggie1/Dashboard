# Dashboard

## Backlog
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "Backlog"
sort priority asc, due_date asc

kanban
```

## Planned
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "Planned"
sort priority asc, due_date asc

kanban
```

## In Progress
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "In Progress"
sort priority asc, due_date asc

kanban
```

## Blocked
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "Blocked"
sort priority asc, due_date asc

kanban
```

## Review
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "Review"
sort priority asc, due_date asc

kanban
```

## Complete
```dataview
table priority as Priority, assigned_to as Assigned, due_date as Due
from "Work-Items"
where status = "Complete"
sort priority asc, due_date asc

kanban
```

