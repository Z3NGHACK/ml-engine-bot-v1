# ============================================
# FILE: analysis/technical_enhanced.py
# ============================================
import pandas as pd
import numpy as np
import config

class EnhancedTechnicalAnalyzer:
    def __init__(self):
        print("✅ EnhancedTechnicalAnalyzer initialized")
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI with smoothing"""
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
        """Calculate MACD with histogram"""
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
            bb_width = (bb_upper - bb_lower) / sma * 100
            return bb_upper, sma, bb_lower, bb_width
        except Exception as e:
            print(f"❌ Bollinger Bands calculation error: {e}")
            close = df['close']
            return close, close, close, pd.Series([0] * len(df), index=df.index)
    
    def calculate_ema(self, df, period):
        """Calculate EMA"""
        try:
            return df['close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            print(f"❌ EMA calculation error: {e}")
            return df['close']
    
    def calculate_sma(self, df, period):
        """Calculate SMA"""
        try:
            return df['close'].rolling(window=period).mean()
        except Exception as e:
            return df['close']
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(period).mean()
            return atr
        except Exception as e:
            print(f"❌ ATR calculation error: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def calculate_stochastic(self, df, period=14):
        """Calculate Stochastic Oscillator"""
        try:
            low_min = df['low'].rolling(window=period).min()
            high_max = df['high'].rolling(window=period).max()
            k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
            d_percent = k_percent.rolling(window=3).mean()
            return k_percent, d_percent
        except Exception as e:
            print(f"❌ Stochastic calculation error: {e}")
            return pd.Series([50] * len(df), index=df.index), pd.Series([50] * len(df), index=df.index)
    
    def calculate_adx(self, df, period=14):
        """Calculate ADX for trend strength"""
        try:
            plus_dm = df['high'].diff()
            minus_dm = -df['low'].diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            tr = self.calculate_atr(df, 1)
            plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
            minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(period).mean()
            return adx, plus_di, minus_di
        except Exception as e:
            print(f"❌ ADX calculation error: {e}")
            return pd.Series([20] * len(df), index=df.index), pd.Series([20] * len(df), index=df.index), pd.Series([20] * len(df), index=df.index)
    
    def calculate_volume_profile(self, df, period=20):
        """Calculate volume trend"""
        try:
            sma_volume = df['volume'].rolling(window=period).mean()
            volume_ratio = df['volume'] / sma_volume
            return volume_ratio
        except Exception as e:
            return pd.Series([1] * len(df), index=df.index)
    
    def calculate_all_indicators(self, df):
        """Calculate all technical indicators"""
        try:
            if df is None or len(df) < 50:
                raise ValueError(f"Insufficient data: {len(df) if df is not None else 0} candles")
            
            df = df.copy()
            
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            print(f"📊 Calculating enhanced indicators for {len(df)} candles...")
            
            # Basic indicators
            df['rsi'] = self.calculate_rsi(df, config.RSI_PERIOD)
            df['macd'], df['macd_signal'], df['macd_histogram'] = self.calculate_macd(
                df, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL
            )
            df['bb_upper'], df['bb_middle'], df['bb_lower'], df['bb_width'] = self.calculate_bollinger_bands(
                df, config.BB_PERIOD, config.BB_STD
            )
            
            # EMAs and SMAs
            df['ema_20'] = self.calculate_ema(df, 20)
            df['ema_50'] = self.calculate_ema(df, 50)
            df['ema_200'] = self.calculate_ema(df, 200)
            df['sma_50'] = self.calculate_sma(df, 50)
            df['sma_200'] = self.calculate_sma(df, 200)
            
            # Advanced indicators
            df['atr'] = self.calculate_atr(df, 14)
            df['stoch_k'], df['stoch_d'] = self.calculate_stochastic(df, 14)
            df['adx'], df['plus_di'], df['minus_di'] = self.calculate_adx(df, 14)
            df['volume_ratio'] = self.calculate_volume_profile(df, 20)
            
            df = df.dropna()
            
            if len(df) == 0:
                raise ValueError("All data became NaN after indicator calculation")
            
            print(f"✅ Indicators calculated successfully. {len(df)} valid candles")
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            raise
    
    def generate_signal(self, df):
        """Generate trading signal with enhanced logic"""
        try:
            if df is None or len(df) < 10:
                return self._neutral_signal("Insufficient data for analysis")
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Extract all indicators
            rsi = float(latest.get('rsi', 50))
            macd = float(latest.get('macd', 0))
            macd_signal = float(latest.get('macd_signal', 0))
            macd_hist = float(latest.get('macd_histogram', 0))
            prev_macd_hist = float(prev.get('macd_histogram', 0))
            
            bb_upper = float(latest.get('bb_upper', latest['close']))
            bb_middle = float(latest.get('bb_middle', latest['close']))
            bb_lower = float(latest.get('bb_lower', latest['close']))
            bb_width = float(latest.get('bb_width', 0))
            
            ema_20 = float(latest.get('ema_20', latest['close']))
            ema_50 = float(latest.get('ema_50', latest['close']))
            ema_200 = float(latest.get('ema_200', latest['close']))
            
            sma_50 = float(latest.get('sma_50', latest['close']))
            sma_200 = float(latest.get('sma_200', latest['close']))
            
            stoch_k = float(latest.get('stoch_k', 50))
            stoch_d = float(latest.get('stoch_d', 50))
            
            adx = float(latest.get('adx', 20))
            plus_di = float(latest.get('plus_di', 20))
            minus_di = float(latest.get('minus_di', 20))
            
            volume_ratio = float(latest.get('volume_ratio', 1))
            price = float(latest['close'])
            
            # Signal scoring
            long_signals = []
            short_signals = []
            
            # 1. RSI Analysis
            if rsi < 30:
                long_signals.append(('RSI Oversold', 2))
            elif rsi < 50:
                long_signals.append(('RSI Neutral-Up', 1))
            
            if rsi > 70:
                short_signals.append(('RSI Overbought', 2))
            elif rsi > 50:
                short_signals.append(('RSI Neutral-Down', 1))
            
            # 2. MACD Crossover
            if macd > macd_signal and macd_hist > 0:
                long_signals.append(('MACD Bullish', 2))
            elif macd < macd_signal and macd_hist < 0:
                short_signals.append(('MACD Bearish', 2))
            
            # 3. MACD Momentum
            if macd_hist > prev_macd_hist and macd_hist > 0:
                long_signals.append(('MACD Momentum', 1))
            elif macd_hist < prev_macd_hist and macd_hist < 0:
                short_signals.append(('MACD Momentum', 1))
            
            # 4. Bollinger Bands
            if price < bb_lower:
                long_signals.append(('BB Lower Bounce', 2))
            elif price > bb_upper:
                short_signals.append(('BB Upper Rejection', 2))
            elif bb_lower < price < bb_middle:
                long_signals.append(('BB Bullish Zone', 1))
            elif bb_middle < price < bb_upper:
                short_signals.append(('BB Bearish Zone', 1))
            
            # 5. EMA Trend (short term)
            if price > ema_20 > ema_50:
                long_signals.append(('EMA Uptrend', 2))
            elif price < ema_20 < ema_50:
                short_signals.append(('EMA Downtrend', 2))
            
            # 6. SMA Trend (long term)
            if ema_50 > sma_200:
                long_signals.append(('SMA Above 200', 1))
            elif ema_50 < sma_200:
                short_signals.append(('SMA Below 200', 1))
            
            # 7. Stochastic
            if stoch_k < 20 and stoch_d < 20:
                long_signals.append(('Stoch Oversold', 2))
            elif stoch_k > 80 and stoch_d > 80:
                short_signals.append(('Stoch Overbought', 2))
            
            if stoch_k > stoch_d:
                long_signals.append(('Stoch Bullish Cross', 1))
            elif stoch_k < stoch_d:
                short_signals.append(('Stoch Bearish Cross', 1))
            
            # 8. ADX Trend Strength
            if adx > 25:
                if plus_di > minus_di:
                    long_signals.append(('ADX Strong Uptrend', 2))
                else:
                    short_signals.append(('ADX Strong Downtrend', 2))
            
            # 9. Volume Analysis
            if volume_ratio > 1.2:
                if macd > 0:
                    long_signals.append(('High Volume Up', 1))
                else:
                    short_signals.append(('High Volume Down', 1))
            
            # Calculate scores
            long_score = sum([s[1] for s in long_signals])
            short_score = sum([s[1] for s in short_signals])
            max_possible_score = 20
            
            # Determine signal
            if long_score > short_score and long_score >= 5:
                signal_type = 'LONG'
                confidence = min(100, (long_score / max_possible_score) * 100)
                signals_detail = long_signals
            elif short_score > long_score and short_score >= 5:
                signal_type = 'SHORT'
                confidence = min(100, (short_score / max_possible_score) * 100)
                signals_detail = short_signals
            else:
                return self._neutral_signal(f"Conflicting signals - Long: {long_score}, Short: {short_score}")
            
            # Generate recommendation
            strength = "Very Strong" if confidence >= 80 else "Strong" if confidence >= 65 else "Moderate" if confidence >= 50 else "Weak"
            
            signal_reasons = ", ".join([f"{s[0]}" for s in signals_detail[:3]])
            
            if signal_type == 'LONG':
                recommendation = f"{strength} BUY signal. Reasons: {signal_reasons}"
            else:
                recommendation = f"{strength} SELL signal. Reasons: {signal_reasons}"
            
            return {
                'type': signal_type,
                'confidence': round(confidence, 2),
                'strength': strength,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'macd': round(macd, 6),
                    'macd_histogram': round(macd_hist, 6),
                    'stoch_k': round(stoch_k, 2),
                    'stoch_d': round(stoch_d, 2),
                    'adx': round(adx, 2),
                    'price': round(price, 2),
                    'ema_20': round(ema_20, 2),
                    'ema_50': round(ema_50, 2),
                    'bb_width_percent': round(bb_width, 2),
                    'volume_ratio': round(volume_ratio, 2)
                },
                'signals_detail': [(s[0], s[1]) for s in signals_detail],
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"❌ Error generating signal: {e}")
            return self._neutral_signal(f"Error: {str(e)}")
    
    def _neutral_signal(self, reason=""):
        return {
            'type': 'NEUTRAL',
            'confidence': 0,
            'strength': 'Neutral',
            'indicators': {},
            'signals_detail': [],
            'recommendation': reason
        }