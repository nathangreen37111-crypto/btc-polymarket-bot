import json
from app.orderbook import get_token_orderbook

def parse_json_list(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return json.loads(value)

    return []


def get_up_down_prices(inner_market: dict) -> dict:
    outcomes = parse_json_list(inner_market.get("outcomes", "[]"))
    outcome_prices = parse_json_list(inner_market.get("outcomePrices", "[]"))
    token_ids = parse_json_list(inner_market.get("clobTokenIds", "[]"))

    result = {
        "question": inner_market.get("question", ""),
        "event_start_time": inner_market.get("eventStartTime"),
        "end_time": inner_market.get("endDate"),

        "up_token_id": None,
        "down_token_id": None,

        "up_price_estimate": None,
        "down_price_estimate": None,

        "up_best_bid": None,
        "up_best_ask": None,
        "up_spread": None,
        "up_ask_depth": None,

        "down_best_bid": None,
        "down_best_ask": None,
        "down_spread": None,
        "down_ask_depth": None,
    }

    for index, outcome in enumerate(outcomes):
        outcome_name = str(outcome).lower()

        price_estimate = float(outcome_prices[index]) if index < len(outcome_prices) else None
        token_id = str(token_ids[index]) if index < len(token_ids) else None

        if outcome_name == "up":
            result["up_token_id"] = token_id
            result["up_price_estimate"] = price_estimate

        if outcome_name == "down":
            result["down_token_id"] = token_id
            result["down_price_estimate"] = price_estimate

    if result["up_token_id"]:
        up_book = get_token_orderbook(result["up_token_id"])
        result["up_best_bid"] = up_book["best_bid"]
        result["up_best_ask"] = up_book["best_ask"]
        result["up_spread"] = up_book["spread"]
        result["up_ask_depth"] = up_book["ask_depth"]

    if result["down_token_id"]:
        down_book = get_token_orderbook(result["down_token_id"])
        result["down_best_bid"] = down_book["best_bid"]
        result["down_best_ask"] = down_book["best_ask"]
        result["down_spread"] = down_book["spread"]
        result["down_ask_depth"] = down_book["ask_depth"]

    return result