## Context

`generate/generate_manhwa_html.py` renders each chapter page's DOM (including `.top-nav`, `.container#container` of `.page-container` divs, and swipe-indicator elements), and `generate/assets/script-chapter.js` + `style-chapter.css` drive all client-side behavior — no server involvement. See proposal.md ("Why") for the regression root cause and motivation.

Two independent things are broken/changing in the same file set:
1. `updateProgress()` (toolbar hide/show + `isAtBottomOfPage` computation) is defined but never invoked — the `window.addEventListener('scroll', updateProgress)` / `resize` lines and the initial call, present as of commit `d2f5629`, are missing as of `25f49c4` onward.
2. The vertical "swipe to next chapter" gesture is armed in `touchstart` based on `distanceFromBottom < screenHeight * 0.30 && isAtBottomOfPage`, i.e. a viewport-relative distance combined with a scroll-position flag that itself depended on the broken `updateProgress()`. This is being replaced with a concrete, always-rendered drop-zone element and bounding-box hit-testing, independent of scroll position, per the proposal.

## Goals / Non-Goals

**Goals:**
- Restore toolbar auto-hide/show on scroll exactly as it behaved before the regression.
- Give the next-chapter swipe gesture an explicit, visible activation area that works consistently even when trailing pages are hidden by the "beyond last page" feature.
- Keep the existing swipe *release* thresholds (distance/midpoint) and visual feedback (indicator, progress line, color transition) unchanged — only how the gesture is *armed* changes.

**Non-Goals:**
- Not changing the horizontal (chapter-to-chapter via right-edge swipe) gesture logic or its thresholds.
- Not changing the "beyond last page" hide/show behavior itself, Edit Mode, or hide-chapter features.
- Not adding automated tests (none exist in this repo); validation is manual per project convention.

## Decisions

**1. Restore the missing listeners rather than redesign toolbar logic.**
The pre-regression behavior (`updateProgress` bound to `scroll`/`resize`, plus an initial call) is exactly what the user wants back ("used to disappear... isn't disappearing now"). Alternative (rewriting with `IntersectionObserver`) is unnecessary scope creep for a straightforward restoration; rejected to keep the fix surgical.

**2. Drop zone is a real DOM element sized with `height: 30vh`, appended after the last `.page-container` (including hidden ones).**
This guarantees the element exists at a fixed, discoverable position at the true end of chapter content, regardless of which pages are hidden by the last-page marker. Rejected alternative: keep using `isAtBottomOfPage` (viewport-scroll-position based) — this is exactly the fragile heuristic the proposal calls out as broken/confusing when trailing pages are hidden, since "near the bottom of scrollable content" no longer means "near the bottom of all page images."

**3. Gesture arming uses `getBoundingClientRect()` hit-testing against the drop zone on `touchstart`, replacing `isAtBottomOfPage` and the `screenHeight * 0.30` distance check.**
`isAtBottomOfPage` and the associated scroll-based bottom detection in `updateProgress()` become unused for gesture arming once the drop zone exists ("removed for gesture activation" per proposal) — computing it is otherwise harmless, but the code that reads it for swipe-arming purposes will be replaced with a rect check: `touchStartY` (and `touchStartX` for horizontal bounds if needed) falls within the drop zone element's `top`/`bottom` (and, since it's full width, no `x` check is needed).

**4. Reuse the existing down-arrow-in-circle visual (`.vertical-swipe-arrow`'s markup/appearance) as a static, always-visible indicator inside the drop zone**, distinct from the existing `#verticalSwipeIndicator`/`#verticalSwipeProgressLine` elements which remain solely for the *active drag* feedback (position tracking, color change, progress line) triggered once a gesture is armed. The static arrow in the drop zone is a passive affordance ("drag from here"); the existing indicator elements continue to provide the dynamic feedback during the drag itself. This avoids conflating "where can I start dragging" (static, always shown) with "how far have I dragged" (dynamic, shown only while `isVerticalSwiping`).

**5. No drop zone (or a non-interactive one) is rendered on the last chapter**, mirroring how `NEXT` is already disabled (`getVisibleNeighbor(chapterFolder, 'next')` returns `null`). `generate_manhwa_html.py` already computes `next_chapter_file`/next-chapter visibility for the nav buttons; the same computed value gates whether the drop zone markup is emitted.

## Risks / Trade-offs

- [Risk] Restoring the scroll listener could reintroduce the same accidental-removal class of bug in a future refactor of the bottom-of-file event wiring. → Mitigation: keep the `addEventListener` calls immediately after the other top-level event registrations (their original location) rather than nesting them inside another handler, making future diffs less likely to drop them silently.
- [Risk] `30vh` on very short chapters (few pages) could make the drop zone occupy a large fraction of the visible page, feeling intrusive. → Mitigation: this matches the proposal's explicit sizing request; no additional min/max clamping is introduced unless the user reports it as a problem after review.
- [Risk] Appending the drop zone after hidden ("beyond last page") pages means it sits far down the DOM/scroll length even when most trailing pages are hidden from view (`display: none`) — hidden elements don't take up layout space, so the drop zone will still visually sit directly after the last *visible* image, which is the desired behavior; only its DOM order (after all `.page-container`s) is fixed regardless of visibility. → No mitigation needed; this is the intended behavior, noted here to avoid confusion during implementation.

## Migration Plan

No data migration. Deploy by regenerating HTML output (`python generate_manhwa_html.py ...`) after the code changes land; existing generated `html_output/` directories are static files that get fully regenerated, so there is no in-place upgrade concern. No rollback beyond reverting the commit and regenerating.
