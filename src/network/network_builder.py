"""
Network Builder - Constructs railway network graph from data.
Creates nodes (stations) and edges (routes) for visualization.
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Optional, Tuple
import numpy as np


class Station:
    """Represents a railway station node."""
    
    def __init__(self, station_id: str, name: str, latitude: float = None, longitude: float = None):
        self.station_id = station_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.platforms: List[str] = []
        self.connections: List[str] = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'station_id': self.station_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'platforms': self.platforms,
            'connections': self.connections
        }


class Route:
    """Represents a railway route (edge between stations)."""
    
    def __init__(self, from_station: str, to_station: str, distance: float = 0, line_name: str = "Main"):
        self.from_station = from_station
        self.to_station = to_station
        self.distance = distance
        self.line_name = line_name
        self.trains_on_route: List[str] = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'from': self.from_station,
            'to': self.to_station,
            'distance': self.distance,
            'line': self.line_name,
            'trains': self.trains_on_route
        }


class NetworkBuilder:
    """
    Builds railway network graph from unified data model.
    
    Features:
    - Creates station nodes
    - Builds route edges
    - Auto-generates layout if coordinates missing
    - Calculates network statistics
    """
    
    def __init__(self, unified_model=None):
        """
        Initialize network builder.
        
        Args:
            unified_model: UnifiedDataModel from transformer
        """
        self.unified_model = unified_model
        self.graph = nx.Graph()
        self.stations: Dict[str, Station] = {}
        self.routes: List[Route] = []
        self.layout: Dict[str, Tuple[float, float]] = {}
    
    def build_topology(self) -> nx.Graph:
        """
        Build network topology from data.
        
        Returns:
            NetworkX graph representing the railway network
        """
        if self.unified_model is None:
            return self.graph
        
        # Build stations
        self._build_stations()
        
        # Build routes
        self._build_routes()
        
        # Generate layout if coordinates missing
        self._generate_layout()
        
        return self.graph
    
    def _build_stations(self) -> None:
        """Create station nodes."""
        if self.unified_model.stations.empty:
            # Try to infer from events
            if not self.unified_model.events.empty and 'station' in self.unified_model.events.columns:
                unique_stations = self.unified_model.events['station'].dropna().unique()
                for station_name in unique_stations:
                    station = Station(
                        station_id=f"S{len(self.stations)+1}",
                        name=str(station_name)
                    )
                    self.stations[station.station_id] = station
                    self.graph.add_node(station.station_id, **station.to_dict())
        else:
            # Use stations from unified model
            for idx, row in self.unified_model.stations.iterrows():
                station = Station(
                    station_id=row.get('station_id', f"S{idx+1}"),
                    name=row.get('station_name', f"Station {idx+1}"),
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude')
                )
                self.stations[station.station_id] = station
                self.graph.add_node(station.station_id, **station.to_dict())
    
    def _build_routes(self) -> None:
        """Create route edges between stations."""
        # Try to infer routes from train journeys
        if not self.unified_model.events.empty:
            # Group events by train
            if 'train_id' in self.unified_model.events.columns and 'station' in self.unified_model.events.columns:
                for train_id, group in self.unified_model.events.groupby('train_id'):
                    stations_visited = group['station'].dropna().tolist()
                    
                    # Create edges between consecutive stations
                    for i in range(len(stations_visited) - 1):
                        from_station = stations_visited[i]
                        to_station = stations_visited[i + 1]
                        
                        # Find station IDs
                        from_id = self._find_station_id(from_station)
                        to_id = self._find_station_id(to_station)
                        
                        if from_id and to_id:
                            # Add edge if not exists
                            if not self.graph.has_edge(from_id, to_id):
                                route = Route(from_id, to_id)
                                self.routes.append(route)
                                self.graph.add_edge(from_id, to_id, **route.to_dict())
                            
                            # Add train to route
                            edge_data = self.graph[from_id][to_id]
                            if 'trains' not in edge_data:
                                edge_data['trains'] = []
                            if train_id not in edge_data['trains']:
                                edge_data['trains'].append(train_id)
        
        # Use routes from unified model if available
        if not self.unified_model.routes.empty:
            for idx, row in self.unified_model.routes.iterrows():
                route = Route(
                    from_station=row.get('from_station'),
                    to_station=row.get('to_station'),
                    distance=row.get('distance', 0),
                    line_name=row.get('line_name', 'Main')
                )
                self.routes.append(route)
                self.graph.add_edge(route.from_station, route.to_station, **route.to_dict())
    
    def _find_station_id(self, station_name: str) -> Optional[str]:
        """Find station ID by name."""
        for station_id, station in self.stations.items():
            if station.name == station_name:
                return station_id
        return None
    
    def _generate_layout(self) -> None:
        """Generate network layout for visualization."""
        # Check if we have real coordinates
        has_coords = any(
            s.latitude is not None and s.longitude is not None 
            for s in self.stations.values()
        )
        
        if has_coords:
            # Use real coordinates
            for station_id, station in self.stations.items():
                if station.latitude and station.longitude:
                    self.layout[station_id] = (station.longitude, station.latitude)
        else:
            # Generate automatic layout
            if len(self.graph.nodes()) > 0:
                # Use spring layout for aesthetic positioning
                self.layout = nx.spring_layout(self.graph, k=2, iterations=50)
    
    def get_network_stats(self) -> Dict:
        """Get network statistics."""
        return {
            'total_stations': len(self.stations),
            'total_routes': len(self.routes),
            'total_connections': self.graph.number_of_edges(),
            'network_diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) else 0,
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()) if len(self.graph.nodes()) > 0 else 0
        }
    
    def get_shortest_path(self, from_station: str, to_station: str) -> List[str]:
        """
        Find shortest path between two stations.
        
        Args:
            from_station: Starting station ID
            to_station: Destination station ID
            
        Returns:
            List of station IDs in path
        """
        try:
            return nx.shortest_path(self.graph, from_station, to_station)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def get_station_info(self, station_id: str) -> Optional[Dict]:
        """Get detailed station information."""
        if station_id in self.stations:
            station = self.stations[station_id]
            info = station.to_dict()
            info['degree'] = self.graph.degree(station_id)
            info['neighbors'] = list(self.graph.neighbors(station_id))
            return info
        return None


if __name__ == "__main__":
    # Test network builder
    print("\n" + "="*60)
    print("Network Builder - Test")
    print("="*60 + "\n")
    
    # Create sample unified model
    from src.intelligence.data_transformer import UnifiedDataModel
    
    model = UnifiedDataModel()
    model.stations = pd.DataFrame([
        {'station_id': 'S1', 'station_name': 'Mumbai'},
        {'station_id': 'S2', 'station_name': 'Pune'},
        {'station_id': 'S3', 'station_name': 'Delhi'}
    ])
    
    model.events = pd.DataFrame([
        {'train_id': 'T001', 'station': 'Mumbai'},
        {'train_id': 'T001', 'station': 'Pune'},
        {'train_id': 'T002', 'station': 'Pune'},
        {'train_id': 'T002', 'station': 'Delhi'}
    ])
    
    # Build network
    builder = NetworkBuilder(model)
    graph = builder.build_topology()
    
    print("Network Statistics:")
    stats = builder.get_network_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nStations: {list(builder.stations.keys())}")
    print(f"Routes: {len(builder.routes)}")
