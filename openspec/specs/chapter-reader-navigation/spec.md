## Purpose

Defines how the chapter reader page manages toolbar visibility while scrolling and how a reader advances to the next chapter via a touch-drag gesture, so long-press/scroll reading stays uncluttered while chapter-to-chapter navigation remains discoverable and reliable.

## Requirements

### Requirement: Toolbar auto-hides while scrolling down
The top toolbar (containing the TOC link, PREV/NEXT buttons, chapter title, and page counter) SHALL hide when the reader scrolls down past an initial threshold, and SHALL reappear when the reader scrolls up, on every chapter page regardless of Edit Mode state or whether a last page has been marked. When Edit Mode is enabled, the TOC button together with the Prev and Next chapter navigation buttons SHALL be hidden from the visible reader UI until Edit Mode is exited.

#### Scenario: Scrolling down hides the toolbar
- **WHEN** the reader scrolls down more than 400px from the top of the page and has moved at least 100px since the toolbar last changed visibility
- **THEN** the top toolbar SHALL animate out of view (hidden)

#### Scenario: Scrolling up reveals the toolbar
- **WHEN** the reader scrolls upward and has moved at least 100px since the toolbar last changed visibility
- **THEN** the top toolbar SHALL animate back into view (visible)

#### Scenario: Toolbar visibility updates without a page reload
- **WHEN** the chapter page is loaded and the reader scrolls or resizes the viewport
- **THEN** the toolbar visibility state SHALL be recalculated on each scroll and resize event without requiring a page reload

#### Scenario: Edit Mode hides TOC and chapter navigation controls
- **WHEN** the reader enters Edit Mode
- **THEN** the TOC button and the Prev/Next navigation buttons SHALL be hidden from the active chapter reader UI

#### Scenario: Exiting Edit Mode restores navigation controls
- **WHEN** the reader exits Edit Mode
- **THEN** the TOC button and the Prev/Next navigation buttons SHALL reappear in the normal reader UI state

### Requirement: Next-chapter drop zone at the end of chapter content
Each chapter page, except the last chapter in the story, SHALL render a next-chapter drop zone element after all page images in the chapter, including any page images hidden because they are beyond the chapter's marked last page. The drop zone SHALL have a black background, a height equal to 30% of the viewport height, and SHALL always display a downward-arrow-in-circle indicator at its bottom.

#### Scenario: Drop zone present for chapters with a next chapter
- **WHEN** a chapter page is rendered and a next (non-hidden) chapter exists
- **THEN** the drop zone element SHALL appear after the last page image (including any pages hidden by the "beyond last page" marker), with a black background, height equal to 30% of the viewport height, and a visible downward-arrow-in-circle indicator at its bottom

#### Scenario: No drop zone on the final chapter
- **WHEN** a chapter page is rendered and there is no next (non-hidden) chapter to navigate to
- **THEN** the drop zone element SHALL NOT be rendered, or SHALL be rendered without an active gesture affordance, consistent with the NEXT button being disabled

### Requirement: Next-chapter swipe gesture must start inside the drop zone
The touch-drag gesture that navigates to the next chapter SHALL only be armed (begin tracking a potential navigation swipe) when the touch-start point falls within the next-chapter drop zone element's on-screen bounding box. Touch-starts outside the drop zone SHALL NOT trigger next-chapter navigation tracking, regardless of scroll position.

#### Scenario: Touch starts inside the drop zone
- **WHEN** the reader places a touch-start point within the drop zone element's bounding box and a next chapter exists
- **THEN** the system SHALL begin tracking a vertical swipe gesture for next-chapter navigation

#### Scenario: Touch starts outside the drop zone
- **WHEN** the reader places a touch-start point outside the drop zone element's bounding box (even if near the bottom of the viewport)
- **THEN** the system SHALL NOT begin tracking a next-chapter navigation swipe gesture

#### Scenario: Completing the swipe navigates to the next chapter
- **WHEN** a next-chapter swipe gesture was armed by a touch-start inside the drop zone, and the reader drags upward far enough to pass the existing activation distance/midpoint thresholds before releasing
- **THEN** the reader SHALL be navigated to the next chapter's page, matching the existing release-threshold behavior

#### Scenario: Releasing before threshold cancels navigation
- **WHEN** a next-chapter swipe gesture was armed by a touch-start inside the drop zone, but the reader releases the touch before reaching the activation distance/midpoint thresholds
- **THEN** the reader SHALL remain on the current chapter page and the swipe indicator SHALL be cleared

### Requirement: Reader hides pages before the marked first page outside Edit Mode

The chapter reader SHALL hide all pages whose page number is lower than the chapter's marked first-page value whenever a first-page marker is set and Edit Mode is not enabled. While Edit Mode is enabled, the reader SHALL still render those pages in a muted state so the cutoff remains visible and editable without requiring the user to leave editing mode.

#### Scenario: First-page cutoff hides earlier pages
- **WHEN** a chapter has a first-page marker set to page 3
- **THEN** pages 1 and 2 SHALL be hidden from the normal reader view

#### Scenario: Edit Mode reveals the cutoff range for editing
- **WHEN** Edit Mode is enabled on a chapter with a first-page marker
- **THEN** the reader SHALL display earlier pages in a muted but visible state so the user can adjust the first-page selection

#### Scenario: Toggling off the first-page marker clears the cutoff
- **WHEN** a user selects the same page that is currently marked as the chapter's first page
- **THEN** the first-page marker SHALL be cleared and the full chapter SHALL become visible again outside Edit Mode
