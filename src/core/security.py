import os
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")

# True на продакшене (HTTPS), False для локальной разработки (HTTP)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"

SESSION_COOKIE  = "admin_session"
SESSION_MAX_AGE = 60 * 60 * 8

_serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_session_token(admin_id: int) -> str:
    """Создаёт подписанный токен с ID администратора."""
    return _serializer.dumps(admin_id, salt="admin-session")


def decode_session_token(token: str) -> int | None:
    """Проверяет подпись и срок действия токена. Возвращает admin_id или None."""
    try:
        return _serializer.loads(token, salt="admin-session", max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


# ── Зависимости FastAPI ───────────────────────────────

def require_admin(request: Request, db: Session = Depends(get_db)):
    """
    Dependency для защищённых роутов.
    Проверяет cookie → расшифровывает токен → ищет админа в БД.
    При неудаче поднимает 401 → exception_handler редиректит на /admin/login.
    """
    from src.models.admin import Admin  # локальный импорт во избежание циклов

    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401)

    admin_id = decode_session_token(token)
    if not admin_id:
        raise HTTPException(status_code=401)

    admin = db.query(Admin).filter_by(id=admin_id).first()
    if not admin:
        raise HTTPException(status_code=401)

    return admin


def get_optional_admin(request: Request, db: Session = Depends(get_db)) -> bool:
    """
    Dependency для публичных роутов, которым нужно знать — залогинен ли админ.
    Используется для показа кнопок удаления на публичной странице отзывов.
    Не поднимает исключений, просто возвращает True/False.
    """
    from src.models.admin import Admin

    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return False
    admin_id = decode_session_token(token)
    if not admin_id:
        return False
    return db.query(Admin).filter_by(id=admin_id).first() is not None