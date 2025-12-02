# Personal Kanban MVP

A minimal personal kanban board (Jira/Trello style) built for eco-pace coding iterations. This repo holds a static single-page MVP with localStorage persistence plus a lightweight architecture plan.

## Features
- Quick add form for tasks with optional project, priority, due date, tags, and description.
- LocalStorage persistence with column status transitions.
- Filters by status/project plus title search with active filter indicator.
- Inline comments per task stored alongside the card data.
- Pre-seeded demo tasks (if storage is empty) so the board looks alive on first open.

## Quick start
- Open `index.html` directly in a browser or run a tiny server: `python -m http.server 8000` and visit `http://localhost:8000/index.html`.
- If the browser blocks localStorage in file mode, a yellow notice will appear. The board still works, but data will survive only while the tab is open.
- Add tasks via the “Быстро добавить” form and move them between columns with the status buttons on each card.
