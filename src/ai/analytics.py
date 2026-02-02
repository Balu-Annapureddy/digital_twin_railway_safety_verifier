"""
Analytics Module - Calculates Key Performance Indicators and Statistical Metrics.
"""

import pandas as pd
from typing import Dict

def calculate_kpis(merged_df: pd.DataFrame, violations_df: pd.DataFrame) -> Dict:
    """
    Calculates high-level KPIs for the dashboard.
    """
    stats = {}
    
    # Total Events
    stats['total_events'] = len(merged_df)
    
    # Total Violations
    stats['total_violations'] = len(violations_df)
    
    # Violation Rate (Events per violation)
    if stats['total_events'] > 0:
        stats['violation_rate'] = f"{(stats['total_violations'] / stats['total_events']) * 100:.2f}%"
    else:
        stats['violation_rate'] = "0%"

    # Counts by Type
    if not violations_df.empty:
        stats['by_type'] = violations_df['violation_type'].value_counts().to_dict()
        stats['by_severity'] = violations_df['severity'].value_counts().to_dict()
    else:
        stats['by_type'] = {}
        stats['by_severity'] = {}
        
    return stats

def get_hourly_risk(violations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates violations by hour to show risk trends.
    """
    if violations_df.empty:
        return pd.DataFrame(columns=['hour', 'count', 'risk_score'])
    
    df = violations_df.copy()
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    
    hourly = df.groupby('hour').size().reset_index(name='count')
    
    # Simple risk score: count * 10 (arbitrary scaling for academic demo)
    hourly['risk_score'] = hourly['count'] * 10
    
    # Ensure all hours 0-23 exist? Optional, but good for charts.
    # merge with range 0-23
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly = pd.merge(all_hours, hourly, on='hour', how='left').fillna(0)
    
    return hourly
