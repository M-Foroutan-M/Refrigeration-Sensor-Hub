from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_date_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
