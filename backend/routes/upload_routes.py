import io
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from auth import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/upload", tags=["upload"])
limiter = Limiter(key_func=get_remote_address)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_AUDIO_EXTS = {".mp3", ".m4a", ".ogg", ".wav"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

USE_CLOUDINARY = bool(os.getenv("CLOUDINARY_URL"))

if USE_CLOUDINARY:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))


def _save_local(content: bytes, ext: str) -> str:
    filename = f"{uuid.uuid4()}{ext}"
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    with open(os.path.join(upload_dir, filename), "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


def _upload_cloudinary(content: bytes, resource_type: str = "image") -> str:
    result = cloudinary.uploader.upload(
        content,
        resource_type=resource_type,
        folder="megeb",
    )
    return result["secure_url"]


@router.post("/image")
@limiter.limit("10/minute")
async def upload_image(request: Request, file: UploadFile = File(...), user=Depends(get_current_user)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise HTTPException(status_code=400, detail="Invalid type. Allowed: jpg, png, webp")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")

    try:
        from PIL import Image
        Image.open(io.BytesIO(content)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    if USE_CLOUDINARY:
        url = _upload_cloudinary(content, "image")
    else:
        url = _save_local(content, ext)

    return {"url": url}


@router.post("/audio")
@limiter.limit("5/minute")
async def upload_audio(request: Request, file: UploadFile = File(...), user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_AUDIO_EXTS:
        raise HTTPException(status_code=400, detail="Invalid type. Allowed: mp3, m4a, ogg, wav")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")

    if USE_CLOUDINARY:
        url = _upload_cloudinary(content, "video")  # Cloudinary uses "video" type for audio
    else:
        url = _save_local(content, ext)

    return {"url": url}
