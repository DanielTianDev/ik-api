import asyncio
from fastapi import Path
from ib_insync import IB, Stock
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

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
            durationStr='3 M',
            barSizeSetting='1 week',
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ikbr:app", host="127.0.0.1", port=8000, reload=True)