"""
Track Occupancy and Platform Manager.
Manages track states and allocations with safety validation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum
from config.settings import TRACK_IDS, MIN_CLEARANCE_TIME


class TrackState(Enum):
    """Track state enumeration."""
    FREE = "FREE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    CLEARING = "CLEARING"


class Track:
    """
    Represents a single platform track.
    """
    
    def __init__(self, track_id: str):
        """
        Initialize track.
        
        Args:
            track_id: Unique track identifier
        """
        self.track_id = track_id
        self.state = TrackState.FREE
        self.allocated_to: Optional[str] = None
        self.expected_arrival_time: Optional[float] = None
        self.clearance_time = MIN_CLEARANCE_TIME
        self.last_state_change = datetime.now()
        self.history: List[Dict] = []
        
    def reserve(self, train_id: str, eta_seconds: float) -> bool:
        """
        Reserve track for incoming train.
        
        Args:
            train_id: ID of train to reserve for
            eta_seconds: Expected arrival time in seconds
            
        Returns:
            True if reservation successful
        """
        if self.state != TrackState.FREE:
            return False
        
        self.state = TrackState.RESERVED
        self.allocated_to = train_id
        self.expected_arrival_time = eta_seconds
        self.last_state_change = datetime.now()
        
        self._log_state_change("RESERVED", train_id)
        return True
    
    def occupy(self, train_id: str) -> bool:
        """
        Mark track as occupied by train.
        
        Args:
            train_id: ID of train occupying track
            
        Returns:
            True if occupation successful
        """
        if self.state != TrackState.RESERVED or self.allocated_to != train_id:
            return False
        
        self.state = TrackState.OCCUPIED
        self.last_state_change = datetime.now()
        
        self._log_state_change("OCCUPIED", train_id)
        return True
    
    def start_clearing(self) -> bool:
        """
        Start clearing process after train departs.
        
        Returns:
            True if clearing started
        """
        if self.state != TrackState.OCCUPIED:
            return False
        
        self.state = TrackState.CLEARING
        self.last_state_change = datetime.now()
        
        self._log_state_change("CLEARING", self.allocated_to)
        return True
    
    def clear(self) -> bool:
        """
        Mark track as cleared and free.
        
        Returns:
            True if clearing successful
        """
        if self.state != TrackState.CLEARING:
            return False
        
        train_id = self.allocated_to
        
        self.state = TrackState.FREE
        self.allocated_to = None
        self.expected_arrival_time = None
        self.last_state_change = datetime.now()
        
        self._log_state_change("FREE", train_id)
        return True
    
    def get_state(self) -> Dict:
        """
        Get current track state.
        
        Returns:
            Dictionary with track state information
        """
        return {
            "track_id": self.track_id,
            "state": self.state.value,
            "allocated_to": self.allocated_to,
            "expected_arrival": self.expected_arrival_time,
            "clearance_time": self.clearance_time
        }
    
    def _log_state_change(self, new_state: str, train_id: Optional[str]) -> None:
        """Log state change to history."""
        self.history.append({
            "timestamp": datetime.now(),
            "state": new_state,
            "train_id": train_id
        })
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Track({self.track_id}, {self.state.value}, train={self.allocated_to})"


class TrackManager:
    """
    Manages all platform tracks and allocations.
    """
    
    def __init__(self, track_ids: List[str] = None):
        """
        Initialize track manager.
        
        Args:
            track_ids: List of track IDs to manage
        """
        if track_ids is None:
            track_ids = TRACK_IDS
        
        self.tracks: Dict[str, Track] = {
            track_id: Track(track_id) for track_id in track_ids
        }
        
    def allocate_track(self, train_id: str, eta_seconds: float) -> Optional[str]:
        """
        Allocate a free track to a train.
        
        Args:
            train_id: ID of train requesting allocation
            eta_seconds: Expected arrival time
            
        Returns:
            Track ID if allocation successful, None otherwise
        """
        # Find first free track
        for track_id, track in self.tracks.items():
            if track.state == TrackState.FREE:
                if track.reserve(train_id, eta_seconds):
                    return track_id
        
        return None
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Get track by ID.
        
        Args:
            track_id: Track identifier
            
        Returns:
            Track object or None
        """
        return self.tracks.get(track_id)
    
    def get_track_for_train(self, train_id: str) -> Optional[Track]:
        """
        Get track allocated to a specific train.
        
        Args:
            train_id: Train identifier
            
        Returns:
            Track object or None
        """
        for track in self.tracks.values():
            if track.allocated_to == train_id:
                return track
        return None
    
    def get_all_states(self) -> List[Dict]:
        """
        Get states of all tracks.
        
        Returns:
            List of track state dictionaries
        """
        return [track.get_state() for track in self.tracks.values()]
    
    def get_free_track_count(self) -> int:
        """
        Get number of free tracks.
        
        Returns:
            Count of free tracks
        """
        return sum(1 for track in self.tracks.values() if track.state == TrackState.FREE)
    
    def has_conflict(self, train_id: str) -> bool:
        """
        Check if there's a conflict for track allocation.
        
        Args:
            train_id: Train ID to check
            
        Returns:
            True if conflict exists
        """
        # No free tracks = conflict
        if self.get_free_track_count() == 0:
            return True
        
        return False
    
    def __repr__(self) -> str:
        """String representation."""
        free_count = self.get_free_track_count()
        return f"TrackManager(tracks={len(self.tracks)}, free={free_count})"


if __name__ == "__main__":
    # Test track manager
    manager = TrackManager()
    
    print("Track Manager Test\n")
    print(f"Initial state: {manager}")
    print(f"All tracks: {manager.get_all_states()}\n")
    
    # Allocate track
    track_id = manager.allocate_track("T001", 180.0)
    print(f"Allocated track {track_id} to T001")
    print(f"Updated state: {manager}")
    print(f"All tracks: {manager.get_all_states()}\n")
    
    # Occupy track
    track = manager.get_track(track_id)
    track.occupy("T001")
    print(f"Track {track_id} occupied by T001")
    print(f"Track state: {track.get_state()}\n")
    
    # Clear track
    track.start_clearing()
    track.clear()
    print(f"Track {track_id} cleared")
    print(f"Final state: {manager}")
