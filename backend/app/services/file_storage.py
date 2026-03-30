from __future__ import annotations

import re
import uuid
from pathlib import Path

from ..config import settings

_SAFE_NAME = re.compile(r"^[a-zA-Z0-9_.-]+$")


def ensure_cv_dir() -> Path:
    path = Path(settings.CV_STORAGE_DIR).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_pdf_magic(header: bytes) -> bool:
    return len(header) >= 4 and header[:4] == b"%PDF"


def save_cv_file(*, user_id: int, content: bytes, original_filename: str, content_type: str | None = None) -> tuple[str, str]:
    if len(content) > settings.CV_UPLOAD_MAX_BYTES:
        raise ValueError("Fajl je prevelik (max 5MB).")
    if content_type and content_type != "application/pdf":
        raise ValueError("Dozvoljeni su samo PDF dokumenti.")
    if not is_pdf_magic(content[:16]):
        raise ValueError("Dozvoljeni su samo PDF dokumenti.")
    name = f"{user_id}_{uuid.uuid4().hex}.pdf"
    base = ensure_cv_dir()
    full = base / name
    full.write_bytes(content)
    on_disk = Path(original_filename).name[:255] or "cv.pdf"
    return name, on_disk


def delete_cv_file(stored_name: str | None) -> None:
    if not stored_name or not _SAFE_NAME.match(stored_name):
        return
    base = ensure_cv_dir()
    target = (base / stored_name).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return
    if target.is_file():
        target.unlink()


def read_cv_file(stored_name: str) -> bytes:
    if not _SAFE_NAME.match(stored_name):
        raise FileNotFoundError
    base = ensure_cv_dir()
    target = (base / stored_name).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise FileNotFoundError from None
    if not target.is_file():
        raise FileNotFoundError
    return target.read_bytes()
