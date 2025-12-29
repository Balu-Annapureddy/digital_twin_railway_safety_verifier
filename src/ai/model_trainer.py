"""
Model trainer for ETA prediction.
Trains and evaluates Linear Regression and Random Forest models.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import pickle
from typing import Dict
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ETAModelTrainer:
    """
    Trains and evaluates ETA prediction models.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize trainer with dataset.
        
        Args:
            data_path: Path to training data CSV
        """
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        
    def load_data(self) -> None:
        """Load and prepare training data."""
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Loaded {len(self.df)} samples")
        
    def prepare_features(self) -> None:
        """Prepare features and target variables."""
        # Feature columns
        feature_cols = [
            'distance_remaining',
            'current_speed',
            'avg_speed',
            'speed_std',
            'train_type_encoded'
        ]
        
        X = self.df[feature_cols]
        y = self.df['eta_seconds']
        
        # Train-test split (80-20)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"✓ Training set: {len(self.X_train)} samples")
        print(f"✓ Test set: {len(self.X_test)} samples")
        
    def train_linear_regression(self) -> None:
        """Train Linear Regression model."""
        print("\nTraining Linear Regression...")
        
        lr_model = LinearRegression()
        lr_model.fit(self.X_train, self.y_train)
        
        self.models['linear_regression'] = lr_model
        print("✓ Linear Regression trained")
        
    def train_random_forest(self) -> None:
        """Train Random Forest model."""
        print("\nTraining Random Forest...")
        
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(self.X_train, self.y_train)
        
        self.models['random_forest'] = rf_model
        print("✓ Random Forest trained")
        
    def evaluate_models(self) -> Dict:
        """
        Evaluate all trained models.
        
        Returns:
            Dictionary with evaluation metrics
        """
        print("\n" + "="*60)
        print("Model Evaluation Results")
        print("="*60)
        
        results = {}
        
        for model_name, model in self.models.items():
            # Predictions
            y_pred = model.predict(self.X_test)
            
            # Metrics
            mae = mean_absolute_error(self.y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            r2 = r2_score(self.y_test, y_pred)
            
            results[model_name] = {
                'mae': mae,
                'rmse': rmse,
                'r2': r2
            }
            
            print(f"\n{model_name.upper()}:")
            print(f"  MAE:  {mae:.2f} seconds ({mae/60:.2f} minutes)")
            print(f"  RMSE: {rmse:.2f} seconds ({rmse/60:.2f} minutes)")
            print(f"  R²:   {r2:.4f}")
            
        print("\n" + "="*60)
        
        return results
    
    def save_models(self, output_dir: str) -> None:
        """
        Save trained models to disk.
        
        Args:
            output_dir: Directory to save models
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            filepath = os.path.join(output_dir, f"{model_name}.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            print(f"✓ Saved {model_name} to {filepath}")
    
    def train_all(self) -> None:
        """Complete training pipeline."""
        self.load_data()
        self.prepare_features()
        self.train_linear_regression()
        self.train_random_forest()
        self.evaluate_models()


if __name__ == "__main__":
    # Path to training data
    data_path = os.path.join(
        os.path.dirname(__file__),
        '../../data/datasets/eta_training_data.csv'
    )
    
    # Train models
    trainer = ETAModelTrainer(data_path)
    trainer.train_all()
    
    # Save models
    model_dir = os.path.join(os.path.dirname(__file__), '../../data/models')
    trainer.save_models(model_dir)
    
    print("\n✓ Training complete!")
