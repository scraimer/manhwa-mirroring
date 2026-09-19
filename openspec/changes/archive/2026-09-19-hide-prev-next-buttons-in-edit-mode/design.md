## Context

The chapter reader already has an Edit Mode toggle in the shared chapter UI, and the relevant state is managed in `generate/assets/script-chapter.js`. The current code flips a body class and toggles edit-specific controls, but it does not remove the Prev/Next navigation controls from the layout while Edit Mode is active.

## Goals / Non-Goals

**Goals:**
- Keep the chapter editor controls prominent while Edit Mode is active
- Hide the TOC button together with the chapter-level navigation controls only during Edit Mode
- Restore the normal navigation state when Edit Mode is exited

**Non-Goals:**
- Changing chapter ordering, hidden-chapter logic, or page-state persistence
- Changing the scroll-to-hide toolbar behavior outside Edit Mode
- Reworking the chapter navigation API or page-generation pipeline

## Decisions

1. Reuse the existing Edit Mode state instead of introducing a separate UI flag.
   - The document already tracks `editModeEnabled` and toggles a body class (`edit-mode`) in `updateEditModeUi()`.
   - This keeps the behavior aligned with the current reader state and avoids extra synchronization code.

2. Hide the TOC button and the Prev/Next navigation controls while Edit Mode is enabled.
   - The existing chapter nav elements are already represented as `data-nav="prev"` and `data-nav="next"` targets, and the TOC action is part of the same top navigation cluster.
   - A UI-state toggle can hide these controls without altering the chapter selection logic or the fallback link state that remains useful when Edit Mode is off.

3. Restore the control state when Edit Mode is toggled off.
   - Reusing the same state transition ensures the reader returns to the standard navigation layout without a reload.
   - This avoids a mismatch between the visible UI and the underlying `navLinks` state.

## Risks / Trade-offs

- [Potential visual gap in the toolbar] → The navigation controls are hidden only while Edit Mode is active, so the layout may have a temporary gap until the state is restored; this is acceptable because the purpose of Edit Mode is to prioritize editor controls.
- [Accidental hiding of other navigation UI] → Limit the selector logic to the Prev/Next nav links to keep the rest of the controls (TOC, chapter title, page count) visible and unchanged.
- [State mismatch after repeated toggles] → Ensure the toggle logic is idempotent and restored from the same `editModeEnabled` state each time the toggle runs.

## Migration Plan

No migration is required. This is a UI-only change in the generated chapter reader; existing chapter data and page state remain valid.

## Open Questions

None at this time.
