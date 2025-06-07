from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🔧 Helper: Get current price from yfinance ---
def get_current_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        return data["Close"].iloc[-1]  # Last closing price
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

# --- 🔌 API Endpoint: Get current stock price ---
@app.get("/price/{symbol}")
def price(symbol: str):
    price = get_current_price(symbol.upper())
    if price is not None:
        return {"symbol": symbol.upper(), "current_price": round(price, 2)}
    else:
        return {"symbol": symbol.upper(), "current_price": None, "error": "Could not fetch data"} 
    


@app.get("/history/{symbol}")
def get_historical_data(
    symbol: str,
    start: str = Query(..., description="Start date in YYYY-MM-DD"),
    end: str = Query(..., description="End date in YYYY-MM-DD"),
    interval: str = Query("1d", description="Interval: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo"),
):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start, end=end, interval=interval)

        if data.empty:
            return {"symbol": symbol.upper(), "history": [], "error": "No data found."}

        # Convert DataFrame to list of dictionaries
        history = [
            {
                "datetime": idx.strftime("%Y-%m-%d %H:%M:%S"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            }
            for idx, row in data.iterrows()
        ]

        return {"symbol": symbol.upper(), "interval": interval, "history": history}
    except Exception as e:
        return {"symbol": symbol.upper(), "error": str(e)}










# import asyncio
# from ib_insync import IB, Stock
# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from fastapi.concurrency import run_in_threadpool

# app = FastAPI()

# def get_ibkr_data():
#     try:
#         asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#     ib = IB()
#     ib.connect('127.0.0.1', 4002, clientId=1)
#     connected = ib.isConnected()
#     ib.reqMarketDataType(3)
#     contract = Stock('MSFT', 'SMART', 'USD')
#     ticker = ib.reqMktData(contract, '', False, False)
#     ib.sleep(2)
#     price = ticker.marketPrice()
#     ib.disconnect()
#     return {
#         "connected": connected,
#         "symbol": contract.symbol,
#         "latest_price": price
#     }

# @app.get("/hello_ibkr")
# async def hello_ibkr_endpoint():
#     result = await run_in_threadpool(get_ibkr_data)
#     return JSONResponse(result)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("ikbr:app", host="127.0.0.1", port=8000, reload=True)



