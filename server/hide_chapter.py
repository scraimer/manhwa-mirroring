#!/usr/bin/env python3
import cgi
import json
import sqlite3

DB_PATH = "/var/lib/manhwa/state.sqlite3"


def ensure_schema(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chapter_limits ("
        "chapter TEXT PRIMARY KEY, last_page INTEGER, hidden INTEGER NOT NULL DEFAULT 0)"
    )
    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(chapter_limits)")
    }
    if "hidden_changed_at" not in columns:
        conn.execute(
            "ALTER TABLE chapter_limits ADD COLUMN hidden_changed_at TEXT"
        )


def respond(payload, status="200 OK"):
    print(f"Status: {status}\r\nContent-Type: application/json\r\n\r\n" + json.dumps(payload))


def main():
    form = cgi.FieldStorage()
    chapter = form.getfirst("chapter", "")
    hidden = form.getfirst("hidden", "1")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)

    if not chapter:
        rows = conn.execute(
            "SELECT chapter, hidden, hidden_changed_at "
            "FROM chapter_limits WHERE hidden = 1 ORDER BY hidden_changed_at DESC, chapter ASC"
        ).fetchall()
        conn.close()
        respond({
            "ok": True,
            "hidden": [
                {
                    "chapter": row[0],
                    "hidden": bool(row[1]),
                    "changed_at": row[2],
                }
                for row in rows
            ],
        })
        return

    is_hidden = 1 if hidden not in ("0", "false", "False", "") else 0
    conn.execute(
        "INSERT INTO chapter_limits(chapter,last_page,hidden,hidden_changed_at) "
        "VALUES(?,0,?,CURRENT_TIMESTAMP) "
        "ON CONFLICT(chapter) DO UPDATE SET "
        "hidden=excluded.hidden, "
        "hidden_changed_at=CURRENT_TIMESTAMP",
        (chapter, is_hidden),
    )
    conn.commit()
    conn.close()
    respond({"ok": True, "chapter": chapter, "hidden": bool(is_hidden)})


if __name__ == "__main__":
    main()
