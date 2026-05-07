from datetime import datetime, timezone

def parse_iso_datetime(value: str):
    if not value:
        return None

    value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)

def seconds_until(iso_datetime: str) -> int | None:
    dt = parse_iso_datetime(iso_datetime)

    if dt is None:
        return None

    now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return int((dt - now).total_seconds())