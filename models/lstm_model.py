import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
from utils.preprocessor import DataPreprocessor

class LSTMModel:
    def __init__(self, lookback=60):
        self.lookback = lookback
        self.model = None
        self.preprocessor = DataPreprocessor()

    def build_model(self, input_shape):
        self.model = Sequential()
        self.model.add(LSTM(50, return_sequences=True, input_shape=(input_shape, 1)))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(50, return_sequences=False))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(25))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        print("✅ LSTM model built")

    def train(self, X, y, epochs=50, batch_size=32):
        if self.model is None:
            self.build_model(X.shape[1])
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2)
        print("✅ LSTM trained")

    def predict(self, df):
        X, _ = self.preprocessor.prepare_for_ml(df, self.lookback)
        if len(X) == 0:
            return None
        X = np.reshape(X[-1], (1, self.lookback, 1))  # Last sequence for next prediction
        predicted_scaled = self.model.predict(X)
        predicted = self.preprocessor.inverse_transform(predicted_scaled)
        return predicted[0][0]  # Predicted next close

    def save(self, path='models/lstm_model.h5'):
        self.model.save(path)
        joblib.dump(self.preprocessor.scaler, 'models/lstm_scaler.pkl')
        print("✅ LSTM saved")

    def load(self, path='models/lstm_model.h5'):
        from tensorflow.keras.models import load_model
        self.model = load_model(path)
        self.preprocessor.scaler = joblib.load('models/lstm_scaler.pkl')
        print("✅ LSTM loaded")