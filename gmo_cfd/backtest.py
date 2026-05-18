"""
バックテストモジュール
過去のローソク足データを使って戦略の有効性を検証する
"""
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
import numpy as np

from gmo_cfd.analysis.indicators import compute_indicators
from gmo_cfd.analysis.signals import generate_signal, Signal
from gmo_cfd.config import Config
from gmo_cfd.utils.logger import logger


@dataclass
class Trade:
    entry_time: str
    exit_time: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    reason: str


@dataclass
class BacktestResult:
    trades: list = field(default_factory=list)
    total_pnl: float = 0.0
    win_count: int = 0
    loss_count: int = 0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0

    @property
    def total_trades(self) -> int:
        return self.win_count + self.loss_count

    @property
    def win_rate(self) -> float:
        return self.win_count / self.total_trades if self.total_trades > 0 else 0.0

    def summary(self) -> str:
        return (
            f"=== Backtest Result ===\n"
            f"Total Trades : {self.total_trades}\n"
            f"Win / Loss   : {self.win_count} / {self.loss_count}\n"
            f"Win Rate     : {self.win_rate:.1%}\n"
            f"Total PnL    : {self.total_pnl:+.2f}\n"
            f"Max Drawdown : {self.max_drawdown:.2f}\n"
            f"Sharpe Ratio : {self.sharpe_ratio:.2f}\n"
        )


def run_backtest(df: pd.DataFrame, cfg: Config) -> BacktestResult:
    """
    DataFrame(OHLCV)に対してバックテストを実行する。
    dfはカラム: open, high, low, close, volume を持つこと。
    """
    result = BacktestResult()
    sl_pips = cfg.trading.stop_loss_pips
    tp_pips = cfg.trading.take_profit_pips
    pip = 0.01

    position: Optional[dict] = None
    equity_curve: list[float] = [0.0]
    min_bars = cfg.strategy.ma_long + 1

    for i in range(min_bars, len(df)):
        window = df.iloc[:i]
        iv = compute_indicators(window, cfg.strategy)
        price = float(window["close"].iloc[-1])
        signal = generate_signal(iv, price, cfg.strategy)

        # ポジションのSL/TP確認
        if position is not None:
            hi = float(df["high"].iloc[i])
            lo = float(df["low"].iloc[i])
            side = position["side"]
            sl = position["sl"]
            tp = position["tp"]
            exit_price: Optional[float] = None
            exit_reason = ""

            if side == "BUY":
                if lo <= sl:
                    exit_price, exit_reason = sl, "SL"
                elif hi >= tp:
                    exit_price, exit_reason = tp, "TP"
            else:
                if hi >= sl:
                    exit_price, exit_reason = sl, "SL"
                elif lo <= tp:
                    exit_price, exit_reason = tp, "TP"

            if exit_price is not None:
                ep = position["entry_price"]
                multiplier = 1 if side == "BUY" else -1
                pnl = (exit_price - ep) * multiplier * position["size"] / pip
                result.total_pnl += pnl
                equity_curve.append(equity_curve[-1] + pnl)

                trade = Trade(
                    entry_time=position["entry_time"],
                    exit_time=str(df.index[i] if hasattr(df.index, '__getitem__') else i),
                    side=side,
                    entry_price=ep,
                    exit_price=exit_price,
                    size=position["size"],
                    pnl=pnl,
                    reason=exit_reason,
                )
                result.trades.append(trade)
                if pnl > 0:
                    result.win_count += 1
                else:
                    result.loss_count += 1
                position = None
                continue

        # 新規エントリー
        if position is None and signal.signal != Signal.HOLD and signal.strength >= 0.5:
            side = signal.signal.value
            if side == "BUY":
                sl = price - sl_pips * pip
                tp = price + tp_pips * pip
            else:
                sl = price + sl_pips * pip
                tp = price - tp_pips * pip
            position = {
                "side": side,
                "entry_price": price,
                "sl": sl,
                "tp": tp,
                "size": cfg.trading.lot_size,
                "entry_time": str(df.index[i] if hasattr(df.index, '__getitem__') else i),
            }

    # 最大ドローダウン計算
    equity = np.array(equity_curve)
    peak = np.maximum.accumulate(equity)
    drawdowns = peak - equity
    result.max_drawdown = float(drawdowns.max()) if len(drawdowns) > 0 else 0.0

    # シャープレシオ
    if len(result.trades) > 1:
        pnls = [t.pnl for t in result.trades]
        mean_pnl = np.mean(pnls)
        std_pnl = np.std(pnls)
        result.sharpe_ratio = float(mean_pnl / std_pnl * np.sqrt(252)) if std_pnl > 0 else 0.0

    return result


def load_csv(path: str) -> pd.DataFrame:
    """CSVファイルからOHLCVデータを読み込む
    期待するカラム: time/date, open, high, low, close, volume
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    col_map = {
        "date": "time", "datetime": "time", "timestamp": "time",
        "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume",
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["close"], inplace=True)
    return df
