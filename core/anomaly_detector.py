import os
import joblib
import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, model_path='models/isolation_forest.pkl'):
        self.model_path = model_path
        # Use a slightly higher contamination to ensure we catch things, 
        # but in a real system this would be tuned.
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False
        self.last_training_time = None
        self.training_samples = 0
        self.features_used = []
        
        # Load model if it exists
        self.load_model()

    def train(self, ml_df):
        if ml_df is None or ml_df.empty:
            return False
            
        self.features_used = list(ml_df.columns)
        self.training_samples = len(ml_df)
        self.model.fit(ml_df)
        self.is_trained = True
        self.last_training_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_model()
        return True

    def predict(self, ml_df):
        """
        Returns an anomaly score for each row.
        Higher score = more anomalous.
        """
        if not self.is_trained or ml_df is None or ml_df.empty:
            return np.zeros(len(ml_df) if ml_df is not None else 0)
            
        # decision_function returns > 0 for normal, < 0 for anomalies
        # We invert it so higher is more anomalous, then normalize to 0-1
        scores = self.model.decision_function(ml_df)
        
        # Invert: now higher values mean more anomalous
        scores = -scores
        
        # Normalize: Typically scores range from -0.5 to 0.5. 
        # Let's clip and scale to [0, 1] for easier risk engine mapping
        min_score, max_score = -0.3, 0.3
        normalized_scores = (scores - min_score) / (max_score - min_score)
        normalized_scores = np.clip(normalized_scores, 0, 1)
        
        return normalized_scores
        
    def save_model(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'is_trained': self.is_trained,
                'last_training_time': self.last_training_time,
                'training_samples': self.training_samples,
                'features_used': self.features_used
            }, self.model_path)
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.is_trained = data['is_trained']
                self.last_training_time = data['last_training_time']
                self.training_samples = data['training_samples']
                self.features_used = data['features_used']
            except Exception as e:
                print(f"Error loading model: {e}")
                self.is_trained = False
