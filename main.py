import asyncio
import os
from fastapi import Path, Query
from ib_insync import IB, Stock, MarketOrder
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
from datetime import datetime
from mock_data import MockIBKRService
from services.IKBRClient import IBKRClient



IB_PORT = 4002  # 4001 for live trading, 4002 for paper trading
IB_HOST = '127.0.0.1'
USE_MOCK = os.getenv('USE_MOCK', 'false').lower() == 'true'
app = FastAPI()
ib_client = IBKRClient(host=IB_HOST, port=IB_PORT, client_id=1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:4200"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_ibkr_data():
    price = ib_client.get_realtime_price('MSFT')
    return {"connected": True, "symbol": "MSFT", "latest_price": price}



@app.get("/historical_stock/{symbol}")
async def historical_stock(symbol: str = Path(...)):
    def fetch():
        bars = ib_client.get_historical_data(
            symbol=symbol,
            duration='1 M',
            bar_size='1 day',
            what_to_show='TRADES',
        )
        return [
            {
                "date": bar.date.strftime('%Y-%m-%d'),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]

    return JSONResponse(await run_in_threadpool(fetch))


def execute_swing_trade():
    price = ib_client.get_realtime_price('AAPL')
    order = MarketOrder('SELL' if price > 150 else 'BUY', 10)
    trade = ib_client.place_market_order(Stock('AAPL', 'SMART', 'USD'), order)
    return {
        "symbol": 'AAPL',
        "action": order.action,
        "quantity": order.totalQuantity,
        "price": price,
        "status": trade.orderStatus.status,
    }

def get_account_balance():
    summary = ib_client.get_account_summary()
    balance = next((item.value for item in summary if item.tag == 'NetLiquidation'), None)
    return {"balance": balance}

@app.get("/earliest_data/{symbol}")
async def get_earliest_data(symbol: str = Path(...)):
    if USE_MOCK:
        return JSONResponse(MockIBKRService.get_mock_earliest_data(symbol))

    def fetch():
        timestamp = ib_client.get_head_timestamp(symbol, what_to_show='TRADES')
        return {
            "symbol": symbol.upper(),
            "earliest_data_date": timestamp.strftime('%Y-%m-%d') if timestamp else None,
        }

    return JSONResponse(await run_in_threadpool(fetch))

@app.get("/add")
async def add_numbers(a: float = Query(...), b: float = Query(...)):
    """
    Test endpoint that adds two numbers.
    Example: /add?a=5&b=7 returns {"result": 12}
    """
    return {"result": a + b}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)