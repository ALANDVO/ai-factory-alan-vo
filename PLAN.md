# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

ignore-local-artifacts

## Roadmap

### clean-flag — Add --clean flag to remove local build artifacts and state

Status: done

Acceptance:
- ai-factory --clean removes repos directory, state.json, and pushed.log
- Command reports what was removed or already clean
- No syntax warnings when running CLI

Implementation: `factory.py:clean_all function`, `factory.py:main argument parser --clean flag`

Tests: `tests/test_factory.py (existing tests pass)`

### fix-syntax-warnings — Fix SyntaxWarning invalid escape sequences in appdefs_batch3.py

Status: done

Acceptance:
- No SyntaxWarning on import of appdefs_batch3
- All triple-quoted code templates are raw strings

Implementation: `appdefs_batch3.py: first two triple-quoted strings now raw (r''')`

Tests: `python3 -W error::SyntaxWarning -c 'import appdefs_batch3' passes`

### fix-gitignore — Add .venv/ to .gitignore

Status: done

Acceptance:
- .venv/ directory excluded from git

Implementation: `.gitignore: added .venv/`

Tests: `git status shows .venv/ ignored`

### version-flag — Add --version flag to show version from VERSION file

Status: done

Acceptance:
- ai-factory --version prints version and exits
- Version read from VERSION file at project root
- Flag exits early without loading apps or logging

Implementation: `factory.py:get_version function reads VERSION file`, `factory.py:main argument parser --version flag`, `factory.py:main handles --version before any other logic`

Tests: `tests/test_factory.py::TestVersion::test_version_flag_prints_version`, `tests/test_factory.py::TestVersion::test_version_flag_exits_early`

### ignore-local-artifacts — Keep virtualenvs, databases, and dependency trees out of the publish index

Status: done

Acceptance:
- .gitignore excludes .venv, node_modules, dist, bytecode, env files, databases, egg-info, and local agent metadata
- git check-ignore matches those paths and still tracks .env.example
- The git index does not list .venv or ai_factory.egg-info

Implementation: `.gitignore`, `.env.example`, `setup_mx26.sh`

Tests: `tests/test_publish_ignore.py`

### browser-console — Browser console for catalog, dry-run, and build history

Status: in_progress

Acceptance:
- Operator can list templates, dry-run one app, and read build history from the API and UI
- Docker build uses only files inside the backend context
- Clean and cycle actions do not touch the operator home directory or GitHub unless explicitly configured
- Login is unimplemented until a later milestone

