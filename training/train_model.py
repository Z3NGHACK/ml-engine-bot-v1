import pandas as pd
from utils.data_loader import DataLoader
from analysis.technical import TechnicalAnalyzer
from models.lstm_model import LSTMModel
from models.random_forest import RandomForestModel
import config

def train_models():
    loader = DataLoader()
    analyzer = TechnicalAnalyzer()
    
    # Load all BTC data (your 2500+ docs)
    df = loader.get_latest_candles('BTC', limit=3000)  # More than 2500
    if df is None or len(df) < 100:
        print("❌ Insufficient data for training")
        return
    
    df_with_indicators = analyzer.calculate_all_indicators(df)
    
    # Train LSTM
    lstm = LSTMModel()
    X, y = lstm.preprocessor.prepare_for_ml(df_with_indicators)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    lstm.build_model(X.shape[1])
    lstm.train(X, y, epochs=config.EPOCHS, batch_size=config.BATCH_SIZE)
    lstm.save()
    
    # Train RF
    rf = RandomForestModel()
    rf.train(df_with_indicators)
    rf.save()
    
    print("✅ Training complete")

if __name__ == "__main__":
    train_models()