"""
Global configuration settings for the railway system.
"""

# Simulation settings
SIMULATION_TIME_STEP = 1.0  # seconds

# Track settings
TRACK_IDS = ["P1", "P2", "P3"]  # Platform track IDs
MIN_CLEARANCE_TIME = 120  # seconds - minimum time between trains on same track

# Signal settings
SIGNAL_YELLOW_ADVANCE_TIME = 60  # seconds - when to show yellow before green

# Gate settings
GATE_DANGER_ZONE = 500  # meters - distance at which gates must be closed
GATE_CLOSE_ADVANCE_TIME = 60  # seconds - when to start closing gates

# ETA prediction settings
ETA_CONFIDENCE_THRESHOLD = 0.7  # minimum confidence for predictions
DEFAULT_MODEL = "random_forest"  # or "linear_regression"

# Logging
LOG_DIRECTORY = "data/logs"
LOG_LEVEL = "INFO"
