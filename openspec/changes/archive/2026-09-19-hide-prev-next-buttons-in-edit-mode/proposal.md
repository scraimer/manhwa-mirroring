## Why

The chapter reader keeps the Prev and Next navigation buttons visible while Edit Mode is active, even though the UI is meant to prioritize chapter-edit actions. This makes the editing controls feel crowded and reduces the available space for the actions users actually need in Edit Mode.

## What Changes

- The reader will hide the TOC button together with the Prev and Next chapter navigation controls whenever Edit Mode is enabled.
- Those navigation controls will return automatically when Edit Mode is exited.
- The change is limited to the chapter-reader UI state and does not alter chapter navigation logic outside Edit Mode.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `chapter-reader-navigation`: Update the reader behavior so the TOC button and the Prev/Next controls are hidden while Edit Mode is active, while preserving normal navigation when Edit Mode is off.

## Impact

- `generate/assets/script-chapter.js`: toggles the reader UI state for Edit Mode
- `generate/generate_manhwa_html.py`: renders the nav controls that will be selectively hidden
- `generate/assets/style-chapter.css`: may need additional selectors or state classes for the hidden navigation state
- No server-side API or storage changes are required
