"""
Event Logger - Logs all system events for audit trail.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List
from datetime import datetime
import json


class EventLogger:
    """
    Logs all system events for monitoring and audit.
    """
    
    def __init__(self, log_file: str = None):
        """
        Initialize event logger.
        
        Args:
            log_file: Path to log file (optional)
        """
        self.events: List[Dict] = []
        self.log_file = log_file
        
    def log_event(
        self,
        event_type: str,
        entity_id: str,
        action: str,
        result: str,
        details: str = ""
    ) -> None:
        """
        Log an event.
        
        Args:
            event_type: Type of event (TRAIN, TRACK, SIGNAL, GATE, VERIFICATION)
            entity_id: ID of entity involved
            action: Action taken
            result: Result (SUCCESS, FAILURE, BLOCKED)
            details: Additional details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "entity_id": entity_id,
            "action": action,
            "result": result,
            "details": details
        }
        
        self.events.append(event)
        
        # Write to file if specified
        if self.log_file:
            self._write_to_file(event)
    
    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """
        Get most recent events.
        
        Args:
            count: Number of events to retrieve
            
        Returns:
            List of recent events
        """
        return self.events[-count:]
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """
        Get events by type.
        
        Args:
            event_type: Type of event to filter
            
        Returns:
            List of matching events
        """
        return [e for e in self.events if e['type'] == event_type]
    
    def get_events_by_entity(self, entity_id: str) -> List[Dict]:
        """
        Get events for specific entity.
        
        Args:
            entity_id: Entity ID to filter
            
        Returns:
            List of matching events
        """
        return [e for e in self.events if e['entity_id'] == entity_id]
    
    def clear_events(self) -> None:
        """Clear all logged events."""
        self.events.clear()
    
    def _write_to_file(self, event: Dict) -> None:
        """Write event to log file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"EventLogger(events={len(self.events)})"
