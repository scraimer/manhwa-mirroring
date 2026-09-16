## 1. Restore toolbar auto-hide on scroll

- [x] 1.1 Re-add `window.addEventListener('scroll', updateProgress)` and `window.addEventListener('resize', updateProgress)` plus an initial `updateProgress()` call at the bottom of `generate/assets/script-chapter.js`, placed alongside the other top-level event registrations; verify by regenerating a sample chapter's HTML and confirming in a browser that `.top-nav` gains the `hidden` class after scrolling down past ~400px and loses it when scrolling back up.
- [x] 1.2 Confirm the fix works with both an untouched chapter and a chapter that has a "last page" marked (some pages hidden via `.beyond-last-page`), verifying the toolbar still hides/shows correctly in both cases.

## 2. Add the next-chapter drop zone element

- [x] 2.1 In `generate/generate_manhwa_html.py`, emit a new drop-zone element (e.g. `<div class="next-chapter-dropzone" id="nextChapterDropzone">...</div>`) immediately after the closing of the last `.page-container` inside `.container#container`, only when a next chapter file exists (reuse the same `next_chapter_file` check already used for the NEXT nav button); verify by generating HTML for a mid-story chapter and confirming the element appears once, after all page-container divs (including any pages a reader would later mark as beyond-last-page), and confirming it is absent for the final chapter.
- [x] 2.2 In `generate/assets/style-chapter.css`, add `.next-chapter-dropzone` styles: full width, `height: 30vh`, black (`background: #000` or equivalent) background, and a nested static arrow element reusing the visual appearance of `.vertical-swipe-arrow` (down arrow in a circle) anchored at the bottom of the drop zone; verify visually in a browser that the drop zone is black, roughly 30% of viewport height, and shows a down-arrow-in-circle at its bottom without requiring an active drag.

## 3. Rewire next-chapter swipe gesture activation to the drop zone

- [x] 3.1 In `generate/assets/script-chapter.js`, update the `touchstart` handler so that `isVerticalSwiping` is armed based on whether the touch point (`touchStartX`/`touchStartY`) falls within `nextChapterDropzone.getBoundingClientRect()` (when the element exists and a next chapter is available), removing the `distanceFromBottom < screenHeight * 0.30 && isAtBottomOfPage` condition for this purpose; verify by testing (via browser dev tools touch emulation) that a touch-start inside the drop zone arms the gesture and a touch-start elsewhere near the bottom of the viewport does not.
- [x] 3.2 Verify `updateVerticalSwipeIndicator` and `handleVerticalSwipeRelease` (the dynamic drag feedback: arrow tracking, color change, progress line, and release-threshold navigation) continue to work unchanged once armed from the drop zone, confirming the existing distance/midpoint release thresholds still trigger navigation to the next chapter file.
- [x] 3.3 Confirm no next-chapter swipe gesture can be armed at all on the final chapter (no drop zone present) and that the NEXT button remains disabled there, matching existing behavior.

## 4. Regenerate and manually validate

- [x] 4.1 Run `python generate_manhwa_html.py <sample-manga-folder>` and spot-check the generated `html_output/` in a browser: toolbar hides/shows correctly on scroll, drop zone appears at the true end of chapter content (including when a last page is marked), and next-chapter swipe only starts from within the drop zone.
