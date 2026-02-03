"""
Track Occupancy Calculator - Calculate platform occupancy based on schedule data.
Supports time-based queries and multi-station tracking.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class TrackOccupancyCalculator:
    """
    Calculates track/platform occupancy for stations based on train schedules.
    Implements intelligent platform allocation algorithm.
    """
    
    def __init__(self, schedule_data: pd.DataFrame, network_topology: Dict):
        """
        Initialize track occupancy calculator.
        
        Args:
            schedule_data: DataFrame with train schedule information
            network_topology: Dictionary with station and route information
        """
        self.schedule_data = schedule_data
        self.network_topology = network_topology
        self.occupancy_timeline = {}  # station_id -> timeline data
        self.platform_allocations = {}  # (train_id, station_id) -> platform_id
        
        # Build station platform mapping
        self.station_platforms = self._build_station_platform_map()
        
        # Calculate occupancy timelines for all stations
        self._calculate_all_timelines()
    
    def _build_station_platform_map(self) -> Dict[str, List[str]]:
        """
        Build mapping of station IDs to their platform IDs.
        
        Returns:
            Dictionary mapping station_id to list of platform IDs
        """
        station_platforms = {}
        
        if 'stations' in self.network_topology:
            for station in self.network_topology['stations']:
                station_id = station.get('station_id')
                station_name = station.get('station_name')
                platform_count = station.get('platforms', 3)  # Default to 3
                
                # Generate platform IDs (P1, P2, P3, ...)
                platforms = [f"P{i+1}" for i in range(platform_count)]
                station_platforms[station_id] = platforms
                station_platforms[station_name] = platforms  # Also map by name
        
        return station_platforms
    
    def _parse_time(self, time_str: str, base_date: str = "2024-01-01") -> datetime:
        """
        Parse time string to datetime object.
        
        Args:
            time_str: Time string in HH:MM or HH:MM:SS format
            base_date: Base date to use for datetime
            
        Returns:
            datetime object
        """
        try:
            # Handle different time formats
            if isinstance(time_str, str):
                if ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) == 2:
                        time_str = f"{time_str}:00"
                    return datetime.strptime(f"{base_date} {time_str}", "%Y-%m-%d %H:%M:%S")
            return datetime.strptime(f"{base_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.strptime(f"{base_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    def _extract_station_stops(self) -> List[Dict]:
        """
        Extract all station stops from schedule data.
        Each row represents a segment, we need to extract arrival/departure per station.
        
        Returns:
            List of station stop dictionaries
        """
        stops = []
        
        for _, row in self.schedule_data.iterrows():
            train_id = row.get('train_id')
            
            # Departure station stop
            dep_station = row.get('departure_station')
            dep_time = row.get('scheduled_time', row.get('actual_time'))
            
            if dep_station and dep_time:
                stops.append({
                    'train_id': train_id,
                    'station_name': dep_station,
                    'arrival_time': None,  # Train starts here
                    'departure_time': self._parse_time(dep_time),
                    'event_type': 'DEPARTURE'
                })
            
            # Arrival station stop
            arr_station = row.get('arrival_station')
            arr_time = row.get('actual_time', row.get('scheduled_time'))
            
            if arr_station and arr_time:
                stops.append({
                    'train_id': train_id,
                    'station_name': arr_station,
                    'arrival_time': self._parse_time(arr_time),
                    'departure_time': None,  # Train ends here or continues
                    'event_type': 'ARRIVAL'
                })
        
        return stops
    
    def _allocate_platform(self, train_id: str, station_name: str, 
                          arrival_time: datetime, departure_time: Optional[datetime],
                          occupied_platforms: Dict[str, Tuple[datetime, datetime]]) -> Optional[str]:
        """
        Allocate a platform for a train at a station.
        
        Args:
            train_id: Train identifier
            station_name: Station name
            arrival_time: Arrival time
            departure_time: Departure time (None if terminal)
            occupied_platforms: Currently occupied platforms with time ranges
            
        Returns:
            Platform ID or None if no platform available
        """
        # Get available platforms for this station
        platforms = self.station_platforms.get(station_name, ['P1', 'P2', 'P3'])
        
        # Default dwell time if no departure time
        if departure_time is None:
            departure_time = arrival_time + timedelta(minutes=30)
        
        # Find first available platform
        for platform_id in platforms:
            if platform_id not in occupied_platforms:
                # Platform is free
                return platform_id
            
            # Check if platform is free during our time window
            occupied_start, occupied_end = occupied_platforms[platform_id]
            
            # No overlap if we arrive after they depart or depart before they arrive
            if arrival_time >= occupied_end or departure_time <= occupied_start:
                return platform_id
        
        # No platform available (shouldn't happen with proper data)
        return platforms[0] if platforms else None
    
    def _calculate_all_timelines(self):
        """
        Calculate occupancy timelines for all stations.
        """
        stops = self._extract_station_stops()
        
        # Group stops by station
        station_stops = {}
        for stop in stops:
            station = stop['station_name']
            if station not in station_stops:
                station_stops[station] = []
            station_stops[station].append(stop)
        
        # For each station, calculate platform allocations
        for station_name, stops_list in station_stops.items():
            self._calculate_station_timeline(station_name, stops_list)
    
    def _calculate_station_timeline(self, station_name: str, stops: List[Dict]):
        """
        Calculate platform occupancy timeline for a specific station.
        
        Args:
            station_name: Station name
            stops: List of stop events at this station
        """
        # Merge arrival and departure events for same train
        train_visits = {}
        
        for stop in stops:
            train_id = stop['train_id']
            
            if train_id not in train_visits:
                train_visits[train_id] = {
                    'train_id': train_id,
                    'station_name': station_name,
                    'arrival_time': None,
                    'departure_time': None
                }
            
            if stop['event_type'] == 'ARRIVAL':
                train_visits[train_id]['arrival_time'] = stop['arrival_time']
            else:  # DEPARTURE
                train_visits[train_id]['departure_time'] = stop['departure_time']
        
        # Sort by arrival time (or departure time if no arrival)
        visits = sorted(train_visits.values(), 
                       key=lambda x: x['arrival_time'] or x['departure_time'])
        
        # Allocate platforms
        timeline = []
        occupied_platforms = {}  # platform_id -> (start_time, end_time)
        
        for visit in visits:
            train_id = visit['train_id']
            arrival = visit['arrival_time']
            departure = visit['departure_time']
            
            # Determine time range
            if arrival and departure:
                start_time = arrival
                end_time = departure
            elif arrival:
                start_time = arrival
                end_time = arrival + timedelta(minutes=30)  # Default dwell
            else:  # departure only
                start_time = departure - timedelta(minutes=30)  # Assume 30 min before
                end_time = departure
            
            # Allocate platform
            platform_id = self._allocate_platform(
                train_id, station_name, start_time, end_time, occupied_platforms
            )
            
            # Update occupied platforms
            if platform_id:
                occupied_platforms[platform_id] = (start_time, end_time)
                
                # Store allocation
                self.platform_allocations[(train_id, station_name)] = platform_id
                
                # Add to timeline
                timeline.append({
                    'train_id': train_id,
                    'platform_id': platform_id,
                    'arrival_time': arrival,
                    'departure_time': departure,
                    'start_time': start_time,
                    'end_time': end_time
                })
        
        self.occupancy_timeline[station_name] = timeline
    
    def get_occupancy_at_time(self, station_name: str, timestamp: datetime) -> Dict:
        """
        Get platform occupancy at a specific time for a station.
        
        Args:
            station_name: Station name
            timestamp: Time to query
            
        Returns:
            Dictionary with platform occupancy information
        """
        timeline = self.occupancy_timeline.get(station_name, [])
        platforms = self.station_platforms.get(station_name, ['P1', 'P2', 'P3'])
        
        # Initialize all platforms as free
        occupancy = {
            'station_name': station_name,
            'timestamp': timestamp,
            'total_platforms': len(platforms),
            'occupied_count': 0,
            'free_count': len(platforms),
            'platforms': {}
        }
        
        for platform_id in platforms:
            occupancy['platforms'][platform_id] = {
                'platform_id': platform_id,
                'status': 'FREE',
                'train_id': None,
                'arrival_time': None,
                'departure_time': None
            }
        
        # Check which trains are at the station at this time
        for event in timeline:
            if event['start_time'] <= timestamp <= event['end_time']:
                platform_id = event['platform_id']
                occupancy['platforms'][platform_id] = {
                    'platform_id': platform_id,
                    'status': 'OCCUPIED',
                    'train_id': event['train_id'],
                    'arrival_time': event['arrival_time'],
                    'departure_time': event['departure_time']
                }
        
        # Update counts
        occupied = sum(1 for p in occupancy['platforms'].values() if p['status'] == 'OCCUPIED')
        occupancy['occupied_count'] = occupied
        occupancy['free_count'] = len(platforms) - occupied
        
        return occupancy
    
    def get_all_stations_occupancy(self, timestamp: datetime) -> Dict[str, Dict]:
        """
        Get platform occupancy for all stations at a specific time.
        
        Args:
            timestamp: Time to query
            
        Returns:
            Dictionary mapping station names to occupancy data
        """
        all_occupancy = {}
        
        for station_name in self.occupancy_timeline.keys():
            all_occupancy[station_name] = self.get_occupancy_at_time(station_name, timestamp)
        
        return all_occupancy
    
    def get_platform_allocation(self, train_id: str, station_name: str) -> Optional[str]:
        """
        Get platform allocation for a specific train at a station.
        
        Args:
            train_id: Train identifier
            station_name: Station name
            
        Returns:
            Platform ID or None
        """
        return self.platform_allocations.get((train_id, station_name))
    
    def get_station_summary(self, station_name: str) -> Dict:
        """
        Get summary statistics for a station.
        
        Args:
            station_name: Station name
            
        Returns:
            Dictionary with station statistics
        """
        timeline = self.occupancy_timeline.get(station_name, [])
        platforms = self.station_platforms.get(station_name, [])
        
        # Count unique trains
        unique_trains = set(event['train_id'] for event in timeline)
        
        return {
            'station_name': station_name,
            'total_platforms': len(platforms),
            'total_train_visits': len(timeline),
            'unique_trains': len(unique_trains),
            'platform_ids': platforms
        }
    
    def get_time_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the time range covered by the schedule data.
        
        Returns:
            Tuple of (min_time, max_time)
        """
        all_times = []
        
        for timeline in self.occupancy_timeline.values():
            for event in timeline:
                if event['start_time']:
                    all_times.append(event['start_time'])
                if event['end_time']:
                    all_times.append(event['end_time'])
        
        if all_times:
            return min(all_times), max(all_times)
        return None, None
    
    def __repr__(self) -> str:
        """String representation."""
        return f"TrackOccupancyCalculator(stations={len(self.occupancy_timeline)}, allocations={len(self.platform_allocations)})"


if __name__ == "__main__":
    # Test with sample data
    print("\n" + "="*60)
    print("Track Occupancy Calculator Test")
    print("="*60 + "\n")
    
    # Load sample data
    try:
        schedule_df = pd.read_csv("data/sample_indian_railways.csv")
        with open("data/sample_network_topology.json", 'r') as f:
            topology = json.load(f)
        
        calculator = TrackOccupancyCalculator(schedule_df, topology)
        
        print(f"Calculator: {calculator}")
        print(f"\nTime range: {calculator.get_time_range()}")
        
        # Test occupancy at specific time
        test_time = datetime(2024, 1, 1, 8, 30)
        print(f"\n--- Occupancy at {test_time.strftime('%H:%M')} ---")
        
        all_occupancy = calculator.get_all_stations_occupancy(test_time)
        for station, occ in all_occupancy.items():
            print(f"\n{station}: {occ['occupied_count']}/{occ['total_platforms']} occupied")
            for platform_id, platform_data in occ['platforms'].items():
                if platform_data['status'] == 'OCCUPIED':
                    print(f"  {platform_id}: {platform_data['train_id']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
