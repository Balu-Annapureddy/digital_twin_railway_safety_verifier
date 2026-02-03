"""
Schedule Loader - Load real-world train schedule data from CSV/JSON.
This is a DATA LAYER ONLY module - does not affect safety logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import json
from typing import List, Dict, Optional
from datetime import datetime


class ScheduleLoader:
    """
    Loads train schedule data from external sources (CSV/JSON).
    Falls back to simulation if data is unavailable.
    
    ⚠️ DATA LAYER ONLY - Does not modify safety logic.
    """
    
    def __init__(self, schedule_file: Optional[str] = None):
        """
        Initialize schedule loader.
        
        Args:
            schedule_file: Path to schedule file (CSV or JSON)
        """
        self.schedule_file = schedule_file
        self.schedules: List[Dict] = []
        self.loaded = False
        
    def load_from_csv(self, filepath: str) -> bool:
        """
        Load train schedules from CSV file.
        
        Expected columns:
        - train_id: Unique train identifier
        - source_station: Origin station
        - destination_station: Destination station
        - scheduled_arrival: Scheduled arrival time (HH:MM format)
        - average_speed: Average speed in kmph
        - train_type: STOPPING or NON_STOPPING
        - initial_distance: Starting distance from station in km
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            True if loaded successfully
        """
        try:
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_cols = [
                'train_id', 'source_station', 'destination_station',
                'scheduled_arrival', 'average_speed', 'train_type', 'initial_distance'
            ]
            
            if not all(col in df.columns for col in required_cols):
                print(f"❌ CSV missing required columns. Required: {required_cols}")
                return False
            
            # Convert to list of dictionaries
            self.schedules = df.to_dict('records')
            self.loaded = True
            
            print(f"✓ Loaded {len(self.schedules)} train schedules from CSV")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def load_from_json(self, filepath: str) -> bool:
        """
        Load train schedules from JSON file.
        
        Expected format:
        {
            "schedules": [
                {
                    "train_id": "T001",
                    "source_station": "Station A",
                    "destination_station": "Station B",
                    "scheduled_arrival": "14:30",
                    "average_speed": 80,
                    "train_type": "STOPPING",
                    "initial_distance": 10.0
                },
                ...
            ]
        }
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if 'schedules' not in data:
                print("❌ JSON must contain 'schedules' key")
                return False
            
            self.schedules = data['schedules']
            self.loaded = True
            
            print(f"✓ Loaded {len(self.schedules)} train schedules from JSON")
            return True
            
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load schedule from configured file.
        Auto-detects format based on extension.
        
        Returns:
            True if loaded successfully
        """
        if not self.schedule_file:
            print("⚠️ No schedule file specified, will use simulation")
            return False
        
        if not os.path.exists(self.schedule_file):
            print(f"⚠️ Schedule file not found: {self.schedule_file}")
            return False
        
        # Auto-detect format
        if self.schedule_file.endswith('.csv'):
            return self.load_from_csv(self.schedule_file)
        elif self.schedule_file.endswith('.json'):
            return self.load_from_json(self.schedule_file)
        else:
            print(f"❌ Unsupported file format. Use .csv or .json")
            return False
    
    def get_schedules(self) -> List[Dict]:
        """
        Get loaded schedules.
        
        Returns:
            List of schedule dictionaries
        """
        return self.schedules
    
    def get_schedule_by_train_id(self, train_id: str) -> Optional[Dict]:
        """
        Get schedule for specific train.
        
        Args:
            train_id: Train identifier
            
        Returns:
            Schedule dictionary or None
        """
        for schedule in self.schedules:
            if schedule.get('train_id') == train_id:
                return schedule
        return None
    
    def get_station_stops(self, station_name: str) -> List[Dict]:
        """
        Get all schedule entries involving a specific station.
        
        Args:
            station_name: Station name to filter by
            
        Returns:
            List of schedule dictionaries
        """
        stops = []
        for schedule in self.schedules:
            if (schedule.get('departure_station') == station_name or 
                schedule.get('arrival_station') == station_name):
                stops.append(schedule)
        return stops
    
    def get_trains_at_station_time(self, station_name: str, time_str: str) -> List[str]:
        """
        Get trains at a station at a specific time (simplified).
        
        Args:
            station_name: Station name
            time_str: Time in HH:MM format
            
        Returns:
            List of train IDs
        """
        # This is a simplified version - actual implementation would need
        # proper time parsing and comparison
        trains = []
        stops = self.get_station_stops(station_name)
        
        for stop in stops:
            # Check if train is at station around this time
            scheduled = stop.get('scheduled_time', '')
            actual = stop.get('actual_time', '')
            
            if time_str in scheduled or time_str in actual:
                train_id = stop.get('train_id')
                if train_id and train_id not in trains:
                    trains.append(train_id)
        
        return trains
    
    def get_time_range(self) -> tuple:
        """
        Get the time range covered by schedules.
        
        Returns:
            Tuple of (min_time_str, max_time_str)
        """
        times = []
        
        for schedule in self.schedules:
            scheduled = schedule.get('scheduled_time')
            actual = schedule.get('actual_time')
            
            if scheduled:
                times.append(scheduled)
            if actual:
                times.append(actual)
        
        if times:
            return min(times), max(times)
        return None, None
    
    def validate_schedule(self, schedule: Dict) -> bool:
        """
        Validate a single schedule entry.
        
        Args:
            schedule: Schedule dictionary
            
        Returns:
            True if valid
        """
        required_fields = [
            'train_id', 'source_station', 'destination_station',
            'scheduled_arrival', 'average_speed', 'train_type', 'initial_distance'
        ]
        
        # Check all required fields present
        if not all(field in schedule for field in required_fields):
            return False
        
        # Validate train_type
        if schedule['train_type'] not in ['STOPPING', 'NON_STOPPING']:
            return False
        
        # Validate numeric fields
        try:
            float(schedule['average_speed'])
            float(schedule['initial_distance'])
        except (ValueError, TypeError):
            return False
        
        return True
    
    def get_valid_schedules(self) -> List[Dict]:
        """
        Get only valid schedules.
        
        Returns:
            List of validated schedule dictionaries
        """
        return [s for s in self.schedules if self.validate_schedule(s)]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about loaded schedules.
        
        Returns:
            Dictionary with statistics
        """
        valid_schedules = self.get_valid_schedules()
        
        return {
            'total_schedules': len(self.schedules),
            'valid_schedules': len(valid_schedules),
            'invalid_schedules': len(self.schedules) - len(valid_schedules),
            'loaded': self.loaded,
            'source_file': self.schedule_file
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ScheduleLoader(schedules={len(self.schedules)}, loaded={self.loaded})"


if __name__ == "__main__":
    # Test schedule loader
    print("\n" + "="*60)
    print("Schedule Loader Test")
    print("="*60 + "\n")
    
    # Test with non-existent file (should fallback)
    loader = ScheduleLoader("nonexistent.csv")
    loader.load()
    
    print(f"\nLoader status: {loader}")
    print(f"Statistics: {loader.get_stats()}")
