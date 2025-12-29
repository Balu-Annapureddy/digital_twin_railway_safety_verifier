"""
Demo script to test train simulation.
Run this to see the simulator in action.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation.simulator import TrainSimulator
import time


def main():
    """Run a simple simulation demo."""
    print("\n" + "="*60)
    print("Railway Digital Twin - Train Simulation Demo")
    print("="*60 + "\n")
    
    # Create simulator
    sim = TrainSimulator(time_step=1.0)
    
    # Add multiple trains
    print("Adding trains to simulation...")
    sim.add_train("T001", 10.0, 80.0, "INBOUND", "STOPPING")
    sim.add_train("T002", 15.0, 90.0, "INBOUND", "STOPPING")
    sim.add_train("T003", 8.0, 70.0, "INBOUND", "NON_STOPPING")
    
    print(f"✓ Added {sim.get_active_train_count()} trains\n")
    
    # Run simulation for 20 steps
    print("Running simulation (20 time steps)...\n")
    
    for step in range(20):
        state = sim.run_step()
        
        print(f"Step {step + 1} | Time: {state['simulation_time']}s | Active Trains: {state['active_trains']}")
        
        for train in state['trains']:
            print(f"  {train['id']}: {train['position']:.3f}km @ {train['speed']}kmph ({train['train_type']})")
        
        print()
        time.sleep(0.2)  # Slow down for readability
        
        if state['active_trains'] == 0:
            print("All trains have reached the station!")
            break
    
    print("\n" + "="*60)
    print("Simulation Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
