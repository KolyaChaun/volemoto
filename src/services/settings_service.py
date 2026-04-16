from sqlalchemy.orm import Session

from src.models.site_settings import SiteSettings


def get_settings(db: Session) -> dict:
    rows = db.query(SiteSettings).all()
    return {r.key: r.value for r in rows}


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(SiteSettings).filter_by(key=key).first()
    if row:
        row.value = value
    else:
        db.add(SiteSettings(key=key, value=value))


def fmt_number(value: str) -> str:
    try:
        return f"{int(value):,}".replace(",", "\u00a0")
    except (ValueError, TypeError):
        return value
