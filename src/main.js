const STORAGE_KEY = 'mini-kanban-tasks-v1';
const statuses = [
  { id: 'inbox', label: 'Inbox' },
  { id: 'plan', label: 'План' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'done', label: 'Готово' }
];

const priorityLabels = { low: 'Низкий', medium: 'Средний', high: 'Высокий' };

const boardEl = document.getElementById('board');
const formEl = document.getElementById('taskForm');
const statsEl = document.getElementById('stats');
const filterStatusEl = document.getElementById('filterStatus');
const filterProjectEl = document.getElementById('filterProject');
const filterSearchEl = document.getElementById('filterSearch');
const resetFiltersBtn = document.getElementById('resetFilters');
const activeFiltersEl = document.getElementById('activeFilters');

function loadTasks() {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) return [];
  try {
    const parsed = JSON.parse(data);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn('Не удалось прочитать хранилище, очищаю', e);
    localStorage.removeItem(STORAGE_KEY);
    return [];
  }
}

function saveTasks(tasks) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function createId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function summarize(tasks) {
  const total = tasks.length;
  const byStatus = statuses.map(({ id }) => [id, tasks.filter((t) => t.status === id).length]);
  return { total, byStatus: Object.fromEntries(byStatus) };
}

function renderStats(allTasks, visibleTasks) {
  const { total, byStatus } = summarize(visibleTasks);
  const base = [`На доске: ${total}`].concat(
    statuses.map((s) => `${s.label}: ${byStatus[s.id] || 0}`)
  );

  if (visibleTasks.length !== allTasks.length) {
    base.unshift(`Всего задач: ${allTasks.length}`);
  }

  statsEl.textContent = base.join(' · ');
}

function renderComments(listEl, comments) {
  listEl.innerHTML = '';
  if (!comments.length) {
    const empty = document.createElement('li');
    empty.className = 'muted';
    empty.textContent = 'Комментариев пока нет';
    listEl.appendChild(empty);
    return;
  }

  comments
    .slice()
    .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
    .forEach((comment) => {
      const li = document.createElement('li');
      const date = new Date(comment.createdAt).toLocaleString();
      li.innerHTML = `<span class="comment-date">${date}</span> — ${comment.text}`;
      listEl.appendChild(li);
    });
}

function createCard(task, onUpdateStatus, onAddComment) {
  const template = document.getElementById('card-template');
  const card = template.content.firstElementChild.cloneNode(true);

  card.querySelector('.card-title').textContent = task.title;
  card.querySelector('.card-desc').textContent = task.description || 'Без описания';
  card.querySelector('.card-project').textContent = task.project || 'Без проекта';

  const badge = card.querySelector('.badge');
  badge.textContent = task.status === 'done' ? '✓' : '·';

  card.querySelector('.priority').textContent = `Приоритет: ${priorityLabels[task.priority]}`;
  card.querySelector('.due').textContent = task.dueDate ? `Дедлайн: ${task.dueDate}` : 'Без дедлайна';
  card.querySelector('.tags').textContent = task.tags.length ? `Теги: ${task.tags.join(', ')}` : 'Тегов нет';

  const actions = card.querySelector('.card-actions');
  statuses.forEach((status) => {
    if (status.id === task.status) return;
    const btn = document.createElement('button');
    btn.textContent = status.label;
    btn.addEventListener('click', () => onUpdateStatus(task.id, status.id));
    actions.appendChild(btn);
  });

  const commentsList = card.querySelector('.comments-list');
  renderComments(commentsList, task.comments);

  const commentForm = card.querySelector('.comment-form');
  commentForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const input = commentForm.comment;
    const text = input.value.trim();
    if (!text) return;
    onAddComment(task.id, text);
    input.value = '';
  });

  return card;
}

function applyFilters(tasks, filters) {
  const search = filters.search.toLowerCase();
  const project = filters.project.toLowerCase();

  return tasks.filter((task) => {
    const matchesStatus = filters.status === 'all' || task.status === filters.status;
    const matchesProject = !project || task.project.toLowerCase().includes(project);
    const matchesSearch = !search || task.title.toLowerCase().includes(search);
    return matchesStatus && matchesProject && matchesSearch;
  });
}

function renderActiveFilters(filters) {
  const active = [];
  if (filters.status !== 'all') {
    const statusLabel = statuses.find((s) => s.id === filters.status)?.label || filters.status;
    active.push(`Статус: ${statusLabel}`);
    filterStatusEl.classList.add('active');
  } else {
    filterStatusEl.classList.remove('active');
  }

  if (filters.project.trim()) {
    active.push(`Проект: ${filters.project}`);
    filterProjectEl.classList.add('active');
  } else {
    filterProjectEl.classList.remove('active');
  }

  if (filters.search.trim()) {
    active.push(`Поиск: ${filters.search}`);
    filterSearchEl.classList.add('active');
  } else {
    filterSearchEl.classList.remove('active');
  }

  activeFiltersEl.textContent = active.length ? `Активно: ${active.join(' · ')}` : 'Фильтры не заданы';
}

function renderBoard(tasks) {
  const filtered = applyFilters(tasks, state.filters);
  boardEl.innerHTML = '';
  statuses.forEach((status) => {
    const template = document.getElementById('column-template');
    const columnEl = template.content.firstElementChild.cloneNode(true);
    columnEl.querySelector('.column-title').textContent = status.label;

    const columnTasks = filtered.filter((t) => t.status === status.id);
    columnEl.querySelector('.count').textContent = columnTasks.length;

    const body = columnEl.querySelector('.column-body');
    if (!columnTasks.length) {
      const empty = document.createElement('p');
      empty.className = 'muted';
      empty.textContent = 'Пока пусто';
      body.appendChild(empty);
    } else {
      columnTasks
        .sort((a, b) => new Date(a.dueDate || a.createdAt) - new Date(b.dueDate || b.createdAt))
        .forEach((task) => body.appendChild(createCard(task, handleUpdateStatus, handleAddComment)));
    }

    boardEl.appendChild(columnEl);
  });
  renderStats(tasks, filtered);
  renderActiveFilters(state.filters);
}

function handleUpdateStatus(taskId, nextStatus) {
  state.tasks = state.tasks.map((t) =>
    t.id === taskId ? { ...t, status: nextStatus, updatedAt: new Date().toISOString() } : t
  );
  saveTasks(state.tasks);
  renderBoard(state.tasks);
}

function handleCreateTask(event) {
  event.preventDefault();
  const formData = new FormData(formEl);
  const tags = (formData.get('tags') || '')
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean);

  const task = {
    id: createId(),
    title: formData.get('title')?.toString().trim() || 'Без названия',
    description: formData.get('description')?.toString().trim() || '',
    status: 'inbox',
    priority: formData.get('priority') || 'medium',
    project: formData.get('project')?.toString().trim() || '',
    tags,
    dueDate: formData.get('dueDate') || '',
    comments: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  state.tasks = [task, ...state.tasks];
  saveTasks(state.tasks);
  renderBoard(state.tasks);
  formEl.reset();
  formEl.title.focus();
}

function handleAddComment(taskId, text) {
  state.tasks = state.tasks.map((task) =>
    task.id === taskId
      ? {
          ...task,
          comments: [
            ...task.comments,
            { id: createId(), taskId, text, createdAt: new Date().toISOString() }
          ],
          updatedAt: new Date().toISOString(),
        }
      : task
  );
  saveTasks(state.tasks);
  renderBoard(state.tasks);
}

function handleFilterChange() {
  state.filters = {
    status: filterStatusEl.value,
    project: filterProjectEl.value.trim(),
    search: filterSearchEl.value.trim(),
  };
  renderBoard(state.tasks);
}

function resetFilters() {
  filterStatusEl.value = 'all';
  filterProjectEl.value = '';
  filterSearchEl.value = '';
  handleFilterChange();
}

const state = {
  tasks: loadTasks(),
  filters: { status: 'all', project: '', search: '' },
};

formEl.addEventListener('submit', handleCreateTask);
filterStatusEl.addEventListener('change', handleFilterChange);
filterProjectEl.addEventListener('input', handleFilterChange);
filterSearchEl.addEventListener('input', handleFilterChange);
resetFiltersBtn.addEventListener('click', resetFilters);

renderBoard(state.tasks);
