#!/usr/bin/env python3
import cgi
import json
import sqlite3

DB_PATH = "/var/lib/manhwa/state.sqlite3"


def main():
    form = cgi.FieldStorage()
    chapter = form.getfirst("chapter", "")
    hidden = form.getfirst("hidden", "1")
    if not chapter:
        print(
            "Status: 400 Bad Request\r\nContent-Type: application/json\r\n\r\n"
            "{\"error\":\"invalid input\"}"
        )
        return
    is_hidden = 1 if hidden not in ("0", "false", "False", "") else 0
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chapter_limits ("
        "chapter TEXT PRIMARY KEY, last_page INTEGER, hidden INTEGER NOT NULL DEFAULT 0)"
    )
    conn.execute(
        "INSERT INTO chapter_limits(chapter,last_page,hidden) VALUES(?,0,?) "
        "ON CONFLICT(chapter) DO UPDATE SET hidden=excluded.hidden",
        (chapter, is_hidden),
    )
    conn.commit()
    conn.close()
    print("Content-Type: application/json\r\n\r\n" + json.dumps({"ok": True}))


if __name__ == "__main__":
    main()
