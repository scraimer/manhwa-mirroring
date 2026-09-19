# chapter-state-persistence Specification

## Purpose
Provides story-scoped persistence for chapter visibility and reading position so
identically named chapters in different stories never share state.

## Requirements

### Requirement: Chapter state identity includes the parent story directory

The system SHALL identify persisted chapter state with both the parent story directory name and the chapter directory name. A request missing either component SHALL be rejected as invalid input.

#### Scenario: Same chapter name in different stories remains independent

- **WHEN** state is written for `Story Alpha` and `Chapter001`, and separately for `Story Beta` and `Chapter001`
- **THEN** each story-and-chapter pair SHALL retain and return its own hidden and last-page state without overwriting the other pair

#### Scenario: Missing story identity is rejected

- **WHEN** a hidden-state or last-page request omits the parent story directory name or chapter name
- **THEN** the endpoint SHALL return a client error and SHALL NOT create or modify chapter state

### Requirement: Hidden chapter state is scoped by story and chapter

The hidden-chapter endpoint SHALL read, write, and list hidden records using the parent story directory name together with the chapter directory name. Hidden-state responses SHALL identify both values.

#### Scenario: Hide and unhide a chapter within a story

- **WHEN** a client sets or clears hidden state for a story-and-chapter pair
- **THEN** subsequent hidden-state reads for that pair SHALL reflect the requested value and records for other stories SHALL remain unchanged

#### Scenario: List hidden chapters for a story

- **WHEN** a client requests hidden chapters for a parent story directory
- **THEN** the response SHALL contain only hidden chapters belonging to that story, with both story and chapter identity included for each result

### Requirement: Last-page state is scoped by story and chapter

The last-page endpoint SHALL read, write, and toggle the last-page marker using the parent story directory name together with the chapter directory name.

#### Scenario: Read and set an independent last-page marker

- **WHEN** a client reads or sets a last-page marker for a story-and-chapter pair
- **THEN** the returned marker SHALL belong only to that pair and SHALL not affect a chapter with the same name in another story

#### Scenario: Toggle a last-page marker off

- **WHEN** a client sets the same page as the current marker for a story-and-chapter pair
- **THEN** the marker for that pair SHALL be cleared while all other story-and-chapter markers remain unchanged

### Requirement: Existing persisted state is handled without accidental cross-story attribution

The system SHALL preserve existing state only when its story identity can be established unambiguously, and SHALL NOT guess a parent story for legacy chapter-only records. Any legacy records that cannot be attributed SHALL be excluded from story-scoped results or surfaced for explicit migration handling without being assigned to a different story.

#### Scenario: Legacy record has no unambiguous story

- **WHEN** the state database contains a chapter-only record from before story-scoped identity was available
- **THEN** the system SHALL NOT expose that record as belonging to an arbitrary story and SHALL continue serving new story-scoped records normally
