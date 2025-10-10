# ============================================
# FILE: analysis/technical.py
# ============================================
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
import config

class TechnicalAnalyzer:
    def calculate_all_indicators(self, df):
        if df is None or len(df) < 50:
            return None
        
        result = pd.DataFrame(index=df.index)
        result['close'] = df['close']
        result['volume'] = df['volume']
        
        rsi = RSIIndicator(df['close'], window=config.RSI_PERIOD)
        result['rsi'] = rsi.rsi()
        
        macd = MACD(df['close'], window_fast=config.MACD_FAST,
                    window_slow=config.MACD_SLOW, window_sign=config.MACD_SIGNAL)
        result['macd'] = macd.macd()
        result['macd_signal'] = macd.macd_signal()
        result['macd_histogram'] = macd.macd_diff()
        
        bb = BollingerBands(df['close'], window=config.BB_PERIOD, window_dev=config.BB_STD)
        result['bb_upper'] = bb.bollinger_hband()
        result['bb_middle'] = bb.bollinger_mavg()
        result['bb_lower'] = bb.bollinger_lband()
        
        ema_fast = EMAIndicator(df['close'], window=config.EMA_FAST)
        ema_slow = EMAIndicator(df['close'], window=config.EMA_SLOW)
        result['ema_fast'] = ema_fast.ema_indicator()
        result['ema_slow'] = ema_slow.ema_indicator()
        
        result['price_change'] = df['close'].pct_change()
        result['volume_change'] = df['volume'].pct_change()
        
        return result.dropna()
    
    def generate_signal(self, df):
        if df is None or len(df) == 0:
            return None
        
        latest = df.iloc[-1]
        
        long_score = 0
        short_score = 0
        
        if latest['rsi'] < 30:
            long_score += 25
        elif latest['rsi'] > 70:
            short_score += 25
        
        if latest['macd_histogram'] > 0:
            long_score += 20
        else:
            short_score += 20
        
        bb_range = latest['bb_upper'] - latest['bb_lower']
        if bb_range > 0:
            bb_position = (latest['close'] - latest['bb_lower']) / bb_range
            if bb_position < 0.2:
                long_score += 20
            elif bb_position > 0.8:
                short_score += 20
        
        if latest['ema_fast'] > latest['ema_slow']:
            long_score += 20
        else:
            short_score += 20
        
        signal_type = None
        confidence = 0
        
        if long_score > short_score and long_score >= config.CONFIDENCE_THRESHOLD:
            signal_type = 'LONG'
            confidence = min(long_score, 100)
        elif short_score > long_score and short_score >= config.CONFIDENCE_THRESHOLD:
            signal_type = 'SHORT'
            confidence = min(short_score, 100)
        
        return {
            'type': signal_type,
            'confidence': confidence,
            'indicators': {
                'rsi': float(latest['rsi']),
                'macd': float(latest['macd']),
                'macd_signal': float(latest['macd_signal']),
                'macd_histogram': float(latest['macd_histogram']),
                'bb_upper': float(latest['bb_upper']),
                'bb_middle': float(latest['bb_middle']),
                'bb_lower': float(latest['bb_lower']),
                'ema_fast': float(latest['ema_fast']),
                'ema_slow': float(latest['ema_slow']),
                'price': float(latest['close']),
                'volume': float(latest['volume'])
            }
        }