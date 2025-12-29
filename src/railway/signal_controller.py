"""
Signal Controller - Manages railway signal states.
All signal changes must be verified by Digital Twin before execution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class SignalState(Enum):
    """Signal state enumeration."""
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class Signal:
    """
    Represents a railway signal.
    """
    
    def __init__(self, signal_id: str, track_id: str):
        """
        Initialize signal.
        
        Args:
            signal_id: Unique signal identifier
            track_id: Associated track ID
        """
        self.signal_id = signal_id
        self.track_id = track_id
        self.state = SignalState.RED  # Default to RED for safety
        self.last_change = datetime.now()
        self.history: List[Dict] = []
        
    def change_state(self, new_state: SignalState, verified: bool = False) -> bool:
        """
        Change signal state.
        
        Args:
            new_state: New signal state
            verified: Whether change has been verified by Digital Twin
            
        Returns:
            True if state changed successfully
        """
        if not verified:
            # Should not change state without verification
            return False
        
        old_state = self.state
        self.state = new_state
        self.last_change = datetime.now()
        
        self._log_change(old_state, new_state)
        return True
    
    def get_state(self) -> Dict:
        """
        Get current signal state.
        
        Returns:
            Dictionary with signal state information
        """
        return {
            "signal_id": self.signal_id,
            "track_id": self.track_id,
            "state": self.state.value,
            "last_change": self.last_change
        }
    
    def _log_change(self, old_state: SignalState, new_state: SignalState) -> None:
        """Log state change to history."""
        self.history.append({
            "timestamp": datetime.now(),
            "old_state": old_state.value,
            "new_state": new_state.value
        })
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Signal({self.signal_id}, {self.state.value}, track={self.track_id})"


class SignalController:
    """
    Controls all railway signals with Digital Twin verification.
    """
    
    def __init__(self, safety_verifier=None):
        """
        Initialize signal controller.
        
        Args:
            safety_verifier: Digital Twin safety verifier instance
        """
        self.signals: Dict[str, Signal] = {}
        self.safety_verifier = safety_verifier
        self.command_log: List[Dict] = []
        
    def add_signal(self, signal_id: str, track_id: str) -> Signal:
        """
        Add a new signal.
        
        Args:
            signal_id: Signal identifier
            track_id: Associated track ID
            
        Returns:
            Created Signal object
        """
        signal = Signal(signal_id, track_id)
        self.signals[signal_id] = signal
        return signal
    
    def change_signal(
        self,
        signal_id: str,
        new_state: str,
        override: bool = False
    ) -> Tuple[bool, str]:
        """
        Change signal state with Digital Twin verification.
        
        Args:
            signal_id: Signal to change
            new_state: New state (RED, YELLOW, GREEN)
            override: Station Master override (skip verification)
            
        Returns:
            Tuple of (success, message)
        """
        signal = self.signals.get(signal_id)
        if not signal:
            return (False, f"Signal {signal_id} not found")
        
        # Convert string to enum
        try:
            new_state_enum = SignalState[new_state]
        except KeyError:
            return (False, f"Invalid signal state: {new_state}")
        
        # If override, allow change without verification
        if override:
            signal.change_state(new_state_enum, verified=True)
            self._log_command(signal_id, new_state, True, "OVERRIDE")
            return (True, f"Signal {signal_id} changed to {new_state} (OVERRIDE)")
        
        # Verify with Digital Twin
        if self.safety_verifier:
            result, reason = self.safety_verifier.verify_signal_change(
                signal_id,
                new_state,
                signal.track_id
            )
            
            if result.value == "SAFE":
                signal.change_state(new_state_enum, verified=True)
                self._log_command(signal_id, new_state, True, "VERIFIED")
                return (True, f"Signal {signal_id} changed to {new_state}")
            else:
                self._log_command(signal_id, new_state, False, reason)
                return (False, f"Signal change blocked: {reason}")
        else:
            # No verifier - allow change (for testing only)
            signal.change_state(new_state_enum, verified=True)
            self._log_command(signal_id, new_state, True, "NO_VERIFIER")
            return (True, f"Signal {signal_id} changed to {new_state} (NO VERIFICATION)")
    
    def get_signal(self, signal_id: str) -> Optional[Signal]:
        """Get signal by ID."""
        return self.signals.get(signal_id)
    
    def get_all_states(self) -> List[Dict]:
        """Get states of all signals."""
        return [signal.get_state() for signal in self.signals.values()]
    
    def _log_command(
        self,
        signal_id: str,
        new_state: str,
        success: bool,
        reason: str
    ) -> None:
        """Log signal command."""
        self.command_log.append({
            "timestamp": datetime.now(),
            "signal_id": signal_id,
            "new_state": new_state,
            "success": success,
            "reason": reason
        })
    
    def __repr__(self) -> str:
        """String representation."""
        return f"SignalController(signals={len(self.signals)})"


if __name__ == "__main__":
    # Test signal controller
    controller = SignalController()
    
    print("Signal Controller Test\n")
    
    # Add signals
    controller.add_signal("S1", "P1")
    controller.add_signal("S2", "P2")
    
    print(f"Added signals: {controller}")
    print(f"All signals: {controller.get_all_states()}\n")
    
    # Change signal (no verifier for testing)
    success, msg = controller.change_signal("S1", "YELLOW")
    print(f"Change S1 to YELLOW: {msg}")
    
    success, msg = controller.change_signal("S1", "GREEN")
    print(f"Change S1 to GREEN: {msg}")
    
    print(f"\nFinal states: {controller.get_all_states()}")
