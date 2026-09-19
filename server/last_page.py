#!/usr/bin/env python3
import cgi
import json
import os
import sqlite3

DB_PATH = "/var/lib/manhwa/state.sqlite3"


def normalize_identity(value, label):
    if value is None:
        raise ValueError(f"missing {label}")
    value = str(value).strip()
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError(f"invalid {label}")
    return value


def ensure_schema(conn):
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    if "chapter_limits" not in tables:
        conn.execute(
            "CREATE TABLE chapter_limits ("
            "story TEXT NOT NULL, "
            "chapter TEXT NOT NULL, "
            "last_page INTEGER, "
            "hidden INTEGER NOT NULL DEFAULT 0, "
            "PRIMARY KEY(story, chapter))"
        )
        return

    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(chapter_limits)")
    }
    if "story" not in columns:
        conn.execute("ALTER TABLE chapter_limits RENAME TO chapter_limits_legacy")
        conn.execute(
            "CREATE TABLE chapter_limits ("
            "story TEXT NOT NULL, "
            "chapter TEXT NOT NULL, "
            "last_page INTEGER, "
            "hidden INTEGER NOT NULL DEFAULT 0, "
            "PRIMARY KEY(story, chapter))"
        )


def get_last_page(story, chapter):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    row = conn.execute(
        "SELECT last_page FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story, chapter),
    ).fetchone()
    conn.close()
    value = row[0] if row else None
    return None if value in (None, 0) else value


def set_last_page(story, chapter, page_num):
    story = normalize_identity(story, "story")
    chapter = normalize_identity(chapter, "chapter")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    row = conn.execute(
        "SELECT last_page FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story, chapter),
    ).fetchone()
    current_last_page = row[0] if row else None
    new_last_page = None if current_last_page == page_num else page_num
    conn.execute(
        "INSERT INTO chapter_limits(story,chapter,last_page,hidden) VALUES(?,?,?,0) "
        "ON CONFLICT(story, chapter) DO UPDATE SET last_page=excluded.last_page",
        (story, chapter, new_last_page),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "story": story, "chapter": chapter, "last_page": new_last_page}


def respond(payload, status="200 OK"):
    print(f"Status: {status}\r\nContent-Type: application/json\r\n\r\n" + json.dumps(payload))


def main():
    form = cgi.FieldStorage()
    story = form.getfirst("story", "")
    chapter = form.getfirst("chapter", "")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)

    try:
        story_name = normalize_identity(story, "story")
    except ValueError:
        story_name = ""

    try:
        chapter_name = normalize_identity(chapter, "chapter")
    except ValueError:
        chapter_name = ""

    if not story_name or not chapter_name:
        conn.close()
        respond({"error": "invalid input", "story": story_name, "chapter": chapter_name}, "400 Bad Request")
        return

    method = os.environ.get("REQUEST_METHOD", "GET").upper()

    if method == "GET":
        row = conn.execute(
            "SELECT last_page FROM chapter_limits WHERE story = ? AND chapter = ?",
            (story_name, chapter_name),
        ).fetchone()
        conn.close()
        value = row[0] if row else None
        respond({"ok": True, "story": story_name, "chapter": chapter_name, "last_page": None if value in (None, 0) else value})
        return

    page = form.getfirst("page", "")
    if not page.isdigit():
        conn.close()
        respond({"error": "invalid input", "story": story_name, "chapter": chapter_name}, "400 Bad Request")
        return

    page_num = int(page)
    row = conn.execute(
        "SELECT last_page FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story_name, chapter_name),
    ).fetchone()
    current_last_page = row[0] if row else None
    new_last_page = None if current_last_page == page_num else page_num

    conn.execute(
        "INSERT INTO chapter_limits(story,chapter,last_page,hidden) VALUES(?,?,?,0) "
        "ON CONFLICT(story, chapter) DO UPDATE SET last_page=excluded.last_page",
        (story_name, chapter_name, new_last_page),
    )
    conn.commit()
    conn.close()
    respond({"ok": True, "story": story_name, "chapter": chapter_name, "last_page": new_last_page})


if __name__ == "__main__":
    main()
