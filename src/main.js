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

function renderStats(tasks) {
  const { total, byStatus } = summarize(tasks);
  const parts = [`Всего: ${total}`].concat(
    statuses.map((s) => `${s.label}: ${byStatus[s.id] || 0}`)
  );
  statsEl.textContent = parts.join(' · ');
}

function createCard(task, onUpdateStatus) {
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

  return card;
}

function renderBoard(tasks) {
  boardEl.innerHTML = '';
  statuses.forEach((status) => {
    const template = document.getElementById('column-template');
    const columnEl = template.content.firstElementChild.cloneNode(true);
    columnEl.querySelector('.column-title').textContent = status.label;

    const columnTasks = tasks.filter((t) => t.status === status.id);
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
        .forEach((task) => body.appendChild(createCard(task, handleUpdateStatus)));
    }

    boardEl.appendChild(columnEl);
  });
  renderStats(tasks);
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

const state = {
  tasks: loadTasks(),
};

formEl.addEventListener('submit', handleCreateTask);
renderBoard(state.tasks);
