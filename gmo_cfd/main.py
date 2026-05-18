"""
GMOクリックCFD 自動売買システム エントリーポイント

使い方:
  # シミュレーション(DRY-RUN)モードで起動
  python -m gmo_cfd.main

  # ライブトレードモードで起動(要APIキー設定)
  GMO_API_KEY=xxx GMO_API_SECRET=yyy DRY_RUN=false python -m gmo_cfd.main

  # バックテスト
  python -m gmo_cfd.main --backtest --csv path/to/data.csv
"""
import argparse
import os
import sys

from gmo_cfd.api.client import GMOClickClient
from gmo_cfd.trading.risk_manager import RiskManager
from gmo_cfd.trading.order_manager import OrderManager
from gmo_cfd.trading.strategy import TradingStrategy
from gmo_cfd.config import Config, APIConfig, TradingConfig, StrategyConfig
from gmo_cfd.utils.logger import logger, setup_logger


def build_config() -> Config:
    cfg = Config()
    # 環境変数でオーバーライド
    cfg.api.api_key = os.getenv("GMO_API_KEY", "")
    cfg.api.api_secret = os.getenv("GMO_API_SECRET", "")
    cfg.trading.symbol = os.getenv("SYMBOL", "USD_JPY")
    cfg.dry_run = os.getenv("DRY_RUN", "true").lower() not in ("false", "0", "no")
    cfg.log_level = os.getenv("LOG_LEVEL", "INFO")
    return cfg


def run_live(cfg: Config) -> None:
    if not cfg.dry_run and (not cfg.api.api_key or not cfg.api.api_secret):
        logger.error("APIキーが設定されていません。GMO_API_KEY / GMO_API_SECRET を設定してください。")
        sys.exit(1)

    client = GMOClickClient(cfg.api)
    risk_mgr = RiskManager(cfg.trading)
    order_mgr = OrderManager(client, risk_mgr, cfg)
    strategy = TradingStrategy(client, order_mgr, cfg)
    strategy.run_loop()


def run_backtest(cfg: Config, csv_path: str) -> None:
    from gmo_cfd.backtest import run_backtest as _backtest, load_csv
    logger.info(f"Loading data from: {csv_path}")
    df = load_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows")
    result = _backtest(df, cfg)
    print(result.summary())


def main() -> None:
    parser = argparse.ArgumentParser(description="GMOクリックCFD 自動売買システム")
    parser.add_argument("--backtest", action="store_true", help="バックテストモードで実行")
    parser.add_argument("--csv", type=str, help="バックテスト用CSVファイルパス")
    parser.add_argument("--symbol", type=str, help="取引銘柄 (例: USD_JPY, NK225)")
    parser.add_argument("--dry-run", action="store_true", default=None, help="DRY-RUNモード")
    parser.add_argument("--live", action="store_true", help="ライブトレードモード")
    args = parser.parse_args()

    cfg = build_config()
    setup_logger("gmo_cfd", cfg.log_level)

    if args.symbol:
        cfg.trading.symbol = args.symbol
    if args.live:
        cfg.dry_run = False
    if args.dry_run:
        cfg.dry_run = True

    if args.backtest:
        if not args.csv:
            logger.error("--backtest には --csv が必要です")
            sys.exit(1)
        run_backtest(cfg, args.csv)
    else:
        run_live(cfg)


if __name__ == "__main__":
    main()
