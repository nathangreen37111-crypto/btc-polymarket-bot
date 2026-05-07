import asyncio

from app.config import settings
from app.db import init_db, log_tick
from app.btc_feed import get_btc_price
from app.market_finder import find_btc_markets
from app.market_selector import select_nearest_markets
from app.strategy_engine import get_strategy_decisions
from app.paper_research import (
    open_strategy_paper_bet,
    resolve_open_paper_bets,
    print_paper_summary,
)


async def run():
    init_db()

    while True:
        try:
            btc_price = await get_btc_price()
            events = await find_btc_markets()

            print(
                f"mode={settings.mode} | "
                f"BTC=${btc_price:,.2f} | "
                f"candidate BTC markets={len(events)}"
            )

            log_tick(
                mode=settings.mode,
                btc_price=btc_price,
                candidate_markets=len(events),
            )

            if settings.mode == "research":
                resolve_open_paper_bets(btc_price)

                selected_markets = select_nearest_markets(events)

                for market_type, selected in selected_markets.items():
                    if selected is None:
                        print(f"{market_type}: no valid near-term market found")
                        continue

                    market_prices = selected["market_prices"]
                    seconds_left = selected["seconds_left"]

                    # Optional safety: respect old TRADE_5M / TRADE_15M flags if they exist.
                    if market_type == "5m" and hasattr(settings, "trade_5m") and not settings.trade_5m:
                        continue

                    if market_type == "15m" and hasattr(settings, "trade_15m") and not settings.trade_15m:
                        continue

                    print(
                        f"{market_type} SELECTED | "
                        f"seconds_left={seconds_left} | "
                        f"UP ask={market_prices['up_best_ask']} | "
                        f"DOWN ask={market_prices['down_best_ask']} | "
                        f"UP spread={market_prices['up_spread']} | "
                        f"DOWN spread={market_prices['down_spread']} | "
                        f"{market_prices['question']}"
                    )

                    strategy_decisions = get_strategy_decisions(
                        market_type=market_type,
                        btc_price=btc_price,
                        market_prices=market_prices,
                        seconds_left=seconds_left,
                    )

                    for decision in strategy_decisions:
                        if not decision.should_trade:
                            print(f"{decision.strategy_name}: {decision.reason}")
                            continue

                        window_seconds = (
                            seconds_left
                            if seconds_left and seconds_left > 0
                            else (300 if market_type == "5m" else 900)
                        )

                        open_strategy_paper_bet(
                            strategy_name=decision.strategy_name,
                            market_type=market_type,
                            side=decision.side,
                            btc_price=btc_price,
                            entry_price=decision.entry_price,
                            window_seconds=window_seconds,
                            seconds_left_at_entry=decision.seconds_left,
                            momentum_pct=decision.momentum_pct,
                            reason=decision.reason,
                        )

                print_paper_summary()

        except Exception as e:
            print(f"ERROR: {e}")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run())