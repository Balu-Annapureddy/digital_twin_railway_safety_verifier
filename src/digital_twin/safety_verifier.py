"""
Safety Verifier - Core Digital Twin verification engine.
Simulates and verifies all decisions before execution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Tuple
from enum import Enum
from .twin_state import TwinState
from .conflict_detector import ConflictDetector
from config.safety_rules import SAFETY_RULES, validate_track_allocation, validate_signal_change, validate_gate_opening


class VerificationResult(Enum):
    """Verification result enumeration."""
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"


class SafetyVerifier:
    """
    Core safety verification engine using Digital Twin.
    ALL decisions must pass through this verifier.
    """
    
    def __init__(self):
        """Initialize safety verifier."""
        self.twin_state = TwinState()
        self.conflict_detector = ConflictDetector()
        self.verification_log: List[Dict] = []
        
    def sync_state(
        self,
        trains: List[Dict] = None,
        tracks: List[Dict] = None,
        signals: List[Dict] = None,
        gates: List[Dict] = None
    ) -> None:
        """
        Synchronize digital twin with real system state.
        
        Args:
            trains: List of train states
            tracks: List of track states
            signals: List of signal states
            gates: List of gate states
        """
        if trains:
            for train in trains:
                self.twin_state.update_train(train['id'], train)
                
        if tracks:
            for track in tracks:
                self.twin_state.update_track(track['track_id'], track)
                
        if signals:
            for signal in signals:
                self.twin_state.update_signal(signal['signal_id'], signal)
                
        if gates:
            for gate in gates:
                self.twin_state.update_gate(gate['gate_id'], gate)
    
    def verify_track_allocation(
        self,
        train_id: str,
        track_id: str,
        eta_seconds: float
    ) -> Tuple[VerificationResult, str]:
        """
        Verify if track allocation is safe.
        
        Args:
            train_id: Train requesting allocation
            track_id: Track to allocate
            eta_seconds: Expected arrival time
            
        Returns:
            Tuple of (result, reason)
        """
        # Clone state for simulation
        sim_state = self.twin_state.clone()
        
        # Get track state
        track = sim_state.get_track(track_id)
        if not track:
            return (VerificationResult.UNSAFE, f"Track {track_id} not found")
        
        # Check if track is FREE
        if track['state'] != 'FREE':
            return (VerificationResult.UNSAFE, f"Track {track_id} is {track['state']}, not FREE")
        
        # Check for route conflicts
        if self.conflict_detector.check_route_conflicts(sim_state, train_id, track_id):
            return (VerificationResult.UNSAFE, f"Route conflict detected for track {track_id}")
        
        # Check for timing conflicts
        if self.conflict_detector.check_timing_conflicts(sim_state, train_id, eta_seconds):
            return (VerificationResult.UNSAFE, f"Timing conflict detected for train {train_id}")
        
        # Simulate allocation
        track['state'] = 'RESERVED'
        track['allocated_to'] = train_id
        track['expected_arrival'] = eta_seconds
        sim_state.update_track(track_id, track)
        
        # Check for conflicts after simulation
        conflicts = self.conflict_detector.detect_all_conflicts(sim_state)
        if conflicts:
            return (VerificationResult.UNSAFE, f"Conflicts detected: {len(conflicts)} issues")
        
        # Log verification
        self._log_verification("TRACK_ALLOCATION", train_id, track_id, VerificationResult.SAFE)
        
        return (VerificationResult.SAFE, "Track allocation is safe")
    
    def verify_signal_change(
        self,
        signal_id: str,
        new_state: str,
        track_id: str
    ) -> Tuple[VerificationResult, str]:
        """
        Verify if signal state change is safe.
        
        Args:
            signal_id: Signal identifier
            new_state: Proposed new state (RED, YELLOW, GREEN)
            track_id: Associated track ID
            
        Returns:
            Tuple of (result, reason)
        """
        # Clone state for simulation
        sim_state = self.twin_state.clone()
        
        # Get track state
        track = sim_state.get_track(track_id)
        if not track:
            return (VerificationResult.UNSAFE, f"Track {track_id} not found")
        
        # Validate using safety rules
        if not validate_signal_change(new_state, track['state']):
            return (VerificationResult.UNSAFE, f"Signal change violates safety rules")
        
        # Simulate signal change
        signal = sim_state.get_signal(signal_id)
        if not signal:
            signal = {'signal_id': signal_id, 'track_id': track_id, 'state': 'RED'}
        
        signal['state'] = new_state
        sim_state.update_signal(signal_id, signal)
        
        # Check for conflicts
        conflicts = self.conflict_detector.detect_all_conflicts(sim_state)
        if conflicts:
            return (VerificationResult.UNSAFE, f"Signal change causes conflicts: {len(conflicts)} issues")
        
        # Log verification
        self._log_verification("SIGNAL_CHANGE", signal_id, new_state, VerificationResult.SAFE)
        
        return (VerificationResult.SAFE, "Signal change is safe")
    
    def verify_gate_operation(
        self,
        gate_id: str,
        new_state: str,
        nearest_train_distance: float
    ) -> Tuple[VerificationResult, str]:
        """
        Verify if gate operation is safe.
        
        Args:
            gate_id: Gate identifier
            new_state: Proposed new state (OPEN, CLOSING, CLOSED)
            nearest_train_distance: Distance to nearest train in meters
            
        Returns:
            Tuple of (result, reason)
        """
        # If opening gate, check distance
        if new_state == "OPEN":
            if not validate_gate_opening(nearest_train_distance):
                danger_zone = SAFETY_RULES["gate_logic"]["danger_zone_distance"]
                return (
                    VerificationResult.UNSAFE,
                    f"Train too close ({nearest_train_distance}m < {danger_zone}m danger zone)"
                )
        
        # Log verification
        self._log_verification("GATE_OPERATION", gate_id, new_state, VerificationResult.SAFE)
        
        return (VerificationResult.SAFE, "Gate operation is safe")
    
    def verify_decision(self, decision_type: str, **kwargs) -> Tuple[VerificationResult, str]:
        """
        Universal decision verification interface.
        
        Args:
            decision_type: Type of decision (TRACK_ALLOCATION, SIGNAL_CHANGE, GATE_OPERATION)
            **kwargs: Decision-specific parameters
            
        Returns:
            Tuple of (result, reason)
        """
        if decision_type == "TRACK_ALLOCATION":
            return self.verify_track_allocation(
                kwargs['train_id'],
                kwargs['track_id'],
                kwargs['eta_seconds']
            )
        elif decision_type == "SIGNAL_CHANGE":
            return self.verify_signal_change(
                kwargs['signal_id'],
                kwargs['new_state'],
                kwargs['track_id']
            )
        elif decision_type == "GATE_OPERATION":
            return self.verify_gate_operation(
                kwargs['gate_id'],
                kwargs['new_state'],
                kwargs['nearest_train_distance']
            )
        else:
            return (VerificationResult.UNSAFE, f"Unknown decision type: {decision_type}")
    
    def _log_verification(
        self,
        decision_type: str,
        entity_id: str,
        action: str,
        result: VerificationResult
    ) -> None:
        """Log verification result."""
        self.verification_log.append({
            'decision_type': decision_type,
            'entity_id': entity_id,
            'action': action,
            'result': result.value,
            'timestamp': self.twin_state.last_update
        })
    
    def get_verification_stats(self) -> Dict:
        """
        Get verification statistics.
        
        Returns:
            Dictionary with verification stats
        """
        total = len(self.verification_log)
        safe = sum(1 for v in self.verification_log if v['result'] == 'SAFE')
        unsafe = total - safe
        
        return {
            'total_verifications': total,
            'safe': safe,
            'unsafe': unsafe,
            'safety_rate': (safe / total * 100) if total > 0 else 0
        }
    
    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_verification_stats()
        return f"SafetyVerifier(verifications={stats['total_verifications']}, safety_rate={stats['safety_rate']:.1f}%)"
