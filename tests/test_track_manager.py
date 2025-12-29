"""
Unit tests for track manager module.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.railway.track_manager import Track, TrackManager, TrackState


def test_track_creation():
    """Test track creation."""
    track = Track("P1")
    
    assert track.track_id == "P1"
    assert track.state == TrackState.FREE
    assert track.allocated_to is None
    print("✓ Track creation test passed")


def test_track_reservation():
    """Test track reservation."""
    track = Track("P1")
    
    success = track.reserve("T001", 180.0)
    
    assert success is True
    assert track.state == TrackState.RESERVED
    assert track.allocated_to == "T001"
    assert track.expected_arrival_time == 180.0
    print("✓ Track reservation test passed")


def test_track_occupation():
    """Test track occupation."""
    track = Track("P1")
    track.reserve("T001", 180.0)
    
    success = track.occupy("T001")
    
    assert success is True
    assert track.state == TrackState.OCCUPIED
    print("✓ Track occupation test passed")


def test_track_clearing():
    """Test track clearing process."""
    track = Track("P1")
    track.reserve("T001", 180.0)
    track.occupy("T001")
    
    success = track.start_clearing()
    assert success is True
    assert track.state == TrackState.CLEARING
    
    success = track.clear()
    assert success is True
    assert track.state == TrackState.FREE
    assert track.allocated_to is None
    print("✓ Track clearing test passed")


def test_track_manager_allocation():
    """Test track manager allocation."""
    manager = TrackManager(["P1", "P2", "P3"])
    
    track_id = manager.allocate_track("T001", 180.0)
    
    assert track_id is not None
    assert track_id in ["P1", "P2", "P3"]
    assert manager.get_free_track_count() == 2
    print("✓ Track manager allocation test passed")


def test_track_manager_multiple_allocations():
    """Test multiple track allocations."""
    manager = TrackManager(["P1", "P2"])
    
    track1 = manager.allocate_track("T001", 180.0)
    track2 = manager.allocate_track("T002", 200.0)
    
    assert track1 is not None
    assert track2 is not None
    assert track1 != track2
    assert manager.get_free_track_count() == 0
    print("✓ Multiple allocations test passed")


def test_track_manager_no_free_tracks():
    """Test allocation when no tracks are free."""
    manager = TrackManager(["P1"])
    
    track1 = manager.allocate_track("T001", 180.0)
    track2 = manager.allocate_track("T002", 200.0)
    
    assert track1 is not None
    assert track2 is None  # Should fail - no free tracks
    print("✓ No free tracks test passed")


def test_get_track_for_train():
    """Test getting track allocated to specific train."""
    manager = TrackManager(["P1", "P2"])
    
    manager.allocate_track("T001", 180.0)
    
    track = manager.get_track_for_train("T001")
    
    assert track is not None
    assert track.allocated_to == "T001"
    print("✓ Get track for train test passed")


if __name__ == "__main__":
    print("\n=== Running Track Manager Tests ===\n")
    
    test_track_creation()
    test_track_reservation()
    test_track_occupation()
    test_track_clearing()
    test_track_manager_allocation()
    test_track_manager_multiple_allocations()
    test_track_manager_no_free_tracks()
    test_get_track_for_train()
    
    print("\n=== All Tests Passed! ===\n")
