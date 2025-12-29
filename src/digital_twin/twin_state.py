"""
Digital Twin State - Virtual replica of the railway system.
Maintains a complete mirror of all system states for safety verification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Optional
from copy import deepcopy
from datetime import datetime


class TwinState:
    """
    Virtual replica of the entire railway system state.
    Used for simulating decisions before execution.
    """
    
    def __init__(self):
        """Initialize empty twin state."""
        self.trains: Dict[str, Dict] = {}
        self.tracks: Dict[str, Dict] = {}
        self.signals: Dict[str, Dict] = {}
        self.gates: Dict[str, Dict] = {}
        self.last_update = datetime.now()
        
    def update_train(self, train_id: str, train_state: Dict) -> None:
        """
        Update train state in virtual replica.
        
        Args:
            train_id: Train identifier
            train_state: Train state dictionary
        """
        self.trains[train_id] = deepcopy(train_state)
        self.last_update = datetime.now()
        
    def update_track(self, track_id: str, track_state: Dict) -> None:
        """
        Update track state in virtual replica.
        
        Args:
            track_id: Track identifier
            track_state: Track state dictionary
        """
        self.tracks[track_id] = deepcopy(track_state)
        self.last_update = datetime.now()
        
    def update_signal(self, signal_id: str, signal_state: Dict) -> None:
        """
        Update signal state in virtual replica.
        
        Args:
            signal_id: Signal identifier
            signal_state: Signal state dictionary
        """
        self.signals[signal_id] = deepcopy(signal_state)
        self.last_update = datetime.now()
        
    def update_gate(self, gate_id: str, gate_state: Dict) -> None:
        """
        Update gate state in virtual replica.
        
        Args:
            gate_id: Gate identifier
            gate_state: Gate state dictionary
        """
        self.gates[gate_id] = deepcopy(gate_state)
        self.last_update = datetime.now()
        
    def get_train(self, train_id: str) -> Optional[Dict]:
        """Get train state from replica."""
        return self.trains.get(train_id)
        
    def get_track(self, track_id: str) -> Optional[Dict]:
        """Get track state from replica."""
        return self.tracks.get(track_id)
        
    def get_signal(self, signal_id: str) -> Optional[Dict]:
        """Get signal state from replica."""
        return self.signals.get(signal_id)
        
    def get_gate(self, gate_id: str) -> Optional[Dict]:
        """Get gate state from replica."""
        return self.gates.get(gate_id)
        
    def get_all_trains(self) -> List[Dict]:
        """Get all train states."""
        return list(self.trains.values())
        
    def get_all_tracks(self) -> List[Dict]:
        """Get all track states."""
        return list(self.tracks.values())
        
    def get_all_signals(self) -> List[Dict]:
        """Get all signal states."""
        return list(self.signals.values())
        
    def get_all_gates(self) -> List[Dict]:
        """Get all gate states."""
        return list(self.gates.values())
        
    def clone(self) -> 'TwinState':
        """
        Create a deep copy of the current state.
        Used for simulating decisions without affecting the replica.
        
        Returns:
            New TwinState instance with copied data
        """
        new_state = TwinState()
        new_state.trains = deepcopy(self.trains)
        new_state.tracks = deepcopy(self.tracks)
        new_state.signals = deepcopy(self.signals)
        new_state.gates = deepcopy(self.gates)
        return new_state
        
    def get_summary(self) -> Dict:
        """
        Get summary of current state.
        
        Returns:
            Dictionary with state counts
        """
        return {
            "trains": len(self.trains),
            "tracks": len(self.tracks),
            "signals": len(self.signals),
            "gates": len(self.gates),
            "last_update": self.last_update
        }
        
    def __repr__(self) -> str:
        """String representation."""
        return f"TwinState(trains={len(self.trains)}, tracks={len(self.tracks)}, signals={len(self.signals)}, gates={len(self.gates)})"
