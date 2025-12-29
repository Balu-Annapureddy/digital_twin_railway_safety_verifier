"""
Training data generator for ETA prediction.
Generates synthetic dataset from train simulation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
from typing import List, Dict
from src.simulation.simulator import TrainSimulator


class ETADataGenerator:
    """
    Generates training data for ETA prediction models.
    Uses train simulation to create realistic scenarios.
    """
    
    def __init__(self, num_samples: int = 1000):
        """
        Initialize data generator.
        
        Args:
            num_samples: Number of training samples to generate
        """
        self.num_samples = num_samples
        self.data: List[Dict] = []
        
    def generate_dataset(self) -> pd.DataFrame:
        """
        Generate complete training dataset.
        
        Returns:
            DataFrame with features and target ETA values
        """
        print(f"Generating {self.num_samples} training samples...")
        
        for i in range(self.num_samples):
            # Random initial conditions
            initial_distance = np.random.uniform(1.0, 20.0)  # 1-20 km
            initial_speed = np.random.uniform(40.0, 120.0)   # 40-120 kmph
            train_type = np.random.choice(["STOPPING", "NON_STOPPING"])
            
            # Create simulator and train
            sim = TrainSimulator(time_step=1.0)
            train = sim.add_train(
                f"T{i:04d}",
                initial_distance,
                initial_speed,
                "INBOUND",
                train_type
            )
            
            # Simulate with speed variations
            time_elapsed = 0
            speed_history = [initial_speed]
            
            while train.position > 0 and time_elapsed < 3600:  # Max 1 hour
                # Add realistic speed variations
                speed_change = np.random.uniform(-5, 5)
                new_speed = max(20, min(120, train.speed + speed_change))
                train.update_speed(new_speed)
                
                sim.run_step()
                speed_history.append(train.speed)
                time_elapsed += 1
                
                # Sample at random point during journey
                if np.random.random() < 0.3 and train.position > 0.5:
                    # Record this state as a training sample
                    avg_speed = np.mean(speed_history[-10:]) if len(speed_history) >= 10 else train.speed
                    speed_std = np.std(speed_history[-10:]) if len(speed_history) >= 10 else 0
                    
                    # Calculate actual ETA (time remaining to reach station)
                    remaining_distance = train.position
                    current_speed = train.speed
                    
                    # Simple ETA calculation (will be refined by ML)
                    if current_speed > 0:
                        actual_eta = (remaining_distance / current_speed) * 3600  # Convert to seconds
                    else:
                        actual_eta = 9999
                    
                    self.data.append({
                        'distance_remaining': remaining_distance,
                        'current_speed': current_speed,
                        'avg_speed': avg_speed,
                        'speed_std': speed_std,
                        'train_type': train_type,
                        'eta_seconds': actual_eta
                    })
            
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1}/{self.num_samples} scenarios...")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.data)
        
        # Encode train_type
        df['train_type_encoded'] = df['train_type'].map({'STOPPING': 1, 'NON_STOPPING': 0})
        
        # Remove outliers (ETA > 1 hour)
        df = df[df['eta_seconds'] < 3600]
        
        print(f"✓ Generated {len(df)} valid training samples")
        
        return df
    
    def save_dataset(self, filepath: str) -> None:
        """
        Save generated dataset to CSV.
        
        Args:
            filepath: Path to save CSV file
        """
        df = pd.DataFrame(self.data)
        df.to_csv(filepath, index=False)
        print(f"✓ Dataset saved to {filepath}")


if __name__ == "__main__":
    # Generate and save dataset
    generator = ETADataGenerator(num_samples=500)
    df = generator.generate_dataset()
    
    # Save to data folder
    output_path = os.path.join(os.path.dirname(__file__), '../../data/datasets/eta_training_data.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset saved to: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Features: {list(df.columns)}")
