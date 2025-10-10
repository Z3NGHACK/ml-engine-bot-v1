# ============================================
# FILE: utils/preprocessor.py
# ============================================
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataPreprocessor:
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def prepare_for_ml(self, df, lookback=60):
        """Prepare data for ML training"""
        if df is None or len(df) < lookback:
            return None, None
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(df[['close']])
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)
    
    def inverse_transform(self, scaled_prices):
        """Convert scaled prices back to original scale"""
        return self.scaler.inverse_transform(scaled_prices)