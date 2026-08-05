"""Todo リスト Web アプリケーション（Flask）"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date, datetime, timedelta

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

NOTIFY_OPTIONS = {
    "0": "通知なし",
    "10": "10分前",
    "30": "30分前",
    "60": "1時間前",
    "180": "3時間前",
    "1440": "1日前",
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
        "notify_options": NOTIFY_OPTIONS,
        "sort_options": SORT_OPTIONS,
    }


def _normalize_color(color: str) -> str:
    return color if color in COLOR_OPTIONS else ""


def _normalize_notify_before(value: str) -> str:
    return value if value in NOTIFY_OPTIONS else "0"


def _parse_form_todo_fields(form) -> dict:
    return {
        "title": form.get("title", "").strip(),
        "content": form.get("content", "").strip(),
        "due_date": form.get("due_date", "").strip(),
        "due_time": form.get("due_time", "").strip(),
        "color": _normalize_color(form.get("color", "").strip()),
        "notify_before": _normalize_notify_before(form.get("notify_before", "0").strip()),
    }


def _validate_todo_fields(fields: dict) -> str | None:
    if not fields["title"]:
        return "タイトルは必須です。入力してください。"
    if fields["notify_before"] != "0":
        if not fields["due_date"]:
            return "通知を設定する場合は期日を入力してください。"
        if not fields["due_time"]:
            return "通知を設定する場合は予定時刻を入力してください。"
    return None


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
        time_part = t.get("due_time") or "23:59"
        return f"{t['due_date'] or '9999-12-31'} {time_part}"

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


def _parse_due_datetime(due_date: str, due_time: str) -> datetime | None:
    if not due_date:
        return None
    time_part = due_time or "09:00"
    try:
        return datetime.strptime(f"{due_date} {time_part}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def _due_status(due_date: str, due_time: str = "") -> str:
    due_dt = _parse_due_datetime(due_date, due_time)
    if not due_dt:
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

    now = datetime.now()
    if due_dt < now:
        return "overdue"
    if due_dt.date() == now.date():
        return "today"
    return ""


def _build_notifications(todos: list) -> tuple[list, list]:
    now = datetime.now()
    banner_items = []
    scheduled_items = []

    for todo in todos:
        notify_before = _normalize_notify_before(todo.get("notify_before", "0"))
        due_dt = _parse_due_datetime(todo.get("due_date", ""), todo.get("due_time", ""))
        title = todo["title"]

        if notify_before != "0" and due_dt:
            minutes = int(notify_before)
            notify_at = due_dt - timedelta(minutes=minutes)
            label = NOTIFY_OPTIONS[notify_before]
            due_label = due_dt.strftime("%Y-%m-%d %H:%M")

            if now >= notify_at and now <= due_dt:
                banner_items.append({
                    "title": title,
                    "message": f"予定の{label}です（{due_label}）",
                    "type": "reminder",
                })
            elif now > due_dt:
                banner_items.append({
                    "title": title,
                    "message": f"予定時刻 {due_dt.strftime('%H:%M')} を過ぎています",
                    "type": "overdue",
                })

            if now < due_dt:
                scheduled_items.append({
                    "id": todo["id"],
                    "title": title,
                    "message": f"「{title}」の予定が{label}に迫っています（{due_label}）",
                    "notify_at": notify_at.strftime("%Y-%m-%dT%H:%M:%S"),
                    "due_at": due_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                })
        else:
            status = _due_status(todo.get("due_date", ""), todo.get("due_time", ""))
            if status == "today":
                banner_items.append({
                    "title": title,
                    "message": "期日は今日です",
                    "type": "today",
                })
            elif status == "overdue":
                banner_items.append({
                    "title": title,
                    "message": f"期日 {todo.get('due_date', '')} を過ぎています",
                    "type": "overdue",
                })

    return banner_items, scheduled_items


def _enrich_todo(todo: dict) -> None:
    todo["due_status"] = _due_status(todo.get("due_date", ""), todo.get("due_time", ""))
    todo["color_info"] = COLOR_OPTIONS.get(_normalize_color(todo.get("color", "")), COLOR_OPTIONS[""])
    notify_key = _normalize_notify_before(todo.get("notify_before", "0"))
    todo["notify_label"] = NOTIFY_OPTIONS[notify_key]
    if todo.get("due_date") and todo.get("due_time"):
        todo["schedule_label"] = f"{todo['due_date']} {todo['due_time']}"
    elif todo.get("due_date"):
        todo["schedule_label"] = todo["due_date"]
    else:
        todo["schedule_label"] = ""


def _index_context(**form_values):
    query = request.args.get("q", "").strip()
    sort = request.args.get("sort", "due_date_asc").strip()
    all_todos = _safe_get_todos()
    filtered = _filter_todos(all_todos, query)
    sorted_todos = _sort_todos(filtered, sort)
    for todo in sorted_todos:
        _enrich_todo(todo)

    notify_items, scheduled_items = _build_notifications(all_todos)
    return {
        "todos": sorted_todos,
        "search_query": query,
        "sort_key": sort if sort in SORT_OPTIONS else "due_date_asc",
        "notify_items": notify_items,
        "scheduled_items": scheduled_items,
        "show_notify_section": bool(notify_items or scheduled_items),
        "notify_json": json.dumps(notify_items, ensure_ascii=False),
        "scheduled_json": json.dumps(scheduled_items, ensure_ascii=False),
        "form_title": form_values.get("title", form_values.get("form_title", "")),
        "form_content": form_values.get("content", form_values.get("form_content", "")),
        "form_due_date": form_values.get("due_date", form_values.get("form_due_date", "")),
        "form_due_time": form_values.get("due_time", form_values.get("form_due_time", "")),
        "form_color": _normalize_color(form_values.get("color", form_values.get("form_color", ""))),
        "form_notify_before": _normalize_notify_before(
            form_values.get("notify_before", form_values.get("form_notify_before", "0"))
        ),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        fields = _parse_form_todo_fields(request.form)
        error = _validate_todo_fields(fields)
        if error:
            flash(error, "error")
            return render_template("index.html", **_index_context(**fields))

        try:
            create_todo(
                str(uuid.uuid4()),
                fields["title"],
                fields["content"],
                fields["due_date"],
                fields["color"],
                fields["due_time"],
                fields["notify_before"],
            )
            flash("Todo を登録しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template("index.html", **_index_context(**fields))

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
        fields = _parse_form_todo_fields(request.form)
        updated_todo = {**todo, **fields}
        error = _validate_todo_fields(fields)
        if error:
            flash(error, "error")
            return render_template("edit.html", todo=updated_todo)

        try:
            updated = update_todo(
                todo_id,
                fields["title"],
                fields["content"],
                fields["due_date"],
                fields["color"],
                fields["due_time"],
                fields["notify_before"],
            )
            if not updated:
                flash("指定された Todo が見つかりませんでした。", "error")
                return redirect(url_for("index"))
            flash("Todo を更新しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template("edit.html", todo=updated_todo)

    todo["color"] = _normalize_color(todo.get("color", ""))
    todo["notify_before"] = _normalize_notify_before(todo.get("notify_before", "0"))
    return render_template("edit.html", todo=todo)


def _safe_get_todos() -> list:
    try:
        return get_all_todos()
    except SheetsError as exc:
        flash(str(exc), "error")
        return []


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
