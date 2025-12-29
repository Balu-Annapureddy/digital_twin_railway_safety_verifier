"""
Demo script for ETA prediction system.
Generates data, trains models, and demonstrates predictions.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.data_generator import ETADataGenerator
from src.ai.model_trainer import ETAModelTrainer
from src.ai.eta_predictor import ETAPredictor
from src.simulation.simulator import TrainSimulator


def main():
    """Run complete ETA prediction demo."""
    print("\n" + "="*60)
    print("Railway Digital Twin - ETA Prediction Demo")
    print("="*60 + "\n")
    
    # Step 1: Generate training data
    print("STEP 1: Generating training data...")
    print("-" * 60)
    generator = ETADataGenerator(num_samples=500)
    df = generator.generate_dataset()
    
    data_path = 'data/datasets/eta_training_data.csv'
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    df.to_csv(data_path, index=False)
    print(f"✓ Saved {len(df)} samples to {data_path}\n")
    
    # Step 2: Train models
    print("STEP 2: Training ML models...")
    print("-" * 60)
    trainer = ETAModelTrainer(data_path)
    trainer.train_all()
    
    model_dir = 'data/models'
    trainer.save_models(model_dir)
    print()
    
    # Step 3: Test predictions
    print("STEP 3: Testing predictions...")
    print("-" * 60)
    predictor = ETAPredictor(model_dir)
    
    # Create test scenario
    sim = TrainSimulator()
    train = sim.add_train("T001", 10.0, 80.0, "INBOUND", "STOPPING")
    
    print("\nSimulating train and predicting ETA at different points:\n")
    
    for step in range(0, 200, 40):
        # Run simulation
        for _ in range(40):
            sim.run_step()
        
        # Get train state
        if sim.get_active_train_count() == 0:
            print("Train has reached the station!")
            break
            
        train_state = sim.get_all_states()[0]
        
        # Predict ETA
        prediction = predictor.predict_from_train_state(train_state)
        
        print(f"Step {step + 40}:")
        print(f"  Position: {train_state['position']:.2f} km")
        print(f"  Speed: {train_state['speed']:.1f} kmph")
        print(f"  Predicted ETA: {prediction['eta_minutes']:.2f} minutes")
        print(f"  Confidence: {prediction['confidence']:.2f}")
        print()
    
    print("="*60)
    print("Demo Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
