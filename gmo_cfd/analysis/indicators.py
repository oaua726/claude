import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class IndicatorValues:
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    ma_short: Optional[float] = None
    ma_long: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None


def calc_rsi(closes: pd.Series, period: int = 14) -> pd.Series:
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_macd(
    closes: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = closes.ewm(span=fast, adjust=False).mean()
    ema_slow = closes.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger_bands(
    closes: pd.Series,
    period: int = 20,
    std_mult: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    middle = closes.rolling(period).mean()
    std = closes.rolling(period).std()
    return middle + std_mult * std, middle, middle - std_mult * std


def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period).mean()


def compute_indicators(df: pd.DataFrame, cfg) -> IndicatorValues:
    """DataFrameからIndicatorValuesを計算して返す"""
    closes = df["close"]
    highs = df["high"]
    lows = df["low"]

    rsi = calc_rsi(closes, cfg.rsi_period)
    macd_line, sig_line, hist = calc_macd(closes, cfg.macd_fast, cfg.macd_slow, cfg.macd_signal)
    bb_upper, bb_mid, bb_lower = calc_bollinger_bands(closes, cfg.bb_period, cfg.bb_std)
    atr = calc_atr(highs, lows, closes)

    ma_short = closes.rolling(cfg.ma_short).mean()
    ma_long = closes.rolling(cfg.ma_long).mean()

    def last(s: pd.Series) -> Optional[float]:
        v = s.iloc[-1]
        return float(v) if not np.isnan(v) else None

    return IndicatorValues(
        rsi=last(rsi),
        macd=last(macd_line),
        macd_signal=last(sig_line),
        macd_hist=last(hist),
        ma_short=last(ma_short),
        ma_long=last(ma_long),
        bb_upper=last(bb_upper),
        bb_middle=last(bb_mid),
        bb_lower=last(bb_lower),
        atr=last(atr),
    )
