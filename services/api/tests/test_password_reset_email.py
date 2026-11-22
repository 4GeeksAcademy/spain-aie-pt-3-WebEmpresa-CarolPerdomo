import json

from nexova_suppliers import email_service


def test_resend_request_contains_reset_link_without_exposing_secret(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        email_service,
        "get_setting",
        lambda name, default=None: {
            "RESEND_API_KEY": "test-key-never-printed",
            "RESEND_FROM_EMAIL": "Nexova <test@example.com>",
        }.get(name, default),
    )

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data)
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(email_service.urllib.request, "urlopen", fake_urlopen)
    reset_url = "https://backoffice.example/reset-password?token=signed-token"
    email_service.send_password_reset_email("person@example.com", reset_url)

    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["headers"]["Authorization"] == "Bearer test-key-never-printed"
    assert captured["body"]["to"] == ["person@example.com"]
    assert reset_url in captured["body"]["text"]
    assert reset_url in captured["body"]["html"]
    assert captured["timeout"] == 10
