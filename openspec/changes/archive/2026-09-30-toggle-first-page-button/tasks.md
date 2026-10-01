## 1. Chapter state persistence

- [x] 1.1 Extend the chapter-state persistence layer to store a first-page marker keyed by the parent story and chapter, and verify that same-named chapters in different stories remain independent.
- [x] 1.2 Add the clear-on-toggle behavior for a first-page marker and verify that re-selecting the same page clears the marker without affecting the last-page state.

## 2. Reader UI and page visibility

- [x] 2.1 Add a per-page "Set as First Page" control to the generated chapter HTML and verify the button appears alongside the existing last-page control.
- [x] 2.2 Update the chapter reader state logic to load, toggle, and label the first-page marker, and confirm the UI toggles between "Set as First Page" and "Unset First Page".
- [x] 2.3 Update page visibility rules so pages before the marked first page are hidden outside Edit Mode while remaining visible and muted during Edit Mode; verify that the cutoff is editable without leaving edit mode.
- [x] 2.4 Run a regression check on the existing last-page behavior and Edit Mode chapter navigation controls to confirm they remain unchanged while the new first-page workflow works.
