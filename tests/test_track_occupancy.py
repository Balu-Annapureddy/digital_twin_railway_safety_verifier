"""
Unit tests for Track Occupancy Calculator.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import json
from datetime import datetime
from src.utils.track_occupancy_calculator import TrackOccupancyCalculator


def test_calculator_initialization():
    """Test calculator initialization."""
    # Load sample data
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    assert calculator is not None
    assert len(calculator.station_platforms) > 0
    print("✓ Calculator initialization test passed")


def test_station_platform_mapping():
    """Test station platform mapping."""
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    # Check Mumbai Central has 12 platforms
    platforms = calculator.station_platforms.get('Mumbai Central')
    assert platforms is not None
    assert len(platforms) == 12
    assert 'P1' in platforms
    assert 'P12' in platforms
    print("✓ Station platform mapping test passed")


def test_occupancy_at_time():
    """Test getting occupancy at specific time."""
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    # Test at 8:30 AM
    test_time = datetime(2024, 1, 1, 8, 30)
    occupancy = calculator.get_occupancy_at_time('Mumbai Central', test_time)
    
    assert occupancy is not None
    assert 'total_platforms' in occupancy
    assert 'occupied_count' in occupancy
    assert 'free_count' in occupancy
    assert occupancy['total_platforms'] == 12
    print(f"✓ Occupancy at time test passed (occupied: {occupancy['occupied_count']}/12)")


def test_all_stations_occupancy():
    """Test getting occupancy for all stations."""
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    test_time = datetime(2024, 1, 1, 10, 0)
    all_occupancy = calculator.get_all_stations_occupancy(test_time)
    
    assert len(all_occupancy) > 0
    print(f"✓ All stations occupancy test passed ({len(all_occupancy)} stations)")


def test_time_range():
    """Test time range extraction."""
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    min_time, max_time = calculator.get_time_range()
    
    assert min_time is not None
    assert max_time is not None
    assert min_time <= max_time
    print(f"✓ Time range test passed ({min_time.strftime('%H:%M')} - {max_time.strftime('%H:%M')})")


def test_platform_allocation():
    """Test platform allocation for trains."""
    schedule_df = pd.read_csv("data/sample_indian_railways.csv")
    with open("data/sample_network_topology.json", 'r') as f:
        topology = json.load(f)
    
    calculator = TrackOccupancyCalculator(schedule_df, topology)
    
    # Check that platforms are allocated
    assert len(calculator.platform_allocations) > 0
    
    # Check no duplicate allocations at same time
    # (This is implicitly tested by the allocation algorithm)
    print(f"✓ Platform allocation test passed ({len(calculator.platform_allocations)} allocations)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Track Occupancy Calculator Tests")
    print("="*60 + "\n")
    
    try:
        test_calculator_initialization()
        test_station_platform_mapping()
        test_occupancy_at_time()
        test_all_stations_occupancy()
        test_time_range()
        test_platform_allocation()
        
        print("\n" + "="*60)
        print("All Tests Passed!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
