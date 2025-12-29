"""
Conflict Detector - Detects conflicts in railway operations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import List, Dict, Optional
from .twin_state import TwinState


class ConflictDetector:
    """
    Detects conflicts in railway operations.
    """
    
    def __init__(self):
        """Initialize conflict detector."""
        self.detected_conflicts: List[Dict] = []
        
    def check_track_conflicts(self, state: TwinState) -> List[Dict]:
        """
        Check for track occupancy conflicts.
        
        Args:
            state: Current twin state
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check if multiple trains allocated to same track
        track_allocations = {}
        for track in state.get_all_tracks():
            track_id = track['track_id']
            allocated_to = track.get('allocated_to')
            
            if allocated_to:
                if track_id in track_allocations:
                    conflicts.append({
                        'type': 'TRACK_CONFLICT',
                        'track_id': track_id,
                        'trains': [track_allocations[track_id], allocated_to],
                        'severity': 'CRITICAL',
                        'message': f"Multiple trains allocated to track {track_id}"
                    })
                else:
                    track_allocations[track_id] = allocated_to
        
        return conflicts
        
    def check_route_conflicts(self, state: TwinState, train_id: str, target_track: str) -> bool:
        """
        Check if there's a route conflict for a train.
        
        Args:
            state: Current twin state
            train_id: Train requesting route
            target_track: Target track ID
            
        Returns:
            True if conflict exists
        """
        track = state.get_track(target_track)
        if not track:
            return False
            
        # Conflict if track is not FREE
        if track['state'] != 'FREE':
            return True
            
        return False
        
    def check_timing_conflicts(
        self,
        state: TwinState,
        train_id: str,
        eta_seconds: float,
        min_separation: float = 120.0
    ) -> bool:
        """
        Check for timing conflicts between trains.
        
        Args:
            state: Current twin state
            train_id: Train to check
            eta_seconds: Expected arrival time
            min_separation: Minimum time separation in seconds
            
        Returns:
            True if timing conflict exists
        """
        # Check all other trains
        for other_train_id, train_state in state.trains.items():
            if other_train_id == train_id:
                continue
                
            # If trains are too close in ETA, there's a conflict
            other_eta = train_state.get('eta', 0)
            if abs(eta_seconds - other_eta) < min_separation:
                return True
                
        return False
        
    def check_signal_track_consistency(self, state: TwinState) -> List[Dict]:
        """
        Check if signal states are consistent with track states.
        
        Args:
            state: Current twin state
            
        Returns:
            List of inconsistencies
        """
        conflicts = []
        
        for signal in state.get_all_signals():
            signal_id = signal['signal_id']
            track_id = signal.get('track_id')
            signal_state = signal['state']
            
            if track_id:
                track = state.get_track(track_id)
                if track:
                    track_state = track['state']
                    
                    # Signal should be RED if track is OCCUPIED
                    if track_state == 'OCCUPIED' and signal_state != 'RED':
                        conflicts.append({
                            'type': 'SIGNAL_TRACK_INCONSISTENCY',
                            'signal_id': signal_id,
                            'track_id': track_id,
                            'signal_state': signal_state,
                            'track_state': track_state,
                            'severity': 'CRITICAL',
                            'message': f"Signal {signal_id} is {signal_state} but track {track_id} is {track_state}"
                        })
                    
                    # Signal should not be GREEN if track is not RESERVED
                    if signal_state == 'GREEN' and track_state != 'RESERVED':
                        conflicts.append({
                            'type': 'SIGNAL_TRACK_INCONSISTENCY',
                            'signal_id': signal_id,
                            'track_id': track_id,
                            'signal_state': signal_state,
                            'track_state': track_state,
                            'severity': 'HIGH',
                            'message': f"Signal {signal_id} is GREEN but track {track_id} is not RESERVED"
                        })
        
        return conflicts
        
    def detect_all_conflicts(self, state: TwinState) -> List[Dict]:
        """
        Run all conflict detection checks.
        
        Args:
            state: Current twin state
            
        Returns:
            List of all detected conflicts
        """
        all_conflicts = []
        
        # Track conflicts
        all_conflicts.extend(self.check_track_conflicts(state))
        
        # Signal-track consistency
        all_conflicts.extend(self.check_signal_track_consistency(state))
        
        self.detected_conflicts = all_conflicts
        return all_conflicts
        
    def get_conflict_summary(self) -> Dict:
        """
        Get summary of detected conflicts.
        
        Returns:
            Dictionary with conflict statistics
        """
        critical = sum(1 for c in self.detected_conflicts if c.get('severity') == 'CRITICAL')
        high = sum(1 for c in self.detected_conflicts if c.get('severity') == 'HIGH')
        
        return {
            'total': len(self.detected_conflicts),
            'critical': critical,
            'high': high,
            'has_conflicts': len(self.detected_conflicts) > 0
        }
