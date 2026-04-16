import json
import logging
import ssl
import threading
import time
from datetime import datetime
from urllib.request import urlopen

import certifi
import redis as redis_lib

from src.core.config import settings

logger = logging.getLogger(__name__)


_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

_redis: redis_lib.Redis | None = None
_REDIS_KEY = "currency:usd_rate"
_REDIS_TTL = 3600


def _get_redis() -> redis_lib.Redis | None:
    global _redis
    if _redis is None:
        try:
            client = redis_lib.from_url(settings.redis_url, decode_responses=True)
            client.ping()
            _redis = client
        except Exception as e:
            logger.warning("Redis unavailable, falling back to in-process cache: %s", e)
    return _redis


_fallback_rate: float | None = None
_fallback_lock = threading.Lock()
_background_started = False


_MONOBANK_URL = "https://api.monobank.ua/bank/currency"
_NBU_URL = (
    "https://bank.gov.ua/NBU_Exchange/exchange_site"
    "?valcode=usd&sort=exchangedate&order=desc&json"
)
_RATE_MIN = 5.0
_RATE_MAX = 500.0
_MAX_RESPONSE_BYTES = 100 * 1024


def _write_cache(rate: float) -> None:
    r = _get_redis()
    if r is not None:
        try:
            r.setex(_REDIS_KEY, _REDIS_TTL, str(rate))
        except Exception as e:
            logger.warning("Redis write failed: %s", e)

    with _fallback_lock:
        global _fallback_rate
        _fallback_rate = rate


def _read_cache() -> float | None:
    r = _get_redis()
    if r is not None:
        try:
            value = r.get(_REDIS_KEY)
            if value is not None:
                return float(str(value))
        except Exception as e:
            logger.warning("Redis read failed: %s", e)

    with _fallback_lock:
        return _fallback_rate


def _validate_rate(rate: float) -> float | None:
    if _RATE_MIN < rate < _RATE_MAX:
        return rate
    logger.error("Rate out of sane range (%.4f), ignoring", rate)
    return None


def _fetch_monobank() -> float | None:
    try:
        with urlopen(_MONOBANK_URL, timeout=5, context=_SSL_CTX) as resp:
            data = json.loads(resp.read(_MAX_RESPONSE_BYTES))
        for item in data:
            if item.get("currencyCodeA") == 840 and item.get("currencyCodeB") == 980:
                return _validate_rate(float(item["rateSell"]))
    except Exception as e:
        logger.warning("Monobank fetch failed: %s", e)
    return None


def _fetch_nbu() -> float | None:
    today = datetime.now().strftime("%Y%m%d")
    url = f"{_NBU_URL}&start={today}&end={today}"
    try:
        with urlopen(url, timeout=5, context=_SSL_CTX) as resp:
            data = json.loads(resp.read(_MAX_RESPONSE_BYTES))
        if data:
            return _validate_rate(float(data[0]["rate"]))
    except Exception as e:
        logger.warning("NBU fetch failed: %s", e)
    return None


def _save_to_db(rate: float) -> None:
    from src.db.database import SessionLocal
    from src.models.exchange_rate import ExchangeRate

    db = SessionLocal()
    try:
        record = db.query(ExchangeRate).filter_by(currency="USD").first()
        if record:
            record.rate = rate
            record.updated_at = datetime.now()
        else:
            db.add(ExchangeRate(currency="USD", rate=rate, updated_at=datetime.now()))
        db.commit()
    except Exception as e:
        logger.error("Failed to save exchange rate to DB: %s", e)
        db.rollback()
    finally:
        db.close()


def _load_from_db() -> float | None:
    from src.db.database import SessionLocal
    from src.models.exchange_rate import ExchangeRate

    db = SessionLocal()
    try:
        record = db.query(ExchangeRate).filter_by(currency="USD").first()
        return float(record.rate) if record else None
    except Exception as e:
        logger.error("Failed to load exchange rate from DB: %s", e)
        return None
    finally:
        db.close()


def get_cached_rate() -> float | None:
    return _read_cache()


def refresh_rate() -> float | None:
    rate = _fetch_monobank() or _fetch_nbu()

    if rate:
        _write_cache(rate)
        _save_to_db(rate)
        logger.info("Exchange rate updated: 1 USD = %.2f UAH", rate)
        return rate

    rate = _load_from_db()
    if rate:
        _write_cache(rate)
        logger.warning("Using stale exchange rate from DB: %.4f", rate)
    return rate


def init_from_db() -> None:
    rate = _load_from_db()
    if rate:
        _write_cache(rate)
        logger.info("Exchange rate loaded from DB: 1 USD = %.2f UAH", rate)


def start_background_refresh() -> None:
    global _background_started
    if _background_started:
        return
    _background_started = True

    def _loop() -> None:
        while True:
            time.sleep(_REDIS_TTL)
            try:
                r = _get_redis()
                if r is not None:
                    try:
                        ttl = r.ttl(_REDIS_KEY)
                        if ttl > 0:
                            continue
                    except redis_lib.RedisError:
                        pass
                refresh_rate()
            except Exception as e:
                logger.error("Background rate refresh failed: %s", e)

    thread = threading.Thread(target=_loop, daemon=True, name="currency-refresh")
    thread.start()
    logger.info("Currency background refresh thread started")


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0")


def uah_price(usd: int | None) -> str:
    rate = _read_cache()
    if not usd or not rate:
        return ""
    return _fmt(round(usd * rate))


def usd_amount(usd: int | None) -> str:
    if not usd:
        return ""
    return _fmt(usd)
