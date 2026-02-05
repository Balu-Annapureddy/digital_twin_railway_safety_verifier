"""
Simple Platform Tracker - Works directly with schedule CSV data
No topology file required!
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SimplePlatformTracker:
    """
    Simple platform tracking that works with any schedule CSV.
    Automatically infers stations and assigns platforms.
    """
    
    def __init__(self, schedule_df: pd.DataFrame):
        """Initialize with schedule dataframe"""
        self.df = schedule_df
        self.stations = self._extract_stations()
        self.platform_assignments = self._assign_platforms()
        
    def _extract_stations(self) -> Dict[str, int]:
        """Extract unique stations and assign platform counts"""
        stations = {}
        
        # Get all unique stations from departure and arrival columns
        for col in self.df.columns:
            if 'station' in col.lower() or 'source' in col.lower() or 'destination' in col.lower():
                unique_stations = self.df[col].dropna().unique()
                for station in unique_stations:
                    if station not in stations:
                        # Assign 3-6 platforms based on station activity
                        stations[str(station)] = 4  # Default 4 platforms
        
        return stations
    
    def _parse_time(self, time_val) -> Optional[datetime]:
        """Parse time value to datetime"""
        if pd.isna(time_val):
            return None
            
        try:
            if isinstance(time_val, str):
                # Try HH:MM format
                if ':' in time_val:
                    parts = time_val.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    return datetime(2024, 1, 1, hour, minute)
            return None
        except:
            return None
    
    def _assign_platforms(self) -> List[Dict]:
        """Assign platforms to trains based on schedule"""
        assignments = []
        
        for _, row in self.df.iterrows():
            train_id = row.get('train_id', 'UNKNOWN')
            
            # Departure station
            dep_station = row.get('departure_station')
            dep_time = self._parse_time(row.get('scheduled_time', row.get('actual_time')))
            
            if dep_station and dep_time:
                # Assign platform (simple round-robin)
                platform_num = (len(assignments) % 4) + 1
                assignments.append({
                    'train_id': train_id,
                    'station': str(dep_station),
                    'platform': f'P{platform_num}',
                    'arrival_time': dep_time - timedelta(minutes=15),  # Assume arrives 15 min before
                    'departure_time': dep_time,
                    'event': 'DEPARTURE'
                })
            
            # Arrival station
            arr_station = row.get('arrival_station')
            arr_time = self._parse_time(row.get('actual_time', row.get('scheduled_time')))
            
            if arr_station and arr_time:
                platform_num = (len(assignments) % 4) + 1
                assignments.append({
                    'train_id': train_id,
                    'station': str(arr_station),
                    'platform': f'P{platform_num}',
                    'arrival_time': arr_time,
                    'departure_time': arr_time + timedelta(minutes=30),  # Assume departs 30 min after
                    'event': 'ARRIVAL'
                })
        
        return assignments
    
    def get_occupancy_at_time(self, station: str, timestamp: datetime) -> Dict:
        """Get platform occupancy at specific time for a station"""
        
        # Get platform count for this station
        platform_count = self.stations.get(station, 4)
        platforms = [f'P{i+1}' for i in range(platform_count)]
        
        # Initialize all platforms as free
        result = {
            'station': station,
            'timestamp': timestamp,
            'total_platforms': platform_count,
            'occupied_count': 0,
            'free_count': platform_count,
            'platforms': {}
        }
        
        for p in platforms:
            result['platforms'][p] = {
                'platform_id': p,
                'status': 'FREE',
                'train_id': None,
                'arrival_time': None,
                'departure_time': None
            }
        
        # Check which trains are at this station at this time
        for assignment in self.platform_assignments:
            if assignment['station'] == station:
                if assignment['arrival_time'] <= timestamp <= assignment['departure_time']:
                    platform_id = assignment['platform']
                    result['platforms'][platform_id] = {
                        'platform_id': platform_id,
                        'status': 'OCCUPIED',
                        'train_id': assignment['train_id'],
                        'arrival_time': assignment['arrival_time'],
                        'departure_time': assignment['departure_time']
                    }
        
        # Update counts
        occupied = sum(1 for p in result['platforms'].values() if p['status'] == 'OCCUPIED')
        result['occupied_count'] = occupied
        result['free_count'] = platform_count - occupied
        
        return result
    
    def get_time_range(self):
        """Get min and max times from schedule"""
        all_times = []
        
        for assignment in self.platform_assignments:
            if assignment['arrival_time']:
                all_times.append(assignment['arrival_time'])
            if assignment['departure_time']:
                all_times.append(assignment['departure_time'])
        
        if all_times:
            return min(all_times), max(all_times)
        return datetime(2024, 1, 1, 6, 0), datetime(2024, 1, 1, 18, 0)
    
    def get_station_list(self) -> List[str]:
        """Get list of all stations"""
        return list(self.stations.keys())
