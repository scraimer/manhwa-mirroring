## Why

Hidden-chapter state and the reader's last-page marker are currently keyed only by
chapter name. Two stories containing the same chapter name therefore share one
database record, causing one story's state to overwrite or appear in the other.

## What Changes

- Scope hidden-chapter state by the story's parent directory name and chapter name.
- Scope last-page state by the same story-plus-chapter identity.
- Update request and response handling so both endpoints receive and return the
  story identity needed to distinguish duplicate chapter names.
- Migrate existing `chapter_limits` data without silently merging records that
  cannot be assigned to a story.
- Preserve the current hide/unhide, list-hidden, get-last-page, and toggle-last-page
  behavior within each story.

## Capabilities

### New Capabilities

- `chapter-state-persistence`: Store and retrieve hidden and last-page state using
  the parent story directory plus chapter name as the chapter identity.

### Modified Capabilities

None.

## Impact

- `server/hide_chapter.py` and `server/last_page.py` will change their request
  parameters, SQL schema, queries, and response payloads.
- The SQLite `chapter_limits` table will need a migration from a chapter-only key to
  a story-and-chapter key.
- Reader or management clients that call these CGI endpoints must send the parent
  story directory name and handle the expanded identity in responses.
- No external dependencies are expected.
