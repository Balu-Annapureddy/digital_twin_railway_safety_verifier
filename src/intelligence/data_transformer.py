"""
Data Transformer - Converts analyzed datasets into unified format.
Transforms various railway data formats into a standardized structure.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from .dataset_analyzer import DatasetAnalysisResult


class UnifiedDataModel:
    """
    Unified data model for railway operations.
    All datasets are transformed into this standard format.
    """
    
    def __init__(self):
        # Core entities
        self.trains: pd.DataFrame = pd.DataFrame()
        self.stations: pd.DataFrame = pd.DataFrame()
        self.routes: pd.DataFrame = pd.DataFrame()
        self.events: pd.DataFrame = pd.DataFrame()
        
        # Metadata
        self.network_name: str = "Railway Network"
        self.time_range: tuple = (None, None)
        self.total_trains: int = 0
        self.total_stations: int = 0


class DataTransformer:
    """
    Transforms analyzed datasets into unified format.
    
    Handles different dataset types:
    - SCHEDULE: Train schedules with departure/arrival times
    - REALTIME_TRACKING: GPS coordinates and speed data
    - HISTORICAL_LOG: Historical operational logs
    - NETWORK_TOPOLOGY: Station and route definitions
    """
    
    def __init__(self, analysis_result: DatasetAnalysisResult):
        """
        Initialize transformer with analysis results.
        
        Args:
            analysis_result: Results from SmartDatasetAnalyzer
        """
        self.analysis = analysis_result
        self.unified_model = UnifiedDataModel()
    
    def transform(self) -> UnifiedDataModel:
        """
        Transform dataset into unified model.
        
        Returns:
            UnifiedDataModel with standardized data
        """
        df = self.analysis.dataframe
        
        if df is None or df.empty:
            return self.unified_model
        
        # Transform based on dataset type
        if self.analysis.dataset_type == "SCHEDULE":
            self._transform_schedule(df)
        elif self.analysis.dataset_type == "REALTIME_TRACKING":
            self._transform_realtime(df)
        elif self.analysis.dataset_type == "HISTORICAL_LOG":
            self._transform_historical(df)
        elif self.analysis.dataset_type == "NETWORK_TOPOLOGY":
            self._transform_network(df)
        else:
            # Generic transformation
            self._transform_generic(df)
        
        # Extract metadata
        self._extract_metadata()
        
        return self.unified_model
    
    def _transform_schedule(self, df: pd.DataFrame) -> None:
        """Transform schedule dataset."""
        trains_data = []
        events_data = []
        stations_set = set()
        
        # Group by train
        if self.analysis.train_id_column:
            for train_id, group in df.groupby(self.analysis.train_id_column):
                # Create train record
                train_record = {
                    'train_id': train_id,
                    'total_stops': len(group),
                    'route': ' → '.join(group[self.analysis.station_column].astype(str).tolist()) if self.analysis.station_column else ''
                }
                trains_data.append(train_record)
                
                # Create events for each stop
                for idx, row in group.iterrows():
                    event = {
                        'train_id': train_id,
                        'event_type': 'ARRIVAL',
                        'station': row[self.analysis.station_column] if self.analysis.station_column else None,
                        'timestamp': pd.to_datetime(row[self.analysis.timestamp_column]) if self.analysis.timestamp_column else None,
                        'status': row[self.analysis.status_column] if self.analysis.status_column else 'UNKNOWN'
                    }
                    events_data.append(event)
                    
                    if self.analysis.station_column:
                        stations_set.add(row[self.analysis.station_column])
        
        self.unified_model.trains = pd.DataFrame(trains_data)
        self.unified_model.events = pd.DataFrame(events_data)
        self.unified_model.stations = pd.DataFrame([{'station_id': s, 'station_name': s} for s in stations_set])
    
    def _transform_realtime(self, df: pd.DataFrame) -> None:
        """Transform real-time tracking dataset."""
        # Create train records with latest position
        if self.analysis.train_id_column:
            latest_positions = df.groupby(self.analysis.train_id_column).last().reset_index()
            
            trains_data = []
            for idx, row in latest_positions.iterrows():
                train_record = {
                    'train_id': row[self.analysis.train_id_column],
                    'current_speed': row[self.analysis.speed_column] if self.analysis.speed_column else 0,
                    'status': row[self.analysis.status_column] if self.analysis.status_column else 'RUNNING'
                }
                
                # Add location if available
                if len(self.analysis.location_columns) >= 2:
                    train_record['latitude'] = row[self.analysis.location_columns[0]]
                    train_record['longitude'] = row[self.analysis.location_columns[1]]
                
                trains_data.append(train_record)
            
            self.unified_model.trains = pd.DataFrame(trains_data)
        
        # All rows become events
        events_data = []
        for idx, row in df.iterrows():
            event = {
                'train_id': row[self.analysis.train_id_column] if self.analysis.train_id_column else None,
                'event_type': 'POSITION_UPDATE',
                'timestamp': pd.to_datetime(row[self.analysis.timestamp_column]) if self.analysis.timestamp_column else None,
                'speed': row[self.analysis.speed_column] if self.analysis.speed_column else None
            }
            
            if len(self.analysis.location_columns) >= 2:
                event['latitude'] = row[self.analysis.location_columns[0]]
                event['longitude'] = row[self.analysis.location_columns[1]]
            
            events_data.append(event)
        
        self.unified_model.events = pd.DataFrame(events_data)
    
    def _transform_historical(self, df: pd.DataFrame) -> None:
        """Transform historical log dataset."""
        # Similar to schedule but with more event types
        self._transform_schedule(df)
    
    def _transform_network(self, df: pd.DataFrame) -> None:
        """Transform network topology dataset."""
        # Extract stations and routes
        if self.analysis.station_column:
            stations = df[self.analysis.station_column].unique()
            self.unified_model.stations = pd.DataFrame([
                {'station_id': s, 'station_name': s} for s in stations
            ])
    
    def _transform_generic(self, df: pd.DataFrame) -> None:
        """Generic transformation for unknown dataset types."""
        # Try to extract what we can
        if self.analysis.train_id_column:
            trains = df[self.analysis.train_id_column].unique()
            self.unified_model.trains = pd.DataFrame([
                {'train_id': t} for t in trains
            ])
        
        # Store all data as events
        self.unified_model.events = df.copy()
    
    def _extract_metadata(self) -> None:
        """Extract metadata from unified model."""
        self.unified_model.total_trains = len(self.unified_model.trains)
        self.unified_model.total_stations = len(self.unified_model.stations)
        self.unified_model.time_range = (self.analysis.start_time, self.analysis.end_time)
    
    def get_summary(self) -> str:
        """Get transformation summary."""
        summary = []
        summary.append(f"🔄 Data Transformation Summary")
        summary.append(f"=" * 50)
        summary.append(f"Trains: {self.unified_model.total_trains}")
        summary.append(f"Stations: {self.unified_model.total_stations}")
        summary.append(f"Events: {len(self.unified_model.events)}")
        summary.append(f"Routes: {len(self.unified_model.routes)}")
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test transformation
    from dataset_analyzer import SmartDatasetAnalyzer
    
    print("\n" + "="*60)
    print("Data Transformer - Test")
    print("="*60 + "\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'train_id': ['T001', 'T001', 'T002'],
        'timestamp': ['2024-01-01 10:00', '2024-01-01 11:00', '2024-01-01 10:30'],
        'station': ['Mumbai', 'Delhi', 'Chennai'],
        'status': ['ON_TIME', 'DELAYED', 'ON_TIME']
    })
    
    # Analyze
    analyzer = SmartDatasetAnalyzer()
    result = analyzer.analyze(dataframe=sample_data)
    
    # Transform
    transformer = DataTransformer(result)
    unified = transformer.transform()
    
    print(transformer.get_summary())
    print("\nTrains DataFrame:")
    print(unified.trains)
