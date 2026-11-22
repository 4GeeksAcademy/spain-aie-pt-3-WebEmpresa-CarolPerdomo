import html
import json
import urllib.request

from .config import get_setting
from .auth import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES


def send_password_reset_email(recipient: str, reset_url: str) -> None:
    api_key = get_setting("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not configured")

    sender = get_setting("RESEND_FROM_EMAIL", "Nexova <onboarding@resend.dev>")
    safe_url = html.escape(reset_url, quote=True)
    message = {
        "from": sender,
        "to": [recipient],
        "subject": "Restablece tu contraseña de Nexova",
        "text": (
            "Recibimos una solicitud para restablecer la contraseña de tu cuenta Nexova.\n\n"
            f"Abre este enlace en los próximos {PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutos: {reset_url}\n\n"
            "Si no solicitaste este cambio, puedes ignorar este mensaje."
        ),
        "html": f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>Restablecer contraseña</title>
  </head>
  <body style="margin:0;background:#f1f3ed;color:#1c302a;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f3ed;padding:24px 12px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid #d5ddd3;border-radius:16px;">
          <tr><td style="padding:32px 28px 12px;font-size:24px;font-weight:700;color:#23483d;">Nexova<span style="color:#78934b;">.</span></td></tr>
          <tr><td style="padding:8px 28px 32px;">
            <h1 style="margin:0 0 16px;font-size:24px;line-height:1.3;">Restablece tu contraseña</h1>
            <p style="margin:0 0 24px;font-size:16px;line-height:1.6;">Recibimos una solicitud para cambiar la contraseña de tu cuenta. El enlace caduca en {PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutos y solo se puede usar una vez.</p>
            <p style="margin:0 0 24px;"><a href="{safe_url}" style="display:inline-block;padding:14px 20px;border-radius:8px;background:#23483d;color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;">Crear nueva contraseña</a></p>
            <p style="margin:0 0 12px;font-size:14px;line-height:1.6;color:#52635b;">Si el botón no funciona, copia este enlace en tu navegador:</p>
            <p style="margin:0 0 24px;overflow-wrap:anywhere;font-size:13px;line-height:1.6;"><a href="{safe_url}" style="color:#23483d;">{safe_url}</a></p>
            <p style="margin:0;font-size:14px;line-height:1.6;color:#52635b;">Si no solicitaste este cambio, ignora este correo. Tu contraseña seguirá igual.</p>
          </td></tr>
        </table>
        <p style="max-width:560px;margin:16px auto 0;padding:0 12px;color:#66776f;font-size:12px;line-height:1.5;">Este mensaje se envió porque alguien solicitó restablecer una contraseña de Nexova.</p>
      </td></tr>
    </table>
  </body>
</html>""",
    }
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(message).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError("Resend rejected the email request")
