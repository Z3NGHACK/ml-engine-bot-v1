from models.lstm_model import LSTMModel
from models.random_forest import RandomForestModel

class EnsembleModel:
    def __init__(self):
        self.lstm = LSTMModel()
        self.rf = RandomForestModel()
        self.lstm.load()
        self.rf.load()

    def predict(self, df, df_with_indicators):
        lstm_pred_price = self.lstm.predict(df)
        current_price = df['close'].iloc[-1]
        lstm_signal = 'LONG' if lstm_pred_price > current_price else 'SHORT' if lstm_pred_price < current_price else 'NEUTRAL'
        
        rf_signal = self.rf.predict(df_with_indicators)
        
        # Ensemble: Majority vote or average (here, simple vote)
        if lstm_signal == rf_signal:
            return lstm_signal
        elif lstm_signal == 'LONG' or rf_signal == 'LONG':
            return 'LONG'  # Bias towards action if one says so
        elif lstm_signal == 'SHORT' or rf_signal == 'SHORT':
            return 'SHORT'
        return 'NEUTRAL'