"""
Test Loader - Verifies merged data creation.
"""

import unittest
import pandas as pd
import sys
import os
from datetime import datetime

# Adjust path to find src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.historical_loader import HistoricalDataLoader

class TestLoader(unittest.TestCase):
    
    def test_merge_logic_empty(self):
        loader = HistoricalDataLoader()
        loader.is_loaded = True
        # Setup dummy dfs
        loader.gate_df = pd.DataFrame({'gate_timestamp': [datetime(2026,1,1,10,0,0)], 'gate_id': ['G1'], 'status': ['OPEN']})
        
        merged = loader.get_merged_data()
        self.assertFalse(merged.empty)
        self.assertIn('gate_gate_id', merged.columns) # Check prefixing

if __name__ == '__main__':
    unittest.main()
