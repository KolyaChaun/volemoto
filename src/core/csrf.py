import hmac
import re
import secrets
from urllib.parse import parse_qs

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse

CSRF_COOKIE = "csrf_token"
CSRF_FIELD = "csrf_token"


def _token_from_multipart(body: bytes, content_type: str) -> str:
    boundary_match = re.search(r"boundary=([^\s;]+)", content_type)
    if not boundary_match:
        return ""
    field = CSRF_FIELD.encode()
    pattern = b'Content-Disposition: form-data; name="' + field + b'"\r\n\r\n([^\r\n]+)'
    match = re.search(pattern, body)
    return match.group(1).decode("utf-8", errors="replace") if match else ""


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get(CSRF_COOKIE) or secrets.token_hex(32)
        request.state.csrf_token = token

        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            body = await request.body()

            if "application/x-www-form-urlencoded" in content_type:
                params = parse_qs(body.decode("utf-8", errors="replace"))
                form_token = params.get(CSRF_FIELD, [""])[0]
            elif "multipart/form-data" in content_type:
                form_token = _token_from_multipart(body, content_type)
            else:
                form_token = ""

            if not form_token or not hmac.compare_digest(token, form_token):
                return HTMLResponse(
                    "403 Forbidden: CSRF validation failed", status_code=403
                )

        response = await call_next(request)
        response.set_cookie(CSRF_COOKIE, token, httponly=False, samesite="lax")
        return response
