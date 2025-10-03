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

def get_ibkr_data(symbol: str = 'MSFT'):
    ib = IB()
    try:
        # Connect to IBKR
        ib.connect('127.0.0.1', 4002, clientId=1)
        connected = ib.isConnected()
        
        if not connected:
            return {"connected": False, "error": "Failed to connect to IBKR"}
        
        ib.reqMarketDataType(3)

        contract = Stock(symbol, 'SMART', 'USD')
        ticker = ib.reqMktData(contract, '', False, False)
        
        # Wait for market data with timeout
        ib.sleep(2)
        price = ticker.marketPrice()
        
        # Check if price is valid
        if price != price:  # Check for NaN
            return {
                "connected": connected,
                "symbol": contract.symbol,
                "error": "Market data not available",
                "latest_price": None
            }
        
        return {
            "connected": connected,
            "symbol": contract.symbol,
            "latest_price": price
        }
    
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }
    
    finally:
        # Always disconnect
        if ib.isConnected():
            ib.disconnect()

@app.get("/hello_ibkr/{symbol}")
async def hello_ibkr_endpoint(symbol: str = Path(..., description="Stock symbol")):
    result = await run_in_threadpool(get_ibkr_data, symbol)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("learning:app", host="127.0.0.1", port=8000, reload=True)