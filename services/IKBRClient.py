from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import Iterable, List, Optional
from datetime import datetime
from ib_insync import IB, Stock, Contract, BarDataList, Order, Trade
import logging
import matplotlib.pyplot as plt
import os

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
        

    def generate_historical_graph(
        self,
        symbol: str,
        duration: str = "1 M",
        bar_size: str = "1 day",
        output_dir: str = "graphs",
    ) -> Optional[str]:
        """
        Fetches historical data and generates a graph, saving it as a PNG file.

        Args:
            symbol: The stock symbol.
            duration: The duration to fetch data for (e.g., '1 M', '1 Y').
            bar_size: The bar size for the data (e.g., '1 day', '1 hour').
            output_dir: The directory to save the graph in.

        Returns:
            The file path of the generated graph, or None if no data was found.
        """
        bars = self.get_historical_data(
            symbol=symbol,
            duration=duration,
            bar_size=bar_size,
            what_to_show="TRADES",
        )

        if not bars:
            logger.warning(f"No historical data found for {symbol}")
            return None

        dates = [bar.date for bar in bars]
        closes = [bar.close for bar in bars]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, closes, marker="o")
        plt.title(f"{symbol.upper()} Historical Close Prices ({duration})")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{symbol.lower()}_{duration.replace(' ', '')}_{bar_size.replace(' ', '')}_historical.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath)
        plt.close()

        logger.info(f"Generated historical graph for {symbol} at {filepath}")
        return filepath