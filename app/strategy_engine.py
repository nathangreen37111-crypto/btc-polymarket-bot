from dataclasses import dataclass
from app.config import settings
from app.research_metrics import (
    get_momentum_pct,
    get_volatility_pct,
    get_start_price_estimate,
    get_distance_from_start,
)

@dataclass
class StrategyDecision:
    strategy_name: str
    should_trade: bool
    side: str | None
    entry_price: float | None
    reason: str
    momentum_pct: float | None = None
    seconds_left: int | None = None


def _side_from_momentum(momentum_pct: float | None):
    if momentum_pct is None:
        return None

    if momentum_pct > 0:
        return "UP"

    if momentum_pct < 0:
        return "DOWN"

    return None


def _entry_price_for_side(side: str | None, market_prices: dict):
    if side == "UP":
        return market_prices.get("up_best_ask")

    if side == "DOWN":
        return market_prices.get("down_best_ask")

    return None


def _spread_for_side(side: str | None, market_prices: dict):
    if side == "UP":
        return market_prices.get("up_spread")

    if side == "DOWN":
        return market_prices.get("down_spread")

    return None


def _ask_depth_for_side(side: str | None, market_prices: dict):
    if side == "UP":
        return market_prices.get("up_ask_depth")

    if side == "DOWN":
        return market_prices.get("down_ask_depth")

    return None


def _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, max_entry_price):
    if side is None:
        return False, "missing side"

    if entry_price is None:
        return False, f"{strategy_name}: missing entry price"

    if entry_price > max_entry_price:
        return False, f"{strategy_name}: skipped | entry_price={entry_price:.3f} above max={max_entry_price:.3f}"

    if spread is not None and spread > settings.max_spread:
        return False, f"{strategy_name}: skipped | spread={spread:.3f} above max_spread={settings.max_spread:.3f}"

    if ask_depth is not None and ask_depth < settings.paper_stake_usd:
        return False, f"{strategy_name}: skipped | ask_depth={ask_depth:.2f} below stake={settings.paper_stake_usd:.2f}"

    return True, "passed basic filters"


def decide_5m_strong_momentum(btc_price, market_prices, seconds_left):
    strategy_name = "5m_momentum_strong"

    if seconds_left is None:
        return StrategyDecision(strategy_name, False, None, None, "missing seconds_left")

    if seconds_left < settings.strong_5m_min_seconds_left or seconds_left > settings.strong_5m_max_seconds_left:
        return StrategyDecision(strategy_name, False, None, None, f"waiting | seconds_left={seconds_left}")

    momentum_pct = get_momentum_pct(btc_price, 60)

    if momentum_pct is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for 60s price history")

    if abs(momentum_pct) < settings.min_momentum_5m_strong:
        return StrategyDecision(strategy_name, False, None, None, f"momentum too weak {momentum_pct:.4%}", momentum_pct, seconds_left)

    side = _side_from_momentum(momentum_pct)
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, settings.max_entry_price_5m_strong)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, momentum_pct, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | 60s momentum={momentum_pct:.4%}, seconds_left={seconds_left}, entry={entry_price:.3f}",
        momentum_pct,
        seconds_left,
    )


def decide_5m_late_entry(btc_price, market_prices, seconds_left):
    strategy_name = "5m_late_entry"

    if seconds_left is None:
        return StrategyDecision(strategy_name, False, None, None, "missing seconds_left")

    if seconds_left < settings.late_5m_min_seconds_left or seconds_left > settings.late_5m_max_seconds_left:
        return StrategyDecision(strategy_name, False, None, None, f"waiting | seconds_left={seconds_left}")

    momentum_pct = get_momentum_pct(btc_price, 30)

    if momentum_pct is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for 30s price history")

    if abs(momentum_pct) < settings.min_momentum_5m_late:
        return StrategyDecision(strategy_name, False, None, None, f"momentum too weak {momentum_pct:.4%}", momentum_pct, seconds_left)

    side = _side_from_momentum(momentum_pct)
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, settings.max_entry_price_5m_late)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, momentum_pct, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | 30s momentum={momentum_pct:.4%}, seconds_left={seconds_left}, entry={entry_price:.3f}",
        momentum_pct,
        seconds_left,
    )


def decide_15m_momentum(btc_price, market_prices, seconds_left):
    strategy_name = "15m_momentum"

    momentum_pct = get_momentum_pct(btc_price, 180)

    if momentum_pct is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for 180s price history")

    if abs(momentum_pct) < settings.min_momentum_15m:
        return StrategyDecision(strategy_name, False, None, None, f"momentum too weak {momentum_pct:.4%}", momentum_pct, seconds_left)

    side = _side_from_momentum(momentum_pct)
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, settings.max_entry_price_15m)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, momentum_pct, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | 180s momentum={momentum_pct:.4%}, entry={entry_price:.3f}",
        momentum_pct,
        seconds_left,
    )


def decide_15m_late_entry(btc_price, market_prices, seconds_left):
    strategy_name = "15m_late_entry"

    if seconds_left is None:
        return StrategyDecision(strategy_name, False, None, None, "missing seconds_left")

    if seconds_left < settings.late_15m_min_seconds_left or seconds_left > settings.late_15m_max_seconds_left:
        return StrategyDecision(strategy_name, False, None, None, f"waiting | seconds_left={seconds_left}")

    momentum_pct = get_momentum_pct(btc_price, 60)

    if momentum_pct is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for 60s price history")

    if abs(momentum_pct) < settings.min_momentum_15m_late:
        return StrategyDecision(strategy_name, False, None, None, f"momentum too weak {momentum_pct:.4%}", momentum_pct, seconds_left)

    side = _side_from_momentum(momentum_pct)
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, settings.max_entry_price_15m_late)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, momentum_pct, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | 60s momentum={momentum_pct:.4%}, seconds_left={seconds_left}, entry={entry_price:.3f}",
        momentum_pct,
        seconds_left,
    )


def decide_distance_from_start(strategy_name, market_type, btc_price, market_prices, seconds_left):
    start_price = get_start_price_estimate(market_type, market_prices.get("event_start_time"))
    distance = get_distance_from_start(btc_price, start_price)

    if distance is None:
        return StrategyDecision(strategy_name, False, None, None, "missing start price estimate")

    if abs(distance) < settings.min_distance_from_start_usd:
        return StrategyDecision(strategy_name, False, None, None, f"distance too small ${distance:.2f}")

    side = "UP" if distance > 0 else "DOWN"
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    max_entry = settings.max_entry_price_5m_late if market_type == "5m" else settings.max_entry_price_15m_late

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, max_entry)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, None, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | distance_from_start=${distance:.2f}, entry={entry_price:.3f}",
        None,
        seconds_left,
    )


def decide_multitimeframe(strategy_name, market_type, btc_price, market_prices, seconds_left):
    m30 = get_momentum_pct(btc_price, 30)
    m60 = get_momentum_pct(btc_price, 60)
    m180 = get_momentum_pct(btc_price, 180)

    if m30 is None or m60 is None or m180 is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for multitimeframe history")

    all_up = m30 > 0 and m60 > 0 and m180 > 0
    all_down = m30 < 0 and m60 < 0 and m180 < 0

    if not all_up and not all_down:
        return StrategyDecision(strategy_name, False, None, None, f"momenta disagree: 30={m30:.4%}, 60={m60:.4%}, 180={m180:.4%}")

    combined_strength = min(abs(m30), abs(m60), abs(m180))
    min_strength = settings.min_momentum_5m_late if market_type == "5m" else settings.min_momentum_15m_late

    if combined_strength < min_strength:
        return StrategyDecision(strategy_name, False, None, None, f"combined strength too weak {combined_strength:.4%}")

    side = "UP" if all_up else "DOWN"
    entry_price = _entry_price_for_side(side, market_prices)
    spread = _spread_for_side(side, market_prices)
    ask_depth = _ask_depth_for_side(side, market_prices)

    max_entry = settings.max_entry_price_5m_late if market_type == "5m" else settings.max_entry_price_15m_late

    ok, reason = _basic_trade_filters(strategy_name, side, entry_price, spread, ask_depth, max_entry)
    if not ok:
        return StrategyDecision(strategy_name, False, side, entry_price, reason, combined_strength, seconds_left)

    return StrategyDecision(
        strategy_name,
        True,
        side,
        entry_price,
        f"{strategy_name}: TRADE {side} | 30={m30:.4%}, 60={m60:.4%}, 180={m180:.4%}, entry={entry_price:.3f}",
        combined_strength,
        seconds_left,
    )


def decide_volatility_filtered(strategy_name, market_type, btc_price, market_prices, seconds_left):
    vol = get_volatility_pct(60)

    if vol is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for volatility history")

    if vol > settings.max_volatility_1m:
        return StrategyDecision(strategy_name, False, None, None, f"volatility too high {vol:.4%}")

    if market_type == "5m":
        base = decide_5m_late_entry(btc_price, market_prices, seconds_left)
    else:
        base = decide_15m_late_entry(btc_price, market_prices, seconds_left)

    base.strategy_name = strategy_name

    if not base.should_trade:
        base.reason = f"{strategy_name}: volatility ok {vol:.4%}, but base skipped: {base.reason}"
        return base

    base.reason = f"{strategy_name}: volatility ok {vol:.4%}; {base.reason}"
    return base


def decide_reversal_filter(strategy_name, market_type, btc_price, market_prices, seconds_left):
    m30 = get_momentum_pct(btc_price, 30)
    m60 = get_momentum_pct(btc_price, 60)

    if m30 is None or m60 is None:
        return StrategyDecision(strategy_name, False, None, None, "waiting for reversal history")

    if abs(m30) > settings.reversal_spike_threshold and (m30 > 0) != (m60 > 0):
        return StrategyDecision(strategy_name, False, None, None, f"reversal risk: 30={m30:.4%}, 60={m60:.4%}")

    if market_type == "5m":
        base = decide_5m_late_entry(btc_price, market_prices, seconds_left)
    else:
        base = decide_15m_late_entry(btc_price, market_prices, seconds_left)

    base.strategy_name = strategy_name

    if not base.should_trade:
        base.reason = f"{strategy_name}: reversal filter ok, but base skipped: {base.reason}"
        return base

    base.reason = f"{strategy_name}: reversal filter ok; {base.reason}"
    return base


def get_strategy_decisions(market_type, btc_price, market_prices, seconds_left):
    decisions = []

    if market_type == "5m":
        if settings.enable_5m_strong_momentum:
            decisions.append(decide_5m_strong_momentum(btc_price, market_prices, seconds_left))

        if settings.enable_5m_late_entry:
            decisions.append(decide_5m_late_entry(btc_price, market_prices, seconds_left))

        if settings.enable_5m_distance_start:
            decisions.append(decide_distance_from_start("5m_distance_from_start", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_5m_multitimeframe:
            decisions.append(decide_multitimeframe("5m_multitimeframe", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_5m_volatility_filter:
            decisions.append(decide_volatility_filtered("5m_volatility_filtered", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_5m_reversal_filter:
            decisions.append(decide_reversal_filter("5m_reversal_filter", market_type, btc_price, market_prices, seconds_left))

    if market_type == "15m":
        if settings.enable_15m_momentum:
            decisions.append(decide_15m_momentum(btc_price, market_prices, seconds_left))

        if settings.enable_15m_late_entry:
            decisions.append(decide_15m_late_entry(btc_price, market_prices, seconds_left))

        if settings.enable_15m_distance_start:
            decisions.append(decide_distance_from_start("15m_distance_from_start", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_15m_multitimeframe:
            decisions.append(decide_multitimeframe("15m_multitimeframe", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_15m_volatility_filter:
            decisions.append(decide_volatility_filtered("15m_volatility_filtered", market_type, btc_price, market_prices, seconds_left))

        if settings.enable_15m_reversal_filter:
            decisions.append(decide_reversal_filter("15m_reversal_filter", market_type, btc_price, market_prices, seconds_left))

    return decisions