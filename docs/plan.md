# Support Ticket API — Implementation Plan

## Stack
- Python, FastAPI, Pydantic (`pydantic[email]`), pytest, httpx , Uvicorn
- In-memory storage (no database)


---

## Project Structure

```
Mini Support Ticket API/
├── docs/
│   ├── specification.md
│   ├── delegation-contract.md
│   └── plan.md
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app + router
│   ├── models.py      # Pydantic schemas
│   ├── store.py       # In-memory dict store
│   └── routes.py      # Route handlers
├── tests/
│   ├── __init__.py
│   └── test_tickets.py
├── README.md
└── requirements.txt
```

---

## API Routes

| Method   | Path                      | Description          |
|----------|---------------------------|----------------------|
| `POST`   | `/tickets`                | Create a ticket      |
| `GET`    | `/tickets`                | List all tickets     |
| `GET`    | `/tickets/{id}`           | Get one ticket       |
| `PATCH`  | `/tickets/{id}/status`    | Update status only   |
| `DELETE` | `/tickets/{id}`           | Delete a ticket      |

---

## Data Models

### `TicketStatus` (enum)
`open` | `in_progress` | `resolved`

### `TicketCreate` (POST body)
| Field            | Type       | Constraint |
|------------------|------------|------------|
| `customer_name`  | `str`      | required, `min_length=1` |
| `customer_email` | `EmailStr` | required, valid email |
| `subject`        | `str`      | required, `min_length=1` |
| `description`    | `str`      | required, `min_length=1` |

### `StatusUpdate` (PATCH body)
| Field    | Type           |
|----------|----------------|
| `status` | `TicketStatus` |

### `TicketResponse`
All `TicketCreate` fields + `id: int` + `status: TicketStatus`

---

## Business Logic

- New tickets are **always created** with `status = open`.
- **Exactly two valid transitions** (per specification):
  - `open → in_progress`
  - `in_progress → resolved`
- **All other transitions** (reversals, skips, same-state) → **422**.
- Unknown ticket ID on any operation → **404**.
- Invalid email at creation → **422** (Pydantic handles automatically).

---

## Error Handling

| Condition | HTTP Status | Notes |
|-----------|-------------|-------|
| Missing or invalid request fields (email, empty strings) | **422** | Handled automatically by Pydantic/FastAPI |
| Invalid `status` value in PATCH body (not in enum) | **422** | Handled automatically by Pydantic/FastAPI |
| Ticket ID does not exist | **404** | Explicit check in route handler |
| Disallowed status transition | **422** | Explicit check in route handler with descriptive message |
| Unexpected internal error | **500** | FastAPI default behaviour is used; no custom global handler required. Stack traces and internal implementation details must not be exposed in API responses. |

---

## Tests (17 cases)

| # | Scenario                                  | Expected |
|---|-------------------------------------------|----------|
| 1 | Create ticket                             | 201, status = `open` |
| 2 | Create with invalid email                 | 422 |
| 3 | Create with missing required field        | 422 |
| 4 | List tickets                              | 200, array |
| 5 | Get existing ticket                       | 200, correct data |
| 6 | Get non-existent ticket                   | 404 |
| 7 | `open → in_progress`                      | 200 |
| 8 | `in_progress → resolved`                  | 200 |
| 9 | `resolved → open`                         | 422 |
|10 | `open → resolved` (skip)                  | 422 |
|11 | `in_progress → open` (reversal)           | 422 |
|12 | `open → open` (same-state)                | 422 |
|13 | PATCH with invalid status value (`"banana"`) | 422 |
|14 | Create ticket with empty required string field | 422 |
|15 | PATCH status on non-existent ticket       | 404 |
|16 | Delete existing ticket, then GET          | 204, then 404 |
|17 | Delete non-existent ticket                | 404 |

---

## Verification

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the application (must start without errors)
uvicorn app.main:app --reload

# 3. Run the test suite (all 17 must pass)
pytest tests/ -v
```

All 17 tests must pass. Results are reported in `README.md`.

---

## Design Assumptions

The following response codes are not specified in `specification.md`. They follow standard REST conventions and are called out explicitly for human awareness:

| # | Assumption | Value |
|---|------------|-------|
| 1 | **POST** success response code | **201 Created** |
| 2 | **DELETE** success response code | **204 No Content** |
