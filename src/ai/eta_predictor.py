"""
ETA Predictor - Main prediction interface.
Loads trained models and provides ETA predictions with confidence scores.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pickle
import numpy as np
from typing import Dict, Tuple


class ETAPredictor:
    """
    Predicts train arrival time using trained ML models.
    """
    
    def __init__(self, model_dir: str):
        """
        Initialize predictor with trained models.
        
        Args:
            model_dir: Directory containing saved model files
        """
        self.model_dir = model_dir
        self.lr_model = None
        self.rf_model = None
        self.load_models()
        
    def load_models(self) -> None:
        """Load trained models from disk."""
        # Load Linear Regression
        lr_path = os.path.join(self.model_dir, 'linear_regression.pkl')
        if os.path.exists(lr_path):
            with open(lr_path, 'rb') as f:
                self.lr_model = pickle.load(f)
            print("✓ Loaded Linear Regression model")
        
        # Load Random Forest
        rf_path = os.path.join(self.model_dir, 'random_forest.pkl')
        if os.path.exists(rf_path):
            with open(rf_path, 'rb') as f:
                self.rf_model = pickle.load(f)
            print("✓ Loaded Random Forest model")
    
    def predict(
        self,
        distance_remaining: float,
        current_speed: float,
        avg_speed: float,
        speed_std: float,
        train_type: str,
        use_model: str = 'random_forest'
    ) -> Tuple[float, float]:
        """
        Predict ETA for a train.
        
        Args:
            distance_remaining: Distance to station in km
            current_speed: Current speed in kmph
            avg_speed: Average speed in kmph
            speed_std: Speed standard deviation
            train_type: STOPPING or NON_STOPPING
            use_model: 'linear_regression' or 'random_forest'
            
        Returns:
            Tuple of (eta_seconds, confidence_score)
        """
        # Encode train type
        train_type_encoded = 1 if train_type == "STOPPING" else 0
        
        # Prepare features
        features = np.array([[
            distance_remaining,
            current_speed,
            avg_speed,
            speed_std,
            train_type_encoded
        ]])
        
        # Select model
        if use_model == 'linear_regression' and self.lr_model:
            model = self.lr_model
        elif use_model == 'random_forest' and self.rf_model:
            model = self.rf_model
        else:
            raise ValueError(f"Model {use_model} not available")
        
        # Predict
        eta_seconds = model.predict(features)[0]
        
        # Calculate confidence score (simplified)
        # Higher confidence for:
        # - Consistent speed (low std)
        # - Reasonable distance
        # - Normal speed range
        confidence = self._calculate_confidence(
            distance_remaining,
            current_speed,
            speed_std
        )
        
        return eta_seconds, confidence
    
    def _calculate_confidence(
        self,
        distance: float,
        speed: float,
        speed_std: float
    ) -> float:
        """
        Calculate prediction confidence score.
        
        Args:
            distance: Distance remaining
            speed: Current speed
            speed_std: Speed standard deviation
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 1.0
        
        # Reduce confidence for high speed variance
        if speed_std > 10:
            confidence -= 0.2
        elif speed_std > 5:
            confidence -= 0.1
            
        # Reduce confidence for very low or very high speeds
        if speed < 30 or speed > 110:
            confidence -= 0.1
            
        # Reduce confidence for very short or very long distances
        if distance < 0.5 or distance > 18:
            confidence -= 0.1
        
        return max(0.5, min(1.0, confidence))
    
    def predict_from_train_state(self, train_state: Dict) -> Dict:
        """
        Predict ETA from train state dictionary.
        
        Args:
            train_state: Train state from simulator
            
        Returns:
            Dictionary with ETA prediction and confidence
        """
        eta_seconds, confidence = self.predict(
            distance_remaining=train_state['position'],
            current_speed=train_state['speed'],
            avg_speed=train_state['avg_speed'],
            speed_std=train_state['speed_variance'],
            train_type=train_state['train_type'],
            use_model='random_forest'
        )
        
        return {
            'train_id': train_state['id'],
            'eta_seconds': round(eta_seconds, 1),
            'eta_minutes': round(eta_seconds / 60, 2),
            'confidence': round(confidence, 2)
        }


if __name__ == "__main__":
    # Example usage
    model_dir = os.path.join(os.path.dirname(__file__), '../../data/models')
    
    predictor = ETAPredictor(model_dir)
    
    # Test prediction
    eta, conf = predictor.predict(
        distance_remaining=5.0,
        current_speed=80.0,
        avg_speed=78.0,
        speed_std=3.5,
        train_type="STOPPING"
    )
    
    print(f"\nTest Prediction:")
    print(f"  ETA: {eta:.1f} seconds ({eta/60:.2f} minutes)")
    print(f"  Confidence: {conf:.2f}")
