"""Todo リスト Web アプリケーション（Flask）"""

import json
import os
import uuid
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from sheets import SheetsError, create_todo, get_all_todos, get_todo_by_id, update_todo
from styles import APP_CSS

load_dotenv()

COLOR_OPTIONS = {
    "": {"label": "なし", "bg": "#ffffff", "border": "#e5e7eb"},
    "red": {"label": "赤", "bg": "#fef2f2", "border": "#ef4444"},
    "orange": {"label": "オレンジ", "bg": "#fff7ed", "border": "#f97316"},
    "yellow": {"label": "黄", "bg": "#fefce8", "border": "#eab308"},
    "green": {"label": "緑", "bg": "#ecfdf5", "border": "#22c55e"},
    "blue": {"label": "青", "bg": "#eff6ff", "border": "#3b82f6"},
    "purple": {"label": "紫", "bg": "#faf5ff", "border": "#a855f7"},
}

SORT_OPTIONS = {
    "due_date_asc": "期日が近い順",
    "due_date_desc": "期日が遠い順",
    "created_at_desc": "登録が新しい順",
    "created_at_asc": "登録が古い順",
    "title_asc": "タイトル A→Z",
    "title_desc": "タイトル Z→A",
}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


@app.context_processor
def inject_globals():
    return {
        "app_css": APP_CSS,
        "color_options": COLOR_OPTIONS,
        "sort_options": SORT_OPTIONS,
    }


def _normalize_color(color: str) -> str:
    return color if color in COLOR_OPTIONS else ""


def _filter_todos(todos: list, query: str) -> list:
    if not query:
        return todos
    q = query.lower()
    return [
        t
        for t in todos
        if q in t["title"].lower() or q in t["content"].lower()
    ]


def _sort_todos(todos: list, sort_key: str) -> list:
    if sort_key not in SORT_OPTIONS:
        sort_key = "due_date_asc"

    def due_key(t):
        return t["due_date"] or "9999-12-31"

    def created_key(t):
        return t["created_at"] or ""

    if sort_key == "due_date_asc":
        return sorted(todos, key=lambda t: (due_key(t), created_key(t)))
    if sort_key == "due_date_desc":
        return sorted(todos, key=lambda t: (due_key(t), created_key(t)), reverse=True)
    if sort_key == "created_at_desc":
        return sorted(todos, key=created_key, reverse=True)
    if sort_key == "created_at_asc":
        return sorted(todos, key=created_key)
    if sort_key == "title_asc":
        return sorted(todos, key=lambda t: t["title"].lower())
    if sort_key == "title_desc":
        return sorted(todos, key=lambda t: t["title"].lower(), reverse=True)
    return todos


def _due_status(due_date: str) -> str:
    if not due_date:
        return ""
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        return ""
    today = date.today()
    if due < today:
        return "overdue"
    if due == today:
        return "today"
    return ""


def _notification_items(todos: list) -> list:
    items = []
    for todo in todos:
        status = _due_status(todo["due_date"])
        if status == "today":
            items.append({"title": todo["title"], "message": "期日は今日です", "type": "today"})
        elif status == "overdue":
            items.append({"title": todo["title"], "message": f"期日 {todo['due_date']} を過ぎています", "type": "overdue"})
    return items


def _index_context(**form_values):
    query = request.args.get("q", "").strip()
    sort = request.args.get("sort", "due_date_asc").strip()
    all_todos = _safe_get_todos()
    filtered = _filter_todos(all_todos, query)
    sorted_todos = _sort_todos(filtered, sort)
    for todo in sorted_todos:
        todo["due_status"] = _due_status(todo["due_date"])
        todo["color_info"] = COLOR_OPTIONS.get(_normalize_color(todo.get("color", "")), COLOR_OPTIONS[""])
    notify_all = _notification_items(all_todos)
    return {
        "todos": sorted_todos,
        "search_query": query,
        "sort_key": sort if sort in SORT_OPTIONS else "due_date_asc",
        "notify_items": notify_all,
        "notify_json": json.dumps(notify_all, ensure_ascii=False),
        "form_title": form_values.get("form_title", ""),
        "form_content": form_values.get("form_content", ""),
        "form_due_date": form_values.get("form_due_date", ""),
        "form_color": _normalize_color(form_values.get("form_color", "")),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()
        color = _normalize_color(request.form.get("color", "").strip())
        form = {
            "form_title": title,
            "form_content": content,
            "form_due_date": due_date,
            "form_color": color,
        }

        if not title:
            flash("タイトルは必須です。入力してください。", "error")
            return render_template("index.html", **_index_context(**form))

        try:
            create_todo(str(uuid.uuid4()), title, content, due_date, color)
            flash("Todo を登録しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template("index.html", **_index_context(**form))

    return render_template("index.html", **_index_context())


@app.route("/edit/<todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    try:
        todo = get_todo_by_id(todo_id)
    except SheetsError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))

    if todo is None:
        flash("指定された Todo が見つかりませんでした。", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()
        color = _normalize_color(request.form.get("color", "").strip())
        updated_todo = {**todo, "title": title, "content": content, "due_date": due_date, "color": color}

        if not title:
            flash("タイトルは必須です。入力してください。", "error")
            return render_template("edit.html", todo=updated_todo)

        try:
            updated = update_todo(todo_id, title, content, due_date, color)
            if not updated:
                flash("指定された Todo が見つかりませんでした。", "error")
                return redirect(url_for("index"))
            flash("Todo を更新しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template("edit.html", todo=updated_todo)

    todo["color"] = _normalize_color(todo.get("color", ""))
    return render_template("edit.html", todo=todo)


def _safe_get_todos() -> list:
    try:
        return get_all_todos()
    except SheetsError as exc:
        flash(str(exc), "error")
        return []


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
