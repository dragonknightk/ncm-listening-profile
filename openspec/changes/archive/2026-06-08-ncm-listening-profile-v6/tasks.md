## 1. Environment Layer

- [x] 1.1 Replace Windows-only `cloudmusic.exe` helpers with a cross-platform NetEase Cloud Music client abstraction in `scripts/ncm_env.py`.
- [x] 1.2 Implement Windows client discovery for `cloudmusic.exe` using explicit `--client-path`, `NCM_CLIENT_PATH`, registry entries, uninstall entries, and common install paths.
- [x] 1.3 Implement macOS client discovery for `NeteaseMusic.app` using explicit `--client-path`, `NCM_CLIENT_PATH`, `/Applications/NeteaseMusic.app`, and `~/Applications/NeteaseMusic.app`.
- [x] 1.4 Implement Windows and macOS running-process detection, including `cloudmusic.exe`, `NeteaseMusic`, and `NeteaseMusic Helper`.
- [x] 1.5 Implement platform-specific launch commands while preserving fixed CDP port `9222`.
- [x] 1.6 Return clear unsupported-platform, missing-client, multiple-client, running-client, and port-conflict errors with platform-appropriate wording.

## 2. Collector Integration

- [x] 2.1 Replace `--cloudmusic-exe` with `--client-path` in `scripts/collect_ncm_profile.py`.
- [x] 2.2 Replace `cloudmusicExe` diagnostics metadata with platform-neutral fields such as `clientPath`, `clientPlatform`, and launch mode.
- [x] 2.3 Keep CDP target selection, page-context API requests, result shaping, aggregate generation, output layout, and privacy boundaries unchanged.
- [x] 2.4 Ensure dependency checks use the active `Python 3.10+` interpreter and document `python` / `python3` platform usage where commands are shown.

## 3. Tests

- [x] 3.1 Update unit tests for Windows client path discovery, process detection, launch command construction, and port conflict handling.
- [x] 3.2 Add unit tests for macOS app discovery, process detection, launch command construction, unsupported platform handling, and explicit `--client-path` validation.
- [x] 3.3 Update diagnostics tests for platform-neutral client environment fields.
- [x] 3.4 Run the local test suite on Windows and fix any regressions.

## 4. Documentation

- [x] 4.1 Update `SKILL.md` to describe Windows + macOS support, new `--client-path` usage, platform-specific launch rules, and the verified environment matrix.
- [x] 4.2 Update `README.md` and `README.en.md` to remove Windows-only wording and explain the CDP/page-context/API compatibility model.
- [x] 4.3 Update `references/environment.md` with Windows and macOS discovery, process, launch, port, and Python command guidance.
- [x] 4.4 Update `references/api-patterns.md`, `references/troubleshooting.md`, and `references/schemas.md` to remove stale Windows-only assumptions and document platform-neutral diagnostics fields.

## 5. Real-Environment Validation

- [x] 5.1 Validate Windows still passes dependency checks, playlist listing, and collection with the updated CLI and diagnostics fields.
- [x] 5.2 Sync the updated Skill to the Mac test machine over SSH and validate macOS automatic launch, playlist listing, and collection.
- [x] 5.3 Confirm the macOS run writes `raw/`, `result/`, `csv/`, `aggregate/`, and `log/` with non-empty primary/all-time data and privacy-preserving diagnostics.
- [x] 5.4 Record the final verified Windows and macOS environment wording in the user-facing docs.
