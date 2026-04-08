# Repository Guidelines

## Project Structure & Module Organization
`gestion_horarios/` contains the Django project settings, ASGI/WSGI entrypoints, and root URLs. Business logic is split into app folders such as `accounts/`, `planes/`, `grupos/`, `horarios/`, and `periodos/`; keep models, views, forms, serializers, and `tests.py` inside the app they belong to. Shared templates live in `templates/`, static assets in `static/`, seed data in `planes/data/`, and custom management commands under `*/management/commands/`.

## Build, Test, and Development Commands
Create a virtual environment, then install dependencies with `pip install -r requirements.txt`.

- `python manage.py migrate`: apply database migrations.
- `python manage.py runserver`: start the local development server.
- `python manage.py test`: run the full Django test suite.
- `python manage.py collectstatic`: gather static files for production builds.
- `python manage.py cargar_facultades` or `python manage.py cargar_plan`: load bundled reference data when setting up a fresh database.

The default database is SQLite (`db.sqlite3`) unless `DATABASE_URL` is set.

## Coding Style & Naming Conventions
Follow standard Django and PEP 8 conventions: 4-space indentation, snake_case for functions, variables, and module names, and PascalCase for models, forms, and serializers. Keep each change scoped to the relevant app. Prefer class-based or function-based views consistent with nearby code, and match existing Spanish domain terminology in model and field names.

No formatter or linter is configured in this repository, so contributors should self-check imports, line length, and readability before opening a PR.

## Testing Guidelines
Tests use Django’s built-in `TestCase` and are currently organized per app in `tests.py`. Name test methods by behavior, for example `test_crea_grupo_con_periodo_activo`. Add regression coverage for model rules, imports/exports, and authenticated views whenever you change them.

Run focused tests with `python manage.py test grupos` and run the full suite before submitting.

## Commit & Pull Request Guidelines
Recent history uses short, imperative Spanish summaries such as `Correccion generales de bugs y mejoras varias` and `Mejora al importar grupos`. Keep commit messages concise, specific, and action-oriented.

Pull requests should include a brief problem statement, a summary of the solution, any required migration or seed-data steps, and screenshots when templates or static UI files change. Link the related issue or task when available.

## Security & Configuration Tips
Use environment variables for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `DATABASE_URL`; do not commit real secrets. Review CORS and authentication changes carefully because the project exposes both session and token-based endpoints.
