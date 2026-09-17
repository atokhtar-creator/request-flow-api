from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException, Query

from app.db import connect, init_db
from app.schemas import HistoryItem, RequestCreate, RequestOut, RequestStatus, StatusUpdate
from app.workflow import can_transition

DEFAULT_DB = Path(__file__).resolve().parent.parent / "requests.db"
DB_PATH = Path(os.getenv("REQUEST_FLOW_DB", str(DEFAULT_DB)))

app = FastAPI(title="Request Flow API", version="1.0.0", description="A small workflow backend with request history.")
conn = connect(DB_PATH)
init_db(conn)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_row(request_id: int):
    row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return row


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/requests", response_model=RequestOut, status_code=201)
def create_request(payload: RequestCreate):
    now = utc_now()
    cursor = conn.execute(
        "INSERT INTO requests(title, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (payload.title, payload.description, RequestStatus.NEW.value, now, now),
    )
    request_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO request_history(request_id, old_status, new_status, changed_at) VALUES (?, ?, ?, ?)",
        (request_id, None, RequestStatus.NEW.value, now),
    )
    conn.commit()
    return dict(get_row(request_id))


@app.get("/requests", response_model=list[RequestOut])
def list_requests(status: RequestStatus | None = Query(default=None)):
    if status is None:
        rows = conn.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM requests WHERE status = ? ORDER BY id DESC", (status.value,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/requests/{request_id}", response_model=RequestOut)
def get_request(request_id: int):
    return dict(get_row(request_id))


@app.patch("/requests/{request_id}/status", response_model=RequestOut)
def update_status(request_id: int, payload: StatusUpdate):
    row = get_row(request_id)
    old_status = RequestStatus(row["status"])
    new_status = payload.status
    if old_status == new_status:
        return dict(row)
    if not can_transition(old_status, new_status):
        raise HTTPException(status_code=409, detail=f"Transition {old_status.value} -> {new_status.value} is not allowed")
    now = utc_now()
    conn.execute("UPDATE requests SET status = ?, updated_at = ? WHERE id = ?", (new_status.value, now, request_id))
    conn.execute(
        "INSERT INTO request_history(request_id, old_status, new_status, changed_at) VALUES (?, ?, ?, ?)",
        (request_id, old_status.value, new_status.value, now),
    )
    conn.commit()
    return dict(get_row(request_id))


@app.get("/requests/{request_id}/history", response_model=list[HistoryItem])
def request_history(request_id: int):
    get_row(request_id)
    rows = conn.execute(
        "SELECT old_status, new_status, changed_at FROM request_history WHERE request_id = ? ORDER BY id",
        (request_id,),
    ).fetchall()
    return [dict(row) for row in rows]
