## 1. Skill Documentation Contract

- [x] 1.1 Add the agreed first-response sentence to `SKILL.md` and state it is only used for the first user-visible reply after the Skill is invoked.
- [x] 1.2 Add a concise Python environment section requiring `python scripts/collect_ncm_profile.py --check` before collection, playlist listing, or old-run listing.
- [x] 1.3 Update the standard workflow so it uses `--playlist-index` and `--playlist-name`, and removes `--playlist-id`.
- [x] 1.4 Add the user-facing playlist table contract: show only `编号`, `歌单名`, and `曲数`.
- [x] 1.5 Add a prompt output contract requiring both prompt suitability descriptions to be copied exactly from `SKILL.md`.
- [x] 1.6 Add stage-specific reference routing for `environment.md`, `api-patterns.md`, `schemas.md`, and `troubleshooting.md`.

## 2. Playlist Selection CLI and Internals

- [x] 2.1 Add `--playlist-index` to `scripts/collect_ncm_profile.py`.
- [x] 2.2 Remove `--playlist-id` from CLI parsing, validation, diagnostics selection labels, and documented commands.
- [x] 2.3 Update playlist resolution to accept exactly one selector from `--playlist-index` or `--playlist-name`.
- [x] 2.4 Keep internal API `playlistId` resolution for `/api/v6/playlist/detail` after public number or name selection.
- [x] 2.5 Add a public playlist list shape for `--list-playlists` that exposes only `index`, `name`, and `trackCount`.
- [x] 2.6 Ensure ambiguous name matches ask for one public number or exact name without displaying `playlistId` as a user selection option.

## 3. Reference Updates

- [x] 3.1 Update `references/api-patterns.md` so the user-facing playlist choice fields are only `index`, `name`, and `trackCount`.
- [x] 3.2 Remove or rewrite reference text that suggests `playlistId`, `playCount`, `specialType`, `privacy`, `updateTime`, or `source` should be shown to users.
- [x] 3.3 Check reference docs for `--playlist-id` mentions and remove them from user-facing workflows.

## 4. Tests and Validation

- [x] 4.1 Add a unit test proving the public playlist listing output does not contain `playlistId`, `playCount`, `specialType`, `privacy`, `updateTime`, or `source`.
- [x] 4.2 Add a unit test proving `resolve_playlist` can select a playlist by public `index`.
- [x] 4.3 Add a unit test proving `SKILL.md` still contains both complete prompt suitability descriptions.
- [x] 4.4 Run `python scripts/test_ncm_profile.py`.
- [x] 4.5 Run `python scripts/collect_ncm_profile.py --check`.
- [x] 4.6 Manually inspect the updated `SKILL.md` output workflow against the agreed first-response, playlist table, and prompt suitability contracts.

## 5. Final UX Contract Updates

- [x] 5.1 Update `SKILL.md` so playlist selection uses the exact wording: `下面是你创建的歌单。主歌单会作为这次画像数据的对照基准(只能选一个喔www)。你可以回复编号或歌单名。`
- [x] 5.2 Update `SKILL.md` so successful collection output shows only the run directory before prompts, not a separate full path list for every result, CSV, aggregate, or log file.
- [x] 5.3 Update `SKILL.md` so successful collection output summarizes `aggregate/`, `result/`, `csv/`, `raw/`, and `log/` file purposes in a short folder-purpose block.
- [x] 5.4 Update `SKILL.md` so successful collection output does not expand CSV field meanings and instead tells the user they can ask AI if CSV fields are unclear.
- [x] 5.5 Ensure prompt templates still include complete file paths so the prompt remains directly copyable.
- [x] 5.6 Manually inspect the final success-response contract against the latest real collection screenshot feedback.
