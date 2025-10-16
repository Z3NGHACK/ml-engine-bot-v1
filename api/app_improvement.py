# ============================================
# FILE: api/app_improved.py
# ============================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from analysis.technical_enhanced import EnhancedTechnicalAnalyzer
from analysis.pattern_detection_enhanced import EnhancedPatternDetector
import config

app = FastAPI(title="Crypto ML Engine API v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_loader = DataLoader()
technical_analyzer = EnhancedTechnicalAnalyzer()
pattern_detector = EnhancedPatternDetector()

class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"
    min_confidence: Optional[int] = 50

class BacktestRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"
    days: Optional[int] = 7

@app.get("/")
async def root():
    return {
        "service": "Crypto ML Engine v2",
        "status": "running",
        "version": "2.0.0",
        "improvements": [
            "Enhanced technical indicators (ADX, Stochastic, ATR)",
            "Better pattern detection",
            "Multi-factor signal validation",
            "Improved confidence scoring"
        ]
    }

@app.get("/health")
async def health():
    try:
        test_data = data_loader.get_latest_candles("BTC", limit=1)
        db_status = "connected" if test_data is not None else "disconnected"
    except:
        db_status = "error"
    
    return {"status": "healthy", "database": db_status}

@app.post("/api/analyze")
async def api_analyze_symbol(request: AnalysisRequest):
    """Comprehensive analysis with enhanced indicators"""
    try:
        limit = 500 if request.timeframe == "1d" else 200
        df = data_loader.get_latest_candles(request.symbol, limit=limit)
        
        if df is None or len(df) < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for {request.symbol}. Need 50+, got {len(df) if df else 0}"
            )
        
        # Calculate enhanced indicators
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        signal = technical_analyzer.generate_signal(df_with_indicators)
        
        # Detect patterns
        patterns = pattern_detector.detect_patterns(df)
        
        # Apply confidence filter
        if signal['confidence'] < request.min_confidence:
            signal_type = "NEUTRAL"
            confidence = signal['confidence']
        else:
            signal_type = signal['type']
            confidence = signal['confidence']
        
        latest = df_with_indicators.iloc[-1]
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "timestamp": str(latest.name),
            "signal": signal_type,
            "confidence": confidence,
            "strength": signal.get('strength', 'Unknown'),
            "indicators": {
                "price": round(float(latest['close']), 2),
                "rsi": round(float(latest['rsi']), 2),
                "macd": round(float(latest['macd']), 6),
                "macd_histogram": round(float(latest['macd_histogram']), 6),
                "stoch_k": round(float(latest['stoch_k']), 2),
                "stoch_d": round(float(latest['stoch_d']), 2),
                "adx": round(float(latest['adx']), 2),
                "atr": round(float(latest['atr']), 2),
                "ema_20": round(float(latest['ema_20']), 2),
                "ema_50": round(float(latest['ema_50']), 2),
                "ema_200": round(float(latest['ema_200']), 2),
                "bb_upper": round(float(latest['bb_upper']), 2),
                "bb_middle": round(float(latest['bb_middle']), 2),
                "bb_lower": round(float(latest['bb_lower']), 2),
                "bb_width_percent": round(float(latest['bb_width']), 2),
                "volume": round(float(latest['volume']), 2),
                "volume_ratio": round(float(latest['volume_ratio']), 2)
            },
            "patterns": patterns,
            "signals_detail": signal.get('signals_detail', []),
            "recommendation": signal['recommendation']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/api/compare/{symbol}")
async def compare_signals(symbol: str, timeframe: Optional[str] = "1h"):
    """Compare multiple timeframe signals"""
    try:
        timeframes = ["1h", "4h", "1d"]
        results = {}
        
        for tf in timeframes:
            limit = 500 if tf == "1d" else 200 if tf == "4h" else 100
            df = data_loader.get_latest_candles(symbol, limit=limit)
            
            if df is None or len(df) < 50:
                continue
            
            df_analyzed = technical_analyzer.calculate_all_indicators(df)
            signal = technical_analyzer.generate_signal(df_analyzed)
            
            results[tf] = {
                "signal": signal['type'],
                "confidence": signal['confidence'],
                "strength": signal.get('strength'),
                "rsi": round(float(df_analyzed.iloc[-1]['rsi']), 2)
            }
        
        # Determine overall signal
        long_count = sum(1 for r in results.values() if r['signal'] == 'LONG')
        short_count = sum(1 for r in results.values() if r['signal'] == 'SHORT')
        
        if long_count > short_count:
            overall = "LONG"
        elif short_count > long_count:
            overall = "SHORT"
        else:
            overall = "NEUTRAL"
        
        return {
            "symbol": symbol,
            "timeframes": results,
            "overall_signal": overall,
            "alignment_score": max(long_count, short_count) / len(results) * 100
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest")
async def backtest(request: BacktestRequest):
    """Simple backtest with enhanced signals"""
    try:
        candles_per_day = {
            "1m": 1440, "5m": 288, "15m": 96,
            "1h": 24, "4h": 6, "1d": 1
        }
        
        limit = candles_per_day.get(request.timeframe, 24) * request.days
        df = data_loader.get_latest_candles(request.symbol, limit=limit)
        
        if df is None or len(df) < 100:
            raise HTTPException(status_code=400, detail="Insufficient data")
        
        df_analyzed = technical_analyzer.calculate_all_indicators(df)
        
        trades = []
        in_position = False
        entry_price = 0
        
        for i in range(50, len(df_analyzed)):
            row = df_analyzed.iloc[i]
            signal = technical_analyzer.generate_signal(df_analyzed.iloc[:i+1])
            
            if not in_position and signal['type'] == 'LONG' and signal['confidence'] >= 65:
                in_position = True
                entry_price = row['close']
                trades.append({
                    'type': 'LONG',
                    'entry': float(entry_price),
                    'entry_time': str(row.name),
                    'confidence': signal['confidence']
                })
            
            elif in_position:
                exit_triggered = (
                    signal['type'] == 'SHORT' or
                    row['close'] < entry_price * 0.95 or
                    row['close'] > entry_price * 1.05
                )
                
                if exit_triggered:
                    exit_price = row['close']
                    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
                    
                    trades[-1]['exit'] = float(exit_price)
                    trades[-1]['exit_time'] = str(row.name)
                    trades[-1]['pnl_percent'] = round(pnl_percent, 2)
                    
                    in_position = False
        
        winning = [t for t in trades if 'pnl_percent' in t and t['pnl_percent'] > 0]
        losing = [t for t in trades if 'pnl_percent' in t and t['pnl_percent'] <= 0]
        closed = [t for t in trades if 'pnl_percent' in t]
        
        total_pnl = sum(t.get('pnl_percent', 0) for t in trades)
        win_rate = len(winning) / len(closed) * 100 if closed else 0
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "period_days": request.days,
            "total_trades_opened": len(trades),
            "closed_trades": len(closed),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": round(win_rate, 2),
            "total_pnl_percent": round(total_pnl, 2),
            "avg_win": round(np.mean([t['pnl_percent'] for t in winning]), 2) if winning else 0,
            "avg_loss": round(np.mean([t['pnl_percent'] for t in losing]), 2) if losing else 0,
            "profit_factor": round(
                sum(t['pnl_percent'] for t in winning) / abs(sum(t['pnl_percent'] for t in losing)), 2
            ) if losing else 0,
            "recent_trades": trades[-10:]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/api/signals/high-confidence")
async def get_high_confidence_signals(min_confidence: int = 70):
    """Get all symbols with high confidence signals"""
    try:
        symbols = data_loader.get_all_symbols()
        high_confidence_signals = []
        
        for symbol in symbols:
            try:
                df = data_loader.get_latest_candles(symbol, limit=200)
                if df is None or len(df) < 50:
                    continue
                
                df_analyzed = technical_analyzer.calculate_all_indicators(df)
                signal = technical_analyzer.generate_signal(df_analyzed)
                
                if signal['confidence'] >= min_confidence:
                    latest = df_analyzed.iloc[-1]
                    high_confidence_signals.append({
                        "symbol": symbol,
                        "signal": signal['type'],
                        "confidence": signal['confidence'],
                        "price": round(float(latest['close']), 2),
                        "rsi": round(float(latest['rsi']), 2)
                    })
            except:
                continue
        
        return {
            "min_confidence": min_confidence,
            "signals_found": len(high_confidence_signals),
            "signals": sorted(high_confidence_signals, key=lambda x: x['confidence'], reverse=True)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"🚀 Starting Enhanced ML Engine API on {config.API_HOST}:{config.API_PORT}")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)