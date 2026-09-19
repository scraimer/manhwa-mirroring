## 1. Update Edit Mode UI state

- [x] 1.1 Update the chapter reader state so Edit Mode toggles a dedicated hidden-state for the TOC button together with the Prev/Next controls and verify that the DOM state changes when the edit toggle is clicked.
- [x] 1.2 Ensure the TOC button and the Prev/Next navigation links are hidden while Edit Mode is active and restored when Edit Mode is exited, verifying the control visibility changes without reloading the page.

## 2. Validate the reader experience

- [x] 2.1 Run the generator against a sample story and open a generated chapter page in a browser to verify that Edit Mode hides the TOC button and Prev/Next controls while the editing controls remain visible.
- [x] 2.2 Verify that leaving Edit Mode restores the normal TOC and Prev/Next navigation behavior and does not affect unrelated reader functions such as scrolling and chapter selection.
