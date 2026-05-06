from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    mode: str = os.getenv("BOT_MODE", "research")

    max_trade_usd: float = float(os.getenv("MAX_TRADE_USD", "20"))
    max_daily_loss_usd: float = float(os.getenv("MAX_DAILY_LOSS_USD", "60"))
    max_open_positions: int = int(os.getenv("MAX_OPEN_POSITIONS", "1"))

    min_edge: float = float(os.getenv("MIN_EDGE", "0.06"))
    max_spread: float = float(os.getenv("MAX_SPREAD", "0.04"))

    trade_5m: bool = os.getenv("TRADE_5M", "true").lower() == "true"
    trade_15m: bool = os.getenv("TRADE_15M", "true").lower() == "true"

    require_manual_approval: bool = os.getenv("REQUIRE_MANUAL_APPROVAL", "true").lower() == "true"

    paper_stake_usd: float = float(os.getenv("PAPER_STAKE_USD", "20"))
    paper_entry_price: float = float(os.getenv("PAPER_ENTRY_PRICE", "0.50"))
    min_momentum_pct: float = float(os.getenv("MIN_MOMENTUM_PCT", "0.0002"))

    polymarket_gamma_url: str = "https://gamma-api.polymarket.com"
    polymarket_clob_url: str = "https://clob.polymarket.com"

settings = Settings()
