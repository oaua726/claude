from typing import Optional

from gmo_cfd.api.client import GMOClickClient, GMOClickAPIError
from gmo_cfd.analysis.signals import TradeSignal, Signal
from gmo_cfd.trading.risk_manager import RiskManager, OrderParams
from gmo_cfd.config import Config
from gmo_cfd.utils.logger import logger


class OrderManager:
    """注文発注・ポジション管理"""

    def __init__(self, client: GMOClickClient, risk_mgr: RiskManager, cfg: Config):
        self.client = client
        self.risk_mgr = risk_mgr
        self.cfg = cfg

    def _get_balance(self) -> float:
        try:
            data = self.client.get_account()
            if isinstance(data, list):
                data = data[0]
            return float(data.get("availableAmount", 0))
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return 0.0

    def _get_open_positions(self) -> list:
        try:
            return self.client.get_positions(self.cfg.trading.symbol)
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []

    def execute_signal(self, signal: TradeSignal, atr: Optional[float] = None) -> bool:
        if signal.signal == Signal.HOLD:
            logger.info("Signal: HOLD — no action")
            return False

        # 強度フィルター (2/4指標以上が一致していないと発注しない)
        if signal.strength < 0.5:
            logger.info(f"Signal strength too low ({signal.strength:.2f}), skip")
            return False

        positions = self._get_open_positions()

        # 既に同方向のポジションがある場合はスキップ
        for pos in positions:
            if pos.get("side") == signal.signal.value:
                logger.info(f"Already have {signal.signal.value} position, skip")
                return False

        if not self.risk_mgr.check_max_positions(len(positions)):
            return False

        balance = self._get_balance()
        if balance <= 0:
            logger.warning("No available balance")
            return False

        params = self.risk_mgr.calc_order_params(
            side=signal.signal.value,
            price=signal.current_price,
            account_balance=balance,
            atr=atr,
        )
        if params is None:
            return False

        return self._place_order(params, signal)

    def _place_order(self, params: OrderParams, signal: TradeSignal) -> bool:
        symbol = self.cfg.trading.symbol

        if self.cfg.dry_run:
            logger.info(
                f"[DRY-RUN] Order: {symbol} {params.side} {params.size}lot "
                f"@ {signal.current_price:.4f} SL={params.stop_loss:.4f} TP={params.take_profit:.4f} "
                f"reason=[{signal.reason}]"
            )
            return True

        try:
            result = self.client.place_order(
                symbol=symbol,
                side=params.side,
                size=params.size,
                order_type="MARKET",
                stop_loss=params.stop_loss,
                take_profit=params.take_profit,
            )
            order_id = result.get("orderId", "?")
            logger.info(
                f"Order placed: {symbol} {params.side} {params.size}lot "
                f"orderId={order_id} reason=[{signal.reason}]"
            )
            return True
        except GMOClickAPIError as e:
            logger.error(f"Order failed: {e}")
            return False

    def close_all_positions(self) -> None:
        """全ポジションを成行決済"""
        positions = self._get_open_positions()
        if not positions:
            logger.info("No positions to close")
            return

        for pos in positions:
            pos_id = pos.get("positionId")
            side = "SELL" if pos.get("side") == "BUY" else "BUY"
            size = float(pos.get("size", 0))
            symbol = pos.get("symbol", self.cfg.trading.symbol)

            if self.cfg.dry_run:
                logger.info(f"[DRY-RUN] Close: {symbol} {pos_id} {side} {size}lot")
                continue

            try:
                self.client.close_position(pos_id, symbol, side, size)
                logger.info(f"Closed position {pos_id}")
            except GMOClickAPIError as e:
                logger.error(f"Failed to close position {pos_id}: {e}")
