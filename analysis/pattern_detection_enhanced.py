# ============================================
# FILE: analysis/pattern_detection_enhanced.py
# ============================================
import numpy as np
import pandas as pd

class EnhancedPatternDetector:
    def detect_patterns(self, df):
        """Detect multiple chart patterns"""
        if df is None or len(df) < 20:
            return []
        
        patterns = []
        
        # Head and shoulders
        hns = self._detect_head_and_shoulders(df)
        if hns:
            patterns.extend(hns)
        
        # Double tops and bottoms
        dt = self._detect_double_top(df)
        if dt:
            patterns.append(dt)
        
        db = self._detect_double_bottom(df)
        if db:
            patterns.append(db)
        
        # Triangle patterns
        triangles = self._detect_triangles(df)
        if triangles:
            patterns.extend(triangles)
        
        # Trend analysis
        trend = self._detect_trend(df)
        if trend:
            patterns.append(trend)
        
        # Support/Resistance breakouts
        breakout = self._detect_support_resistance_breakout(df)
        if breakout:
            patterns.append(breakout)
        
        return patterns
    
    def _detect_head_and_shoulders(self, df):
        """Detect head and shoulders pattern"""
        try:
            recent = df.tail(30)
            highs = recent['high'].values
            lows = recent['low'].values
            
            # Find local peaks
            peaks = []
            for i in range(1, len(highs) - 1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    peaks.append((i, highs[i]))
            
            if len(peaks) >= 3:
                # Check if pattern: left shoulder < head > right shoulder
                peak1, peak2, peak3 = peaks[0], peaks[1], peaks[2]
                
                if (peak1[1] < peak2[1] and peak3[1] < peak2[1] and 
                    abs(peak1[1] - peak3[1]) / peak1[1] < 0.05):
                    return [{
                        'type': 'head_and_shoulders',
                        'signal': 'SHORT',
                        'strength': 'high',
                        'confidence': 0.8
                    }]
            return []
        except:
            return []
    
    def _detect_double_top(self, df):
        """Detect double top pattern"""
        try:
            recent = df.tail(20)
            highs = recent['high'].values
            
            if len(highs) < 10:
                return None
            
            # Find two highest peaks
            peaks_idx = np.argsort(highs)[-2:]
            if len(peaks_idx) < 2:
                return None
            
            peak1_val, peak2_val = highs[peaks_idx[0]], highs[peaks_idx[1]]
            peak1_idx, peak2_idx = peaks_idx[0], peaks_idx[1]
            
            # Check if peaks are similar (within 2%) and separated
            if (abs(peak1_val - peak2_val) / peak1_val < 0.02 and 
                abs(peak2_idx - peak1_idx) >= 3):
                return {
                    'type': 'double_top',
                    'signal': 'SHORT',
                    'strength': 'high',
                    'confidence': 0.75
                }
            return None
        except:
            return None
    
    def _detect_double_bottom(self, df):
        """Detect double bottom pattern"""
        try:
            recent = df.tail(20)
            lows = recent['low'].values
            
            if len(lows) < 10:
                return None
            
            # Find two lowest troughs
            troughs_idx = np.argsort(lows)[:2]
            if len(troughs_idx) < 2:
                return None
            
            trough1_val, trough2_val = lows[troughs_idx[0]], lows[troughs_idx[1]]
            trough1_idx, trough2_idx = troughs_idx[0], troughs_idx[1]
            
            # Check if troughs are similar (within 2%) and separated
            if (abs(trough1_val - trough2_val) / trough1_val < 0.02 and 
                abs(trough2_idx - trough1_idx) >= 3):
                return {
                    'type': 'double_bottom',
                    'signal': 'LONG',
                    'strength': 'high',
                    'confidence': 0.75
                }
            return None
        except:
            return None
    
    def _detect_triangles(self, df):
        """Detect ascending and descending triangles"""
        try:
            recent = df.tail(25)
            highs = recent['high'].values
            lows = recent['low'].values
            
            patterns = []
            
            # Ascending triangle: higher lows, flat highs
            lower_highs = highs[-1] < highs[-8]
            higher_lows = lows[-1] > lows[-8]
            
            if higher_lows and lower_highs:
                # Check trend of highs (should be relatively flat)
                high_std = np.std(highs[-8:])
                low_slope = np.polyfit(np.arange(len(lows[-8:])), lows[-8:], 1)[0]
                
                if high_std < np.std(lows[-8:]) and low_slope > 0:
                    patterns.append({
                        'type': 'ascending_triangle',
                        'signal': 'LONG',
                        'strength': 'medium',
                        'confidence': 0.65
                    })
            
            # Descending triangle: lower highs, flat lows
            lower_highs = highs[-1] < highs[-8]
            higher_lows = lows[-1] > lows[-8]
            
            if lower_highs and not higher_lows:
                low_std = np.std(lows[-8:])
                high_slope = np.polyfit(np.arange(len(highs[-8:])), highs[-8:], 1)[0]
                
                if low_std < np.std(highs[-8:]) and high_slope < 0:
                    patterns.append({
                        'type': 'descending_triangle',
                        'signal': 'SHORT',
                        'strength': 'medium',
                        'confidence': 0.65
                    })
            
            return patterns
        except:
            return []
    
    def _detect_trend(self, df):
        """Detect trend using linear regression"""
        try:
            recent = df.tail(20)
            prices = recent['close'].values
            x = np.arange(len(prices))
            
            # Fit polynomial
            coeffs = np.polyfit(x, prices, 2)
            slope = coeffs[0]  # First derivative at the end
            price_change = (prices[-1] - prices[0]) / prices[0] * 100
            
            # Calculate R-squared for quality
            p = np.poly1d(coeffs)
            y_pred = p(x)
            ss_res = np.sum((prices - y_pred) ** 2)
            ss_tot = np.sum((prices - np.mean(prices)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            strength = 'strong' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'weak'
            
            if slope > 0.02 and price_change > 1.5:
                return {
                    'type': 'uptrend',
                    'signal': 'LONG',
                    'strength': strength,
                    'confidence': min(0.95, 0.5 + r_squared),
                    'price_change': round(price_change, 2)
                }
            elif slope < -0.02 and price_change < -1.5:
                return {
                    'type': 'downtrend',
                    'signal': 'SHORT',
                    'strength': strength,
                    'confidence': min(0.95, 0.5 + r_squared),
                    'price_change': round(price_change, 2)
                }
            
            return None
        except:
            return None
    
    def _detect_support_resistance_breakout(self, df):
        """Detect support/resistance level breakout"""
        try:
            recent = df.tail(30)
            lows = recent['low'].values
            highs = recent['high'].values
            close = recent['close'].values
            
            # Find support (local lows)
            support_level = np.percentile(lows, 10)
            resistance_level = np.percentile(highs, 90)
            
            current_close = close[-1]
            prev_close = close[-2] if len(close) > 1 else close[-1]
            
            # Breakout above resistance
            if current_close > resistance_level and prev_close <= resistance_level:
                return {
                    'type': 'resistance_breakout',
                    'signal': 'LONG',
                    'strength': 'medium',
                    'confidence': 0.70,
                    'level': round(resistance_level, 2)
                }
            
            # Breakout below support
            if current_close < support_level and prev_close >= support_level:
                return {
                    'type': 'support_breakout',
                    'signal': 'SHORT',
                    'strength': 'medium',
                    'confidence': 0.70,
                    'level': round(support_level, 2)
                }
            
            return None
        except:
            return None