import hashlib
import hmac
import time
import json
from typing import Any, Optional
from urllib.parse import urlencode

import requests

from gmo_cfd.config import APIConfig
from gmo_cfd.utils.logger import logger


class GMOClickAPIError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(f"API Error {status}: {message}")


class GMOClickClient:
    """GMOクリック証券 CFD REST APIクライアント"""

    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        message = timestamp + method + path + body
        return hmac.new(
            self.config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def _headers(self, method: str, path: str, body: str = "") -> dict:
        ts = str(int(time.time() * 1000))
        return {
            "API-KEY": self.config.api_key,
            "API-TIMESTAMP": ts,
            "API-SIGN": self._sign(ts, method, path, body),
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        public: bool = False,
    ) -> Any:
        url = self.config.base_url + path
        body = json.dumps(data) if data else ""
        headers = {} if public else self._headers(method, path, body)

        try:
            resp = self.session.request(
                method,
                url,
                params=params,
                data=body or None,
                headers=headers,
                timeout=self.config.timeout,
            )
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        status = result.get("status", 0)
        if status != 0:
            msgs = result.get("messages", [{}])
            msg = msgs[0].get("message_string", "Unknown error") if msgs else "Unknown error"
            raise GMOClickAPIError(status, msg)

        return result.get("data", result)

    # ── 公開API ──────────────────────────────────────────────────

    def get_ticker(self, symbol: str) -> dict:
        """現在の気配値を取得"""
        return self._request("GET", "/v1/ticker", params={"symbol": symbol}, public=True)

    def get_orderbooks(self, symbol: str) -> dict:
        """板情報を取得"""
        return self._request("GET", "/v1/orderbooks", params={"symbol": symbol}, public=True)

    def get_klines(self, symbol: str, interval: str = "1min", date: Optional[str] = None) -> list:
        """ローソク足データを取得
        interval: 1min, 5min, 10min, 15min, 30min, 1hour, 4hour, 8hour, 12hour, 1day, 1week, 1month
        """
        params: dict = {"symbol": symbol, "interval": interval}
        if date:
            params["date"] = date
        return self._request("GET", "/v1/klines", params=params, public=True)

    # ── 認証API ──────────────────────────────────────────────────

    def get_account(self) -> dict:
        """口座残高・証拠金情報を取得"""
        return self._request("GET", "/v1/account/margin")

    def get_positions(self, symbol: Optional[str] = None) -> list:
        """保有ポジション一覧を取得"""
        params = {"symbol": symbol} if symbol else {}
        data = self._request("GET", "/v1/openPositions", params=params)
        return data.get("list", []) if isinstance(data, dict) else data

    def get_orders(self, symbol: Optional[str] = None) -> list:
        """注文一覧を取得"""
        params = {"symbol": symbol} if symbol else {}
        data = self._request("GET", "/v1/activeOrders", params=params)
        return data.get("list", []) if isinstance(data, dict) else data

    def place_order(
        self,
        symbol: str,
        side: str,          # "BUY" or "SELL"
        size: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        time_in_force: str = "FAK",
    ) -> dict:
        """注文を発注する"""
        body: dict = {
            "symbol": symbol,
            "side": side,
            "executionType": order_type,
            "size": str(size),
            "timeInForce": time_in_force,
        }
        if price is not None:
            body["price"] = str(price)
        if stop_loss is not None:
            body["losscutPrice"] = str(stop_loss)
        if take_profit is not None:
            body["takeProfitPrice"] = str(take_profit)

        return self._request("POST", "/v1/order", data=body)

    def close_position(self, position_id: str, symbol: str, side: str, size: float) -> dict:
        """ポジションを決済する"""
        body = {
            "positionId": position_id,
            "symbol": symbol,
            "side": side,
            "executionType": "MARKET",
            "size": str(size),
            "timeInForce": "FAK",
        }
        return self._request("POST", "/v1/closeOrder", data=body)

    def cancel_order(self, order_id: str) -> dict:
        """注文をキャンセルする"""
        return self._request("POST", "/v1/cancelOrder", data={"orderId": order_id})
