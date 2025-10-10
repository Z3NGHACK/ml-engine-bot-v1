# ============================================
# FILE: config.py
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = 'test'  # ✅ Your database name
COLLECTION_NAME = 'marketdatas'
# Model Configuration
MODEL_TYPE = os.getenv('MODEL_TYPE', 'ensemble')
PREDICTION_HORIZON = int(os.getenv('PREDICTION_HORIZON', 5))
CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', 70))

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))

# Training Configuration
TRAIN_TEST_SPLIT = float(os.getenv('TRAIN_TEST_SPLIT', 0.8))
EPOCHS = int(os.getenv('EPOCHS', 100))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 32))

# Technical Indicators Configuration
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
EMA_FAST = 12
EMA_SLOW = 26
EMA_SHORT = 20
EMA_LONG = 50
SMA_PERIOD = 20

print(f"✅ Config loaded - Database: {DATABASE_NAME}, Collection: {COLLECTION_NAME}")