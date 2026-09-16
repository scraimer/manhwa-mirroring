## Why

Two regressions in the chapter reader (`generate/assets/script-chapter.js`) were introduced by the recent Edit Mode / "Set as Last Page" work: (1) the top toolbar no longer hides while scrolling, and (2) dragging from the bottom of a chapter to jump to the next chapter no longer works. Root cause for both: the `window.addEventListener('scroll', updateProgress)` / `resize` registrations and the initial `updateProgress()` call were dropped in the "Add Hide Chapter" commit (`25f49c4`), so `updateProgress()` — which drives toolbar hide/show and computes `isAtBottomOfPage` — never runs. On top of restoring that, the existing "bottom-of-screen drag" heuristic (touch starts within the last 30% of the *viewport*) is fragile and now conflicts with hidden/last-page content, so we are replacing it with an explicit, always-present drop zone at the true end of the page content.

## What Changes

- Restore toolbar auto-hide on scroll: re-attach `scroll`/`resize` listeners (and an initial call) to `updateProgress()` so `.top-nav` hides/shows based on scroll direction, as it did before the regression.
- Replace the implicit "bottom 30% of viewport" touch-start heuristic for next-chapter swipe with an explicit **next-chapter drop zone** element:
  - Rendered once per chapter page, after all page images (including any images hidden by "beyond last page").
  - Full-width, black background, height = 30% of viewport height (`30vh`).
  - Contains the existing down-arrow-in-circle indicator style (reusing `.vertical-swipe-arrow` visuals) at its bottom, always visible (not just during an active drag) so users know where to start the gesture.
  - The vertical swipe-to-next-chapter gesture may only begin (`isVerticalSwiping = true`) when `touchstart` occurs within this element's bounding box; the previous "distance from bottom of viewport" / `isAtBottomOfPage` scroll-position heuristic is removed for gesture activation.
  - No drop zone (and therefore no swipe-to-next-chapter gesture) is rendered on the last chapter, matching current behavior where `NEXT` is disabled when there is no next chapter.

## Capabilities

### New Capabilities
- `chapter-reader-navigation`: Reader-page behavior for toolbar visibility while scrolling and for the touch-drag gesture that advances to the next chapter, including the new next-chapter drop-zone element.

### Modified Capabilities
(none — no existing specs cover this behavior yet)

## Impact

- `generate/assets/script-chapter.js`: restore scroll/resize listener wiring; replace `isAtBottomOfPage`/viewport-distance based gesture activation with drop-zone bounding-box detection.
- `generate/assets/style-chapter.css`: new `.next-chapter-dropzone` (or similar) styles: black background, `height: 30vh`, arrow-in-circle indicator.
- `generate/generate_manhwa_html.py`: emit the new drop-zone element/markup at the end of each chapter's page container, after all page images (including those beyond the marked last page).
- No server-side (`server/*.py`) or data-format changes.
