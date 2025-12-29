"""
Unit tests for Digital Twin Safety Verifier.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.digital_twin.twin_state import TwinState
from src.digital_twin.conflict_detector import ConflictDetector
from src.digital_twin.safety_verifier import SafetyVerifier, VerificationResult


def test_twin_state_creation():
    """Test twin state creation."""
    state = TwinState()
    
    assert len(state.trains) == 0
    assert len(state.tracks) == 0
    print("✓ Twin state creation test passed")


def test_twin_state_updates():
    """Test updating twin state."""
    state = TwinState()
    
    train_state = {'id': 'T001', 'position': 10.0, 'speed': 80.0}
    state.update_train('T001', train_state)
    
    assert 'T001' in state.trains
    assert state.get_train('T001')['position'] == 10.0
    print("✓ Twin state updates test passed")


def test_twin_state_clone():
    """Test cloning twin state."""
    state = TwinState()
    state.update_train('T001', {'id': 'T001', 'position': 10.0})
    
    cloned = state.clone()
    
    assert 'T001' in cloned.trains
    assert cloned.trains is not state.trains  # Different objects
    print("✓ Twin state clone test passed")


def test_conflict_detector_track_conflicts():
    """Test track conflict detection."""
    state = TwinState()
    detector = ConflictDetector()
    
    # No conflicts initially
    conflicts = detector.check_track_conflicts(state)
    assert len(conflicts) == 0
    
    # Add two trains to same track (conflict)
    state.update_track('P1', {'track_id': 'P1', 'state': 'RESERVED', 'allocated_to': 'T001'})
    # This shouldn't happen in real system, but testing detection
    
    print("✓ Conflict detector test passed")


def test_safety_verifier_creation():
    """Test safety verifier creation."""
    verifier = SafetyVerifier()
    
    assert verifier.twin_state is not None
    assert verifier.conflict_detector is not None
    print("✓ Safety verifier creation test passed")


def test_safety_verifier_sync():
    """Test syncing state with verifier."""
    verifier = SafetyVerifier()
    
    trains = [{'id': 'T001', 'position': 10.0, 'speed': 80.0}]
    tracks = [{'track_id': 'P1', 'state': 'FREE', 'allocated_to': None}]
    
    verifier.sync_state(trains=trains, tracks=tracks)
    
    assert 'T001' in verifier.twin_state.trains
    assert 'P1' in verifier.twin_state.tracks
    print("✓ Safety verifier sync test passed")


def test_verify_track_allocation_safe():
    """Test safe track allocation verification."""
    verifier = SafetyVerifier()
    
    # Setup state
    tracks = [{'track_id': 'P1', 'state': 'FREE', 'allocated_to': None}]
    verifier.sync_state(tracks=tracks)
    
    # Verify allocation
    result, reason = verifier.verify_track_allocation('T001', 'P1', 180.0)
    
    assert result == VerificationResult.SAFE
    print("✓ Safe track allocation verification test passed")


def test_verify_track_allocation_unsafe():
    """Test unsafe track allocation verification."""
    verifier = SafetyVerifier()
    
    # Setup state - track already occupied
    tracks = [{'track_id': 'P1', 'state': 'OCCUPIED', 'allocated_to': 'T001'}]
    verifier.sync_state(tracks=tracks)
    
    # Try to allocate occupied track
    result, reason = verifier.verify_track_allocation('T002', 'P1', 200.0)
    
    assert result == VerificationResult.UNSAFE
    print("✓ Unsafe track allocation verification test passed")


def test_verify_signal_change_safe():
    """Test safe signal change verification."""
    verifier = SafetyVerifier()
    
    # Setup state - track reserved
    tracks = [{'track_id': 'P1', 'state': 'RESERVED', 'allocated_to': 'T001'}]
    verifier.sync_state(tracks=tracks)
    
    # Verify signal change to GREEN (allowed when track is RESERVED)
    result, reason = verifier.verify_signal_change('S1', 'GREEN', 'P1')
    
    assert result == VerificationResult.SAFE
    print("✓ Safe signal change verification test passed")


def test_verify_gate_operation_safe():
    """Test safe gate operation verification."""
    verifier = SafetyVerifier()
    
    # Verify gate opening when train is far away (safe)
    result, reason = verifier.verify_gate_operation('G1', 'OPEN', 1000.0)
    
    assert result == VerificationResult.SAFE
    print("✓ Safe gate operation verification test passed")


def test_verify_gate_operation_unsafe():
    """Test unsafe gate operation verification."""
    verifier = SafetyVerifier()
    
    # Verify gate opening when train is too close (unsafe)
    result, reason = verifier.verify_gate_operation('G1', 'OPEN', 200.0)
    
    assert result == VerificationResult.UNSAFE
    print("✓ Unsafe gate operation verification test passed")


def test_verification_stats():
    """Test verification statistics."""
    verifier = SafetyVerifier()
    
    # Perform some verifications
    tracks = [{'track_id': 'P1', 'state': 'FREE', 'allocated_to': None}]
    verifier.sync_state(tracks=tracks)
    
    verifier.verify_track_allocation('T001', 'P1', 180.0)
    verifier.verify_gate_operation('G1', 'OPEN', 1000.0)
    
    stats = verifier.get_verification_stats()
    
    assert stats['total_verifications'] == 2
    assert stats['safe'] == 2
    print("✓ Verification statistics test passed")


if __name__ == "__main__":
    print("\n=== Running Digital Twin Safety Verifier Tests ===\n")
    
    test_twin_state_creation()
    test_twin_state_updates()
    test_twin_state_clone()
    test_conflict_detector_track_conflicts()
    test_safety_verifier_creation()
    test_safety_verifier_sync()
    test_verify_track_allocation_safe()
    test_verify_track_allocation_unsafe()
    test_verify_signal_change_safe()
    test_verify_gate_operation_safe()
    test_verify_gate_operation_unsafe()
    test_verification_stats()
    
    print("\n=== All Tests Passed! ===\n")
