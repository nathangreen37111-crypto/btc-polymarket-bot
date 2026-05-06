import httpx

COINBASE_PRICE_URL = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
KRAKEN_PRICE_URL = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"

async def get_btc_price_from_coinbase() -> float:
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(
            COINBASE_PRICE_URL,
            headers={"User-Agent": "btc-polymarket-research-bot/0.1"},
        )
        response.raise_for_status()
        data = response.json()
        return float(data["price"])

async def get_btc_price_from_kraken() -> float:
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(
            KRAKEN_PRICE_URL,
            headers={"User-Agent": "btc-polymarket-research-bot/0.1"},
        )
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            raise RuntimeError(f"Kraken API error: {data['error']}")

        pair_data = next(iter(data["result"].values()))
        return float(pair_data["c"][0])

async def get_btc_price() -> float:
    try:
        return await get_btc_price_from_coinbase()
    except Exception as coinbase_error:
        print(f"Coinbase price failed, trying Kraken: {coinbase_error}")
        return await get_btc_price_from_kraken()
