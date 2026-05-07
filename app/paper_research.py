from datetime import datetime, timedelta, timezone
from app.config import settings
from app.db import get_conn

def _utc_now():
    return datetime.now(timezone.utc)

def _entry_profit(stake_usd: float, entry_price: float, won: bool) -> float:
    if not won:
        return -stake_usd

    shares = stake_usd / entry_price
    payout = shares * 1.00
    return payout - stake_usd

def _get_recent_price(seconds_back: int):
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

def _has_open_bet(market_type: str, strategy_name: str):
    with get_conn() as conn:
        row = conn.execute("""
        SELECT id
        FROM paper_bets
        WHERE status = 'open'
        AND market_type = ?
        AND strategy_name = ?
        LIMIT 1
        """, (market_type, strategy_name)).fetchone()

    return row is not None

def _open_paper_bet(
    strategy_name: str,
    market_type: str,
    side: str,
    btc_price: float,
    entry_price: float,
    window_seconds: int,
    seconds_left_at_entry: int | None,
    momentum_pct: float,
    reason: str,
):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO paper_bets (
            mode, strategy_name, market_type, side, stake_usd, entry_price,
            entry_btc_price, window_seconds, seconds_left_at_entry,
            momentum_pct, status, reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            settings.mode,
            strategy_name,
            market_type,
            side,
            settings.paper_stake_usd,
            entry_price,
            btc_price,
            window_seconds,
            seconds_left_at_entry,
            momentum_pct,
            "open",
            reason,
        ))
        conn.commit()

def maybe_open_paper_bet(market_type: str, btc_price: float, market_prices: dict):
    strategy_name = f"{market_type}_momentum"

    if market_type == "5m":
        lookback_seconds = 60
        window_seconds = 5 * 60
    elif market_type == "15m":
        lookback_seconds = 180
        window_seconds = 15 * 60
    else:
        return

    if _has_open_bet(market_type, strategy_name):
        return

    old_price = _get_recent_price(lookback_seconds)

    if old_price is None:
        print(f"{strategy_name}: waiting for enough price history")
        return

    momentum_pct = (btc_price - old_price) / old_price

    if abs(momentum_pct) < settings.min_momentum_pct:
        print(
            f"{strategy_name}: no paper bet | momentum={momentum_pct:.4%} "
            f"is below threshold={settings.min_momentum_pct:.4%}"
        )
        return

    if momentum_pct > 0:
        side = "UP"
        entry_price = market_prices.get("up_best_ask")
        side_spread = market_prices.get("up_spread")
        ask_depth = market_prices.get("up_ask_depth")
    else:
        side = "DOWN"
        entry_price = market_prices.get("down_best_ask")
        side_spread = market_prices.get("down_spread")
        ask_depth = market_prices.get("down_ask_depth")

    if entry_price is None:
        print(f"{strategy_name}: missing Polymarket CLOB best ask for {side}")
        return

    spread = side_spread or 0

    if spread > settings.max_spread:
        print(
            f"{strategy_name}: skipped | {side} spread={spread:.2f} "
            f"is above max_spread={settings.max_spread:.2f}"
        )
        return

    if ask_depth is not None and ask_depth < settings.paper_stake_usd:
        print(
            f"{strategy_name}: skipped | {side} ask depth=${ask_depth:.2f} "
            f"is below stake=${settings.paper_stake_usd:.2f}"
        )
        return

    reason = (
        f"{strategy_name} using real CLOB best ask: "
        f"BTC momentum over {lookback_seconds}s was {momentum_pct:.4%}, "
        f"so bot would choose {side}. "
        f"Entry best ask={entry_price:.3f}, spread={spread:.3f}, "
        f"ask depth={ask_depth}."
    )

    _open_paper_bet(
        strategy_name=strategy_name,
        market_type=market_type,
        side=side,
        btc_price=btc_price,
        entry_price=entry_price,
        window_seconds=window_seconds,
        seconds_left_at_entry=None,
        momentum_pct=momentum_pct,
        reason=reason,
    )

    max_profit = (settings.paper_stake_usd / entry_price) - settings.paper_stake_usd

    print(
        f"OPEN PAPER BET | {strategy_name} | {side} | "
        f"stake=${settings.paper_stake_usd:.2f} | "
        f"Polymarket best ask={entry_price:.3f} | "
        f"possible profit=${max_profit:.2f} | "
        f"entry BTC=${btc_price:,.2f} | "
        f"momentum={momentum_pct:.4%}"
    )

def maybe_open_late_entry_paper_bet(
    market_type: str,
    btc_price: float,
    market_prices: dict,
    seconds_left: int | None,
):
    strategy_name = f"{market_type}_late_entry"

    if seconds_left is None:
        print(f"{strategy_name}: skipped | missing seconds_left")
        return

    if market_type == "5m":
        lookback_seconds = 30
        window_seconds = seconds_left
        min_seconds_left = settings.late_5m_min_seconds_left
        max_seconds_left = settings.late_5m_max_seconds_left
    elif market_type == "15m":
        lookback_seconds = 60
        window_seconds = seconds_left
        min_seconds_left = settings.late_15m_min_seconds_left
        max_seconds_left = settings.late_15m_max_seconds_left
    else:
        return

    if seconds_left < min_seconds_left or seconds_left > max_seconds_left:
        print(
            f"{strategy_name}: waiting | seconds_left={seconds_left} "
            f"needs {min_seconds_left}-{max_seconds_left}"
        )
        return

    if _has_open_bet(market_type, strategy_name):
        return

    old_price = _get_recent_price(lookback_seconds)

    if old_price is None:
        print(f"{strategy_name}: waiting for enough price history")
        return

    momentum_pct = (btc_price - old_price) / old_price

    if abs(momentum_pct) < settings.min_momentum_pct:
        print(
            f"{strategy_name}: no paper bet | momentum={momentum_pct:.4%} "
            f"is below threshold={settings.min_momentum_pct:.4%}"
        )
        return

    if momentum_pct > 0:
        side = "UP"
        entry_price = market_prices.get("up_best_ask")
        side_spread = market_prices.get("up_spread")
        ask_depth = market_prices.get("up_ask_depth")
    else:
        side = "DOWN"
        entry_price = market_prices.get("down_best_ask")
        side_spread = market_prices.get("down_spread")
        ask_depth = market_prices.get("down_ask_depth")

    if entry_price is None:
        print(f"{strategy_name}: missing Polymarket CLOB best ask for {side}")
        return

    spread = side_spread or 0

    if spread > settings.max_spread:
        print(
            f"{strategy_name}: skipped | {side} spread={spread:.2f} "
            f"is above max_spread={settings.max_spread:.2f}"
        )
        return

    if ask_depth is not None and ask_depth < settings.paper_stake_usd:
        print(
            f"{strategy_name}: skipped | {side} ask depth=${ask_depth:.2f} "
            f"is below stake=${settings.paper_stake_usd:.2f}"
        )
        return

    reason = (
        f"{strategy_name} using real CLOB best ask near expiration: "
        f"seconds_left={seconds_left}, "
        f"BTC momentum over {lookback_seconds}s was {momentum_pct:.4%}, "
        f"so bot would choose {side}. "
        f"Entry best ask={entry_price:.3f}, spread={spread:.3f}, "
        f"ask depth={ask_depth}."
    )

    _open_paper_bet(
        strategy_name=strategy_name,
        market_type=market_type,
        side=side,
        btc_price=btc_price,
        entry_price=entry_price,
        window_seconds=window_seconds,
        seconds_left_at_entry=seconds_left,
        momentum_pct=momentum_pct,
        reason=reason,
    )

    max_profit = (settings.paper_stake_usd / entry_price) - settings.paper_stake_usd

    print(
        f"OPEN LATE PAPER BET | {strategy_name} | {side} | "
        f"stake=${settings.paper_stake_usd:.2f} | "
        f"Polymarket best ask={entry_price:.3f} | "
        f"possible profit=${max_profit:.2f} | "
        f"seconds_left={seconds_left} | "
        f"entry BTC=${btc_price:,.2f} | "
        f"momentum={momentum_pct:.4%}"
    )

def resolve_open_paper_bets(current_btc_price: float):
    now = _utc_now()

    with get_conn() as conn:
        rows = conn.execute("""
        SELECT id, created_at, market_type, side, stake_usd, entry_price,
               entry_btc_price, window_seconds
        FROM paper_bets
        WHERE status = 'open'
        ORDER BY created_at ASC
        """).fetchall()

    for row in rows:
        (
            bet_id,
            created_at_str,
            market_type,
            side,
            stake_usd,
            entry_price,
            entry_btc_price,
            window_seconds,
        ) = row

        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        if now < created_at + timedelta(seconds=int(window_seconds)):
            continue

        if side == "UP":
            won = current_btc_price > entry_btc_price
        else:
            won = current_btc_price < entry_btc_price

        profit_usd = _entry_profit(
            stake_usd=float(stake_usd),
            entry_price=float(entry_price),
            won=won,
        )

        with get_conn() as conn:
            conn.execute("""
            UPDATE paper_bets
            SET status = 'resolved',
                resolved_at = CURRENT_TIMESTAMP,
                exit_btc_price = ?,
                won = ?,
                profit_usd = ?
            WHERE id = ?
            """, (
                current_btc_price,
                1 if won else 0,
                profit_usd,
                bet_id,
            ))
            conn.commit()

        result = "WIN" if won else "LOSS"

        print(
            f"RESOLVED PAPER BET | {market_type} | {side} | {result} | "
            f"entry price={entry_price:.3f} | "
            f"entry BTC=${entry_btc_price:,.2f} | "
            f"exit BTC=${current_btc_price:,.2f} | "
            f"P/L=${profit_usd:.2f}"
        )

def print_paper_summary():
    with get_conn() as conn:
        row = conn.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN won = 0 THEN 1 ELSE 0 END),
            COALESCE(SUM(profit_usd), 0)
        FROM paper_bets
        WHERE status = 'resolved'
        """).fetchone()

        by_strategy = conn.execute("""
        SELECT
            COALESCE(strategy_name, market_type) as strategy,
            market_type,
            COUNT(*),
            SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END),
            COALESCE(SUM(profit_usd), 0)
        FROM paper_bets
        WHERE status = 'resolved'
        GROUP BY strategy, market_type
        ORDER BY strategy, market_type
        """).fetchall()

    total, wins, losses, profit = row
    wins = wins or 0
    losses = losses or 0

    if total == 0:
        return

    win_rate = wins / total * 100

    print(
        f"SUMMARY | resolved={total} | wins={wins} | losses={losses} | "
        f"win_rate={win_rate:.1f}% | total P/L=${profit:.2f}"
    )

    for strategy, market_type, count, type_wins, type_profit in by_strategy:
        type_wins = type_wins or 0
        type_win_rate = type_wins / count * 100 if count else 0
        print(
            f"  {strategy}: market={market_type} | trades={count} | "
            f"wins={type_wins} | win_rate={type_win_rate:.1f}% | "
            f"P/L=${type_profit:.2f}"
        )
