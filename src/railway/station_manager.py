"""
Station Manager - Manage multiple railway stations and their track configurations.
Coordinates platform allocations across the network.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Optional
import json
from src.railway.track_manager import TrackManager


class StationManager:
    """
    Manages multiple railway stations and their track/platform configurations.
    Loads station data from network topology and creates track managers.
    """
    
    def __init__(self, network_topology: Dict = None, topology_file: str = None):
        """
        Initialize station manager.
        
        Args:
            network_topology: Dictionary with network topology data
            topology_file: Path to topology JSON file (alternative to network_topology)
        """
        self.stations = {}  # station_id -> station data
        self.track_managers = {}  # station_id -> TrackManager
        
        # Load topology
        if network_topology:
            self.topology = network_topology
        elif topology_file:
            self.topology = self._load_topology_file(topology_file)
        else:
            self.topology = {}
        
        # Initialize stations
        self._initialize_stations()
    
    def _load_topology_file(self, filepath: str) -> Dict:
        """
        Load network topology from JSON file.
        
        Args:
            filepath: Path to topology file
            
        Returns:
            Topology dictionary
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading topology: {e}")
            return {}
    
    def _initialize_stations(self):
        """
        Initialize station data and track managers from topology.
        """
        if 'stations' not in self.topology:
            print("⚠️ No stations found in topology")
            return
        
        for station_data in self.topology['stations']:
            station_id = station_data.get('station_id')
            station_name = station_data.get('station_name')
            platform_count = station_data.get('platforms', 3)
            
            # Store station data
            self.stations[station_id] = {
                'station_id': station_id,
                'station_name': station_name,
                'platform_count': platform_count,
                'latitude': station_data.get('latitude'),
                'longitude': station_data.get('longitude'),
                'zone': station_data.get('zone'),
                'platform_ids': [f"P{i+1}" for i in range(platform_count)]
            }
            
            # Also index by name for convenience
            self.stations[station_name] = self.stations[station_id]
            
            # Create track manager for this station
            self.track_managers[station_id] = TrackManager(
                track_ids=self.stations[station_id]['platform_ids']
            )
            self.track_managers[station_name] = self.track_managers[station_id]
        
        print(f"✓ Initialized {len(self.topology['stations'])} stations")
    
    def get_station(self, station_id: str) -> Optional[Dict]:
        """
        Get station data by ID or name.
        
        Args:
            station_id: Station ID or name
            
        Returns:
            Station data dictionary or None
        """
        return self.stations.get(station_id)
    
    def get_all_stations(self) -> List[Dict]:
        """
        Get all station data.
        
        Returns:
            List of station dictionaries
        """
        # Return unique stations (avoid duplicates from name indexing)
        seen = set()
        stations = []
        
        for station in self.stations.values():
            station_id = station.get('station_id')
            if station_id and station_id not in seen:
                seen.add(station_id)
                stations.append(station)
        
        return stations
    
    def get_station_names(self) -> List[str]:
        """
        Get list of all station names.
        
        Returns:
            List of station names
        """
        return [s['station_name'] for s in self.get_all_stations()]
    
    def get_track_manager(self, station_id: str) -> Optional[TrackManager]:
        """
        Get track manager for a specific station.
        
        Args:
            station_id: Station ID or name
            
        Returns:
            TrackManager instance or None
        """
        return self.track_managers.get(station_id)
    
    def get_station_summary(self, station_id: str) -> Optional[Dict]:
        """
        Get summary information for a station.
        
        Args:
            station_id: Station ID or name
            
        Returns:
            Summary dictionary or None
        """
        station = self.get_station(station_id)
        if not station:
            return None
        
        track_manager = self.get_track_manager(station_id)
        
        summary = {
            'station_id': station['station_id'],
            'station_name': station['station_name'],
            'total_platforms': station['platform_count'],
            'platform_ids': station['platform_ids'],
            'zone': station.get('zone'),
            'location': {
                'latitude': station.get('latitude'),
                'longitude': station.get('longitude')
            }
        }
        
        # Add track manager stats if available
        if track_manager:
            summary['free_platforms'] = track_manager.get_free_track_count()
            summary['occupied_platforms'] = station['platform_count'] - summary['free_platforms']
        
        return summary
    
    def get_all_stations_summary(self) -> List[Dict]:
        """
        Get summary for all stations.
        
        Returns:
            List of station summaries
        """
        summaries = []
        
        for station in self.get_all_stations():
            summary = self.get_station_summary(station['station_id'])
            if summary:
                summaries.append(summary)
        
        return summaries
    
    def get_total_platforms(self) -> int:
        """
        Get total number of platforms across all stations.
        
        Returns:
            Total platform count
        """
        return sum(s['platform_count'] for s in self.get_all_stations())
    
    def __repr__(self) -> str:
        """String representation."""
        unique_stations = len(self.get_all_stations())
        total_platforms = self.get_total_platforms()
        return f"StationManager(stations={unique_stations}, total_platforms={total_platforms})"


if __name__ == "__main__":
    # Test station manager
    print("\n" + "="*60)
    print("Station Manager Test")
    print("="*60 + "\n")
    
    try:
        # Load from file
        manager = StationManager(topology_file="data/sample_network_topology.json")
        
        print(f"Manager: {manager}")
        print(f"\nStation names: {manager.get_station_names()}")
        
        # Test getting station info
        print("\n--- Station Summaries ---")
        for summary in manager.get_all_stations_summary():
            print(f"\n{summary['station_name']} ({summary['station_id']})")
            print(f"  Platforms: {summary['total_platforms']}")
            print(f"  Zone: {summary['zone']}")
            print(f"  Platform IDs: {', '.join(summary['platform_ids'][:5])}...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
