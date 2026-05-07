from app.db import get_conn

def get_recent_btc_price(seconds_back: int):
    with get_conn() as conn:
        row = conn.execute("""
        SELECT btc_price
        FROM bot_ticks
        WHERE created_at <= datetime('now', ?)
        ORDER BY created_at DESC
        LIMIT 1
        """, (f"-{seconds_back} seconds",)).fetchone()

    if not row:
        return None

    return float(row[0])

def get_momentum_pct(current_price: float, seconds_back: int):
    old_price = get_recent_btc_price(seconds_back)

    if old_price is None:
        return None

    return (current_price - old_price) / old_price

def get_volatility_pct(seconds_back: int = 60):
    with get_conn() as conn:
        rows = conn.execute("""
        SELECT btc_price
        FROM bot_ticks
        WHERE created_at >= datetime('now', ?)
        ORDER BY created_at ASC
        """, (f"-{seconds_back} seconds",)).fetchall()

    prices = [float(row[0]) for row in rows]

    if len(prices) < 3:
        return None

    avg = sum(prices) / len(prices)
    variance = sum((p - avg) ** 2 for p in prices) / len(prices)
    std_dev = variance ** 0.5

    return std_dev / avg

def get_start_price_estimate(market_type: str, event_start_time: str | None):
    """
    First version: approximate start price using the closest stored bot tick
    at or before eventStartTime. Later we can improve with Chainlink source data.
    """
    if not event_start_time:
        return None

    event_start_time = event_start_time.replace("Z", "")

    with get_conn() as conn:
        row = conn.execute("""
        SELECT btc_price
        FROM bot_ticks
        WHERE created_at <= ?
        ORDER BY created_at DESC
        LIMIT 1
        """, (event_start_time,)).fetchone()

    if not row:
        return None

    return float(row[0])

def get_distance_from_start(current_price: float, start_price: float | None):
    if start_price is None:
        return None

    return current_price - start_price