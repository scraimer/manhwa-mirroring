## Context

See proposal.md - Why. The reader already uses a chapter-local page marker for the last page and a dedicated page-visibility routine in the JavaScript, so this change can follow the same pattern without changing the chapter navigation model or the hidden-chapter state logic.

## Goals / Non-Goals

**Goals:**
- Add a mirrored first-page selector alongside the last-page selector for each chapter image.
- Persist the first-page marker with the existing story+chapter identity used for read position and hidden chapter state.
- Hide earlier pages in normal reader mode while preserving the cutoff in Edit Mode so the selection stays editable.

**Non-Goals:**
- Reworking chapter ordering, story selection, or archive semantics.
- Altering the behavior of the existing last-page cutoff or the chapter hiding feature outside this new first-page workflow.

## Decisions

1. Reuse the existing per-page action pattern from the last-page toggle so the first-page control matches the UI and persistence semantics already used by the chapter reader.
   - Rationale: This keeps the editor workflow consistent and minimizes new state-handling logic or unfamiliar UX patterns.
   - Alternatives considered: A separate top-level chapter menu or a different marker representation; rejected because it would make the feature harder to discover and would diverge from the existing chapter editing model.

2. Extend the same story-and-chapter state key as the last-page marker instead of introducing a new storage mechanism.
   - Rationale: The project already scopes chapter state by story to avoid collisions between chapters with the same folder name.
   - Alternatives considered: A chapter-only record or a new table; rejected because it would bypass the existing story-scoped contract and risks cross-story contamination.

3. Hide earlier pages only when Edit Mode is off, but keep them visible and muted while editing.
   - Rationale: This preserves the reader experience while allowing authors to adjust the known page cutoff without leaving the editing workflow.
   - Alternatives considered: Always hiding the earlier pages or always revealing them; both would either block editing or reduce visibility too much.

## Risks / Trade-offs

- [Hidden pages can look like missing content if the selector is set incorrectly] → The UI should always show the first-page marker in a clear, toggleable button state and keep a muted preview during Edit Mode so the cut-off can be corrected quickly.
- [The feature adds another persisted marker to the same chapter-state table] → The update should follow the existing transaction and null/clear semantics so it does not accidentally affect the last-page record or hidden chapter data.

## Migration Plan

- This feature can be introduced without a schema migration if the storage layer treats the first-page marker as an additional nullable chapter-state field keyed by story and chapter.
- Existing chapters without a marker remain unaffected and show the full chapter in normal reader mode until the user sets a first-page cutoff.
- If a clear/toggle request is sent with the same page again, the marker is simply cleared to `null` so the start-of-chapter behavior matches the current last-page toggle semantics.
