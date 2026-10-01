## MODIFIED Requirements

### Requirement: First-page state is scoped by story and chapter

The first-page marker SHALL be persisted using the same parent-story and chapter identifiers as the existing last-page marker. A request missing either value SHALL be rejected as invalid input, and the marker SHALL NOT overwrite state for another story/chapter pair.

#### Scenario: Same chapter names in different stories remain independent
- **WHEN** two stories each contain a chapter named `Chapter001` and each sets a different first-page marker
- **THEN** each story-and-chapter pair SHALL retain and return its own first-page state without overwriting the other pair

#### Scenario: Missing story identity is rejected
- **WHEN** a first-page request omits the parent story directory name or chapter name
- **THEN** the endpoint SHALL return a client error and SHALL NOT create or modify the chapter state

#### Scenario: Toggling the same first page off clears the marker
- **WHEN** a client sends the same page as the current first-page marker for a story-and-chapter pair
- **THEN** the first-page marker for that pair SHALL be cleared while all other story-and-chapter markers remain unchanged
