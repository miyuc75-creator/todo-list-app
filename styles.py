"""アプリ共通スタイル（Vercel でも確実に読み込めるよう Python に同梱）"""

APP_CSS = """
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", Meiryo, sans-serif;
  background: #f3f6fb;
  color: #1f2937;
  line-height: 1.6;
}

.container {
  width: min(920px, 92%);
  margin: 0 auto;
  padding: 24px 0 48px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  color: #111827;
}

.subtitle {
  margin: 0;
  color: #6b7280;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  padding: 20px;
}

.form-card {
  margin-bottom: 28px;
}

.form-card h2,
.todo-list-section h2 {
  margin: 0 0 16px;
  font-size: 1.125rem;
}

.messages {
  margin-bottom: 16px;
}

.message {
  margin: 0 0 8px;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 0.95rem;
}

.message-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.message-success {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.todo-form {
  display: grid;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-weight: 600;
  font-size: 0.95rem;
}

.required {
  color: #dc2626;
  font-size: 0.85rem;
  font-weight: 700;
}

input[type="text"],
input[type="date"],
input[type="search"],
select,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font: inherit;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input[type="text"]:focus,
input[type="date"]:focus,
input[type="search"]:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

textarea {
  resize: vertical;
  min-height: 110px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font: inherit;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #eef2ff;
  color: #3730a3;
  border: 1px solid #c7d2fe;
}

.btn-secondary:hover {
  background: #e0e7ff;
}

.btn-link {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-link:hover {
  background: #f9fafb;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.875rem;
}

.notify-banner {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.notify-banner h2 {
  margin: 0 0 10px;
  font-size: 1rem;
}

.notify-banner ul {
  margin: 0 0 12px;
  padding-left: 20px;
}

.notify-item {
  margin-bottom: 4px;
}

.notify-today {
  color: #92400e;
}

.notify-overdue {
  color: #991b1b;
}

.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.color-option input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.color-swatch {
  display: block;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 2px solid #d1d5db;
}

.color-option input:checked + .color-swatch {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.color-label {
  color: #6b7280;
}

.list-toolbar {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
}

.search-sort-form {
  display: grid;
  grid-template-columns: 1fr 1fr auto auto;
  gap: 12px;
  align-items: end;
}

.badge-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.color-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  border: 2px solid;
  font-size: 0.8rem;
  font-weight: 600;
  background: #fff;
}

.due-badge-today {
  background: #fef3c7;
  color: #92400e;
}

.due-badge-overdue {
  background: #fee2e2;
  color: #991b1b;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.todo-list {
  display: grid;
  gap: 16px;
}

.todo-card {
  display: grid;
  gap: 12px;
}

.todo-card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.todo-card-header h3 {
  margin: 0;
  font-size: 1.125rem;
  word-break: break-word;
}

.due-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.due-badge-empty {
  background: #f3f4f6;
  color: #6b7280;
}

.todo-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: #374151;
}

.todo-content-empty {
  color: #9ca3af;
  font-style: italic;
}

.todo-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.85rem;
  color: #6b7280;
}

.empty-state p {
  margin: 0;
  color: #6b7280;
}

@media (max-width: 640px) {
  .container {
    width: 94%;
    padding-top: 16px;
  }

  .card {
    padding: 16px;
  }

  .todo-card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-actions {
    flex-direction: column;
  }

  .search-sort-form {
    grid-template-columns: 1fr;
  }

  .btn {
    width: 100%;
  }
}
"""
