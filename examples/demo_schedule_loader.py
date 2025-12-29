"""
Demo script for schedule loader.
Shows how to load real-world train schedule data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.schedule_loader import ScheduleLoader


def main():
    """Demonstrate schedule loading from CSV and JSON."""
    print("\n" + "="*70)
    print("Railway Digital Twin - Schedule Loader Demo")
    print("="*70 + "\n")
    
    # Test CSV loading
    print("TEST 1: Loading from CSV")
    print("-" * 70)
    csv_path = "data/schedules/sample_schedule.csv"
    
    loader_csv = ScheduleLoader(csv_path)
    success = loader_csv.load()
    
    if success:
        schedules = loader_csv.get_valid_schedules()
        print(f"\n✓ Loaded {len(schedules)} valid schedules:\n")
        
        for schedule in schedules:
            print(f"  {schedule['train_id']}: {schedule['source_station']} → {schedule['destination_station']}")
            print(f"    Arrival: {schedule['scheduled_arrival']}, Speed: {schedule['average_speed']} kmph")
            print(f"    Type: {schedule['train_type']}, Distance: {schedule['initial_distance']} km\n")
        
        print(f"Statistics: {loader_csv.get_stats()}\n")
    
    # Test JSON loading
    print("\nTEST 2: Loading from JSON")
    print("-" * 70)
    json_path = "data/schedules/sample_schedule.json"
    
    loader_json = ScheduleLoader(json_path)
    success = loader_json.load()
    
    if success:
        schedules = loader_json.get_valid_schedules()
        print(f"\n✓ Loaded {len(schedules)} valid schedules from JSON\n")
        
        print(f"Statistics: {loader_json.get_stats()}\n")
    
    # Test fallback behavior
    print("\nTEST 3: Fallback Behavior (No File)")
    print("-" * 70)
    loader_fallback = ScheduleLoader("nonexistent.csv")
    success = loader_fallback.load()
    
    if not success:
        print("✓ Correctly falls back when file not found")
        print("  System will use simulation data instead\n")
    
    print("="*70)
    print("Demo Complete!")
    print("="*70 + "\n")
    
    print("📝 Note: This is DATA LAYER ONLY")
    print("   No safety logic has been modified")
    print("   Digital Twin Safety Verifier remains unchanged\n")


if __name__ == "__main__":
    main()
