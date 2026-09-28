# Monster Display — Modularized

## Modules

- `config.py`: defaults, config loading, password functions
- `runtime.py`: explicit mutable runtime context
- `state.py`: persistence, normalization, setup storage helpers
- `battle.py`: combat-domain helpers
- `importers.py`: `.monster` and CSV parsing
- `media.py`: upload storage and D&D Beyond image lookup
- `auth.py`: cookie/session authorization dependency
- `schemas.py`: HTTP request schemas
- `routes.py`: FastAPI endpoint orchestration
- `app.py`: public application entry point
- `templates/`: independently maintained UI documents

The legacy route file is deliberately separated from the application entry point to make route extraction incremental and avoid a behavior-changing rewrite. New work should target the domain modules, then shrink `routes.py` endpoint by endpoint.
