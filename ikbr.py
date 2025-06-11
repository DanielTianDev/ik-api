import asyncio
from fastapi import Path, Query
from ib_insync import IB, Stock, MarketOrder
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
import matplotlib.pyplot as plt
from datetime import datetime

IB_PORT = 4002  # 4001 for live trading, 4002 for paper trading
IB_HOST = '127.0.0.1'
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
    ib.connect(IB_HOST, IB_PORT, clientId=1) #4001 is for paper trading, 4002 for live trading
    connected = ib.isConnected()
    ib.reqMarketDataType(3)

    contract = Stock('VOO', 'SMART', 'USD')
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
        ib.connect(IB_HOST, IB_PORT, clientId=2)
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


@app.get("/historical_stock_custom/")
async def historical_stock_custom(
    symbol: str = Query(..., description="Stock symbol"),
    end_date: str = Query('', description="End date (format: YYYY-MM-DD, empty for now)"),
    duration_str: str = Query('1 M', description="Duration string (e.g., '1 D', '1 W', '1 M', '1 Y')"),
    bar_size_setting: str = Query('1 day', description="Bar size (e.g., '1 min', '5 mins', '1 hour', '1 day')"),
    what_to_show: str = Query('TRADES', description="What to show (e.g., 'TRADES', 'MIDPOINT', 'BID', 'ASK', etc.)")
):
    def get_historical():
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        ib = IB()
        ib.connect('127.0.0.1', 4002, clientId=2)
        contract = Stock(symbol.upper(), 'SMART', 'USD')
        
        # Convert date format from YYYY-MM-DD to YYYYMMDD 00:00:00
        formatted_end_date = ''
        if end_date:
            try:
                # Parse the input date and format it for IBKR
                date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                formatted_end_date = date_obj.strftime('%Y%m%d 00:00:00')
            except ValueError:
                # If date parsing fails, use empty string (current time)
                formatted_end_date = ''
        
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=formatted_end_date,
            durationStr=duration_str,
            barSizeSetting=bar_size_setting,
            whatToShow=what_to_show,
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

@app.get("/earliest_data/{symbol}")
async def get_earliest_data(symbol: str = Path(..., description="Stock symbol")):
    def get_earliest():
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        ib = IB()
        ib.connect(IB_HOST, IB_PORT, clientId=4)
        contract = Stock(symbol.upper(), 'SMART', 'USD')
        
        # Get the earliest available timestamp
        head_timestamp = ib.reqHeadTimeStamp(
            contract,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        
        ib.disconnect()
        
        return {
            "symbol": symbol.upper(),
            "earliest_data_date": head_timestamp.strftime('%Y-%m-%d') if head_timestamp else None
        }

    result = await run_in_threadpool(get_earliest)
    return JSONResponse(result)

def execute_swing_trade():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=2)
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
    ib.connect(IB_HOST, IB_PORT, clientId=3)
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