# Support Ticket API

A simple FastAPI-based support ticket management API backed by in-memory storage.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Interactive docs available at: http://127.0.0.1:8000/docs

## API Routes

| Method   | Path                       | Description        |
|----------|----------------------------|--------------------|
| `POST`   | `/tickets`                 | Create a ticket    |
| `GET`    | `/tickets`                 | List all tickets   |
| `GET`    | `/tickets/{id}`            | Get one ticket     |
| `PATCH`  | `/tickets/{id}/status`     | Update status only |
| `DELETE` | `/tickets/{id}`            | Delete a ticket    |

## Status Transitions

```
open  →  in_progress  →  resolved
```

All other transitions return **422**.

## Run Tests

```bash
py -m pytest tests/ -v
```

## Actual Test Results

```
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 17 items

tests/test_tickets.py::test_create_ticket_returns_201_and_status_open PASSED         [  5%]
tests/test_tickets.py::test_create_ticket_invalid_email_returns_422 PASSED           [ 11%]
tests/test_tickets.py::test_create_ticket_missing_field_returns_422 PASSED           [ 17%]
tests/test_tickets.py::test_list_tickets_returns_200_and_array PASSED                [ 23%]
tests/test_tickets.py::test_get_existing_ticket_returns_200 PASSED                   [ 29%]
tests/test_tickets.py::test_get_nonexistent_ticket_returns_404 PASSED                [ 35%]
tests/test_tickets.py::test_transition_open_to_in_progress_returns_200 PASSED       [ 41%]
tests/test_tickets.py::test_transition_in_progress_to_resolved_returns_200 PASSED   [ 47%]
tests/test_tickets.py::test_transition_resolved_to_open_returns_422 PASSED           [ 52%]
tests/test_tickets.py::test_transition_open_to_resolved_skip_returns_422 PASSED     [ 58%]
tests/test_tickets.py::test_transition_in_progress_to_open_returns_422 PASSED       [ 64%]
tests/test_tickets.py::test_transition_open_to_open_same_state_returns_422 PASSED   [ 70%]
tests/test_tickets.py::test_patch_invalid_status_value_returns_422 PASSED            [ 76%]
tests/test_tickets.py::test_create_ticket_empty_string_field_returns_422 PASSED     [ 82%]
tests/test_tickets.py::test_patch_status_nonexistent_ticket_returns_404 PASSED      [ 88%]
tests/test_tickets.py::test_delete_existing_ticket_returns_204_then_404 PASSED      [ 94%]
tests/test_tickets.py::test_delete_nonexistent_ticket_returns_404 PASSED            [100%]

17 passed, 2 warnings in 0.87s
```

> **Note on warnings:** Two `DeprecationWarning`s are emitted by installed library versions
> (`httpx` → `httpx2`, `anyio` alias). They are unrelated to application code and do not
> affect correctness or test results.
