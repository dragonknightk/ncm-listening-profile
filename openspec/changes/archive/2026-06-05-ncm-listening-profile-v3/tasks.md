## 1. API Collector Architecture

- [x] 1.1 Create an API-only collector module for page-context `fetch` calls and JSON shape validation.
- [x] 1.2 Implement allowed API request helpers for `/api/nuser/account/get`, `/api/user/playlist`, `/api/v6/playlist/detail`, and `/api/v1/play/record`.
- [x] 1.3 Add API failure handling for unsafe statuses, non-200 API codes, JSON parse failures, missing required fields, and zero-row datasets.
- [x] 1.4 Ensure Python code only contacts local CDP endpoints and never directly requests NetEase Cloud Music business APIs.

## 2. Remove DOM and Cache Collection Paths

- [x] 2.1 Delete DOM playlist listing, playlist opening, play-all clicking, primary playlist row extraction, ranking page opening, ranking tab selection, ranking row extraction, and DOM scroll-loop code.
- [x] 2.2 Delete DOM selector repair hints, DOM strategy names, and DOM-specific diagnostics fields.
- [x] 2.3 Remove `playingList` cache discovery, cache joins, cache status shaping, and local cache dependency from collection.
- [x] 2.4 Remove or rewrite tests that assert DOM extraction, DOM fallback, visible-duration parsing, or cache join behavior.

## 3. API Data Shaping

- [x] 3.1 Rewrite user-created playlist listing to use current-user API plus `/api/user/playlist`, filtering by `userId == current uid` and `subscribed == false`.
- [x] 3.2 Rewrite primary playlist collection to shape result rows from `/api/v6/playlist/detail` `tracks[]` and `trackIds[]`.
- [x] 3.3 Rewrite recent-week ranking collection to shape result rows from `/api/v1/play/record?type=1` `weekData[]`.
- [x] 3.4 Rewrite all-time ranking collection to shape result rows from `/api/v1/play/record?type=0` `allData[]`.
- [x] 3.5 Keep result and CSV field sets exactly compatible with v2.
- [x] 3.6 Format primary playlist `duration` from API millisecond duration and emit API duration as `durationMs`.
- [x] 3.7 Preserve special or invisible-character song titles from API data without treating them as empty rows.

## 4. Raw, Aggregate, and Output Layout

- [x] 4.1 Rewrite raw rows to contain source `api` and agreed song, artist, album, duration, joined-at, rank, play-count, and optional score fields.
- [x] 4.2 Add tests proving raw excludes `creator`, `subscribers`, `privileges`, `coverImgUrl`, `recommendInfo`, complete API responses, cookies, tokens, headers, and request bodies.
- [x] 4.3 Ensure `/api/user/playlist` is used only for user selection and does not create `raw/user_playlists.jsonl`.
- [x] 4.4 Add `aggregate/aggregate.json` output directory and update expected successful run file assertions.
- [x] 4.5 Implement aggregate counts, duration statistics, added-at distributions, ranking concentration metrics, overlap metrics, artist/album indexes, text statistics, and sample indexes.
- [x] 4.6 Name aggregate top, bottom, earliest, latest, overlap, and sample fields with explicit count and ordering rules.

## 5. Diagnostics and Listing Old Runs

- [x] 5.1 Update diagnostics schema version, skill version, phase names, repair hints, and quality counters for API-only collection.
- [x] 5.2 Record API paths, statuses, response shapes, row counts, and field completeness without sensitive payloads.
- [x] 5.3 Add diagnostics for current-user, playlist-listing, primary-playlist, recent-week ranking, all-time ranking, result-shaping, aggregate, output-writing, and validation phases.
- [x] 5.4 Update previous-run listing and final success JSON to include `aggregate/aggregate.json` when present.

## 6. Skill Documentation and Prompts

- [x] 6.1 Rewrite `SKILL.md` standard workflow around API-only collection and remove DOM, selector, playingList, and DOM repair instructions.
- [x] 6.2 Update output layout, file usage, result/csv fields, raw boundaries, aggregate boundaries, and diagnostics documentation.
- [x] 6.3 Update the minimal prompt to include `aggregate/aggregate.json` plus the three result JSONL paths exactly as agreed.
- [x] 6.4 Update the guided prompt with the agreed warm wording and no cold reading-procedure list.
- [x] 6.5 Add the agreed suitability text after each prompt without using the phrase "新会话".
- [x] 6.6 Rewrite or delete reference docs so no DOM collector, DOM fallback, DOM selector, or playingList cache path remains.

## 7. Validation

- [x] 7.1 Add unit tests for API response shaping using fixture-style dictionaries.
- [x] 7.2 Add unit tests for API failure diagnostics and no-DOM-fallback behavior.
- [x] 7.3 Add unit tests for aggregate metric calculations and field naming conventions.
- [x] 7.4 Run `python scripts/test_ncm_profile.py`.
- [x] 7.5 Run `python scripts/collect_ncm_profile.py --check`.
- [x] 7.6 Validate playlist listing against the real local NetEase Cloud Music client.
- [x] 7.7 Validate a full API-only collection against the real local NetEase Cloud Music client.
- [x] 7.8 Document the verified v3 client version/build/patch in Skill docs or references.
