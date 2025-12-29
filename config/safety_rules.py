"""
Safety rules for the railway system.
All decisions must comply with these rules.
"""

SAFETY_RULES = {
    # Track occupancy rules
    "track_occupancy": {
        "max_trains_per_track": 1,
        "min_clearance_time": 120,  # seconds
        "allow_reservation_if_occupied": False,
    },
    
    # Signal control rules
    "signal_logic": {
        "red_if_track_occupied": True,
        "green_requires_track_reserved": True,
        "yellow_advance_time": 60,  # seconds
        "default_state": "RED",
    },
    
    # Gate control rules
    "gate_logic": {
        "danger_zone_distance": 500,  # meters
        "close_advance_time": 60,  # seconds
        "open_only_if_all_clear": True,
        "default_state": "CLOSED",
    },
    
    # Digital twin verification
    "digital_twin": {
        "verify_all_commands": True,
        "block_on_unsafe": True,
        "log_all_decisions": True,
        "simulation_required": True,
    },
    
    # Track allocation rules
    "track_allocation": {
        "require_eta_prediction": True,
        "min_eta_confidence": 0.7,
        "prevent_conflicts": True,
        "reserve_in_advance": True,
    }
}


def validate_track_allocation(track_state: str, has_conflict: bool) -> bool:
    """
    Validate if track allocation is safe.
    
    Args:
        track_state: Current track state
        has_conflict: Whether there's a conflict
        
    Returns:
        True if allocation is safe
    """
    if track_state != "FREE":
        return False
    if has_conflict:
        return False
    return True


def validate_signal_change(new_state: str, track_state: str) -> bool:
    """
    Validate if signal state change is safe.
    
    Args:
        new_state: Proposed signal state
        track_state: Current track state
        
    Returns:
        True if signal change is safe
    """
    rules = SAFETY_RULES["signal_logic"]
    
    if new_state == "GREEN":
        # Green only if track is reserved
        if rules["green_requires_track_reserved"]:
            return track_state == "RESERVED"
    
    if new_state == "RED":
        # Red is always safe
        return True
    
    if new_state == "YELLOW":
        # Yellow is transitional, generally safe
        return True
    
    return False


def validate_gate_opening(nearest_train_distance: float) -> bool:
    """
    Validate if gate can be opened safely.
    
    Args:
        nearest_train_distance: Distance to nearest train in meters
        
    Returns:
        True if gate can be opened
    """
    danger_zone = SAFETY_RULES["gate_logic"]["danger_zone_distance"]
    
    # Gate can only open if no train in danger zone
    return nearest_train_distance > danger_zone
