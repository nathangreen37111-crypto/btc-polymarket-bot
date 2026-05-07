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

    enable_late_entry_model: bool = os.getenv("ENABLE_LATE_ENTRY_MODEL", "true").lower() == "true"

    late_5m_min_seconds_left: int = int(os.getenv("LATE_5M_MIN_SECONDS_LEFT", "30"))
    late_5m_max_seconds_left: int = int(os.getenv("LATE_5M_MAX_SECONDS_LEFT", "90"))

    late_15m_min_seconds_left: int = int(os.getenv("LATE_15M_MIN_SECONDS_LEFT", "60"))
    late_15m_max_seconds_left: int = int(os.getenv("LATE_15M_MAX_SECONDS_LEFT", "180"))

    enable_5m_momentum: bool = os.getenv("ENABLE_5M_MOMENTUM", "false").lower() == "true"
    enable_5m_late_entry: bool = os.getenv("ENABLE_5M_LATE_ENTRY", "true").lower() == "true"
    enable_5m_strong_momentum: bool = os.getenv("ENABLE_5M_STRONG_MOMENTUM", "true").lower() == "true"
    enable_5m_distance_start: bool = os.getenv("ENABLE_5M_DISTANCE_START", "true").lower() == "true"
    enable_5m_multitimeframe: bool = os.getenv("ENABLE_5M_MULTITIMEFRAME", "true").lower() == "true"
    enable_5m_volatility_filter: bool = os.getenv("ENABLE_5M_VOLATILITY_FILTER", "true").lower() == "true"
    enable_5m_odds_confirmation: bool = os.getenv("ENABLE_5M_ODDS_CONFIRMATION", "true").lower() == "true"
    enable_5m_reversal_filter: bool = os.getenv("ENABLE_5M_REVERSAL_FILTER", "true").lower() == "true"

    enable_15m_momentum: bool = os.getenv("ENABLE_15M_MOMENTUM", "true").lower() == "true"
    enable_15m_late_entry: bool = os.getenv("ENABLE_15M_LATE_ENTRY", "true").lower() == "true"
    enable_15m_distance_start: bool = os.getenv("ENABLE_15M_DISTANCE_START", "true").lower() == "true"
    enable_15m_multitimeframe: bool = os.getenv("ENABLE_15M_MULTITIMEFRAME", "true").lower() == "true"
    enable_15m_volatility_filter: bool = os.getenv("ENABLE_15M_VOLATILITY_FILTER", "true").lower() == "true"
    enable_15m_odds_confirmation: bool = os.getenv("ENABLE_15M_ODDS_CONFIRMATION", "true").lower() == "true"
    enable_15m_reversal_filter: bool = os.getenv("ENABLE_15M_REVERSAL_FILTER", "true").lower() == "true"

    min_momentum_5m_strong: float = float(os.getenv("MIN_MOMENTUM_5M_STRONG", "0.0008"))
    min_momentum_5m_late: float = float(os.getenv("MIN_MOMENTUM_5M_LATE", "0.0003"))
    max_entry_price_5m_strong: float = float(os.getenv("MAX_ENTRY_PRICE_5M_STRONG", "0.60"))
    max_entry_price_5m_late: float = float(os.getenv("MAX_ENTRY_PRICE_5M_LATE", "0.80"))

    strong_5m_min_seconds_left: int = int(os.getenv("STRONG_5M_MIN_SECONDS_LEFT", "90"))
    strong_5m_max_seconds_left: int = int(os.getenv("STRONG_5M_MAX_SECONDS_LEFT", "210"))

    min_momentum_15m: float = float(os.getenv("MIN_MOMENTUM_15M", "0.0003"))
    min_momentum_15m_late: float = float(os.getenv("MIN_MOMENTUM_15M_LATE", "0.00025"))
    max_entry_price_15m: float = float(os.getenv("MAX_ENTRY_PRICE_15M", "0.70"))
    max_entry_price_15m_late: float = float(os.getenv("MAX_ENTRY_PRICE_15M_LATE", "0.82"))

    min_distance_from_start_usd: float = float(os.getenv("MIN_DISTANCE_FROM_START_USD", "40"))
    max_volatility_1m: float = float(os.getenv("MAX_VOLATILITY_1M", "0.0015"))
    odds_confirmation_min_move: float = float(os.getenv("ODDS_CONFIRMATION_MIN_MOVE", "0.01"))
    reversal_spike_threshold: float = float(os.getenv("REVERSAL_SPIKE_THRESHOLD", "0.0012"))

    require_manual_approval: bool = os.getenv("REQUIRE_MANUAL_APPROVAL", "true").lower() == "true"

    paper_stake_usd: float = float(os.getenv("PAPER_STAKE_USD", "20"))
    paper_entry_price: float = float(os.getenv("PAPER_ENTRY_PRICE", "0.50"))
    min_momentum_pct: float = float(os.getenv("MIN_MOMENTUM_PCT", "0.0002"))

    polymarket_gamma_url: str = "https://gamma-api.polymarket.com"
    polymarket_clob_url: str = "https://clob.polymarket.com"

settings = Settings()
