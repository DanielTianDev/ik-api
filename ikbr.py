import asyncio
from fastapi import Path
from ib_insync import IB, Stock, MarketOrder
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
import matplotlib.pyplot as plt
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:4200"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_ibkr_data():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    ib = IB()   
    ib.connect('127.0.0.1', 4002, clientId=1)
    connected = ib.isConnected()
    ib.reqMarketDataType(3)

    contract = Stock('MSFT', 'SMART', 'USD')
    ticker = ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    price = ticker.marketPrice()
    ib.disconnect()
    return {
        "connected": connected,
        "symbol": contract.symbol,
        "latest_price": price
    }

@app.get("/hello_ibkr")
async def hello_ibkr_endpoint():
    result = await run_in_threadpool(get_ibkr_data)
    return JSONResponse(result)

@app.get("/historical_stock/{symbol}")
async def historical_stock(symbol: str = Path(..., description="Stock symbol")):
    def get_historical():
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        ib = IB()
        ib.connect('127.0.0.1', 4002, clientId=2)
        contract = Stock(symbol.upper(), 'SMART', 'USD')
        end_date = ''
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='1 M',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        ib.disconnect()
        data = [
            {
                "date": bar.date.strftime('%Y-%m-%d'),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            }
            for bar in bars
        ]
        return data

    result = await run_in_threadpool(get_historical)
    return JSONResponse(result)

def execute_swing_trade():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=2)
    ib.reqMarketDataType(3)  # Use delayed data

    contract = Stock('AAPL', 'SMART', 'USD')
    ticker = ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    price = ticker.marketPrice()

    # Example swing trade logic
    if price > 150:  # Example condition
        order = MarketOrder('SELL', 10)
    else:
        order = MarketOrder('BUY', 10)

    trade = ib.placeOrder(contract, order)
    ib.sleep(2)
    ib.disconnect()

    return {
        "symbol": contract.symbol,
        "action": order.action,
        "quantity": order.totalQuantity,
        "price": price,
        "status": trade.orderStatus.status
    }

@app.get("/swing_trade")
async def swing_trade_endpoint():
    result = await run_in_threadpool(execute_swing_trade)
    return JSONResponse(result)

@app.get("/graph_results")
async def graph_results():
    # Example graphing logic
    data = {
        "dates": [datetime.now()],
        "prices": [150]  # Example data
    }

    plt.plot(data["dates"], data["prices"], marker='o')
    plt.title("Swing Trade Results")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.savefig("swing_trade_results.png")

    return JSONResponse({"message": "Graph saved as swing_trade_results.png"})

def get_account_balance():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=3)
    account_summary = ib.accountSummary()
    ib.disconnect()

    balance = next((item.value for item in account_summary if item.tag == 'NetLiquidation'), None)
    return {"balance": balance}

@app.get("/account_balance")
async def account_balance_endpoint():
    result = await run_in_threadpool(get_account_balance)
    return JSONResponse(result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ikbr:app", host="127.0.0.1", port=8000, reload=True)