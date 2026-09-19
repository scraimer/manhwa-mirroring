#!/usr/bin/env python3
import cgi
import json
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
            "hidden_changed_at TEXT, "
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
            "hidden_changed_at TEXT, "
            "PRIMARY KEY(story, chapter))"
        )
        return

    if "hidden_changed_at" not in columns:
        conn.execute(
            "ALTER TABLE chapter_limits ADD COLUMN hidden_changed_at TEXT"
        )


def get_hidden_chapters(story):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT chapter, hidden, hidden_changed_at "
        "FROM chapter_limits WHERE story = ? AND hidden = 1 ORDER BY hidden_changed_at DESC, chapter ASC",
        (story,),
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


def set_hidden_state(story, chapter, is_hidden):
    story = normalize_identity(story, "story")
    chapter = normalize_identity(chapter, "chapter")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)
    conn.execute(
        "INSERT INTO chapter_limits(story,chapter,last_page,hidden,hidden_changed_at) "
        "VALUES(?, ?, NULL, ?, CURRENT_TIMESTAMP) "
        "ON CONFLICT(story, chapter) DO UPDATE SET "
        "hidden=excluded.hidden, "
        "hidden_changed_at=CURRENT_TIMESTAMP",
        (story, chapter, 1 if is_hidden else 0),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "story": story, "chapter": chapter, "hidden": bool(is_hidden)}


def respond(payload, status="200 OK"):
    print(f"Status: {status}\r\nContent-Type: application/json\r\n\r\n" + json.dumps(payload))


def main():
    form = cgi.FieldStorage()
    story = form.getfirst("story", "")
    chapter = form.getfirst("chapter", "")
    hidden = form.getfirst("hidden", "1")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = MEMORY")
    conn.execute("PRAGMA temp_store = MEMORY")
    ensure_schema(conn)

    try:
        story_name = normalize_identity(story, "story")
    except ValueError:
        story_name = ""

    if not chapter and not story_name:
        rows = conn.execute(
            "SELECT story, chapter, hidden, hidden_changed_at "
            "FROM chapter_limits WHERE hidden = 1 ORDER BY hidden_changed_at DESC, story ASC, chapter ASC"
        ).fetchall()
        conn.close()
        respond({
            "ok": True,
            "hidden": [
                {
                    "story": row[0],
                    "chapter": row[1],
                    "hidden": bool(row[2]),
                    "changed_at": row[3],
                }
                for row in rows
            ],
        })
        return

    if not chapter and story_name:
        rows = conn.execute(
            "SELECT story, chapter, hidden, hidden_changed_at "
            "FROM chapter_limits WHERE story = ? AND hidden = 1 ORDER BY hidden_changed_at DESC, chapter ASC",
            (story_name,),
        ).fetchall()
        conn.close()
        respond({
            "ok": True,
            "hidden": [
                {
                    "story": row[0],
                    "chapter": row[1],
                    "hidden": bool(row[2]),
                    "changed_at": row[3],
                }
                for row in rows
            ],
        })
        return

    if not story_name or not chapter:
        conn.close()
        respond({"error": "invalid input", "story": story_name, "chapter": chapter}, "400 Bad Request")
        return

    is_hidden = 1 if hidden not in ("0", "false", "False", "") else 0
    conn.execute(
        "INSERT INTO chapter_limits(story,chapter,last_page,hidden,hidden_changed_at) "
        "VALUES(?, ?, NULL, ?, CURRENT_TIMESTAMP) "
        "ON CONFLICT(story, chapter) DO UPDATE SET "
        "hidden=excluded.hidden, "
        "hidden_changed_at=CURRENT_TIMESTAMP",
        (story_name, chapter, is_hidden),
    )
    conn.commit()
    conn.close()
    respond({"ok": True, "story": story_name, "chapter": chapter, "hidden": bool(is_hidden)})


if __name__ == "__main__":
    main()
