## 1. Define Shared Identity and Schema Migration

- [x] 1.1 Identify every in-repository caller of `hide_chapter.py` and `last_page.py`, document the current request/response contract, and verify the caller inventory covers generated reader and server workflows
- [x] 1.2 Implement shared story-and-chapter validation and schema initialization, including a composite `(story, chapter)` key and a non-active quarantine path for legacy chapter-only rows; verify initialization succeeds when invoked from either CGI endpoint
- [x] 1.3 Add migration checks for existing databases and verify legacy rows are never assigned to an arbitrary story or returned in story-scoped results

## 2. Update Hidden-Chapter Endpoint

- [x] 2.1 Require and validate the parent story directory name with each hide/unhide request, then read and write state by `(story, chapter)`; verify same-named chapters in two stories remain independent
- [x] 2.2 Add story filtering to hidden-chapter listing and include both story and chapter identity in each response; verify a story listing excludes hidden chapters from other stories
- [x] 2.3 Preserve hidden-state timestamps and current hide/unhide semantics while updating invalid-input responses; verify missing story or chapter produces a client error without mutation

## 3. Update Last-Page Endpoint

- [x] 3.1 Require and validate the parent story directory name for GET and write requests, then query and mutate last-page state by `(story, chapter)`; verify same-named chapters in two stories have independent markers
- [x] 3.2 Preserve toggle behavior that clears a marker when the same page is submitted; verify clearing one story-and-chapter pair does not alter another pair
- [x] 3.3 Return the expanded story-and-chapter identity in last-page responses and preserve existing invalid-page handling; verify malformed identity and page inputs produce client errors without mutation

## 4. Integrate Callers and Verify Deployment Behavior

- [x] 4.1 Update all repository callers to send the parent story directory name and consume the expanded response fields; verify generated reader and server workflows use the new contract
- [x] 4.2 Add focused endpoint/integration tests using a temporary SQLite database, including schema initialization through either endpoint, duplicate chapter names across stories, hidden listing, last-page get/set/toggle, and legacy quarantine; verify the test suite passes
- [x] 4.3 Run the documented Python validation or test command and manually exercise the deployed CGI endpoints with two stories containing the same chapter name; verify no cross-story state leakage occurs
