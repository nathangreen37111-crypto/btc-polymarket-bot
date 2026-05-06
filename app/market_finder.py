import httpx
from app.config import settings

async def find_btc_markets(limit: int = 100) -> list[dict]:
    url = f"{settings.polymarket_gamma_url}/events"

    params = {
        "limit": limit,
        "closed": "false",
        "active": "true",
        "order": "startDate",
        "ascending": "false",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        events = response.json()

    candidates = []

    for event in events:
        slug = str(event.get("slug", "")).lower()
        title = str(event.get("title", "")).lower()

        is_5m = "btc-updown-5m" in slug
        is_15m = "btc-updown-15m" in slug

        if not is_5m and not is_15m:
            continue

        markets = event.get("markets") or []
        if not markets:
            continue

        market = markets[0]

        if not market.get("acceptingOrders", False):
            continue

        candidates.append(event)

    return candidates


def get_market_type(event: dict) -> str | None:
    slug = str(event.get("slug", "")).lower()

    if "btc-updown-5m" in slug:
        return "5m"

    if "btc-updown-15m" in slug:
        return "15m"

    return None


def get_inner_market(event: dict) -> dict | None:
    markets = event.get("markets") or []
    if not markets:
        return None
    return markets[0]
