from datetime import datetime, timedelta
from typing import List, Dict


class MockIBKRService:
    @staticmethod
    def get_mock_ticker_data(symbol: str) -> Dict:
        return {
            "connected": True,
            "symbol": symbol,
            "latest_price": 150.25
        }
    
    @staticmethod
    def get_mock_historical_data(symbol: str, days: int = 30) -> List[Dict]:
        data = []
        base_price = 145.0
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": base_price + i * 0.5,
                "high": base_price + i * 0.7,
                "low": base_price + i * 0.3,
                "close": base_price + i * 0.5,
                "volume": 1000000 + i * 50000
            })
        return data
    
    @staticmethod
    def get_mock_account_balance() -> Dict:
        return {"balance": "500000.00"}
    
    @staticmethod
    def get_mock_earliest_data(symbol: str) -> Dict:
        return {
            "symbol": symbol,
            "earliest_data_date": (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        }
    
    @staticmethod
    def get_mock_swing_trade() -> Dict:
        return {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 10,
            "price": 150.25,
            "status": "Submitted"
        }
