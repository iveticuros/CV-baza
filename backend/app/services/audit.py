from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models.audit_log import AuditLog


def write_audit(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    row = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        request_id=request_id,
        details=details,
    )
    db.add(row)
