import asyncio
from app.config import settings
from app.db import init_db, log_tick
from app.btc_feed import get_btc_price
from app.market_finder import find_btc_markets, get_market_type, get_inner_market
from app.polymarket_prices import get_up_down_prices
from app.paper_research import (
    maybe_open_paper_bet,
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

                for event in events:
                    market_type = get_market_type(event)

                    if market_type == "5m" and not settings.trade_5m:
                        continue

                    if market_type == "15m" and not settings.trade_15m:
                        continue

                    inner_market = get_inner_market(event)
                    if not inner_market:
                        continue

                    market_prices = get_up_down_prices(inner_market)

                    print(
    f"{market_type} market | "
    f"UP ask={market_prices['up_best_ask']} | "
    f"DOWN ask={market_prices['down_best_ask']} | "
    f"UP spread={market_prices['up_spread']} | "
    f"DOWN spread={market_prices['down_spread']} | "
    f"{market_prices['question']}"
)

                    maybe_open_paper_bet(
                        market_type=market_type,
                        btc_price=btc_price,
                        market_prices=market_prices,
                    )

                print_paper_summary()

        except Exception as e:
            print(f"ERROR: {e}")

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run())
