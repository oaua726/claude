from dataclasses import dataclass
from typing import Optional

from gmo_cfd.config import TradingConfig
from gmo_cfd.utils.logger import logger


@dataclass
class OrderParams:
    side: str
    size: float
    stop_loss: float
    take_profit: float


class RiskManager:
    """リスク管理: ポジションサイジング・損切り・利確価格の計算"""

    def __init__(self, cfg: TradingConfig):
        self.cfg = cfg

    def calc_order_params(
        self,
        side: str,
        price: float,
        account_balance: float,
        pip_value: float = 0.01,   # 1pipの価値(銘柄によって異なる)
        atr: Optional[float] = None,
    ) -> Optional[OrderParams]:
        # ATRベースの損切り幅(設定値と比較して大きい方を使用)
        sl_pips = self.cfg.stop_loss_pips
        if atr is not None:
            atr_pips = atr / pip_value
            sl_pips = max(sl_pips, atr_pips * 1.5)  # ATRの1.5倍を最低損切り幅とする

        # リスクベースのポジションサイジング
        risk_amount = account_balance * (self.cfg.risk_per_trade_pct / 100)
        size = risk_amount / (sl_pips * pip_value)
        size = max(self.cfg.lot_size, round(size, 1))

        if side == "BUY":
            sl = price - sl_pips * pip_value
            tp = price + self.cfg.take_profit_pips * pip_value
        else:
            sl = price + sl_pips * pip_value
            tp = price - self.cfg.take_profit_pips * pip_value

        logger.info(
            f"RiskManager: side={side} size={size} SL={sl:.4f} TP={tp:.4f} "
            f"risk¥={risk_amount:.0f}"
        )
        return OrderParams(side=side, size=size, stop_loss=sl, take_profit=tp)

    def check_max_positions(self, current_positions: int) -> bool:
        if current_positions >= self.cfg.max_position:
            logger.warning(
                f"Max positions reached ({current_positions}/{self.cfg.max_position})"
            )
            return False
        return True
