import time
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from gmo_cfd.api.client import GMOClickClient
from gmo_cfd.analysis.indicators import compute_indicators
from gmo_cfd.analysis.signals import generate_signal
from gmo_cfd.trading.order_manager import OrderManager
from gmo_cfd.config import Config
from gmo_cfd.utils.logger import logger


def _klines_to_df(klines: list) -> Optional[pd.DataFrame]:
    if not klines:
        return None
    df = pd.DataFrame(klines)
    rename = {
        "openTime": "time", "openPrice": "open", "highPrice": "high",
        "lowPrice": "low", "closePrice": "close", "volume": "volume",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["close"], inplace=True)
    return df


def _get_current_price(ticker_data) -> Optional[float]:
    if isinstance(ticker_data, list):
        ticker_data = ticker_data[0] if ticker_data else {}
    ask = ticker_data.get("ask")
    bid = ticker_data.get("bid")
    if ask and bid:
        return (float(ask) + float(bid)) / 2
    if ask:
        return float(ask)
    if bid:
        return float(bid)
    return None


class TradingStrategy:
    """メイン戦略ループ: データ取得 → 指標計算 → シグナル生成 → 注文"""

    def __init__(self, client: GMOClickClient, order_mgr: OrderManager, cfg: Config):
        self.client = client
        self.order_mgr = order_mgr
        self.cfg = cfg
        self.symbol = cfg.trading.symbol

    def run_once(self) -> None:
        """1サイクルの処理"""
        try:
            ticker = self.client.get_ticker(self.symbol)
            price = _get_current_price(ticker)
            if price is None:
                logger.warning("Could not get current price")
                return

            klines = self.client.get_klines(self.symbol, interval="5min")
            df = _klines_to_df(klines)
            if df is None or len(df) < self.cfg.strategy.ma_long:
                logger.warning(f"Not enough candle data (got {len(df) if df is not None else 0})")
                return

            iv = compute_indicators(df, self.cfg.strategy)
            signal = generate_signal(iv, price, self.cfg.strategy)

            logger.info(
                f"{self.symbol} @ {price:.4f} | "
                f"RSI={iv.rsi:.1f} MACD={iv.macd:.4f} "
                f"MA({self.cfg.strategy.ma_short}/{self.cfg.strategy.ma_long})="
                f"{iv.ma_short:.4f}/{iv.ma_long:.4f} | "
                f"Signal: {signal.signal.value} [{signal.reason}] strength={signal.strength:.2f}"
            )

            self.order_mgr.execute_signal(signal, atr=iv.atr)

        except Exception as e:
            logger.error(f"Strategy error: {e}", exc_info=True)

    def run_loop(self) -> None:
        """定期実行ループ"""
        interval = self.cfg.strategy.interval_seconds
        mode = "DRY-RUN" if self.cfg.dry_run else "LIVE"
        logger.info(f"Starting strategy loop [{mode}] symbol={self.symbol} interval={interval}s")

        while True:
            self.run_once()
            logger.debug(f"Sleeping {interval}s...")
            time.sleep(interval)
