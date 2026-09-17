# Request Flow API

A small workflow backend for tracking service requests through a clear lifecycle.

It demonstrates API design, validation, persistence, status transitions, and automated tests without requiring external services.

## Features

- FastAPI
- SQLite persistence
- Request lifecycle validation
- Request history
- Filtering by status
- Pydantic schemas
- Tests
- Docker
- GitHub Actions

## Status flow

```text
NEW -> IN_PROGRESS -> RESOLVED -> CLOSED
  \\        |
   \\       v
    ----> CANCELLED
```

Invalid transitions return HTTP `409 Conflict`.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Docs: `http://127.0.0.1:8000/docs`

## API examples

Create a request:

```bash
curl -X POST http://127.0.0.1:8000/requests \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Cannot access LMS\",\"description\":\"Login fails after password change\"}"
```

Update status:

```bash
curl -X PATCH http://127.0.0.1:8000/requests/1/status \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"IN_PROGRESS\"}"
```

Get request history:

```bash
curl http://127.0.0.1:8000/requests/1/history
```

## Project structure

```text
app/
  db.py
  main.py
  schemas.py
  workflow.py
tests/
  test_requests.py
```

## Engineering ideas demonstrated

- deterministic workflow rules
- server-side validation
- persistence separated from API schemas
- audit-style history
- API-level tests

## Roadmap

- [ ] PostgreSQL
- [ ] JWT authentication
- [ ] Role-based access
- [ ] SLA tracking
- [ ] Webhooks
- [ ] Admin dashboard

## License

MIT
