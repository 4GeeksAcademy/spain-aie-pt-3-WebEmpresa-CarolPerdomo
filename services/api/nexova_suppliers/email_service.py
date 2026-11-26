"""Transactional email delivery through the Resend REST API."""
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class EmailDeliveryError(RuntimeError):
    pass


def _safe_provider_message(body: bytes) -> str:
    """Extract a useful provider error while redacting email addresses and keys."""
    try:
        response = json.loads(body.decode("utf-8"))
        message = response.get("message") or response.get("error") or response.get("name")
        if isinstance(message, dict):
            message = message.get("message") or message.get("name")
        if not isinstance(message, str):
            return "No provider detail was returned"
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "No provider detail was returned"
    message = re.sub(r"\b[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[email redacted]", message)
    message = re.sub(r"\bre_[A-Za-z0-9_-]{8,}\b", "[API key redacted]", message)
    return message[:400]


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise EmailDeliveryError("RESEND_API_KEY is not configured")

    sender = os.getenv("EMAIL_FROM", "Nexova <onboarding@resend.dev>")
    payload = {
        "from": sender,
        "to": [to_email],
        "subject": "Restablece tu contraseña de Nexova",
        "html": (
            "<p>Recibimos una solicitud para restablecer tu contraseña.</p>"
            f'<p><a href="{reset_url}">Crear una contraseña nueva</a></p>'
            "<p>El enlace caduca en 30 minutos y solo se puede usar una vez. "
            "Si no solicitaste este cambio, ignora este mensaje.</p>"
        ),
        "text": (
            "Recibimos una solicitud para restablecer tu contraseña. "
            f"Abre este enlace (caduca en 30 minutos): {reset_url}\n\n"
            "Si no solicitaste este cambio, ignora este mensaje."
        ),
    }
    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            if not 200 <= response.status < 300:
                raise EmailDeliveryError("Resend rejected the email request")
    except HTTPError as exc:
        provider_message = _safe_provider_message(exc.read(4096))
        raise EmailDeliveryError(f"Resend returned HTTP {exc.code}: {provider_message}") from None
    except (URLError, TimeoutError) as exc:
        raise EmailDeliveryError(f"Resend could not be reached ({type(exc).__name__})") from None
