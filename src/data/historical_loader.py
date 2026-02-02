"""
Historical Data Loader - Load and query historical CSV data for replay.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class HistoricalDataLoader:
    """
    Loads and serves historical data from CSV logs.
    Supports querying state at specific timestamps.
    """
    
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir
        self.gate_df: Optional[pd.DataFrame] = None
        self.platform_df: Optional[pd.DataFrame] = None
        self.signal_df: Optional[pd.DataFrame] = None
        self.event_log_df: Optional[pd.DataFrame] = None
        self.min_time: Optional[datetime] = None
        self.max_time: Optional[datetime] = None
        self.is_loaded = False

    def load_data(self) -> bool:
        """Loads all CSV files from the data directory."""
        try:
            # Load Gate Status
            gate_path = os.path.join(self.data_dir, 'gate_status.csv')
            if os.path.exists(gate_path):
                self.gate_df = pd.read_csv(gate_path)
                self.gate_df['timestamp'] = pd.to_datetime(self.gate_df['timestamp'])
                self.gate_df = self.gate_df.sort_values('timestamp')
            
            # Load Platform Status
            platform_path = os.path.join(self.data_dir, 'platform_status.csv')
            if os.path.exists(platform_path):
                self.platform_df = pd.read_csv(platform_path)
                self.platform_df['timestamp'] = pd.to_datetime(self.platform_df['timestamp'])
                self.platform_df = self.platform_df.sort_values('timestamp')

            # Load Signal State
            signal_path = os.path.join(self.data_dir, 'signal_state.csv')
            if os.path.exists(signal_path):
                self.signal_df = pd.read_csv(signal_path)
                self.signal_df['timestamp'] = pd.to_datetime(self.signal_df['timestamp'])
                self.signal_df = self.signal_df.sort_values('timestamp')
                
            # Load Event Log
            event_path = os.path.join(self.data_dir, 'event_log.csv')
            if os.path.exists(event_path):
                self.event_log_df = pd.read_csv(event_path)
                self.event_log_df['timestamp'] = pd.to_datetime(self.event_log_df['timestamp'])
                self.event_log_df = self.event_log_df.sort_values('timestamp')

            # Determine time range
            timestamps = []
            for df in [self.gate_df, self.platform_df, self.signal_df, self.event_log_df]:
                if df is not None and not df.empty:
                    timestamps.extend([df['timestamp'].min(), df['timestamp'].max()])
            
            if timestamps:
                self.min_time = min(timestamps)
                self.max_time = max(timestamps)
                self.is_loaded = True
                return True
            else:
                return False

        except Exception as e:
            print(f"Error loading historical data: {e}")
            return False

    def load_from_bytes(self, gate_file, platform_file, signal_file, event_file) -> bool:
        """Loads data from file-like objects (e.g., Streamlit uploads)."""
        try:
            if gate_file:
                self.gate_df = pd.read_csv(gate_file)
                self.gate_df['timestamp'] = pd.to_datetime(self.gate_df['timestamp'])
                self.gate_df = self.gate_df.sort_values('timestamp')
            
            if platform_file:
                self.platform_df = pd.read_csv(platform_file)
                self.platform_df['timestamp'] = pd.to_datetime(self.platform_df['timestamp'])
                self.platform_df = self.platform_df.sort_values('timestamp')

            if signal_file:
                self.signal_df = pd.read_csv(signal_file)
                self.signal_df['timestamp'] = pd.to_datetime(self.signal_df['timestamp'])
                self.signal_df = self.signal_df.sort_values('timestamp')
                
            if event_file:
                self.event_log_df = pd.read_csv(event_file)
                self.event_log_df['timestamp'] = pd.to_datetime(self.event_log_df['timestamp'])
                self.event_log_df = self.event_log_df.sort_values('timestamp')

            # Determine time range
            timestamps = []
            for df in [self.gate_df, self.platform_df, self.signal_df, self.event_log_df]:
                if df is not None and not df.empty:
                    timestamps.extend([df['timestamp'].min(), df['timestamp'].max()])
            
            if timestamps:
                self.min_time = min(timestamps)
                self.max_time = max(timestamps)
                self.is_loaded = True
                return True
            else:
                return False

        except Exception as e:
            print(f"Error loading uploaded data: {e}")
            return False

    def get_state_at_time(self, query_time: datetime) -> Dict:
        """
        Returns the system state at the specified time.
        Uses 'asof' logic to get the most recent record before or at query_time.
        """
        if not self.is_loaded:
            return {}

        state = {
            'gates': [],
            'platforms': [],
            'signals': [],
            'active_events': []
        }

        # Gate State
        if self.gate_df is not None:
            # We want the latest state for EACH gate_id provided it's <= query_time
            # Sort by time first (done in load), then filter
            valid_rows = self.gate_df[self.gate_df['timestamp'] <= query_time]
            if not valid_rows.empty:
                # Group by gate_id and take the last one (most recent)
                latest_gates = valid_rows.groupby('gate_id').last().reset_index()
                state['gates'] = latest_gates.to_dict('records')

        # Platform State
        if self.platform_df is not None:
            valid_rows = self.platform_df[self.platform_df['timestamp'] <= query_time]
            if not valid_rows.empty:
                latest_platforms = valid_rows.groupby('platform_id').last().reset_index()
                state['platforms'] = latest_platforms.to_dict('records')

        # Signal State
        if self.signal_df is not None:
            valid_rows = self.signal_df[self.signal_df['timestamp'] <= query_time]
            if not valid_rows.empty:
                latest_signals = valid_rows.groupby('signal_id').last().reset_index()
                state['signals'] = latest_signals.to_dict('records')

        return state

    def get_time_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        return self.min_time, self.max_time

    def get_merged_data(self) -> pd.DataFrame:
        """
        Merges all loaded DataFrames into a single timeline.
        Every row represents a system state change.
        Forward-fills missing values to represent continuous state.
        """
        if not self.is_loaded:
            return pd.DataFrame()

        dfs_to_merge = []
        
        # Prepare Gate Data
        if self.gate_df is not None:
            gate_prep = self.gate_df.copy()
            gate_prep = gate_prep.add_prefix('gate_')
            gate_prep = gate_prep.rename(columns={'gate_timestamp': 'timestamp'})
            dfs_to_merge.append(gate_prep)

        # Prepare Platform Data
        if self.platform_df is not None:
            plat_prep = self.platform_df.copy()
            plat_prep = plat_prep.add_prefix('platform_')
            plat_prep = plat_prep.rename(columns={'platform_timestamp': 'timestamp'})
            dfs_to_merge.append(plat_prep)

        # Prepare Signal Data
        if self.signal_df is not None:
            sig_prep = self.signal_df.copy()
            sig_prep = sig_prep.add_prefix('signal_')
            sig_prep = sig_prep.rename(columns={'signal_timestamp': 'timestamp'})
            dfs_to_merge.append(sig_prep)
            
        if not dfs_to_merge:
            return pd.DataFrame()

        # Merge all dataframes on timestamp using outer join to preserve all events
        merged_df = dfs_to_merge[0]
        for df in dfs_to_merge[1:]:
            merged_df = pd.merge(merged_df, df, on='timestamp', how='outer')

        # Sort by timestamp
        merged_df = merged_df.sort_values('timestamp')

        # Forward fill to propagate state
        # (e.g., if signal changes at T1, it remains in that state at T2 when gate changes)
        merged_df = merged_df.ffill()
        
        # Fill remaining NaNs (initial state) with defaults if needed, or leave as is
        # For safety checks, we check for presence of data.
        
        return merged_df
