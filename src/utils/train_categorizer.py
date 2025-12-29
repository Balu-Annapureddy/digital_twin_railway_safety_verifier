"""
Train Categorizer - Categorize trains by operational status.
This is a UTILITY module - does not affect safety logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import List, Dict


class TrainCategorizer:
    """
    Categorizes trains by operational status.
    
    Categories:
    - INCOMING: Approaching station (position > 0)
    - ON_PLATFORM: Currently on platform (track OCCUPIED)
    - DEPARTED: Cleared from system
    
    ⚠️ READ-ONLY categorization - does not control logic.
    """
    
    @staticmethod
    def categorize_train(train_state: Dict, track_states: List[Dict]) -> str:
        """
        Categorize a single train.
        
        Args:
            train_state: Train state dictionary
            track_states: List of all track states
            
        Returns:
            Category: INCOMING, ON_PLATFORM, or DEPARTED
        """
        train_id = train_state.get('id')
        position = train_state.get('position', 0)
        
        # Check if train is on a platform
        for track in track_states:
            if track.get('allocated_to') == train_id and track.get('state') == 'OCCUPIED':
                return 'ON_PLATFORM'
        
        # Check if train is approaching
        if position > 0:
            return 'INCOMING'
        
        # Train has departed or cleared
        return 'DEPARTED'
    
    @staticmethod
    def categorize_all_trains(train_states: List[Dict], track_states: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize all trains.
        
        Args:
            train_states: List of train states
            track_states: List of track states
            
        Returns:
            Dictionary with categories as keys and train lists as values
        """
        categories = {
            'INCOMING': [],
            'ON_PLATFORM': [],
            'DEPARTED': []
        }
        
        for train in train_states:
            category = TrainCategorizer.categorize_train(train, track_states)
            categories[category].append(train)
        
        return categories
    
    @staticmethod
    def get_train_status_emoji(category: str) -> str:
        """
        Get emoji for train status.
        
        Args:
            category: Train category
            
        Returns:
            Emoji string
        """
        emojis = {
            'INCOMING': '🚂',
            'ON_PLATFORM': '🚉',
            'DEPARTED': '✅'
        }
        return emojis.get(category, '❓')
    
    @staticmethod
    def get_train_status_color(category: str) -> str:
        """
        Get color for train status.
        
        Args:
            category: Train category
            
        Returns:
            Color name
        """
        colors = {
            'INCOMING': 'blue',
            'ON_PLATFORM': 'orange',
            'DEPARTED': 'green'
        }
        return colors.get(category, 'gray')


if __name__ == "__main__":
    # Test categorizer
    print("\nTrain Categorizer Test\n")
    
    # Sample data
    trains = [
        {'id': 'T001', 'position': 5.0},
        {'id': 'T002', 'position': 0.0},
    ]
    
    tracks = [
        {'track_id': 'P1', 'state': 'OCCUPIED', 'allocated_to': 'T002'},
        {'track_id': 'P2', 'state': 'FREE', 'allocated_to': None},
    ]
    
    categories = TrainCategorizer.categorize_all_trains(trains, tracks)
    
    for category, train_list in categories.items():
        emoji = TrainCategorizer.get_train_status_emoji(category)
        print(f"{emoji} {category}: {len(train_list)} trains")
