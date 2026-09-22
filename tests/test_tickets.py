import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Reset store before every test for full isolation."""
    store.clear()
    yield
    store.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_valid_ticket(**overrides):
    payload = {
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "subject": "Login broken",
        "description": "Cannot log in since yesterday",
    }
    payload.update(overrides)
    return client.post("/tickets", json=payload)


# ---------------------------------------------------------------------------
# Test 1 – Create ticket → 201, status is open
# ---------------------------------------------------------------------------

def test_create_ticket_returns_201_and_status_open():
    r = create_valid_ticket()
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "open"
    assert body["id"] == 1
    assert body["customer_name"] == "Alice"
    assert body["customer_email"] == "alice@example.com"


# ---------------------------------------------------------------------------
# Test 2 – Create with invalid email → 422
# ---------------------------------------------------------------------------

def test_create_ticket_invalid_email_returns_422():
    r = create_valid_ticket(customer_email="not-an-email")
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 3 – Create with missing required field → 422
# ---------------------------------------------------------------------------

def test_create_ticket_missing_field_returns_422():
    r = client.post("/tickets", json={
        "customer_email": "alice@example.com",
        "subject": "Missing name",
        "description": "No name field",
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 4 – List tickets → 200, returns array
# ---------------------------------------------------------------------------

def test_list_tickets_returns_200_and_array():
    create_valid_ticket()
    create_valid_ticket(customer_name="Bob", customer_email="bob@example.com")
    r = client.get("/tickets")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2


# ---------------------------------------------------------------------------
# Test 5 – Get existing ticket → 200, correct data
# ---------------------------------------------------------------------------

def test_get_existing_ticket_returns_200():
    create_valid_ticket()
    r = client.get("/tickets/1")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 1
    assert body["subject"] == "Login broken"


# ---------------------------------------------------------------------------
# Test 6 – Get non-existent ticket → 404
# ---------------------------------------------------------------------------

def test_get_nonexistent_ticket_returns_404():
    r = client.get("/tickets/999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Test 7 – open → in_progress → 200
# ---------------------------------------------------------------------------

def test_transition_open_to_in_progress_returns_200():
    create_valid_ticket()
    r = client.patch("/tickets/1/status", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


# ---------------------------------------------------------------------------
# Test 8 – in_progress → resolved → 200
# ---------------------------------------------------------------------------

def test_transition_in_progress_to_resolved_returns_200():
    create_valid_ticket()
    client.patch("/tickets/1/status", json={"status": "in_progress"})
    r = client.patch("/tickets/1/status", json={"status": "resolved"})
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"


# ---------------------------------------------------------------------------
# Test 9 – resolved → open → 422
# ---------------------------------------------------------------------------

def test_transition_resolved_to_open_returns_422():
    create_valid_ticket()
    client.patch("/tickets/1/status", json={"status": "in_progress"})
    client.patch("/tickets/1/status", json={"status": "resolved"})
    r = client.patch("/tickets/1/status", json={"status": "open"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 10 – open → resolved (skip) → 422
# ---------------------------------------------------------------------------

def test_transition_open_to_resolved_skip_returns_422():
    create_valid_ticket()
    r = client.patch("/tickets/1/status", json={"status": "resolved"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 11 – in_progress → open (reversal) → 422
# ---------------------------------------------------------------------------

def test_transition_in_progress_to_open_returns_422():
    create_valid_ticket()
    client.patch("/tickets/1/status", json={"status": "in_progress"})
    r = client.patch("/tickets/1/status", json={"status": "open"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 12 – open → open (same-state) → 422
# ---------------------------------------------------------------------------

def test_transition_open_to_open_same_state_returns_422():
    create_valid_ticket()
    r = client.patch("/tickets/1/status", json={"status": "open"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 13 – PATCH with invalid status value → 422
# ---------------------------------------------------------------------------

def test_patch_invalid_status_value_returns_422():
    create_valid_ticket()
    r = client.patch("/tickets/1/status", json={"status": "banana"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 14 – Create with empty required string field → 422
# ---------------------------------------------------------------------------

def test_create_ticket_empty_string_field_returns_422():
    r = create_valid_ticket(subject="")
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test 15 – PATCH status on non-existent ticket → 404
# ---------------------------------------------------------------------------

def test_patch_status_nonexistent_ticket_returns_404():
    r = client.patch("/tickets/999/status", json={"status": "in_progress"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Test 16 – Delete existing ticket → 204, then GET → 404
# ---------------------------------------------------------------------------

def test_delete_existing_ticket_returns_204_then_404():
    create_valid_ticket()
    r = client.delete("/tickets/1")
    assert r.status_code == 204
    r2 = client.get("/tickets/1")
    assert r2.status_code == 404


# ---------------------------------------------------------------------------
# Test 17 – Delete non-existent ticket → 404
# ---------------------------------------------------------------------------

def test_delete_nonexistent_ticket_returns_404():
    r = client.delete("/tickets/999")
    assert r.status_code == 404
