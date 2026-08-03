"""Todo リスト Web アプリケーション（Flask）"""

import os
import uuid

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from sheets import SheetsError, create_todo, get_all_todos, get_todo_by_id, update_todo

load_dotenv()

app = Flask(__name__, static_folder="public/static", static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due_date = request.form.get("due_date", "").strip()

        if not title:
            flash("タイトルは必須です。入力してください。", "error")
            return render_template(
                "index.html",
                todos=_safe_get_todos(),
                form_title=title,
                form_content=content,
                form_due_date=due_date,
            )

        try:
            create_todo(str(uuid.uuid4()), title, content, due_date)
            flash("Todo を登録しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template(
                "index.html",
                todos=[],
                form_title=title,
                form_content=content,
                form_due_date=due_date,
            )

    return render_template(
        "index.html",
        todos=_safe_get_todos(),
        form_title="",
        form_content="",
        form_due_date="",
    )


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

        if not title:
            flash("タイトルは必須です。入力してください。", "error")
            return render_template("edit.html", todo={**todo, "title": title, "content": content, "due_date": due_date})

        try:
            updated = update_todo(todo_id, title, content, due_date)
            if not updated:
                flash("指定された Todo が見つかりませんでした。", "error")
                return redirect(url_for("index"))
            flash("Todo を更新しました。", "success")
            return redirect(url_for("index"))
        except SheetsError as exc:
            flash(str(exc), "error")
            return render_template("edit.html", todo={**todo, "title": title, "content": content, "due_date": due_date})

    return render_template("edit.html", todo=todo)


def _safe_get_todos() -> list:
    try:
        return get_all_todos()
    except SheetsError as exc:
        flash(str(exc), "error")
        return []


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
