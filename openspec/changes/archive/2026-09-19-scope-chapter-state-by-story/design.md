## Context

The two CGI endpoints currently share the `chapter_limits` SQLite table, whose primary key is the chapter name alone. Both endpoints also create their schema independently, so the migration must be safe when either endpoint is invoked first. See proposal.md for the motivation and `specs/chapter-state-persistence/spec.md` for the behavior contract.

## Goals / Non-Goals

**Goals:**

- Introduce a stable composite identity composed of the parent story directory name and chapter directory name.
- Keep hidden state and last-page state in one shared table so the existing endpoint relationship remains intact.
- Make both endpoints apply the same schema initialization and validation rules.
- Prevent legacy chapter-only rows from being silently assigned to a story.
- Preserve the existing HTTP methods and toggle semantics where they remain meaningful.

**Non-Goals:**

- Do not redesign the reader UI or chapter discovery format.
- Do not infer story identity from filesystem paths inside the CGI endpoints.
- Do not add an external database or dependency.
- Do not attempt to merge duplicate legacy rows into multiple stories.

## Decisions

### Use explicit `story` and `chapter` columns with a composite primary key

Add a story column and make `(story, chapter)` the uniqueness boundary. Keep the two values separate in API payloads rather than encoding them into one opaque string, so callers can display and validate them independently.

An opaque concatenated key was rejected because delimiter escaping would create ambiguity and make SQL queries and responses harder to reason about. A separate state table per story was rejected because it would complicate initialization and discovery.

### Centralize schema migration behavior in a shared server-side helper

The schema setup used by both endpoints should converge on one migration routine, either in a small shared Python module or an equivalent duplicated routine kept byte-for-byte consistent if CGI deployment constraints require standalone files. The routine should detect the chapter-only schema, create the composite-key table, copy only rows with an explicitly known story identity, and retain unresolved legacy data in a non-active legacy structure or equivalent quarantine.

Dropping legacy rows outright was rejected because it destroys recoverable user state. Assigning every legacy row to the first or only current story was rejected because it can corrupt an unrelated story.

### Require story identity in endpoint requests

Both endpoints should accept the parent story directory name as an explicit request field alongside `chapter`. Hidden listing should accept the story filter and return the story and chapter fields for each record. The endpoints should reject blank values before database mutation.

Deriving the story from the chapter name was rejected because that is the collision being fixed. Deriving it from the CGI request path was rejected because deployment paths do not reliably encode the story directory.

### Validate identity as a path component, not as a path

The implementation should reject empty values and values containing path separators or traversal components, while allowing the existing chapter/story naming conventions. This keeps the identity scoped to names and prevents a request from escaping the intended namespace.

## Risks / Trade-offs

- [Risk] Existing callers that send only `chapter` will receive client errors. -> Mitigation: update all in-repository callers and document the required `story` field; do not silently fall back to ambiguous chapter-only behavior.
- [Risk] CGI scripts may be deployed as standalone files and cannot import a sibling helper in the production image. -> Mitigation: verify the server packaging layout during implementation and use a shared module only if it is included by the image; otherwise keep the migration logic synchronized in both endpoints and test both entry points.
- [Risk] Legacy records may not be recoverable without external story metadata. -> Mitigation: quarantine rather than guess, and make the migration outcome observable in implementation tests or administrative diagnostics.
- [Risk] Two endpoint implementations could drift in schema details. -> Mitigation: add integration coverage that initializes the database through either endpoint and exercises both state types against the same composite key.

## Migration Plan

1. Deploy schema initialization that can recognize the chapter-only table and prepare a story-scoped table without assigning ambiguous legacy rows.
2. Deploy the endpoint contract and update all repository callers to send the parent story directory name.
3. Verify same-name chapters in two stories, hide/list behavior, last-page get/set/toggle behavior, and initialization through each CGI endpoint.
4. Roll back application code only if needed; retain the migrated database structure and compatibility/quarantine table so rollback does not destroy state. A full rollback to chapter-only behavior is intentionally not supported because it would reintroduce cross-story collisions.
