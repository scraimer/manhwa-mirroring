## MODIFIED Requirements

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
