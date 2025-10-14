# Repository Guidelines

## Project Structure & Module Organization
- `app/app.py` holds the Flask + Socket.IO server, HTTP routes, agent orchestration, and the EXE packaging endpoint.
- `app/agents.py` defines the `paperai` and `chater` agents using `agno` plus DeepSeek models; update instructions here when adding tools.
- `app/templates/` and `app/static/` contain the single-page chat UI, JavaScript streaming client, and CSS assets.
- `app/traitRecognizePackager.py` is the interactive baseline script that the backend rewrites for PyInstaller builds.
- `tests/` contains `pytest` suites and packaging fixtures (see `tests/traitRecognize/` for sample assets).

## Build, Test, and Development Commands
- `pip install -r requirements.txt` — install runtime and tooling dependencies.
- `python app/app.py` — launch the development server on `127.0.0.1:8080`.
- `pytest` — run all automated tests; use `pytest tests/test_app.py::test_index_route` for focused runs.
- `python -m PyInstaller app/traitRecognizePackager.py --onefile` — manual packaging check mirroring the `/generate_exe` workflow.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation; prefer descriptive snake_case for functions and variables.
- Flask routes use lower-case, hyphen-free endpoints; Socket.IO events use snake_case (`send_message`, `stop_generation`).
- Keep agent IDs (`paperai`, `chater`) consistent across backend and front-end selectors.
- Document non-obvious control flow with concise comments; avoid inline prints in production paths.

## Testing Guidelines
- Use `pytest` fixtures (see `tests/test_app.py`) for Flask clients; name tests `test_<feature>_<expectation>`.
- Add regression assets under `tests/traitRecognize/` when validating packaging or vision pipelines.
- Aim to cover new routes, background tasks, and error branches; prefer streaming-friendly unit tests over full end-to-end runs.

## Commit & Pull Request Guidelines
- Start commit summaries with a concise verb (“Add”, “Fix”, “Refactor”); keep body lines under 72 characters.
- Reference related issues in the footer (`Refs #123`) and note environment variables or migrations.
- Pull requests should include: purpose statement, testing evidence (`pytest` output or screenshots), and rollout considerations (API keys, PyInstaller requirements).
- Coordinate agent changes: highlight new external dependencies, model IDs, or configuration switches that contributors must adopt.

## Security & Configuration Tips
- Never commit secrets; load `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, and `FLASK_SECRET_KEY` via environment variables or `.env` ignored by Git.
- `/generate_exe` enforces upload caps; adjust `MAX_REQUEST_BYTES`, `MAX_TRAIT_IMAGE_BASE64`, `MAX_WORKSPACE_FILE_BASE64`, and `MAX_TOTAL_WORKSPACE_BASE64` if larger artifacts are required, and document the change in PRs.
- PyInstaller now runs inside a thread-pool with `PACKAGER_CONCURRENCY` workers and `PYINSTALLER_TIMEOUT_SEC` timeout—raise these carefully and monitor resource usage.
- When testing `/generate_exe`, ensure temporary directories are cleaned and PyInstaller is available locally.
- Review third-party API limits before enabling long-running background tasks in shared environments.
