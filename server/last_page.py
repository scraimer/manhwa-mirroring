#!/usr/bin/env python3
import cgi
import json
import sqlite3

DB_PATH = "/var/lib/manhwa/state.sqlite3"


def main():
    form = cgi.FieldStorage()
    chapter = form.getfirst("chapter", "")
    page = form.getfirst("page", "")
    if not chapter or not page.isdigit():
        print(
            "Status: 400 Bad Request\r\nContent-Type: application/json\r\n\r\n"
            "{\"error\":\"invalid input\"}"
        )
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chapter_limits ("
        "chapter TEXT PRIMARY KEY, last_page INTEGER, hidden INTEGER NOT NULL DEFAULT 0)"
    )
    conn.execute(
        "INSERT INTO chapter_limits(chapter,last_page,hidden) VALUES(?,?,0) "
        "ON CONFLICT(chapter) DO UPDATE SET last_page=excluded.last_page",
        (chapter, int(page)),
    )
    conn.commit()
    conn.close()
    print("Content-Type: application/json\r\n\r\n" + json.dumps({"ok": True}))


if __name__ == "__main__":
    main()
