from fastapi import APIRouter, HTTPException
from models.schemas import SignupRequest, LoginRequest, TokenResponse
from database import users
from auth import hash_password, verify_password, create_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(u: dict) -> dict:
    return {
        "id": str(u["_id"]),
        "name": u["name"],
        "email": u["email"],
        "nationality": u["nationality"],
        "role": u.get("role", "user"),
    }


@router.post("/signup", response_model=TokenResponse)
async def signup(body: SignupRequest):
    if await users.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "nationality": body.nationality or "Ethiopian",
        "role": "user",
    }
    result = await users.insert_one(doc)
    doc["_id"] = result.inserted_id

    token = create_token({"sub": str(result.inserted_id)})
    return {"access_token": token, "user": _user_out(doc)}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = await users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": str(user["_id"])})
    return {"access_token": token, "user": _user_out(user)}
