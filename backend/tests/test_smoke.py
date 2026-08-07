"""
Smoke tests — run from backend/:
    pip install pytest pytest-anyio httpx anyio
    pytest tests/test_smoke.py -v
Requires the FastAPI app to import cleanly; MongoDB/env vars must be set.
"""
import os
import sys
import pytest

# Allow importing from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET", "test-secret-32-chars-xxxxxxxxxxxx")
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")

from httpx import AsyncClient, ASGITransport
from main import app

BASE = "http://test"
TRANSPORT = ASGITransport(app=app)

# Mark every test in this module as anyio so we don't need @pytest.mark.anyio on each one
pytestmark = pytest.mark.anyio


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _register(client: AsyncClient, suffix: str = "") -> dict:
    email = f"smoke{suffix}@test.com"
    r = await client.post("/auth/signup", json={
        "name": f"Smoke{suffix}", "email": email, "password": "Test1234!", "nationality": "Ethiopian"
    })
    # If already registered, log in instead
    if r.status_code == 400:
        r = await client.post("/auth/login", json={"email": email, "password": "Test1234!"})
    assert r.status_code in (200, 201), f"Register/login failed: {r.text}"
    return r.json()


# ─── Auth ─────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_signup_and_login():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        data = await _register(c, suffix="_auth")
        assert "access_token" in data
        assert data["user"]["role"] == "user"


@pytest.mark.anyio
async def test_login_bad_password():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        r = await c.post("/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
        assert r.status_code == 401


# ─── Dish submission ──────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_dish_submit_requires_auth():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        r = await c.post("/api/dishes", json={
            "name": "Unauthenticated Dish", "category": "main", "description": "test"
        })
        assert r.status_code == 401


@pytest.mark.anyio
async def test_dish_submit_and_list():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        auth = await _register(c, suffix="_dish")
        token = auth["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await c.post("/api/dishes", json={
            "name": "Smoke Test Dish Unique123",
            "category": "main",
            "description": "A smoke test dish",
        }, headers=headers)
        assert r.status_code == 201
        dish = r.json()
        assert dish["status"] == "pending"
        assert dish["slug"] == "smoke-test-dish-unique123"

        # Should NOT appear in public list (pending)
        r2 = await c.get("/api/dishes")
        ids = [d["id"] for d in r2.json().get("dishes", [])]
        assert dish["id"] not in ids


# ─── Variation submission ─────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_variation_submit_requires_auth():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        r = await c.post("/api/dishes/doro-wat/variations", json={
            "variation_name": "Test", "ingredients": ["x"], "steps": [{"title": "s", "text": "t"}]
        })
        assert r.status_code == 401


@pytest.mark.anyio
async def test_variation_submit_nonexistent_dish():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        auth = await _register(c, suffix="_var")
        headers = {"Authorization": f"Bearer {auth['access_token']}"}
        r = await c.post("/api/dishes/this-dish-does-not-exist/variations", json={
            "variation_name": "My version",
            "ingredients": ["onion"],
            "steps": [{"title": "Step 1", "text": "Cook it"}],
        }, headers=headers)
        assert r.status_code == 404


# ─── Moderation ───────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_moderation_queue_requires_admin():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        # Unauthenticated
        r = await c.get("/api/moderation/queue")
        assert r.status_code == 401

        # Regular user
        auth = await _register(c, suffix="_mod")
        headers = {"Authorization": f"Bearer {auth['access_token']}"}
        r2 = await c.get("/api/moderation/queue", headers=headers)
        assert r2.status_code == 403


@pytest.mark.anyio
async def test_moderate_dish_requires_admin():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        auth = await _register(c, suffix="_modact")
        headers = {"Authorization": f"Bearer {auth['access_token']}"}
        r = await c.patch("/api/moderation/dishes/000000000000000000000000",
                          json={"action": "approve"}, headers=headers)
        assert r.status_code == 403


# ─── Image upload ─────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_upload_requires_auth():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        r = await c.post("/api/upload/image",
                         files={"file": ("test.jpg", b"fake", "image/jpeg")})
        assert r.status_code == 401


@pytest.mark.anyio
async def test_upload_rejects_invalid_file():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        auth = await _register(c, suffix="_upload")
        headers = {"Authorization": f"Bearer {auth['access_token']}"}

        # Wrong extension
        r = await c.post("/api/upload/image",
                         files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
                         headers=headers)
        assert r.status_code == 400

        # Right extension but fake bytes (not a real image)
        r2 = await c.post("/api/upload/image",
                          files={"file": ("fake.jpg", b"notanimage", "image/jpeg")},
                          headers=headers)
        assert r2.status_code == 400


# ─── Dish feed & pagination ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_dish_list_pagination_shape():
    async with AsyncClient(transport=TRANSPORT, base_url=BASE) as c:
        r = await c.get("/api/dishes?page=1&limit=5")
        assert r.status_code == 200
        body = r.json()
        assert "dishes" in body
        assert "total" in body
        assert "page" in body
        assert len(body["dishes"]) <= 5
