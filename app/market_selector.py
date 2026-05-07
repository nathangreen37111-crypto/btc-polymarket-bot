cat > app/market_selector.py <<'EOF'
from app.market_finder import get_market_type, get_inner_market
from app.polymarket_prices import get_up_down_prices
from app.time_utils import seconds_until


def select_nearest_markets(events: list[dict]) -> dict:
    """
    Select the nearest valid 5m and 15m BTC markets.

    5m: only allow markets ending within 10 minutes.
    15m: only allow markets ending within 30 minutes.
    """
    selected = {
        "5m": None,
        "15m": None,
    }

    best_seconds_left = {
        "5m": None,
        "15m": None,
    }

    for event in events:
        market_type = get_market_type(event)

        if market_type not in ("5m", "15m"):
            continue

        inner_market = get_inner_market(event)
        if not inner_market:
            continue

        market_prices = get_up_down_prices(inner_market)
        seconds_left = seconds_until(market_prices.get("end_time"))

        if seconds_left is None or seconds_left <= 0:
            continue

        if market_type == "5m" and seconds_left > 600:
            continue

        if market_type == "15m" and seconds_left > 1800:
            continue

        current_best = best_seconds_left[market_type]

        if current_best is None or seconds_left < current_best:
            best_seconds_left[market_type] = seconds_left
            selected[market_type] = {
                "event": event,
                "inner_market": inner_market,
                "market_prices": market_prices,
                "seconds_left": seconds_left,
            }

    return selected
EOF