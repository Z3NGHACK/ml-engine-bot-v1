# ============================================
# FILE: api/app.py
# ============================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
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
    days: Optional[int] = 7

@app.get("/")
async def root():
    return {"service": "Crypto ML Engine", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_symbol(request: AnalysisRequest):
    try:
        df = data_loader.get_latest_candles(request.symbol, limit=100)
        
        if df is None or len(df) < 50:
            raise HTTPException(status_code=400, 
                detail=f"Insufficient data for {request.symbol}")
        
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        signal = technical_analyzer.generate_signal(df_with_indicators)
        patterns = pattern_detector.detect_patterns(df)
        
        return {
            "symbol": request.symbol,
            "signal_type": signal['type'],
            "confidence": signal['confidence'],
            "indicators": signal['indicators'],
            "patterns": patterns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indicators/{symbol}")
async def get_indicators(symbol: str):
    try:
        df = data_loader.get_latest_candles(symbol, limit=100)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        latest = df_with_indicators.iloc[-1]
        
        return {
            "symbol": symbol,
            "indicators": {
                "rsi": float(latest['rsi']),
                "macd": float(latest['macd']),
                "price": float(latest['close']),
                "volume": float(latest['volume'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)