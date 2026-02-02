"""
Test Safety Logic - Verifies the 4 mandatory safety rules.
"""

import unittest
import pandas as pd
import sys
import os

# Adjust path to find src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.digital_twin.safety_checker import HistoricalSafetyChecker

class TestSafetyLogic(unittest.TestCase):
    
    def setUp(self):
        self.checker = HistoricalSafetyChecker()
        
    def test_rule_1_signal_gate_conflict(self):
        """Rule 1: Signal GREEN and Gate OPEN -> Violation"""
        data = pd.DataFrame([{
            'timestamp': pd.Timestamp('2026-01-01 10:00:00'),
            'signal_color': 'GREEN',
            'gate_status': 'OPEN',
            'gate_nearest_train_m': 1000,
            'signal_signal_id': 'S1',
            'gate_gate_id': 'G1'
        }])
        
        violations = self.checker.detect_violations(data)
        self.assertFalse(violations.empty)
        self.assertEqual(violations.iloc[0]['violation_type'], 'SIGNAL_GATE_CONFLICT')

    def test_rule_2_train_gate_conflict(self):
        """Rule 2: Train < 500m and Gate OPEN -> Violation"""
        data = pd.DataFrame([{
            'timestamp': pd.Timestamp('2026-01-01 10:00:00'),
            'signal_color': 'RED',
            'gate_status': 'OPEN',
            'gate_nearest_train_m': 400, # < 500
            'signal_signal_id': 'S1',
            'gate_gate_id': 'G1'
        }])
        
        violations = self.checker.detect_violations(data)
        self.assertFalse(violations.empty)
        self.assertTrue('TRAIN_GATE_CONFLICT' in violations['violation_type'].values)

    def test_rule_3_crowd_safety(self):
        """Rule 3: Platform OCCUPIED and Signal GREEN -> Violation"""
        data = pd.DataFrame([{
            'timestamp': pd.Timestamp('2026-01-01 10:00:00'),
            'signal_color': 'GREEN',
            'signal_platform': 'P1',
            'platform_status': 'OCCUPIED',
            'platform_platform_id': 'P1',
            'gate_status': 'CLOSED'
        }])
        
        violations = self.checker.detect_violations(data)
        self.assertFalse(violations.empty)
        self.assertTrue('CROWD_SAFETY_RISK' in violations['violation_type'].values)

    def test_rule_4_red_signal_violation(self):
        """Rule 4: Signal RED and Train Moving -> Violation"""
        # Need two rows to show movement
        data = pd.DataFrame([
            {
                'timestamp': pd.Timestamp('2026-01-01 10:00:00'),
                'signal_color': 'RED',
                'gate_nearest_train_m': 1000,
                'signal_signal_id': 'S1'
            },
            {
                'timestamp': pd.Timestamp('2026-01-01 10:00:01'),
                'signal_color': 'RED',
                'gate_nearest_train_m': 900, # Moving closer (100m delta)
                'signal_signal_id': 'S1'
            }
        ])
        
        violations = self.checker.detect_violations(data)
        self.assertFalse(violations.empty)
        self.assertEqual(violations.iloc[0]['violation_type'], 'RED_SIGNAL_VIOLATION')

if __name__ == '__main__':
    unittest.main()
