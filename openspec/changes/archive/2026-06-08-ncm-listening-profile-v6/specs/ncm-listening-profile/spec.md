## ADDED Requirements

### Requirement: Desktop client support covers Windows and macOS
The Skill SHALL support local NetEase Cloud Music desktop client collection on Windows and macOS by launching the platform-native client with CDP port `9222`.

#### Scenario: Windows desktop client is supported
- **WHEN** the Skill runs on Windows and finds a unique NetEase Cloud Music desktop executable
- **THEN** it launches that `cloudmusic.exe` with `--force-renderer-accessibility=complete` and `--remote-debugging-port=9222`

#### Scenario: macOS desktop client is supported
- **WHEN** the Skill runs on macOS and finds a unique `NeteaseMusic.app`
- **THEN** it launches that app with `open -na <NeteaseMusic.app> --args --force-renderer-accessibility=complete --remote-debugging-port=9222`

#### Scenario: Unsupported platform is used
- **WHEN** the Skill runs on a platform other than Windows or macOS
- **THEN** it fails before client launch with a clear unsupported-platform message

#### Scenario: Shared API collection is used after launch
- **WHEN** either Windows or macOS client launch exposes CDP on `127.0.0.1:9222`
- **THEN** the Skill uses the same CDP target selection, page-context API fetches, result shaping, aggregate generation, and output writing behavior

### Requirement: Verified environments are documented
The Skill SHALL document verified environments as a matrix of real collection successes instead of treating one client version as the only supported environment.

#### Scenario: Windows verified environments are documented
- **WHEN** a user reads the Skill or README environment section
- **THEN** it states that Windows has been verified on Windows 10 with `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`, and on higher Windows systems with newer NetEase Cloud Music desktop clients through real collection runs

#### Scenario: macOS verified environment is documented
- **WHEN** a user reads the Skill or README environment section
- **THEN** it states that macOS has been verified on `macOS 26.3.1 arm64` with `NeteaseMusicDesktop/3.1.7.3283` through a real collection run

#### Scenario: Compatibility explanation is documented
- **WHEN** a user reads environment or troubleshooting documentation
- **THEN** it explains that data compatibility primarily depends on the NetEase server API response shape, while operating system and client versions mainly affect client launch, CDP exposure, login state, and page-context execution

## MODIFIED Requirements

### Requirement: Python environment is checked before Skill operations
The Skill SHALL check the active Python runtime and required packages before collecting data, listing playlists, or reading existing runs.

#### Scenario: Any operation starts
- **WHEN** the Skill is about to collect data, list playlists, or list existing output runs
- **THEN** it first runs `scripts/collect_ncm_profile.py --check` with the active `Python 3.10+` interpreter from the Skill root

#### Scenario: Dependency check fails
- **WHEN** the dependency check reports missing Python packages
- **THEN** the Skill tells the user to install dependencies with the same active Python interpreter, using `python -m pip install -r scripts/requirements.txt` or `python3 -m pip install -r scripts/requirements.txt` as appropriate for the platform

#### Scenario: Python requirements are documented
- **WHEN** an agent reads `SKILL.md`
- **THEN** it documents that the scripts require `Python 3.10+`, `psutil`, `requests`, and `websocket-client`

### Requirement: Existing NetEase Cloud Music process requires a user choice
The Skill SHALL stop when a NetEase Cloud Music desktop client is already running before Skill launch and SHALL ask the user whether to recollect or use an existing output run.

#### Scenario: User chooses recollect
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user chooses to recollect
- **THEN** the Skill asks the user to close NetEase Cloud Music manually before running collection again

#### Scenario: User chooses old data
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user chooses to use old data
- **THEN** the Skill does not launch or attach to the existing client and instead reports available prior output runs or asks the user which prior run to use

#### Scenario: No choice has been made
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user has not chosen recollect or old data
- **THEN** the Skill MUST NOT analyze existing outputs or start a new collection

#### Scenario: Windows client process is detected
- **WHEN** the Skill runs on Windows and detects `cloudmusic.exe`
- **THEN** it treats NetEase Cloud Music as already running and reports the detected PID and executable path when available

#### Scenario: macOS client process is detected
- **WHEN** the Skill runs on macOS and detects `NeteaseMusic` or `NeteaseMusic Helper`
- **THEN** it treats NetEase Cloud Music as already running and reports the detected PID and executable path when available

### Requirement: Executable discovery requires a unique path
The Skill SHALL use a unique NetEase Cloud Music desktop client path before launching the client.

#### Scenario: One Windows executable path is found
- **WHEN** the Skill runs on Windows and discovery finds exactly one `cloudmusic.exe` candidate
- **THEN** the Skill uses that executable path

#### Scenario: One macOS app path is found
- **WHEN** the Skill runs on macOS and discovery finds exactly one `NeteaseMusic.app` candidate
- **THEN** the Skill uses that app path

#### Scenario: Explicit client path is provided
- **WHEN** the user or agent provides `--client-path` or `NCM_CLIENT_PATH`
- **THEN** the Skill validates that path as the platform's NetEase Cloud Music desktop client path before launching

#### Scenario: No client path is found
- **WHEN** executable discovery finds no NetEase Cloud Music desktop client candidate
- **THEN** the Skill asks the user to provide the NetEase Cloud Music desktop client path with `--client-path`

#### Scenario: Multiple client paths are found
- **WHEN** executable discovery finds multiple NetEase Cloud Music desktop client candidates
- **THEN** the Skill asks the user to choose which client path to use and pass it with `--client-path`
