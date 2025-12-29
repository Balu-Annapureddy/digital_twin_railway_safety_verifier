"""
Train class for railway simulation.
Represents a single train with position, speed, and movement logic.
"""

from typing import List, Dict
from datetime import datetime


class Train:
    """
    Represents a train in the railway system.
    
    Attributes:
        id (str): Unique train identifier
        position (float): Distance from station in kilometers
        speed (float): Current speed in kmph
        direction (str): INBOUND or OUTBOUND
        train_type (str): STOPPING or NON_STOPPING
        speed_history (List[float]): Historical speed values
    """
    
    def __init__(
        self,
        train_id: str,
        initial_position: float,
        initial_speed: float,
        direction: str = "INBOUND",
        train_type: str = "STOPPING"
    ):
        """
        Initialize a new train.
        
        Args:
            train_id: Unique identifier for the train
            initial_position: Starting distance from station (km)
            initial_speed: Starting speed (kmph)
            direction: INBOUND or OUTBOUND
            train_type: STOPPING or NON_STOPPING
        """
        self.id = train_id
        self.position = initial_position
        self.speed = initial_speed
        self.direction = direction
        self.train_type = train_type
        self.speed_history: List[float] = [initial_speed]
        self.created_at = datetime.now()
        
    def update_position(self, time_step: float = 1.0) -> None:
        """
        Update train position based on current speed and time step.
        
        Args:
            time_step: Time interval in seconds (default: 1 second)
        """
        # Convert speed from kmph to km/s
        speed_km_per_sec = self.speed / 3600.0
        
        # Calculate distance traveled in this time step
        distance_traveled = speed_km_per_sec * time_step
        
        # Update position (decrease if INBOUND, increase if OUTBOUND)
        if self.direction == "INBOUND":
            self.position -= distance_traveled
        else:
            self.position += distance_traveled
            
        # Record speed in history
        self.speed_history.append(self.speed)
        
        # Keep only last 100 speed records to avoid memory issues
        if len(self.speed_history) > 100:
            self.speed_history = self.speed_history[-100:]
    
    def update_speed(self, new_speed: float) -> None:
        """
        Update train speed.
        
        Args:
            new_speed: New speed in kmph
        """
        self.speed = max(0, new_speed)  # Ensure speed is non-negative
    
    def get_state(self) -> Dict:
        """
        Get current train state as a dictionary.
        
        Returns:
            Dictionary containing all train state information
        """
        return {
            "id": self.id,
            "position": round(self.position, 3),
            "speed": round(self.speed, 2),
            "direction": self.direction,
            "train_type": self.train_type,
            "avg_speed": round(sum(self.speed_history) / len(self.speed_history), 2),
            "speed_variance": round(self._calculate_speed_variance(), 2)
        }
    
    def _calculate_speed_variance(self) -> float:
        """
        Calculate variance in speed history.
        
        Returns:
            Speed variance value
        """
        if len(self.speed_history) < 2:
            return 0.0
        
        avg_speed = sum(self.speed_history) / len(self.speed_history)
        variance = sum((s - avg_speed) ** 2 for s in self.speed_history) / len(self.speed_history)
        return variance ** 0.5  # Return standard deviation
    
    def has_reached_station(self) -> bool:
        """
        Check if train has reached the station.
        
        Returns:
            True if position <= 0 (for INBOUND trains)
        """
        if self.direction == "INBOUND":
            return self.position <= 0
        return False
    
    def __repr__(self) -> str:
        """String representation of the train."""
        return f"Train({self.id}, pos={self.position:.2f}km, speed={self.speed}kmph, {self.direction})"
