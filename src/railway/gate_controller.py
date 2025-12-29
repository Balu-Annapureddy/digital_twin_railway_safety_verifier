"""
Gate Controller - Manages level crossing gates.
All gate operations must be verified by Digital Twin before execution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class GateState(Enum):
    """Gate state enumeration."""
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class Gate:
    """
    Represents a level crossing gate.
    """
    
    def __init__(self, gate_id: str):
        """
        Initialize gate.
        
        Args:
            gate_id: Unique gate identifier
        """
        self.gate_id = gate_id
        self.state = GateState.CLOSED  # Default to CLOSED for safety
        self.nearest_train_id: Optional[str] = None
        self.nearest_train_distance: float = 9999.0  # meters
        self.last_change = datetime.now()
        self.history: List[Dict] = []
        
    def change_state(self, new_state: GateState, verified: bool = False) -> bool:
        """
        Change gate state.
        
        Args:
            new_state: New gate state
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
    
    def update_nearest_train(self, train_id: str, distance: float) -> None:
        """
        Update information about nearest train.
        
        Args:
            train_id: ID of nearest train
            distance: Distance to train in meters
        """
        self.nearest_train_id = train_id
        self.nearest_train_distance = distance
    
    def get_state(self) -> Dict:
        """
        Get current gate state.
        
        Returns:
            Dictionary with gate state information
        """
        return {
            "gate_id": self.gate_id,
            "state": self.state.value,
            "nearest_train": self.nearest_train_id,
            "distance": self.nearest_train_distance,
            "last_change": self.last_change
        }
    
    def _log_change(self, old_state: GateState, new_state: GateState) -> None:
        """Log state change to history."""
        self.history.append({
            "timestamp": datetime.now(),
            "old_state": old_state.value,
            "new_state": new_state.value,
            "nearest_train_distance": self.nearest_train_distance
        })
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Gate({self.gate_id}, {self.state.value}, nearest_train={self.nearest_train_distance:.0f}m)"


class GateController:
    """
    Controls all level crossing gates with Digital Twin verification.
    """
    
    def __init__(self, safety_verifier=None):
        """
        Initialize gate controller.
        
        Args:
            safety_verifier: Digital Twin safety verifier instance
        """
        self.gates: Dict[str, Gate] = {}
        self.safety_verifier = safety_verifier
        self.command_log: List[Dict] = []
        
    def add_gate(self, gate_id: str) -> Gate:
        """
        Add a new gate.
        
        Args:
            gate_id: Gate identifier
            
        Returns:
            Created Gate object
        """
        gate = Gate(gate_id)
        self.gates[gate_id] = gate
        return gate
    
    def change_gate(
        self,
        gate_id: str,
        new_state: str,
        override: bool = False
    ) -> Tuple[bool, str]:
        """
        Change gate state with Digital Twin verification.
        
        Args:
            gate_id: Gate to change
            new_state: New state (OPEN, CLOSING, CLOSED)
            override: Station Master override (skip verification)
            
        Returns:
            Tuple of (success, message)
        """
        gate = self.gates.get(gate_id)
        if not gate:
            return (False, f"Gate {gate_id} not found")
        
        # Convert string to enum
        try:
            new_state_enum = GateState[new_state]
        except KeyError:
            return (False, f"Invalid gate state: {new_state}")
        
        # If override, allow change without verification
        if override:
            gate.change_state(new_state_enum, verified=True)
            self._log_command(gate_id, new_state, True, "OVERRIDE")
            return (True, f"Gate {gate_id} changed to {new_state} (OVERRIDE)")
        
        # Verify with Digital Twin
        if self.safety_verifier:
            result, reason = self.safety_verifier.verify_gate_operation(
                gate_id,
                new_state,
                gate.nearest_train_distance
            )
            
            if result.value == "SAFE":
                gate.change_state(new_state_enum, verified=True)
                self._log_command(gate_id, new_state, True, "VERIFIED")
                return (True, f"Gate {gate_id} changed to {new_state}")
            else:
                self._log_command(gate_id, new_state, False, reason)
                return (False, f"Gate change blocked: {reason}")
        else:
            # No verifier - allow change (for testing only)
            gate.change_state(new_state_enum, verified=True)
            self._log_command(gate_id, new_state, True, "NO_VERIFIER")
            return (True, f"Gate {gate_id} changed to {new_state} (NO VERIFICATION)")
    
    def update_train_proximity(self, gate_id: str, train_id: str, distance: float) -> None:
        """
        Update nearest train information for a gate.
        
        Args:
            gate_id: Gate identifier
            train_id: Nearest train ID
            distance: Distance in meters
        """
        gate = self.gates.get(gate_id)
        if gate:
            gate.update_nearest_train(train_id, distance)
    
    def auto_close_if_needed(self, gate_id: str, threshold: float = 500.0) -> Tuple[bool, str]:
        """
        Automatically close gate if train is within threshold.
        
        Args:
            gate_id: Gate to check
            threshold: Distance threshold in meters
            
        Returns:
            Tuple of (changed, message)
        """
        gate = self.gates.get(gate_id)
        if not gate:
            return (False, f"Gate {gate_id} not found")
        
        if gate.nearest_train_distance < threshold and gate.state != GateState.CLOSED:
            success, msg = self.change_gate(gate_id, "CLOSING")
            if success:
                return (True, f"Auto-closing gate {gate_id} (train at {gate.nearest_train_distance:.0f}m)")
        
        return (False, "No action needed")
    
    def get_gate(self, gate_id: str) -> Optional[Gate]:
        """Get gate by ID."""
        return self.gates.get(gate_id)
    
    def get_all_states(self) -> List[Dict]:
        """Get states of all gates."""
        return [gate.get_state() for gate in self.gates.values()]
    
    def _log_command(
        self,
        gate_id: str,
        new_state: str,
        success: bool,
        reason: str
    ) -> None:
        """Log gate command."""
        self.command_log.append({
            "timestamp": datetime.now(),
            "gate_id": gate_id,
            "new_state": new_state,
            "success": success,
            "reason": reason
        })
    
    def __repr__(self) -> str:
        """String representation."""
        return f"GateController(gates={len(self.gates)})"


if __name__ == "__main__":
    # Test gate controller
    controller = GateController()
    
    print("Gate Controller Test\n")
    
    # Add gates
    controller.add_gate("G1")
    controller.add_gate("G2")
    
    print(f"Added gates: {controller}")
    print(f"All gates: {controller.get_all_states()}\n")
    
    # Update train proximity
    controller.update_train_proximity("G1", "T001", 1000.0)
    print(f"Updated G1 train proximity: {controller.get_gate('G1')}")
    
    # Change gate (no verifier for testing)
    success, msg = controller.change_gate("G1", "OPEN")
    print(f"Change G1 to OPEN: {msg}")
    
    # Simulate train approaching
    controller.update_train_proximity("G1", "T001", 400.0)
    success, msg = controller.auto_close_if_needed("G1")
    print(f"Auto-close check: {msg}")
    
    print(f"\nFinal states: {controller.get_all_states()}")
