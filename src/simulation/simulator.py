"""
Train movement simulator.
Manages multiple trains and simulates their movement over time.
"""

from typing import List, Dict, Optional
import time
from datetime import datetime
from .train import Train


class TrainSimulator:
    """
    Simulates movement of multiple trains in the railway system.
    
    Manages train creation, position updates, and state tracking.
    """
    
    def __init__(self, time_step: float = 1.0):
        """
        Initialize the simulator.
        
        Args:
            time_step: Simulation time step in seconds (default: 1 second)
        """
        self.trains: List[Train] = []
        self.time_step = time_step
        self.simulation_time = 0.0  # Total simulation time in seconds
        self.is_running = False
        
    def add_train(
        self,
        train_id: str,
        initial_position: float,
        initial_speed: float,
        direction: str = "INBOUND",
        train_type: str = "STOPPING"
    ) -> Train:
        """
        Add a new train to the simulation.
        
        Args:
            train_id: Unique identifier
            initial_position: Starting distance from station (km)
            initial_speed: Starting speed (kmph)
            direction: INBOUND or OUTBOUND
            train_type: STOPPING or NON_STOPPING
            
        Returns:
            The created Train object
        """
        train = Train(train_id, initial_position, initial_speed, direction, train_type)
        self.trains.append(train)
        return train
    
    def remove_train(self, train_id: str) -> bool:
        """
        Remove a train from the simulation.
        
        Args:
            train_id: ID of train to remove
            
        Returns:
            True if train was removed, False if not found
        """
        for i, train in enumerate(self.trains):
            if train.id == train_id:
                self.trains.pop(i)
                return True
        return False
    
    def get_train(self, train_id: str) -> Optional[Train]:
        """
        Get a train by ID.
        
        Args:
            train_id: ID of train to retrieve
            
        Returns:
            Train object or None if not found
        """
        for train in self.trains:
            if train.id == train_id:
                return train
        return None
    
    def update_all_trains(self) -> None:
        """
        Update positions of all trains by one time step.
        """
        for train in self.trains:
            train.update_position(self.time_step)
        
        self.simulation_time += self.time_step
        
        # Remove trains that have reached the station
        self.trains = [t for t in self.trains if not t.has_reached_station()]
    
    def get_all_states(self) -> List[Dict]:
        """
        Get current state of all trains.
        
        Returns:
            List of train state dictionaries
        """
        return [train.get_state() for train in self.trains]
    
    def get_active_train_count(self) -> int:
        """
        Get number of active trains.
        
        Returns:
            Count of trains in simulation
        """
        return len(self.trains)
    
    def run_step(self) -> Dict:
        """
        Run one simulation step and return current state.
        
        Returns:
            Dictionary with simulation state
        """
        self.update_all_trains()
        
        return {
            "simulation_time": round(self.simulation_time, 1),
            "active_trains": self.get_active_train_count(),
            "trains": self.get_all_states()
        }
    
    def reset(self) -> None:
        """
        Reset the simulation to initial state.
        """
        self.trains.clear()
        self.simulation_time = 0.0
        self.is_running = False
    
    def __repr__(self) -> str:
        """String representation of the simulator."""
        return f"TrainSimulator(trains={len(self.trains)}, time={self.simulation_time:.1f}s)"
