# ============================================
# FILE: config.py
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
MODEL_TYPE = os.getenv('MODEL_TYPE', 'ensemble')
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', 70))

RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
EMA_FAST = 9
EMA_SLOW = 21
