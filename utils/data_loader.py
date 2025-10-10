# ============================================
# FILE: utils/data_loader.py
# ============================================
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import config

class DataLoader:
    def __init__(self):
        try:
            self.client = MongoClient(config.MONGODB_URI)
            self.db = self.client[config.DATABASE_NAME]  # ✅ Use 'test' database
            self.collection = self.db[config.COLLECTION_NAME]
            
            # Test connection
            self.client.server_info()
            print(f"✅ DataLoader connected to {config.DATABASE_NAME}.{config.COLLECTION_NAME}")
        except Exception as e:
            print(f"❌ DataLoader connection failed: {e}")
            raise
    
    def get_latest_candles(self, symbol, limit=100):
        """Get the latest N candles for a symbol"""
        try:
            # Query MongoDB
            cursor = self.collection.find(
                {'symbol': symbol},
                {'_id': 0}  # Exclude MongoDB _id field
            ).sort('timestamp', -1).limit(limit)
            
            # Convert to DataFrame
            data = list(cursor)
            
            if not data:
                print(f"⚠️ No data found for {symbol}")
                return None
            
            df = pd.DataFrame(data)
            
            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                df.set_index('timestamp', inplace=True)
            
            print(f"✅ Loaded {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data for {symbol}: {e}")
            return None
    
    def get_candles_by_date_range(self, symbol, start_date, end_date):
        """Get candles within a date range"""
        try:
            cursor = self.collection.find({
                'symbol': symbol,
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }, {'_id': 0}).sort('timestamp', 1)
            
            data = list(cursor)
            if not data:
                return None
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading date range for {symbol}: {e}")
            return None
    
    def get_all_symbols(self):
        """Get list of all available symbols"""
        try:
            symbols = self.collection.distinct('symbol')
            return symbols
        except Exception as e:
            print(f"❌ Error getting symbols: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()