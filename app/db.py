import sqlite3
from pathlib import Path

DB_PATH = Path("data/bot.db")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS bot_ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            mode TEXT,
            btc_price REAL,
            candidate_markets INTEGER
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS paper_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            mode TEXT,
            strategy_name TEXT,
            market_type TEXT,
            side TEXT,
            stake_usd REAL,
            entry_price REAL,
            entry_btc_price REAL,
            exit_btc_price REAL,
            window_seconds INTEGER,
            seconds_left_at_entry INTEGER,
            momentum_pct REAL,
            status TEXT,
            won INTEGER,
            profit_usd REAL,
            reason TEXT
        )
        """)

        existing_columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(paper_bets)").fetchall()
        ]

        if "strategy_name" not in existing_columns:
            conn.execute("ALTER TABLE paper_bets ADD COLUMN strategy_name TEXT")

        if "seconds_left_at_entry" not in existing_columns:
            conn.execute("ALTER TABLE paper_bets ADD COLUMN seconds_left_at_entry INTEGER")

        conn.commit()

def log_tick(mode: str, btc_price: float, candidate_markets: int):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO bot_ticks (mode, btc_price, candidate_markets)
        VALUES (?, ?, ?)
        """, (mode, btc_price, candidate_markets))
        conn.commit()