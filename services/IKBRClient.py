from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import Iterable, List, Optional
from datetime import datetime
from ib_insync import IB, Stock, Contract, BarDataList, Order, Trade
import logging

logger = logging.getLogger(__name__)

class IBKRConnectionError(Exception):
    """Raised when unable to connect to IBKR."""
    pass

class IBKRClient:
    """Thin wrapper around ib_insync with shared connection + helpers."""

    def __init__(self, host: str, port: int, client_id: int = 1) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id

    def _ensure_loop(self) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    @contextmanager
    def connection(self) -> Iterable[IB]:
        self._ensure_loop()
        ib = IB()
        try:
            ib.connect(self.host, self.port, clientId=self.client_id)
            yield ib
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {e}")
            raise IBKRConnectionError(f"Unable to connect to IBKR at {self.host}:{self.port}") from e
        finally:
            if ib.isConnected():
                ib.disconnect()

    def get_realtime_price(self, symbol: str, market_data_type: int = 3) -> float:
        with self.connection() as ib:
            ib.reqMarketDataType(market_data_type)
            contract = Stock(symbol.upper(), "SMART", "USD")
            ticker = ib.reqMktData(contract, "", False, False)
            ib.sleep(2)
            return ticker.marketPrice()

    def get_historical_data(
        self,
        symbol: str,
        duration: str,
        bar_size: str,
        what_to_show: str,
        end_time: str = "",
        use_rth: bool = True,
    ) -> BarDataList:
        with self.connection() as ib:
            contract = Stock(symbol.upper(), "SMART", "USD")
            return ib.reqHistoricalData(
                contract,
                endDateTime=end_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1,
            )

    def place_market_order(
        self, contract: Contract, order: Order, sleep_seconds: float = 2.0
    ) -> Trade:
        with self.connection() as ib:
            ib.reqMarketDataType(3)
            trade = ib.placeOrder(contract, order)
            ib.sleep(sleep_seconds)
            return trade

    def get_account_summary(self) -> List:
        with self.connection() as ib:
            return ib.accountSummary()
        
    def get_head_timestamp(self, symbol: str, what_to_show: str = 'TRADES') -> Optional[datetime]:
        with self.connection() as ib:
            contract = Stock(symbol.upper(), "SMART", "USD")
            return ib.reqHeadTimeStamp(contract, whatToShow=what_to_show, useRTH=True)
        
    