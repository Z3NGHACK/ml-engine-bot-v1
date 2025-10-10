# ============================================
# FILE: analysis/pattern_detection.py
# ============================================
import numpy as np

class PatternDetector:
    def detect_patterns(self, df):
        if df is None or len(df) < 20:
            return []
        
        patterns = []
        
        if self._is_double_bottom(df):
            patterns.append({'type': 'double_bottom', 'signal': 'LONG', 'strength': 'high'})
        
        if self._is_double_top(df):
            patterns.append({'type': 'double_top', 'signal': 'SHORT', 'strength': 'high'})
        
        trend = self._detect_trend(df)
        if trend:
            patterns.append(trend)
        
        return patterns
    
    def _is_double_bottom(self, df):
        recent = df.tail(20)
        lows = recent['low'].values
        min_idx = np.argsort(lows)[:2]
        
        if len(min_idx) < 2:
            return False
        
        low1, low2 = lows[min_idx[0]], lows[min_idx[1]]
        if abs(low1 - low2) / low1 < 0.02:
            return True
        return False
    
    def _is_double_top(self, df):
        recent = df.tail(20)
        highs = recent['high'].values
        max_idx = np.argsort(highs)[-2:]
        
        if len(max_idx) < 2:
            return False
        
        high1, high2 = highs[max_idx[0]], highs[max_idx[1]]
        if abs(high1 - high2) / high1 < 0.02:
            return True
        return False
    
    def _detect_trend(self, df):
        recent = df.tail(20)
        prices = recent['close'].values
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        price_change = (prices[-1] - prices[0]) / prices[0] * 100
        
        if slope > 0 and price_change > 2:
            return {'type': 'uptrend', 'signal': 'LONG', 'strength': 'medium'}
        elif slope < 0 and price_change < -2:
            return {'type': 'downtrend', 'signal': 'SHORT', 'strength': 'medium'}
        return None