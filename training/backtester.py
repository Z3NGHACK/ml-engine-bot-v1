import pandas as pd
from utils.data_loader import DataLoader
from analysis.technical import TechnicalAnalyzer
from models.ensemble import EnsembleModel
import config

def run_backtest(symbol='BTC', timeframe='1h', days=30):
    loader = DataLoader()
    analyzer = TechnicalAnalyzer()
    ensemble = EnsembleModel()
    
    limit = 24 * days  # Assuming 1h
    df = loader.get_latest_candles(symbol, limit=limit)
    if df is None or len(df) < 100:
        return {"error": "Insufficient data"}
    
    df_with_indicators = analyzer.calculate_all_indicators(df)
    
    trades = []
    in_position = False
    entry_price = 0
    
    for i in range(60, len(df_with_indicators)):  # Start after lookback
        sub_df = df.iloc[:i+1]
        sub_ind = df_with_indicators.iloc[:i+1]
        signal = analyzer.generate_signal(sub_ind)  # Rule-based
        ml_signal = ensemble.predict(sub_df, sub_ind)  # ML
        
        combined_signal = ml_signal if ml_signal != 'NEUTRAL' else signal['type']
        confidence = signal['confidence'] + 20 if ml_signal == combined_signal else signal['confidence']  # Boost if agree
        
        if not in_position and combined_signal == 'LONG' and confidence >= config.CONFIDENCE_THRESHOLD:
            in_position = True
            entry_price = sub_ind['close'].iloc[-1]
            trades.append({'type': 'LONG', 'entry': entry_price, 'entry_time': sub_ind.index[-1], 'confidence': confidence})
        
        elif in_position and (combined_signal == 'SHORT' or sub_ind['close'].iloc[-1] < entry_price * 0.95):
            exit_price = sub_ind['close'].iloc[-1]
            pnl = ((exit_price - entry_price) / entry_price) * 100
            trades[-1].update({'exit': exit_price, 'exit_time': sub_ind.index[-1], 'pnl_percent': pnl})
            in_position = False
    
    # Stats
    completed = [t for t in trades if 'pnl_percent' in t]
    wins = len([t for t in completed if t['pnl_percent'] > 0])
    total_pnl = sum(t['pnl_percent'] for t in completed)
    
    return {
        "total_trades": len(completed),
        "win_rate": (wins / len(completed) * 100) if completed else 0,
        "total_pnl_percent": total_pnl,
        "trades": trades
    }

if __name__ == "__main__":
    print(run_backtest())