"""Google スプレッドシートとの連携を担当するモジュール"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["id", "title", "content", "due_date", "created_at", "updated_at"]


class SheetsError(Exception):
    """スプレッドシート操作に関するエラー"""


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise SheetsError(
            f"環境変数「{name}」が設定されていません。"
            f"ローカルでは .env ファイル、Vercel では Environment Variables を確認してください。"
        )
    return value.strip()


def _get_client() -> gspread.Client:
    try:
        service_account_json = _get_env("GOOGLE_SERVICE_ACCOUNT_JSON")
        credentials_info = json.loads(service_account_json)
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        return gspread.authorize(credentials)
    except json.JSONDecodeError as exc:
        raise SheetsError(
            "GOOGLE_SERVICE_ACCOUNT_JSON の形式が正しくありません。JSON 文字列である必要があります。"
        ) from exc
    except Exception as exc:
        raise SheetsError(
            "Google スプレッドシートへの接続に失敗しました。"
            "サービスアカウントの設定とスプレッドシートの共有設定を確認してください。"
        ) from exc


def _get_worksheet():
    try:
        client = _get_client()
        spreadsheet_id = _get_env("GOOGLE_SPREADSHEET_ID")
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        _ensure_headers(worksheet)
        return worksheet
    except SheetsError:
        raise
    except Exception as exc:
        raise SheetsError(
            "スプレッドシートを開けませんでした。"
            "GOOGLE_SPREADSHEET_ID が正しいか、サービスアカウントに編集権限が付与されているか確認してください。"
        ) from exc


def _ensure_headers(worksheet) -> None:
    first_row = worksheet.row_values(1)
    if not first_row:
        worksheet.append_row(HEADERS)
        return
    if first_row != HEADERS:
        worksheet.update("A1:F1", [HEADERS])


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _row_to_todo(row: list) -> dict:
    padded = row + [""] * (len(HEADERS) - len(row))
    return {
        "id": padded[0],
        "title": padded[1],
        "content": padded[2],
        "due_date": padded[3],
        "created_at": padded[4],
        "updated_at": padded[5],
    }


def get_all_todos() -> list[dict]:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_values()
    if len(rows) <= 1:
        return []
    todos = [_row_to_todo(row) for row in rows[1:] if any(cell.strip() for cell in row)]
    todos.sort(key=lambda t: (t["due_date"] or "9999-12-31", t["created_at"] or ""))
    return todos


def get_todo_by_id(todo_id: str) -> dict | None:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_values()
    for row in rows[1:]:
        todo = _row_to_todo(row)
        if todo["id"] == todo_id:
            return todo
    return None


def create_todo(todo_id: str, title: str, content: str, due_date: str) -> None:
    worksheet = _get_worksheet()
    now = _now_iso()
    worksheet.append_row([todo_id, title, content, due_date, now, now])


def update_todo(todo_id: str, title: str, content: str, due_date: str) -> bool:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_values()
    for index, row in enumerate(rows[1:], start=2):
        if row and row[0] == todo_id:
            created_at = row[4] if len(row) > 4 else _now_iso()
            worksheet.update(
                f"A{index}:F{index}",
                [[todo_id, title, content, due_date, created_at, _now_iso()]],
            )
            return True
    return False
