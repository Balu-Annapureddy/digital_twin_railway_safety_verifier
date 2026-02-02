"""
Smart Dataset Analyzer - Automatically detects and analyzes railway datasets.
Supports CSV, JSON, Excel formats with intelligent column detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
from pathlib import Path


class DatasetAnalysisResult:
    """Container for dataset analysis results."""
    
    def __init__(self):
        self.file_format: str = ""
        self.total_rows: int = 0
        self.total_columns: int = 0
        self.data_quality: float = 0.0
        
        # Detected entities
        self.train_count: int = 0
        self.station_count: int = 0
        self.route_count: int = 0
        
        # Detected columns
        self.train_id_column: Optional[str] = None
        self.timestamp_column: Optional[str] = None
        self.station_column: Optional[str] = None
        self.location_columns: List[str] = []
        self.speed_column: Optional[str] = None
        self.status_column: Optional[str] = None
        
        # Time range
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Data type
        self.dataset_type: str = "UNKNOWN"  # SCHEDULE, REALTIME, NETWORK, HISTORICAL
        
        # Issues found
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
        # Original dataframe
        self.dataframe: Optional[pd.DataFrame] = None


class SmartDatasetAnalyzer:
    """
    Intelligent analyzer that automatically detects railway dataset structure.
    
    Features:
    - Auto-detects file format (CSV, JSON, Excel)
    - Identifies column types (train_id, timestamp, location, etc.)
    - Determines dataset type (schedule, real-time, network)
    - Validates data quality
    - Provides helpful suggestions
    """
    
    # Common column name patterns
    TRAIN_ID_PATTERNS = ['train_id', 'train', 'trainid', 'train_no', 'train_number', 'id']
    TIMESTAMP_PATTERNS = ['timestamp', 'time', 'datetime', 'date', 'scheduled_time', 'actual_time']
    STATION_PATTERNS = ['station', 'station_name', 'station_id', 'stop', 'location', 'departure_station', 'arrival_station']
    LATITUDE_PATTERNS = ['lat', 'latitude', 'y']
    LONGITUDE_PATTERNS = ['lon', 'lng', 'longitude', 'x']
    SPEED_PATTERNS = ['speed', 'velocity', 'kmph', 'mph']
    STATUS_PATTERNS = ['status', 'state', 'condition']
    
    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize analyzer.
        
        Args:
            file_path: Path to dataset file (optional)
        """
        self.file_path = file_path
        self.result = DatasetAnalysisResult()
    
    def analyze(self, file_path: Optional[str] = None, dataframe: Optional[pd.DataFrame] = None) -> DatasetAnalysisResult:
        """
        Analyze dataset and return comprehensive results.
        
        Args:
            file_path: Path to dataset file
            dataframe: Pre-loaded dataframe (alternative to file_path)
            
        Returns:
            DatasetAnalysisResult with all findings
        """
        if file_path:
            self.file_path = file_path
        
        # Load data
        if dataframe is not None:
            df = dataframe
            self.result.file_format = "DataFrame"
        elif self.file_path:
            df = self._load_file()
        else:
            raise ValueError("Either file_path or dataframe must be provided")
        
        if df is None or df.empty:
            self.result.issues.append("Failed to load data or data is empty")
            return self.result
        
        self.result.dataframe = df
        self.result.total_rows = len(df)
        self.result.total_columns = len(df.columns)
        
        # Analyze structure
        self._detect_columns(df)
        self._detect_entities(df)
        self._determine_dataset_type(df)
        self._calculate_data_quality(df)
        self._extract_time_range(df)
        self._validate_data(df)
        
        return self.result
    
    def _load_file(self) -> Optional[pd.DataFrame]:
        """Load file based on extension."""
        try:
            path = Path(self.file_path)
            extension = path.suffix.lower()
            
            if extension == '.csv':
                self.result.file_format = "CSV"
                return pd.read_csv(self.file_path)
            elif extension == '.json':
                self.result.file_format = "JSON"
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                # Handle different JSON structures
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Check for common keys
                    for key in ['data', 'trains', 'schedules', 'records']:
                        if key in data:
                            return pd.DataFrame(data[key])
                    return pd.DataFrame([data])
            elif extension in ['.xlsx', '.xls']:
                self.result.file_format = "Excel"
                return pd.read_excel(self.file_path)
            else:
                self.result.issues.append(f"Unsupported file format: {extension}")
                return None
                
        except Exception as e:
            self.result.issues.append(f"Error loading file: {str(e)}")
            return None
    
    def _detect_columns(self, df: pd.DataFrame) -> None:
        """Detect column types using pattern matching."""
        columns_lower = {col: col.lower().replace('_', '').replace(' ', '') for col in df.columns}
        
        # Detect train ID column
        for col, col_lower in columns_lower.items():
            if any(pattern in col_lower for pattern in self.TRAIN_ID_PATTERNS):
                self.result.train_id_column = col
                break
        
        # Detect timestamp column
        for col in df.columns:
            if any(pattern in columns_lower[col] for pattern in self.TIMESTAMP_PATTERNS):
                # Verify it's actually a datetime
                try:
                    pd.to_datetime(df[col].dropna().iloc[0] if not df[col].dropna().empty else None)
                    self.result.timestamp_column = col
                    break
                except:
                    continue
        
        # Detect station column
        for col, col_lower in columns_lower.items():
            if any(pattern in col_lower for pattern in self.STATION_PATTERNS):
                self.result.station_column = col
                break
        
        # Detect location columns (lat/lon)
        for col, col_lower in columns_lower.items():
            if any(pattern in col_lower for pattern in self.LATITUDE_PATTERNS):
                self.result.location_columns.append(col)
            elif any(pattern in col_lower for pattern in self.LONGITUDE_PATTERNS):
                self.result.location_columns.append(col)
        
        # Detect speed column
        for col, col_lower in columns_lower.items():
            if any(pattern in col_lower for pattern in self.SPEED_PATTERNS):
                self.result.speed_column = col
                break
        
        # Detect status column
        for col, col_lower in columns_lower.items():
            if any(pattern in col_lower for pattern in self.STATUS_PATTERNS):
                self.result.status_column = col
                break
    
    def _detect_entities(self, df: pd.DataFrame) -> None:
        """Count unique entities in the dataset."""
        # Count trains
        if self.result.train_id_column:
            self.result.train_count = df[self.result.train_id_column].nunique()
        
        # Count stations
        if self.result.station_column:
            self.result.station_count = df[self.result.station_column].nunique()
        
        # Estimate routes (simplified)
        if self.result.train_id_column and self.result.station_column:
            # Group by train and count unique station sequences
            self.result.route_count = df.groupby(self.result.train_id_column)[self.result.station_column].nunique().sum()
    
    def _determine_dataset_type(self, df: pd.DataFrame) -> None:
        """Determine what type of railway dataset this is."""
        has_timestamp = self.result.timestamp_column is not None
        has_train_id = self.result.train_id_column is not None
        has_location = len(self.result.location_columns) >= 2
        has_station = self.result.station_column is not None
        has_speed = self.result.speed_column is not None
        
        if has_timestamp and has_train_id and has_location and has_speed:
            self.result.dataset_type = "REALTIME_TRACKING"
        elif has_timestamp and has_train_id and has_station:
            self.result.dataset_type = "SCHEDULE"
        elif has_station and 'route' in str(df.columns).lower():
            self.result.dataset_type = "NETWORK_TOPOLOGY"
        elif has_timestamp and (has_train_id or has_station):
            self.result.dataset_type = "HISTORICAL_LOG"
        else:
            self.result.dataset_type = "UNKNOWN"
            self.result.warnings.append("Could not determine dataset type. Please verify column names.")
    
    def _calculate_data_quality(self, df: pd.DataFrame) -> None:
        """Calculate overall data quality score."""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        # Adjust for detected columns
        detected_columns = sum([
            self.result.train_id_column is not None,
            self.result.timestamp_column is not None,
            self.result.station_column is not None,
            len(self.result.location_columns) > 0,
            self.result.speed_column is not None
        ])
        
        column_score = (detected_columns / 5) * 100
        
        # Combined score
        self.result.data_quality = (completeness * 0.7 + column_score * 0.3)
    
    def _extract_time_range(self, df: pd.DataFrame) -> None:
        """Extract time range from dataset."""
        if self.result.timestamp_column:
            try:
                df_time = pd.to_datetime(df[self.result.timestamp_column], errors='coerce')
                self.result.start_time = df_time.min()
                self.result.end_time = df_time.max()
            except Exception as e:
                self.result.warnings.append(f"Could not parse timestamps: {str(e)}")
    
    def _validate_data(self, df: pd.DataFrame) -> None:
        """Validate data and report issues."""
        # Check for missing critical columns
        if not self.result.train_id_column:
            self.result.issues.append("No train ID column detected. Please ensure column contains 'train' or 'id'")
        
        if not self.result.timestamp_column and self.result.dataset_type != "NETWORK_TOPOLOGY":
            self.result.warnings.append("No timestamp column detected. Time-based analysis will be limited.")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            self.result.warnings.append(f"Found {duplicates} duplicate rows")
        
        # Check data quality threshold
        if self.result.data_quality < 70:
            self.result.issues.append(f"Data quality is low ({self.result.data_quality:.1f}%). Consider cleaning the dataset.")
    
    def get_summary(self) -> str:
        """Get human-readable summary of analysis."""
        summary = []
        summary.append(f"📊 Dataset Analysis Summary")
        summary.append(f"=" * 50)
        summary.append(f"Format: {self.result.file_format}")
        summary.append(f"Type: {self.result.dataset_type}")
        summary.append(f"Rows: {self.result.total_rows:,}")
        summary.append(f"Columns: {self.result.total_columns}")
        summary.append(f"Data Quality: {self.result.data_quality:.1f}%")
        summary.append("")
        
        summary.append(f"🚂 Detected Entities:")
        summary.append(f"  - Trains: {self.result.train_count}")
        summary.append(f"  - Stations: {self.result.station_count}")
        summary.append(f"  - Routes: {self.result.route_count}")
        summary.append("")
        
        if self.result.start_time and self.result.end_time:
            summary.append(f"📅 Time Range:")
            summary.append(f"  - Start: {self.result.start_time}")
            summary.append(f"  - End: {self.result.end_time}")
            summary.append("")
        
        if self.result.issues:
            summary.append(f"❌ Issues Found:")
            for issue in self.result.issues:
                summary.append(f"  - {issue}")
            summary.append("")
        
        if self.result.warnings:
            summary.append(f"⚠️ Warnings:")
            for warning in self.result.warnings:
                summary.append(f"  - {warning}")
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test with sample data
    print("\n" + "="*60)
    print("Smart Dataset Analyzer - Test")
    print("="*60 + "\n")
    
    # Create sample dataset
    sample_data = pd.DataFrame({
        'train_id': ['T001', 'T001', 'T002', 'T002'],
        'timestamp': ['2024-01-01 10:00', '2024-01-01 11:00', '2024-01-01 10:30', '2024-01-01 11:30'],
        'station': ['Mumbai', 'Delhi', 'Chennai', 'Bangalore'],
        'speed': [80, 85, 75, 82],
        'status': ['ON_TIME', 'DELAYED', 'ON_TIME', 'ON_TIME']
    })
    
    analyzer = SmartDatasetAnalyzer()
    result = analyzer.analyze(dataframe=sample_data)
    
    print(analyzer.get_summary())
