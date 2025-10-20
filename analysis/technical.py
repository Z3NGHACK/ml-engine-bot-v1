# ============================================
# FILE: analysis/technical.py (IMPROVED)
# ============================================
import pandas as pd
import numpy as np
import config

class TechnicalAnalyzer:
    def __init__(self):
        print("✅ TechnicalAnalyzer initialized")
    
    def calculate_rsi(self, df, period=14):
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"❌ RSI calculation error: {e}")
            return pd.Series([50] * len(df), index=df.index)
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        try:
            exp1 = df['close'].ewm(span=fast, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=signal, adjust=False).mean()
            macd_histogram = macd - macd_signal
            return macd, macd_signal, macd_histogram
        except Exception as e:
            print(f"❌ MACD calculation error: {e}")
            zeros = pd.Series([0] * len(df), index=df.index)
            return zeros, zeros, zeros
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        try:
            sma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            bb_upper = sma + (std * std_dev)
            bb_lower = sma - (std * std_dev)
            return bb_upper, sma, bb_lower
        except Exception as e:
            print(f"❌ Bollinger Bands calculation error: {e}")
            close = df['close']
            return close, close, close
    
    def calculate_ema(self, df, period):
        try:
            return df['close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            print(f"❌ EMA calculation error: {e}")
            return df['close']
    
    def calculate_volatility(self, df, period=20):
        """Calculate volatility as % of current price"""
        try:
            returns = df['close'].pct_change()
            volatility = returns.rolling(window=period).std() * 100
            return volatility
        except Exception as e:
            return pd.Series([0] * len(df), index=df.index)
    
    def calculate_all_indicators(self, df):
        try:
            if df is None or len(df) < 50:
                raise ValueError(f"Insufficient data: {len(df) if df is not None else 0} candles")
            
            df = df.copy()
            
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            print(f"📊 Calculating indicators for {len(df)} candles...")
            
            # Technical indicators
            df['rsi'] = self.calculate_rsi(df, config.RSI_PERIOD)
            df['macd'], df['macd_signal'], df['macd_histogram'] = self.calculate_macd(
                df, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL
            )
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.calculate_bollinger_bands(
                df, config.BB_PERIOD, config.BB_STD
            )
            df['ema_20'] = self.calculate_ema(df, 20)
            df['ema_50'] = self.calculate_ema(df, 50)
            df['volatility'] = self.calculate_volatility(df, 20)
            
            # Additional metrics
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            df = df.dropna()
            
            if len(df) == 0:
                raise ValueError("All data became NaN after indicator calculation")
            
            print(f"✅ Indicators calculated successfully. {len(df)} valid candles")
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            raise
    
    def is_choppy_market(self, df, threshold=0.02):
        """Check if market is too choppy (low volatility, low BB width)"""
        if len(df) < 5:
            return False
        
        latest_vol = df['volatility'].iloc[-1]
        latest_bb = df['bb_width'].iloc[-1]
        
        # Consider choppy if volatility < 0.5% AND BB width < 2%
        return latest_vol < 0.5 and latest_bb < threshold
    
    def are_indicators_aligned(self, df, signal_type):
        """Check if multiple indicators point in same direction"""
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        rsi = float(latest['rsi'])
        macd_hist = float(latest['macd_histogram'])
        price = float(latest['close'])
        ema_20 = float(latest['ema_20'])
        ema_50 = float(latest['ema_50'])
        
        if signal_type == 'LONG':
            indicators_agree = 0
            # RSI in bullish zone (not overbought)
            if rsi < 70 and rsi > 40:
                indicators_agree += 1
            # MACD positive and increasing
            if macd_hist > 0 and macd_hist > float(prev['macd_histogram']):
                indicators_agree += 1
            # Price above EMAs
            if price > ema_20 > ema_50:
                indicators_agree += 1
            
            return indicators_agree >= 2  # At least 2 indicators must agree
        
        elif signal_type == 'SHORT':
            indicators_agree = 0
            # RSI in bearish zone (not oversold)
            if rsi > 30 and rsi < 60:
                indicators_agree += 1
            # MACD negative and decreasing
            if macd_hist < 0 and macd_hist < float(prev['macd_histogram']):
                indicators_agree += 1
            # Price below EMAs
            if price < ema_20 < ema_50:
                indicators_agree += 1
            
            return indicators_agree >= 2
        
        return False
    
    def calculate_signal_strength(self, df, signal_type):
        """Calculate signal strength with weighted indicators (0-100)"""
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        rsi = float(latest['rsi'])
        macd = float(latest['macd'])
        macd_signal = float(latest['macd_signal'])
        macd_hist = float(latest['macd_histogram'])
        price = float(latest['close'])
        ema_20 = float(latest['ema_20'])
        ema_50 = float(latest['ema_50'])
        
        strength = 0
        
        if signal_type == 'LONG':
            # RSI: Weight 20% (oversold = strong signal)
            if rsi < 30:
                strength += 20
            elif rsi < 50:
                strength += 10
            
            # MACD: Weight 25% (crossover = strong signal)
            if macd > macd_signal and macd_hist > float(prev['macd_histogram']):
                strength += 25
            elif macd > macd_signal:
                strength += 12
            
            # Price vs EMA20: Weight 25%
            if price > ema_20:
                strength += 15
            
            # EMA alignment: Weight 30%
            if ema_20 > ema_50:
                if price > ema_20:
                    strength += 30
                else:
                    strength += 15
        
        elif signal_type == 'SHORT':
            # RSI: Weight 20% (overbought = strong signal)
            if rsi > 70:
                strength += 20
            elif rsi > 50:
                strength += 10
            
            # MACD: Weight 25% (crossover = strong signal)
            if macd < macd_signal and macd_hist < float(prev['macd_histogram']):
                strength += 25
            elif macd < macd_signal:
                strength += 12
            
            # Price vs EMA20: Weight 25%
            if price < ema_20:
                strength += 15
            
            # EMA alignment: Weight 30%
            if ema_20 < ema_50:
                if price < ema_20:
                    strength += 30
                else:
                    strength += 15
        
        return min(strength, 100)
    
    def generate_signal(self, df):
        """Generate trading signal with improved accuracy"""
        try:
            if df is None or len(df) < 10:
                return {
                    'type': 'NEUTRAL',
                    'confidence': 0,
                    'indicators': {},
                    'reason': 'Insufficient data',
                    'recommendation': 'Insufficient data for analysis'
                }
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Extract indicators
            rsi = float(latest.get('rsi', 50))
            macd = float(latest.get('macd', 0))
            macd_signal = float(latest.get('macd_signal', 0))
            macd_hist = float(latest.get('macd_histogram', 0))
            price = float(latest['close'])
            ema_20 = float(latest.get('ema_20', price))
            ema_50 = float(latest.get('ema_50', price))
            volatility = float(latest.get('volatility', 0))
            
            # Check for choppy market - reject signals in consolidation
            if self.is_choppy_market(df):
                return {
                    'type': 'NEUTRAL',
                    'confidence': 0,
                    'indicators': {'rsi': rsi, 'macd': macd, 'price': price, 'volatility': volatility},
                    'reason': 'Market too choppy - consolidating',
                    'recommendation': 'Market is consolidating. Wait for breakout.'
                }
            
            # Determine potential signal
            long_potential = (
                rsi < 50 and  # Not overbought
                macd_hist > 0 and  # MACD bullish
                price >= ema_20  # Price above short EMA
            )
            
            short_potential = (
                rsi > 50 and  # Not oversold
                macd_hist < 0 and  # MACD bearish
                price <= ema_20  # Price below short EMA
            )
            
            signal_type = 'NEUTRAL'
            confidence = 0
            reason = 'No clear alignment'
            
            # Check LONG
            if long_potential and self.are_indicators_aligned(df, 'LONG'):
                confidence = self.calculate_signal_strength(df, 'LONG')
                if confidence >= 60:  # Minimum 60% strength
                    signal_type = 'LONG'
                    reason = f'Strong buy setup - RSI: {rsi:.1f}, MACD positive, Price > EMA20'
            
            # Check SHORT
            elif short_potential and self.are_indicators_aligned(df, 'SHORT'):
                confidence = self.calculate_signal_strength(df, 'SHORT')
                if confidence >= 60:  # Minimum 60% strength
                    signal_type = 'SHORT'
                    reason = f'Strong sell setup - RSI: {rsi:.1f}, MACD negative, Price < EMA20'
            
            if signal_type == 'NEUTRAL':
                reason = 'Indicators not aligned or volatility too low'
                recommendation = 'Waiting for clearer setup'
            else:
                strength_level = 'Very Strong' if confidence >= 80 else 'Strong' if confidence >= 70 else 'Moderate'
                recommendation = f'{strength_level} {signal_type} signal. {reason}'
            
            return {
                'type': signal_type,
                'confidence': round(confidence, 2),
                'indicators': {
                    'rsi': round(rsi, 2),
                    'macd': round(macd, 4),
                    'macd_signal': round(macd_signal, 4),
                    'macd_histogram': round(macd_hist, 4),
                    'price': round(price, 2),
                    'ema_20': round(ema_20, 2),
                    'ema_50': round(ema_50, 2),
                    'volatility': round(volatility, 2)
                },
                'reason': reason,
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"❌ Error generating signal: {e}")
            return {
                'type': 'NEUTRAL',
                'confidence': 0,
                'indicators': {},
                'reason': 'Error in calculation',
                'recommendation': f'Error: {str(e)}'
            }