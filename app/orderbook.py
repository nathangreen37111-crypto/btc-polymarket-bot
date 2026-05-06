from py_clob_client.client import ClobClient
from app.config import settings

client = ClobClient(settings.polymarket_clob_url)

def get_token_orderbook(token_id: str) -> dict:
    """
    Fetch the CLOB order book for one outcome token.
    This is read-only and does not require wallet auth.
    """
    orderbook = client.get_order_book(token_id)

    bids = [
        {"price": float(bid.price), "size": float(bid.size)}
        for bid in orderbook.bids
    ]

    asks = [
        {"price": float(ask.price), "size": float(ask.size)}
        for ask in orderbook.asks
    ]

    bids.sort(key=lambda x: x["price"], reverse=True)
    asks.sort(key=lambda x: x["price"])

    best_bid = bids[0]["price"] if bids else None
    best_ask = asks[0]["price"] if asks else None

    spread = None
    if best_bid is not None and best_ask is not None:
        spread = best_ask - best_bid

    return {
        "token_id": token_id,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "bid_depth": sum(b["size"] for b in bids),
        "ask_depth": sum(a["size"] for a in asks),
        "bids": bids[:5],
        "asks": asks[:5],
    }