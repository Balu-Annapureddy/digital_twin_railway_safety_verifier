"""
Unit tests for Station Manager.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.railway.station_manager import StationManager


def test_station_manager_initialization():
    """Test station manager initialization."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    assert manager is not None
    assert len(manager.get_all_stations()) > 0
    print("✓ Station manager initialization test passed")


def test_get_all_stations():
    """Test getting all stations."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    stations = manager.get_all_stations()
    
    assert len(stations) == 8  # Sample topology has 8 stations
    assert all('station_id' in s for s in stations)
    assert all('station_name' in s for s in stations)
    print(f"✓ Get all stations test passed ({len(stations)} stations)")


def test_get_station_by_id():
    """Test getting station by ID."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    station = manager.get_station('S001')
    
    assert station is not None
    assert station['station_id'] == 'S001'
    assert station['station_name'] == 'Mumbai Central'
    assert station['platform_count'] == 12
    print("✓ Get station by ID test passed")


def test_get_station_by_name():
    """Test getting station by name."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    station = manager.get_station('Mumbai Central')
    
    assert station is not None
    assert station['station_id'] == 'S001'
    assert station['platform_count'] == 12
    print("✓ Get station by name test passed")


def test_track_manager_creation():
    """Test track manager creation for stations."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    track_manager = manager.get_track_manager('S001')
    
    assert track_manager is not None
    # Mumbai Central has 12 platforms, so should have 12 free tracks initially
    assert track_manager.get_free_track_count() == 12
    print("✓ Track manager creation test passed")


def test_station_summary():
    """Test getting station summary."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    summary = manager.get_station_summary('Mumbai Central')
    
    assert summary is not None
    assert summary['station_name'] == 'Mumbai Central'
    assert summary['total_platforms'] == 12
    assert 'platform_ids' in summary
    assert len(summary['platform_ids']) == 12
    print("✓ Station summary test passed")


def test_total_platforms():
    """Test total platforms calculation."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    total = manager.get_total_platforms()
    
    # Sum of all platforms: 12+16+12+23+10+8+6+12 = 99
    assert total == 99
    print(f"✓ Total platforms test passed ({total} platforms)")


def test_station_names():
    """Test getting station names."""
    manager = StationManager(topology_file="data/sample_network_topology.json")
    
    names = manager.get_station_names()
    
    assert len(names) == 8
    assert 'Mumbai Central' in names
    assert 'Delhi Junction' in names
    print(f"✓ Station names test passed ({len(names)} names)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Station Manager Tests")
    print("="*60 + "\n")
    
    try:
        test_station_manager_initialization()
        test_get_all_stations()
        test_get_station_by_id()
        test_get_station_by_name()
        test_track_manager_creation()
        test_station_summary()
        test_total_platforms()
        test_station_names()
        
        print("\n" + "="*60)
        print("All Tests Passed!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
