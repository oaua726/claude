import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class APIConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GMO_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("GMO_API_SECRET", ""))
    base_url: str = "https://api.click-sec.com"
    timeout: int = 10

@dataclass
class TradingConfig:
    symbol: str = "USD_JPY"          # 取引銘柄 (CFD: NK225, DOW, GOLD 等も可)
    lot_size: float = 1.0            # 1ロットのサイズ
    max_position: int = 3            # 最大ポジション数
    stop_loss_pips: float = 30.0     # 損切りpips
    take_profit_pips: float = 60.0   # 利確pips
    risk_per_trade_pct: float = 1.0  # 1トレードのリスク(口座残高の%)

@dataclass
class StrategyConfig:
    # RSI
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0

    # MACD
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    # Moving Average
    ma_short: int = 25
    ma_long: int = 75

    # Bollinger Bands
    bb_period: int = 20
    bb_std: float = 2.0

    # 実行間隔(秒)
    interval_seconds: int = 60

@dataclass
class Config:
    api: APIConfig = field(default_factory=APIConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    log_level: str = "INFO"
    dry_run: bool = True             # True=シミュレーションのみ(実際には注文しない)

config = Config()
