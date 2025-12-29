"""
Unit tests for train simulation module.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation.train import Train
from src.simulation.simulator import TrainSimulator


def test_train_creation():
    """Test train object creation."""
    train = Train("T001", 10.0, 80.0, "INBOUND", "STOPPING")
    
    assert train.id == "T001"
    assert train.position == 10.0
    assert train.speed == 80.0
    assert train.direction == "INBOUND"
    assert train.train_type == "STOPPING"
    print("✓ Train creation test passed")


def test_train_movement():
    """Test train position update."""
    train = Train("T001", 10.0, 80.0, "INBOUND", "STOPPING")
    
    initial_position = train.position
    train.update_position(1.0)  # 1 second
    
    # Speed is 80 kmph = 80/3600 km/s = 0.0222 km/s
    # After 1 second, position should decrease by ~0.0222 km
    assert train.position < initial_position
    assert abs(train.position - (10.0 - 80.0/3600.0)) < 0.001
    print("✓ Train movement test passed")


def test_train_reaches_station():
    """Test train reaching station detection."""
    train = Train("T001", 0.01, 80.0, "INBOUND", "STOPPING")
    
    # Update position multiple times
    for _ in range(10):
        train.update_position(1.0)
    
    assert train.has_reached_station()
    print("✓ Train reaches station test passed")


def test_simulator_add_train():
    """Test adding trains to simulator."""
    sim = TrainSimulator()
    
    sim.add_train("T001", 10.0, 80.0)
    sim.add_train("T002", 15.0, 90.0)
    
    assert sim.get_active_train_count() == 2
    print("✓ Simulator add train test passed")


def test_simulator_update():
    """Test simulator update step."""
    sim = TrainSimulator()
    sim.add_train("T001", 10.0, 80.0, "INBOUND", "STOPPING")
    
    state = sim.run_step()
    
    assert state["simulation_time"] == 1.0
    assert state["active_trains"] == 1
    assert len(state["trains"]) == 1
    print("✓ Simulator update test passed")


def test_simulator_remove_arrived_trains():
    """Test automatic removal of trains that reached station."""
    sim = TrainSimulator()
    sim.add_train("T001", 0.01, 80.0, "INBOUND", "STOPPING")
    
    # Run simulation until train reaches station
    for _ in range(10):
        sim.run_step()
    
    # Train should be automatically removed
    assert sim.get_active_train_count() == 0
    print("✓ Simulator remove arrived trains test passed")


if __name__ == "__main__":
    print("\n=== Running Train Simulation Tests ===\n")
    
    test_train_creation()
    test_train_movement()
    test_train_reaches_station()
    test_simulator_add_train()
    test_simulator_update()
    test_simulator_remove_arrived_trains()
    
    print("\n=== All Tests Passed! ===\n")
