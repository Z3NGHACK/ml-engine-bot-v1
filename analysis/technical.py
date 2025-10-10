# ============================================
# FILE: analysis/technical.py
# ============================================
import pandas as pd
import numpy as np
import config

class TechnicalAnalyzer:
    def __init__(self):
        print("✅ TechnicalAnalyzer initialized")
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI (Relative Strength Index)"""
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
        """Calculate MACD (Moving Average Convergence Divergence)"""
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
        """Calculate Bollinger Bands"""
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
        """Calculate EMA (Exponential Moving Average)"""
        try:
            return df['close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            print(f"❌ EMA calculation error: {e}")
            return df['close']
    
    def calculate_all_indicators(self, df):
        """Calculate all technical indicators"""
        try:
            if df is None or len(df) < 50:
                raise ValueError(f"Insufficient data: {len(df) if df is not None else 0} candles")
            
            # Make a copy to avoid modifying original
            df = df.copy()
            
            # Ensure we have required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            print(f"📊 Calculating indicators for {len(df)} candles...")
            
            # RSI
            df['rsi'] = self.calculate_rsi(df, config.RSI_PERIOD)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_histogram'] = self.calculate_macd(
                df, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL
            )
            
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.calculate_bollinger_bands(
                df, config.BB_PERIOD, config.BB_STD
            )
            
            # EMAs
            df['ema_20'] = self.calculate_ema(df, 20)
            df['ema_50'] = self.calculate_ema(df, 50)
            
            # Drop NaN values
            df = df.dropna()
            
            if len(df) == 0:
                raise ValueError("All data became NaN after indicator calculation")
            
            print(f"✅ Indicators calculated successfully. {len(df)} valid candles")
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            raise
    
    def generate_signal(self, df):
        """Generate trading signal based on technical indicators"""
        try:
            if df is None or len(df) < 10:
                return {
                    'type': 'NEUTRAL',
                    'confidence': 0,
                    'indicators': {},
                    'recommendation': 'Insufficient data for analysis'
                }
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Extract indicators with safe defaults
            rsi = float(latest.get('rsi', 50))
            macd = float(latest.get('macd', 0))
            macd_signal = float(latest.get('macd_signal', 0))
            macd_hist = float(latest.get('macd_histogram', 0))
            bb_upper = float(latest.get('bb_upper', latest['close']))
            bb_middle = float(latest.get('bb_middle', latest['close']))
            bb_lower = float(latest.get('bb_lower', latest['close']))
            ema_20 = float(latest.get('ema_20', latest['close']))
            ema_50 = float(latest.get('ema_50', latest['close']))
            price = float(latest['close'])
            
            # Signal scoring
            long_signals = 0
            short_signals = 0
            max_signals = 6
            
            # 1. RSI Analysis (Oversold/Overbought)
            if rsi < 30:
                long_signals += 1
            elif rsi > 70:
                short_signals += 1
            
            # 2. MACD Crossover
            if macd > macd_signal and macd_hist > 0:
                long_signals += 1
            elif macd < macd_signal and macd_hist < 0:
                short_signals += 1
            
            # 3. Bollinger Bands
            if price < bb_lower:
                long_signals += 1
            elif price > bb_upper:
                short_signals += 1
            
            # 4. EMA Trend
            if price > ema_20 > ema_50:
                long_signals += 1
            elif price < ema_20 < ema_50:
                short_signals += 1
            
            # 5. Price vs EMA_20
            if price > ema_20:
                long_signals += 1
            else:
                short_signals += 1
            
            # 6. MACD momentum
            prev_macd_hist = float(prev.get('macd_histogram', 0))
            if macd_hist > prev_macd_hist and macd_hist > 0:
                long_signals += 1
            elif macd_hist < prev_macd_hist and macd_hist < 0:
                short_signals += 1
            
            # Determine signal and confidence
            if long_signals > short_signals:
                signal_type = 'LONG'
                confidence = (long_signals / max_signals) * 100
            elif short_signals > long_signals:
                signal_type = 'SHORT'
                confidence = (short_signals / max_signals) * 100
            else:
                signal_type = 'NEUTRAL'
                confidence = 50
            
            # Generate recommendation
            if confidence >= 70:
                strength = "Strong"
            elif confidence >= 50:
                strength = "Moderate"
            else:
                strength = "Weak"
            
            if signal_type == 'LONG':
                recommendation = f"{strength} buy signal. RSI: {rsi:.1f}, MACD histogram: {macd_hist:.4f}, Price above EMA20: {price > ema_20}"
            elif signal_type == 'SHORT':
                recommendation = f"{strength} sell signal. RSI: {rsi:.1f}, MACD histogram: {macd_hist:.4f}, Price below EMA20: {price < ema_20}"
            else:
                recommendation = "No clear trend. Market is consolidating."
            
            return {
                'type': signal_type,
                'confidence': round(confidence, 2),
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'macd_signal': macd_signal,
                    'macd_histogram': macd_hist,
                    'price': price,
                    'ema_20': ema_20,
                    'ema_50': ema_50,
                    'bb_upper': bb_upper,
                    'bb_middle': bb_middle,
                    'bb_lower': bb_lower
                },
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"❌ Error generating signal: {e}")
            return {
                'type': 'NEUTRAL',
                'confidence': 0,
                'indicators': {},
                'recommendation': f'Error: {str(e)}'
            }