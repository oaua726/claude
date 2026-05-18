from enum import Enum
from dataclasses import dataclass
from typing import Optional

from gmo_cfd.analysis.indicators import IndicatorValues
from gmo_cfd.config import StrategyConfig


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradeSignal:
    signal: Signal
    reason: str
    strength: float = 0.0   # 0.0〜1.0 (強いほど確信度が高い)
    current_price: float = 0.0


def _rsi_signal(iv: IndicatorValues, cfg: StrategyConfig) -> Optional[Signal]:
    if iv.rsi is None:
        return None
    if iv.rsi < cfg.rsi_oversold:
        return Signal.BUY
    if iv.rsi > cfg.rsi_overbought:
        return Signal.SELL
    return None


def _macd_signal(iv: IndicatorValues) -> Optional[Signal]:
    if iv.macd is None or iv.macd_signal is None or iv.macd_hist is None:
        return None
    # ゼロライン上でMACDがシグナルを上抜け → BUY
    if iv.macd > iv.macd_signal and iv.macd_hist > 0 and iv.macd > 0:
        return Signal.BUY
    # ゼロライン下でMACDがシグナルを下抜け → SELL
    if iv.macd < iv.macd_signal and iv.macd_hist < 0 and iv.macd < 0:
        return Signal.SELL
    return None


def _ma_crossover_signal(iv: IndicatorValues) -> Optional[Signal]:
    if iv.ma_short is None or iv.ma_long is None:
        return None
    if iv.ma_short > iv.ma_long:
        return Signal.BUY
    if iv.ma_short < iv.ma_long:
        return Signal.SELL
    return None


def _bb_signal(iv: IndicatorValues, price: float) -> Optional[Signal]:
    if iv.bb_upper is None or iv.bb_lower is None:
        return None
    if price < iv.bb_lower:
        return Signal.BUY
    if price > iv.bb_upper:
        return Signal.SELL
    return None


def generate_signal(iv: IndicatorValues, price: float, cfg: StrategyConfig) -> TradeSignal:
    """複数指標を集約してトレードシグナルを生成する(多数決)"""
    votes: dict[Signal, int] = {Signal.BUY: 0, Signal.SELL: 0}
    reasons: list[str] = []

    checks = [
        ("RSI", _rsi_signal(iv, cfg)),
        ("MACD", _macd_signal(iv)),
        ("MA", _ma_crossover_signal(iv)),
        ("BB", _bb_signal(iv, price)),
    ]

    for name, sig in checks:
        if sig in (Signal.BUY, Signal.SELL):
            votes[sig] += 1
            reasons.append(f"{name}:{sig.value}")

    total = votes[Signal.BUY] + votes[Signal.SELL]
    if total == 0:
        return TradeSignal(Signal.HOLD, "No signals", 0.0, price)

    if votes[Signal.BUY] > votes[Signal.SELL]:
        strength = votes[Signal.BUY] / len(checks)
        return TradeSignal(Signal.BUY, ", ".join(reasons), strength, price)

    if votes[Signal.SELL] > votes[Signal.BUY]:
        strength = votes[Signal.SELL] / len(checks)
        return TradeSignal(Signal.SELL, ", ".join(reasons), strength, price)

    return TradeSignal(Signal.HOLD, "Conflicting signals", 0.0, price)
