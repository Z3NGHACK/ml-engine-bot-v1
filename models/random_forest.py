import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from utils.preprocessor import DataPreprocessor

class RandomForestModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.preprocessor = DataPreprocessor()

    def prepare_features(self, df_with_indicators):
        # Features from indicators
        features = df_with_indicators[['rsi', 'macd', 'macd_histogram', 'bb_upper', 'bb_lower', 'ema_20', 'ema_50', 'volume']].values
        # Labels: 1=LONG (price up), -1=SHORT (down), 0=NEUTRAL
        shifts = df_with_indicators['close'].shift(-1) - df_with_indicators['close']
        labels = np.where(shifts > 0.001, 1, np.where(shifts < -0.001, -1, 0))[:-1]  # Trim last for shift
        features = features[:-1]  # Align
        return features, labels

    def train(self, df_with_indicators):
        X, y = self.prepare_features(df_with_indicators)
        if len(X) < 100:
            return
        self.model.fit(X, y)
        print(f"✅ RF trained. Accuracy: {accuracy_score(y, self.model.predict(X)):.2f}")

    def predict(self, df_with_indicators):
        latest = df_with_indicators.iloc[-1:]
        features = latest[['rsi', 'macd', 'macd_histogram', 'bb_upper', 'bb_lower', 'ema_20', 'ema_50', 'volume']].values
        pred = self.model.predict(features)[0]
        if pred == 1:
            return 'LONG'
        elif pred == -1:
            return 'SHORT'
        return 'NEUTRAL'

    def save(self, path='models/rf_model.pkl'):
        joblib.dump(self.model, path)
        print("✅ RF saved")

    def load(self, path='models/rf_model.pkl'):
        self.model = joblib.load(path)
        print("✅ RF loaded")