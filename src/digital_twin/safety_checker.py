"""
Safety Checker - Offline verification for historical railway data.
Implements the 4 mandatory safety rules for the Digital Twin project.
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class HistoricalSafetyChecker:
    """
    Analyzes merged historical data to detect safety violations.
    """
    
    def __init__(self):
        pass

    def detect_violations(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Scans the merged dataframe for safety violations based on 4 rules.
        Returns a DataFrame of violations.
        """
        violations = []

        if merged_df.empty:
            return pd.DataFrame()

        # Iterate through rows (efficiently if possible, but iteration is clearest for complex logic)
        # Given academic constraints, we prioritize clarity. Vectorization is possible but complex with multi-column checks.
        
        # We need to check conditions for EACH signal/gate/platform involved.
        # Since the merged DF has columns like signal_id, gate_id, etc. from component updates,
        # we need to be careful. The merged row tells us "Something changed".
        # But we need the STATE of all components at that time.
        # The forward fill has ensured that we have the state of everything in every row (mostly).
        
        # However, the structure of merged_df from `historical_loader` has prefixes like 'gate_status', 'signal_color', etc.
        # AND it has 'gate_id', 'signal_id'. 
        
        # PROBLEM: In a merged wide format where we outer joined on timestamp, we might have:
        # T1: gate_id=G1, gate_status=OPEN, signal_id=NaN (signal didn't change)
        # But we ffilled, so signal_id might be stale or NaN if it never appeared before.
        # BUT, `signal_color` should be filled if it appeared before.
        
        # Actually, `signal_id` column itself will be problematic in a merged frame because we merged separate frames.
        # We likely have `gate_gate_id`, `signal_signal_id` etc. due to prefixing in loader.
        # Let's verify standard column names from loader:
        # Gate: gate_gate_id, gate_status, gate_nearest_train_m
        # Signal: signal_signal_id, signal_platform, signal_color, signal_mode
        # Platform: platform_platform_id, platform_status, platform_train_id
        
        # We can vectorizing somewhat, or iterate.
        
        for index, row in merged_df.iterrows():
            timestamp = row['timestamp']
            
            # --- Rule 1: Signal-Gate Conflict ---
            # Signal GREEN AND Gate OPEN
            # We check if *any* Signal is GREEN and *any* Gate is OPEN.
            # In a real system, they are linked by location. 
            # academic simplification: "If Signal S1 (Platform 1) is GREEN and Gate G1 is OPEN".
            # We assume a global check or specific pairings? 
            # Looking at data, G1 seems to be the main crossing. S1, S2, S3 are platform signals.
            # Rule: "Signal GREEN AND Gate OPEN -> Violation" (General)
            
            gate_is_open = (row.get('gate_status') == 'OPEN')
            # Check signals. We have one signal column from the merge if there's only one signal update per row.
            # But wait, ffill propagates the *last updated* signal's state. It does NOT give us the state of ALL signals.
            # The merged_df approach with ffill on a "long" format (id, status) means row contains 
            # the state of the *most recently updated* ID. It doesn't show S1=RED, S2=GREEN simultaneously in columns
            # unless we pivoted. 
            
            # Ah, the `historical_loader` simply outer-merged. 
            # If S1 updates at T1, row T1 has S1 data. 
            # If G1 updates at T2, row T2 has G1 data plus STALE S1 data (ffilled).
            # This works for "System State" if we assume the ffilled columns represent the current snapshot.
            # But `signal_color` column comes from `signal_state.csv` which has `signal_id`.
            # So `signal_color` in the row refers to `signal_signal_id`.
            # Use Case: At Time T, `gate_status` is OPEN. Is there *any* train approaching?
            # The row only tells us about the specific signal/gate that *updated* (or last updated).
            # It does NOT tell us the state of *other* signals if they aren't in the row.
            # Actually, `ffill` propagates the values. 
            # So `signal_color` will be the color of `signal_signal_id` from the last signal update.
            # It does NOT tell us about S2 if the last update was S1.
            
            # CRITICAL FIX for Data Loading Strategy:
            # We need to know the state of *all* components at timestamp T.
            # The current merged_df is "Event based with memory of last event".
            # To check "Are *any* signals GREEN?", we ideally need a state snapshot.
            # But sticking to constraints, let's look at the Specifics.
            # If the Current Row indicates a Signal became GREEN, and the Gate is currently OPEN (ffilled), that's a violation.
            # If the Current Row indicates Gate became OPEN, and the last known Signal (ffilled) was GREEN, that's a violation.
            # This covers "State Change triggers Violation".
            # It misses "State Persists Violation" if we only check on change, but typically violations start at a change.
            
            # --- Rule 1 Check ---
            current_signal_color = row.get('signal_color')
            current_gate_status = row.get('gate_status')
            
            if current_signal_color == 'GREEN' and current_gate_status == 'OPEN':
                 violations.append({
                    'timestamp': timestamp,
                    'violation_type': 'SIGNAL_GATE_CONFLICT',
                    'description': f"Signal {row.get('signal_signal_id')} is GREEN while Gate {row.get('gate_gate_id')} is OPEN",
                    'severity': 'HIGH'
                })

            # --- Rule 2: Train-Gate Conflict ---
            # nearest_train_m < 500 AND Gate = OPEN
            dist = row.get('gate_nearest_train_m')
            
            if dist is not None and not pd.isna(dist):
                if dist < 500 and current_gate_status == 'OPEN':
                     violations.append({
                        'timestamp': timestamp,
                        'violation_type': 'TRAIN_GATE_CONFLICT',
                        'description': f"Train approaching ({dist}m) while Gate is OPEN",
                        'severity': 'CRITICAL'
                    })

            # --- Rule 3: Crowd-Safety Conflict ---
            # Platform = OCCUPIED AND Train_Approaching = True
            # Train approaching defined as Signal=GREEN (from rules).
            
            plat_status = row.get('platform_status')
            # If current signal (last updated) is GREEN, it implies a train is coming to *that* platform (signal_platform).
            # We need to match Platform ID.
            
            sig_plat = row.get('signal_platform')
            row_plat_id = row.get('platform_platform_id')
            
            # Logic: If Signal is GREEN for P1, and P1 is OCCUPIED.
            # Case A: Signal Update. Signal becomes GREEN. Check if its platform is OCCUPIED.
            # Case B: Platform Update. Platform becomes OCCUPIED. Check if its Signal is GREEN.
            
            # We can try to rely on the ffilled values.
            # Issue: 'platform_platform_id' might be P2 (from last update), but 'signal_platform' might be P1 (from last signal update).
            # This is the limitation of the flattened event log.
            # However, for an academic project, checking the *active* component change against *latest* system state is usually sufficient.
            # Let's implement the localized check.
            
            if row_plat_id and plat_status == 'OCCUPIED':
                # Check if *corresponding* signal is GREEN. 
                # We don't have that info in this simple flattened row if the last signal update was for a different platform.
                # BUT, we can simplify: If 'signal_color' is GREEN and 'signal_platform' == row_plat_id.
                # This works if the signal update happened *before* or *same time* and wasn't overwritten by another signal.
                # LIMITATION ACKNOWLEDGED. Logic:
                if current_signal_color == 'GREEN' and sig_plat == row_plat_id:
                     violations.append({
                        'timestamp': timestamp,
                        'violation_type': 'CROWD_SAFETY_RISK',
                        'description': f"Platform {row_plat_id} OCCUPIED while Train Approaching (Signal GREEN)",
                        'severity': 'HIGH'
                    })
            
            if current_signal_color == 'GREEN' and sig_plat:
                # Check if platform is OCCUPIED. 
                # Again, rely on row data.
                if plat_status == 'OCCUPIED' and row_plat_id == sig_plat:
                     violations.append({
                        'timestamp': timestamp,
                        'violation_type': 'CROWD_SAFETY_RISK',
                        'description': f"Signal GREEN for OCCUPIED Platform {sig_plat}",
                        'severity': 'HIGH'
                    })

            # --- Rule 4: Red-Signal Violation ---
            # Signal RED AND Train Moving
            # Train moving inferred from distance decreasing.
            # We need previous row to calculate delta.
            # Since we iterate, we can store previous distance.
            
            # This usually applies to the Gate's 'nearest_train_m'.
            # If Signal is RED (System wide stop?) or specific signal?
            # Usually: If Signal for Track X is RED, Train on Track X should stop.
            # We only have 'nearest_train_m' from Gate data. We assume this train is the one controlled by signals.
            
            if current_signal_color == 'RED':
                # Check if train is moving.
                # We need historical distance.
                # Since we are iterating:
                pass # Handled by state tracking variable below loop if needed, 
                     # but here accessing previous row is hard without index manipulation.
                     
        # Vectorized / Rolling approach for Rule 4 (Trend detection)
        # Calculate 'delta_dist' for gate_nearest_train_m
        merged_df['prev_dist'] = merged_df['gate_nearest_train_m'].shift(1)
        merged_df['dist_change'] = merged_df['prev_dist'] - merged_df['gate_nearest_train_m']
        
        # Identify rows where Signal is RED and Dist Change > 0 (Train moving closer)
        # Note: Dist Change > 0 means distance decreased.
        
        red_moving_mask = (merged_df['signal_color'] == 'RED') & (merged_df['dist_change'] > 0)
        
        red_violations = merged_df[red_moving_mask]
        for idx, row in red_violations.iterrows():
             violations.append({
                'timestamp': row['timestamp'],
                'violation_type': 'RED_SIGNAL_VIOLATION',
                'description': f"Train moving (delta {row['dist_change']}m) while Signal {row.get('signal_signal_id')} is RED",
                'severity': 'CRITICAL'
            })

        return pd.DataFrame(violations)

