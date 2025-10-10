# ============================================
# FILE: utils/data_loader.py
# ============================================
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import config

class DataLoader:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URI)
        self.db = self.client.crypto_data
        self.collection = self.db.marketdatas
    
    def load_data(self, symbol, days=30, interval='1m'):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        cursor = self.collection.find({
            'symbol': symbol,
            'interval': interval,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }).sort('timestamp', 1)
        
        data = list(cursor)
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']]
    
    def get_latest_candles(self, symbol, limit=100):
        cursor = self.collection.find({
            'symbol': symbol,
            'interval': '1m'
        }).sort('timestamp', -1).limit(limit)
        
        data = list(cursor)
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = df.sort_index()
        return df[['open', 'high', 'low', 'close', 'volume']]