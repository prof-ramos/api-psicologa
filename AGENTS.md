# Agent Guidelines for Astrologer API

## Build, Lint, and Test Commands
- **Run all tests**: `uv run pytest` or `pipenv run test`
- **Run single test**: `pytest tests/test_main.py::test_status` (replace with specific test function)
- **Type checking**: `pipenv run quality` (runs mypy)
- **Code formatting**: `pipenv run format` (runs black with line length 200)
- **Development server**: `pipenv run dev` ou `uv run flask --app app.main:create_app --reload`

## Code Style Guidelines
- **Formatting**: 4-space indentation, max line length 120 (.editorconfig), black formatting
- **Imports**: Standard library → third-party → local imports (blank lines between groups)
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type annotations with Pydantic models; prefer Union over Optional
- **Error handling**: Return structured JSON responses with "status": "OK"/"KO" pattern
- **Logging**: Use logging.getLogger(__name__) with proper configuration
- **Docstrings**: Include module-level and function docstrings following Google style
- **Validation**: Use Pydantic field validators for input validation with descriptive error messages
- **Security**: Never log or expose secrets; use environment variables for sensitive config

## Linting Tools
- **ruff**: Fast Python linting and formatting
- **flake8**: Style guide enforcement
- **mypy**: Static type checking (ignore missing imports in dev)

## Testing Guidelines
- Tests usam pytest com o `FlaskClient` (`app.test_client()`)
- Mirror module structure with `test_*.py` files
- Include docstrings for test functions
- Test API endpoints with realistic data and assert both status codes and response structure

## Key Principles
- Prioritize concise, technical responses with accurate Python examples and the RORO pattern.
- Favor functional, declarative programming; avoid introducing classes when a function works.
- Prefer iteration and modularization instead of duplicating logic.
- Use descriptive variable names with auxiliary verbs such as `is_active` and `has_permission`.
- Keep directory and file names lowercase with underscores (for example, `routers/user_routes.py`).
- Export named routes and utilities to make dependencies explicit.
- Interaja com o usuário exclusivamente em português do Brasil.

## Python and WSGI Conventions
- Declare handlers HTTP síncronos com `def`; utilize corrotinas apenas quando integrar bibliotecas compatíveis com Flask assíncrono.
- Annotate every function signature; rely on Pydantic models over raw dictionaries for validation.
- Organize modules into routers, sub-routes, utilities, static content, and types.
- Mantenha condicionais enxutas seguindo `if condition: do_something()` quando melhora a legibilidade.
- Utilize blueprints e middlewares WSGI para compartilhar estado e configurar fluxos globais.

## Error Handling and Validation
- Guard against invalid states at the top of functions with early returns and guard clauses.
- Return structured JSON with a `status` key set to `"OK"` or `"KO"` for predictable clients.
- Utilize `flask.abort` ou exceções de `werkzeug.exceptions` para erros esperados e middlewares/handlers globais para falhas inesperadas.
- Use descriptive Pydantic field validators to communicate validation errors clearly.
- Never log or expose secrets; rely on environment variables for sensitive data.

## Performance Considerations
- Use chamadas síncronas por padrão e delegue tarefas pesadas para jobs/background quando necessário.
- Cache static or frequently accessed payloads when it helps response latency.
- Optimize Pydantic serialization/deserialization paths for large payloads and avoid redundant work.
- Use lazy loading or pagination for large data sets to keep response sizes manageable.
- Monitor response time, latency, and throughput when assessing API changes.
