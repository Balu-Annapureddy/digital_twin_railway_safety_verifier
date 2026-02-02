"""
ML Models - Lightweight Machine Learning for Digital Twin.
Includes Anomaly Detection (Isolation Forest) and Rule-based Risk Scoring.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple

class AnomalyDetector:
    """
    Detects anomalies in system behavior using Isolation Forest.
    Features: Event frequency, Active Trains (proxy), Violation Count.
    """
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        
    def prepare_features(self, merged_df: pd.DataFrame, violations_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates data into fixed time windows (e.g., minutes) to create features.
        """
        if merged_df.empty:
            return pd.DataFrame()
            
        df = merged_df.copy()
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('datetime')
        
        # Resample to 1-minute intervals
        # Feature 1: Events per minute
        features = df.resample('1min').size().to_frame(name='events_per_min')
        
        # Feature 2: Violations per minute
        if not violations_df.empty:
            v_df = violations_df.copy()
            v_df['datetime'] = pd.to_datetime(v_df['timestamp'])
            v_df = v_df.set_index('datetime')
            v_counts = v_df.resample('1min').size()
            features['violations_per_min'] = v_counts
        else:
            features['violations_per_min'] = 0
            
        features = features.fillna(0)
        
        # Feature 3: Train movement (proxy for system activity)
        # We can sum distance changes
        if 'gate_nearest_train_m' in df.columns:
            # Calculate sum of absolute changes in distance per minute
            dist_change = df['gate_nearest_train_m'].diff().abs()
            features['activity_index'] = dist_change.resample('1min').sum()
        else:
            features['activity_index'] = 0
            
        features = features.fillna(0)
            
        return features
        
    def train_and_predict(self, merged_df: pd.DataFrame, violations_df: pd.DataFrame) -> pd.DataFrame:
        """
        Trains the model and returns dataframe with 'anomaly_score' (-1 to 1).
        """
        features = self.prepare_features(merged_df, violations_df)
        
        if features.empty:
            return pd.DataFrame()
            
        # Train
        X = features.values
        self.model.fit(X)
        self.is_trained = True
        
        # Predict
        # Decision function: lower = more anomalous
        scores = self.model.decision_function(X)
        predictions = self.model.predict(X) # -1 for outlier, 1 for inlier
        
        features['anomaly_score'] = scores
        features['is_anomaly'] = predictions
        
        # Scale score for UI (0-100)
        # raw score roughly -0.5 to 0.5. 
        # Flip: Lower score is simpler for users (0=Normal, 100=Anomaly)? 
        # Or standard "Anomaly Score" where higher is weird. 
        # Let's map: Min score -> 100, Max score -> 0
        min_s, max_s = scores.min(), scores.max()
        if max_s != min_s:
            features['ui_score'] = 100 - ((scores - min_s) / (max_s - min_s) * 100)
        else:
            features['ui_score'] = 0
            
        return features.reset_index()

class RiskScorer:
    """
    Calculates a composite Risk Score (0-100).
    """
    
    def calculate_score(self, signal_violations: int, gate_violations: int, congestion_events: int) -> int:
        """
        Weighted formula:
        Risk = (w1 * Sig) + (w2 * Gate) + (w3 * Congest)
        Max capped at 100.
        """
        w1 = 20 # High risk
        w2 = 15 # Medium risk
        w3 = 10 # Congestion
        
        raw_score = (w1 * signal_violations) + (w2 * gate_violations) + (w3 * congestion_events)
        
        return min(100, raw_score)
