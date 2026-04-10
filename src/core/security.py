import bcrypt
from fastapi import Depends, HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import get_db

SESSION_COOKIE = "admin_session"
SESSION_MAX_AGE = 60 * 60 * 8

_serializer = URLSafeTimedSerializer(settings.secret_key)



def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_session_token(admin_id: int) -> str:
    return _serializer.dumps(admin_id, salt="admin-session")


def decode_session_token(token: str) -> int | None:
    try:
        return _serializer.loads(token, salt="admin-session", max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def require_admin(request: Request, db: Session = Depends(get_db)):
    from src.models.admin import Admin

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
    from src.models.admin import Admin

    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return False
    admin_id = decode_session_token(token)
    if not admin_id:
        return False
    return db.query(Admin).filter_by(id=admin_id).first() is not None
