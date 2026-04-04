from fastapi import Request


def check_admin(request: Request) -> bool:
    return request.cookies.get("admin") == "ok"
