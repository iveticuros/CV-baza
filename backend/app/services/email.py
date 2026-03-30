from __future__ import annotations

import logging
from email.message import EmailMessage

import aiosmtplib

from ..config import settings

log = logging.getLogger(__name__)


async def send_email(*, to: str, subject: str, body_text: str, body_html: str | None = None) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_TLS,
        )
    except Exception:
        log.exception("SMTP failed for to=%s subject=%s", to, subject)
        raise


async def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/verify-email?token={token}"
    await send_email(
        to=to,
        subject="Potvrdite email — CV Baza",
        body_text=f"Kliknite na link da potvrdite email (važi 24h): {link}",
        body_html=f'<p>Kliknite <a href="{link}">ovde</a> da potvrdite email. Link važi 24 sata.</p>',
    )


async def send_approval_email(to: str) -> None:
    await send_email(
        to=to,
        subject="Nalog odobren — CV Baza",
        body_text="Administrator je odobrio vaš nalog. Možete se prijaviti.",
    )


async def send_password_reset_email(to: str, token: str) -> None:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token}"
    await send_email(
        to=to,
        subject="Reset lozinke — CV Baza",
        body_text=f"Link za reset (važi 2h): {link}",
        body_html=f'<p><a href="{link}">Reset lozinke</a> (važi 2 sata)</p>',
    )
