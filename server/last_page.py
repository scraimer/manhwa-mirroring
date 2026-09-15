#!/usr/bin/env python3
import cgi
import json
import os
import sqlite3

DB_PATH = "/var/lib/manhwa/state.sqlite3"


def ensure_schema(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chapter_limits ("
        "chapter TEXT PRIMARY KEY, last_page INTEGER, hidden INTEGER NOT NULL DEFAULT 0)"
    )


def respond(payload, status="200 OK"):
    print(f"Status: {status}\r\nContent-Type: application/json\r\n\r\n" + json.dumps(payload))


def main():
    form = cgi.FieldStorage()
    chapter = form.getfirst("chapter", "")
    if not chapter:
        respond({"error": "invalid input"}, "400 Bad Request")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)

    method = os.environ.get("REQUEST_METHOD", "GET").upper()

    if method == "GET":
        row = conn.execute(
            "SELECT last_page FROM chapter_limits WHERE chapter = ?", (chapter,)
        ).fetchone()
        conn.close()
        respond({"ok": True, "chapter": chapter, "last_page": row[0] if row else None})
        return

    page = form.getfirst("page", "")
    if not page.isdigit():
        conn.close()
        respond({"error": "invalid input"}, "400 Bad Request")
        return

    # Toggling the same page again clears the limit, acting as an undo.
    page_num = int(page)
    row = conn.execute(
        "SELECT last_page FROM chapter_limits WHERE chapter = ?", (chapter,)
    ).fetchone()
    current_last_page = row[0] if row else None
    new_last_page = None if current_last_page == page_num else page_num

    conn.execute(
        "INSERT INTO chapter_limits(chapter,last_page,hidden) VALUES(?,?,0) "
        "ON CONFLICT(chapter) DO UPDATE SET last_page=excluded.last_page",
        (chapter, new_last_page),
    )
    conn.commit()
    conn.close()
    respond({"ok": True, "chapter": chapter, "last_page": new_last_page})


if __name__ == "__main__":
    main()
