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
            "first_page INTEGER, "
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
            "first_page INTEGER, "
            "hidden INTEGER NOT NULL DEFAULT 0, "
            "PRIMARY KEY(story, chapter))"
        )
        return

    if "first_page" not in columns:
        conn.execute("ALTER TABLE chapter_limits ADD COLUMN first_page INTEGER")


def get_page_marker(story, chapter, marker):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    row = conn.execute(
        f"SELECT {marker} FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story, chapter),
    ).fetchone()
    conn.close()
    value = row[0] if row else None
    return None if value in (None, 0) else value


def set_page_marker(story, chapter, page_num, marker):
    story = normalize_identity(story, "story")
    chapter = normalize_identity(chapter, "chapter")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    row = conn.execute(
        f"SELECT {marker} FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story, chapter),
    ).fetchone()
    current_page = row[0] if row else None
    new_page = None if current_page == page_num else page_num
    conn.execute(
        f"INSERT INTO chapter_limits(story,chapter,{marker},hidden) VALUES(?,?,?,0) "
        f"ON CONFLICT(story, chapter) DO UPDATE SET {marker}=excluded.{marker}",
        (story, chapter, new_page),
    )
    conn.commit()
    conn.close()
    return new_page


def get_last_page(story, chapter):
    return get_page_marker(story, chapter, "last_page")


def set_last_page(story, chapter, page_num):
    new_page = set_page_marker(story, chapter, page_num, "last_page")
    return {"ok": True, "story": story, "chapter": chapter, "last_page": new_page}


def get_first_page(story, chapter):
    return get_page_marker(story, chapter, "first_page")


def set_first_page(story, chapter, page_num):
    new_page = set_page_marker(story, chapter, page_num, "first_page")
    return {"ok": True, "story": story, "chapter": chapter, "first_page": new_page}


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
            "SELECT last_page, first_page FROM chapter_limits WHERE story = ? AND chapter = ?",
            (story_name, chapter_name),
        ).fetchone()
        conn.close()
        last_page = row[0] if row else None
        first_page = row[1] if row else None
        respond({
            "ok": True,
            "story": story_name,
            "chapter": chapter_name,
            "last_page": None if last_page in (None, 0) else last_page,
            "first_page": None if first_page in (None, 0) else first_page,
        })
        return

    page = form.getfirst("page", "")
    if not page.isdigit():
        conn.close()
        respond({"error": "invalid input", "story": story_name, "chapter": chapter_name}, "400 Bad Request")
        return

    page_num = int(page)
    marker = form.getfirst("marker", "last_page")
    if marker not in {"last_page", "first_page"}:
        conn.close()
        respond({"error": "invalid input", "story": story_name, "chapter": chapter_name}, "400 Bad Request")
        return

    row = conn.execute(
        f"SELECT {marker} FROM chapter_limits WHERE story = ? AND chapter = ?",
        (story_name, chapter_name),
    ).fetchone()
    current_page = row[0] if row else None
    new_page = None if current_page == page_num else page_num

    conn.execute(
        f"INSERT INTO chapter_limits(story,chapter,{marker},hidden) VALUES(?,?,?,0) "
        f"ON CONFLICT(story, chapter) DO UPDATE SET {marker}=excluded.{marker}",
        (story_name, chapter_name, new_page),
    )
    conn.commit()
    conn.close()
    respond({"ok": True, "story": story_name, "chapter": chapter_name, marker: new_page})


if __name__ == "__main__":
    main()
