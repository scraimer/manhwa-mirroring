## Why

The chapter reader already supports a "Set as Last Page" cutoff, but it does not provide the mirror workflow for a starting page marker. Readers and editors need a way to hide early pages from the normal view while still being able to adjust the cutoff in Edit Mode without losing the chapter's reading context.

## What Changes

- Add a "Set as First Page" toggle next to each image in a chapter, parallel to the existing "Set as Last Page" control.
- Persist the first-page marker alongside the chapter state that already records the last-page marker, scoped by story and chapter.
- Hide every page before the marked first page in normal reader mode while preserving visibility in Edit Mode so the cutoff remains editable without re-reading the whole chapter.
- Keep the existing last-page logic and chapter visibility rules unchanged outside this new cutoff behavior.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- chapter-reader-navigation: Extend chapter reader page visibility so a first-page marker hides prior pages outside Edit Mode while keeping those pages visible and muted during edits.
- chapter-state-persistence: Extend story-scoped chapter state to persist a first-page marker with the same identifier and toggle semantics used for the last-page marker.

## Impact

- `generate/generate_manhwa_html.py`: adds a first-page toggle button next to each page element for generated chapters.
- `generate/assets/script-chapter.js`: loads, toggles, and applies the first-page marker in the page visibility logic.
- `generate/assets/style-chapter.css`: adds muted or hidden presentation for pages before the first page while respecting Edit Mode.
- `server/last_page.py` or the companion chapter-state persistence layer: reuses the existing story+chapter state model for the first-page marker, without changing unrelated chapter state behavior.
