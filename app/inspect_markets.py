import asyncio
import json
from app.market_finder import find_btc_markets

async def main():
    markets = await find_btc_markets(limit=25)

    print(f"Found {len(markets)} BTC candidate markets")

    for i, market in enumerate(markets[:5], start=1):
        print("\n" + "=" * 80)
        print(f"MARKET #{i}")
        print("=" * 80)
        print(json.dumps(market, indent=2)[:5000])

if __name__ == "__main__":
    asyncio.run(main())