# ============================================
# FILE: worker.py (Root directory)
# ============================================
import os
import time
import logging
from dotenv import load_dotenv
import schedule
from datetime import datetime
import requests

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import your modules
try:
    from utils.data_loader import DataLoader
    from analysis.technical_enhanced import EnhancedTechnicalAnalyzer
    from analysis.pattern_detection_enhanced import EnhancedPatternDetector
    logger.info("✅ All imports successful")
except Exception as e:
    logger.error(f"❌ Import error: {e}")
    exit(1)

# Initialize components
try:
    data_loader = DataLoader()
    analyzer = EnhancedTechnicalAnalyzer()
    pattern_detector = EnhancedPatternDetector()
    logger.info("✅ Components initialized")
except Exception as e:
    logger.error(f"❌ Initialization error: {e}")
    exit(1)

# Optional: Telegram notifier (if you want alerts)
try:
    from telegram_bot.notifier import TelegramNotifier
    notifier = TelegramNotifier()
    HAS_TELEGRAM = True
except:
    HAS_TELEGRAM = False
    logger.warning("⚠️ Telegram notifier not available")

def collect_data():
    """Collect latest market data"""
    try:
        logger.info("🔄 Starting data collection...")
        
        # List of symbols to collect
        symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'LINK', 'MATIC', 'UNI']
        
        # You can import your collector here
        # from data_collector.binance_collector import BinanceCollector
        # collector = BinanceCollector()
        # collector.collect_all_symbols()
        
        logger.info(f"✅ Data collection completed for {len(symbols)} symbols")
    
    except Exception as e:
        logger.error(f"❌ Data collection error: {e}", exc_info=True)

def keep_alive():
    try:
        response = requests.get("https://ml-engine-bot-v1.onrender.com/health")
        logger.info(f"Keep-alive ping: {response.status_code}")
    except Exception as e:
        logger.error(f"Keep-alive failed: {e}")

# In schedule_tasks()
schedule.every(10).minutes.do(keep_alive)

def analyze_all():
    """Analyze all symbols and generate signals"""
    try:
        logger.info("📊 Starting analysis...")
        
        symbols = data_loader.get_all_symbols()
        high_confidence_signals = []
        
        for symbol in symbols:
            try:
                # Get latest candles
                df = data_loader.get_latest_candles(symbol, limit=200)
                
                if df is None or len(df) < 50:
                    continue
                
                # Calculate indicators
                df_analyzed = analyzer.calculate_all_indicators(df)
                
                # Generate signal
                signal = analyzer.generate_signal(df_analyzed)
                
                # Check confidence threshold
                if signal['confidence'] >= 65:
                    latest = df_analyzed.iloc[-1]
                    signal_data = {
                        'symbol': symbol,
                        'signal': signal['type'],
                        'confidence': signal['confidence'],
                        'strength': signal.get('strength'),
                        'price': round(float(latest['close']), 2),
                        'rsi': round(float(latest['rsi']), 2),
                        'macd': round(float(latest['macd']), 6),
                        'patterns': pattern_detector.detect_patterns(df),
                        'recommendation': signal['recommendation']
                    }
                    high_confidence_signals.append(signal_data)
                    logger.info(f"📈 Signal: {symbol} - {signal['type']} ({signal['confidence']}%)")
                    
                    # Send Telegram notification if available
                    if HAS_TELEGRAM:
                        try:
                            notifier.send_signal(symbol, signal)
                        except Exception as e:
                            logger.warning(f"Failed to send Telegram notification: {e}")
            
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        logger.info(f"✅ Analysis completed. Found {len(high_confidence_signals)} high confidence signals")
        return high_confidence_signals
    
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}", exc_info=True)
        return []

def health_check():
    """Check system health"""
    try:
        test_data = data_loader.get_latest_candles("BTC", limit=1)
        if test_data is not None:
            logger.info("✅ Health check passed - Database connected")
            return True
        else:
            logger.error("❌ Health check failed - No data from database")
            return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def schedule_tasks():
    """Configure task schedule"""
    # Data collection every 1 minute
    schedule.every(1).minutes.do(collect_data)
    
    # Analysis every 5 minutes
    schedule.every(5).minutes.do(analyze_all)
    
    # Health check every 30 minutes
    schedule.every(30).minutes.do(health_check)
    
    logger.info("✅ Tasks scheduled:")
    logger.info("   - Data collection: every 1 minute")
    logger.info("   - Analysis: every 5 minutes")
    logger.info("   - Health check: every 30 minutes")

def main():
    """Main worker loop"""
    logger.info("=" * 50)
    logger.info("🚀 Trading Bot Worker Started")
    logger.info("=" * 50)
    logger.info(f"Start time: {datetime.now()}")
    
    # Perform initial health check
    if not health_check():
        logger.error("❌ Initial health check failed. Exiting.")
        exit(1)
    
    # Schedule tasks
    schedule_tasks()
    
    # Run initial analysis
    try:
        logger.info("Running initial analysis...")
        analyze_all()
    except Exception as e:
        logger.error(f"Initial analysis failed: {e}")
    
    # Main loop
    logger.info("Entering main loop...")
    try:
        while True:
            # Run pending tasks
            schedule.run_pending()
            
            # Sleep briefly to prevent CPU spinning
            time.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("🛑 Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Critical error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Worker shutdown complete")

if __name__ == "__main__":
    main()