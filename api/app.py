from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from utils.data_loader import DataLoader
from analysis.technical import TechnicalAnalyzer
from analysis.pattern_detection import PatternDetector
import config

app = FastAPI(title="Crypto ML Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_loader = DataLoader()
technical_analyzer = TechnicalAnalyzer()
pattern_detector = PatternDetector()

class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"
    days: Optional[int] = 7

class BacktestRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"
    days: Optional[int] = 7

@app.get("/")
async def root():
    return {"service": "Crypto ML Engine", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health():
    try:
        # Test MongoDB connection
        test_data = data_loader.get_latest_candles("BTC", limit=1)
        db_status = "connected" if test_data is not None else "disconnected"
    except:
        db_status = "error"
    
    return {
        "status": "healthy",
        "database": db_status
    }

# Analysis endpoints (with /api prefix for Trading Bot)
@app.post("/api/analyze")
async def api_analyze_symbol(request: AnalysisRequest):
    return await analyze_symbol(request)

@app.get("/api/indicators/{symbol}")
async def api_get_indicators(symbol: str, timeframe: Optional[str] = "1h"):
    return await get_indicators(symbol, timeframe)

@app.get("/api/patterns/{symbol}")
async def api_get_patterns(symbol: str, timeframe: Optional[str] = "1h"):
    return await get_patterns(symbol, timeframe)

@app.post("/api/backtest")
async def api_backtest(request: BacktestRequest):
    return await backtest(request)

# Direct endpoints (without /api for testing)
@app.post("/analyze")
async def analyze_symbol(request: AnalysisRequest):
    try:
        # Get data based on timeframe
        limit = 500 if request.timeframe == "1d" else 200 if request.timeframe == "1h" else 100
        df = data_loader.get_latest_candles(request.symbol, limit=limit)
        
        if df is None or len(df) < 50:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for {request.symbol}. Need at least 50 candles, got {len(df) if df is not None else 0}"
            )
        
        # Calculate indicators
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        
        # Generate signal
        signal = technical_analyzer.generate_signal(df_with_indicators)
        
        # Detect patterns
        patterns = pattern_detector.detect_patterns(df)
        
        # Get latest values
        latest = df_with_indicators.iloc[-1]
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "signal": signal['type'],
            "confidence": round(signal['confidence'], 2),
            "indicators": {
                "rsi": round(float(latest['rsi']), 2),
                "macd": round(float(latest['macd']), 4),
                "macd_signal": round(float(latest['macd_signal']), 4),
                "macd_histogram": round(float(latest['macd_histogram']), 4),
                "bb_upper": round(float(latest['bb_upper']), 2),
                "bb_middle": round(float(latest['bb_middle']), 2),
                "bb_lower": round(float(latest['bb_lower']), 2),
                "ema_20": round(float(latest['ema_20']), 2),
                "ema_50": round(float(latest['ema_50']), 2),
                "price": round(float(latest['close']), 2),
                "volume": round(float(latest['volume']), 2)
            },
            "patterns": patterns,
            "recommendation": signal['recommendation']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/indicators/{symbol}")
async def get_indicators(symbol: str, timeframe: Optional[str] = "1h"):
    try:
        limit = 200 if timeframe == "1h" else 100
        df = data_loader.get_latest_candles(symbol, limit=limit)
        
        if df is None or len(df) == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {symbol}"
            )
        
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        latest = df_with_indicators.iloc[-1]
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": str(latest.name),
            "indicators": {
                "rsi": round(float(latest['rsi']), 2),
                "macd": round(float(latest['macd']), 4),
                "macd_signal": round(float(latest['macd_signal']), 4),
                "macd_histogram": round(float(latest['macd_histogram']), 4),
                "bb_upper": round(float(latest['bb_upper']), 2),
                "bb_middle": round(float(latest['bb_middle']), 2),
                "bb_lower": round(float(latest['bb_lower']), 2),
                "ema_20": round(float(latest['ema_20']), 2),
                "ema_50": round(float(latest['ema_50']), 2),
                "price": round(float(latest['close']), 2),
                "volume": round(float(latest['volume']), 2)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching indicators: {str(e)}")

@app.get("/patterns/{symbol}")
async def get_patterns(symbol: str, timeframe: Optional[str] = "1h"):
    try:
        limit = 200 if timeframe == "1h" else 100
        df = data_loader.get_latest_candles(symbol, limit=limit)
        
        if df is None or len(df) == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {symbol}"
            )
        
        patterns = pattern_detector.detect_patterns(df)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "patterns": patterns
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting patterns: {str(e)}")

@app.post("/backtest")
async def backtest(request: BacktestRequest):
    try:
        # Calculate how many candles we need
        candles_per_day = {
            "1m": 1440,
            "5m": 288,
            "15m": 96,
            "1h": 24,
            "4h": 6,
            "1d": 1
        }
        
        limit = candles_per_day.get(request.timeframe, 24) * request.days
        df = data_loader.get_latest_candles(request.symbol, limit=limit)
        
        if df is None or len(df) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for backtest. Need at least 100 candles."
            )
        
        # Simple backtest logic
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        
        trades = []
        in_position = False
        entry_price = 0
        
        for i in range(50, len(df_with_indicators)):
            row = df_with_indicators.iloc[i]
            signal = technical_analyzer.generate_signal(df_with_indicators.iloc[:i+1])
            
            if not in_position and signal['type'] == 'LONG' and signal['confidence'] >= config.CONFIDENCE_THRESHOLD:
                in_position = True
                entry_price = row['close']
                trades.append({
                    'type': 'LONG',
                    'entry': float(entry_price),
                    'entry_time': str(row.name),
                    'confidence': signal['confidence']
                })
            
            elif in_position:
                # Exit conditions: opposite signal or stop loss
                if signal['type'] == 'SHORT' or (row['close'] < entry_price * 0.95):
                    exit_price = row['close']
                    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
                    
                    trades[-1]['exit'] = float(exit_price)
                    trades[-1]['exit_time'] = str(row.name)
                    trades[-1]['pnl_percent'] = round(pnl_percent, 2)
                    
                    in_position = False
        
        # Calculate stats
        winning_trades = [t for t in trades if 'pnl_percent' in t and t['pnl_percent'] > 0]
        losing_trades = [t for t in trades if 'pnl_percent' in t and t['pnl_percent'] <= 0]
        
        total_trades = len([t for t in trades if 'pnl_percent' in t])
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum([t.get('pnl_percent', 0) for t in trades])
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "days": request.days,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 2),
            "total_pnl_percent": round(total_pnl, 2),
            "trades": trades[-10:]  # Return last 10 trades
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Starting ML Engine API on {config.API_HOST}:{config.API_PORT}")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)