# Repository Guidelines

## Project Structure & Module Organization
- Entry point: `main.py`. Core orchestration in `core/` (`base_game.py`, `module_manager.py`).
- Configuration: `config/` (`game_config.py`, `modules.json`).
- Systems live as top-level modules (e.g., `traffic_system.py`, `economic_system.py`, `visual_system.py`, `sound_effects_system.py`); see `PROJECT_STRUCTURE.md` for the planned folderization (`systems/`, `ui/`, `world/`).
- Assets: `assets/` (tiles, icons, fonts). Data: `data/` (e.g., `economy/resources.json`, saves).
- Docs: `docs/` (architecture, API). Experimental/legacy: `misc/`. Tests currently reside in `misc/tests/` and some modules include `def test_*` helpers.

## Build, Test, and Development Commands
- Run game: `python main.py`
- Install Pyxel: `pip install pyxel` (Python 3.8+ required)
- Quick tests: `pytest misc/tests -q` (if using pytest)
- Lint/format (suggested): `ruff .` / `black .` (not enforced; keep PEP 8)

## Coding Style & Naming Conventions
- Indentation: 4 spaces; follow PEP 8. Type hints encouraged.
- Files: prefer feature-based names ending with `_system.py` (e.g., `disaster_system.py`).
- Names: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Docstrings: module, class, and public function docstrings using triple quotes; keep summaries one line.
- Imports: no side effects at import time; keep Pyxel-specific code isolated to rendering modules.

## Testing Guidelines
- Location: `misc/tests/` (e.g., `test_sound_effects.py`). Name tests `test_*.py`.
- Framework: prefer `pytest`. Some modules include lightweight `def test_*()`—port these to pytest as you touch files.
- Running: `pytest misc/tests -q`. For Pyxel-dependent tests, guard with skips or dependency checks.

## Commit & Pull Request Guidelines
- Messages: conventional style — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`. Scope by module (e.g., `feat(sound): add disaster bgm`).
- PRs must include: summary, rationale, before/after notes or screenshots for UI, and steps to run (`python main.py`). Link related issues.
- Keep changes focused; update `docs/` and config when APIs or assets change. Do not commit large binaries or local saves (e.g., `savegame.dat`).

## Security & Configuration Tips
- Configuration lives in `config/`; avoid secrets in code. Respect asset licenses under `assets/`.
- Validate file paths and user inputs; prefer read-only access to `data/` at runtime where possible.
