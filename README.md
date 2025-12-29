# Railway Digital Twin System - Final Project Documentation

## Project Overview
**AI-Driven Digital Twin–Based Real-Time Railway Interlock and Signal Logic Verifier**

A software-first, simulation-based academic project that demonstrates safety-critical system design using Digital Twin architecture for railway operations.

## System Architecture

### Core Components

1. **Train Movement Simulator** (`src/simulation/`)
   - Simulates multiple trains moving toward station
   - Time-step based position updates
   - Speed tracking and history

2. **ETA Prediction Module** (`src/ai/`)
   - Machine Learning models (Linear Regression, Random Forest)
   - Synthetic training data generation
   - Confidence scoring for predictions

3. **Track Occupancy Manager** (`src/railway/track_manager.py`)
   - Track state management (FREE, RESERVED, OCCUPIED, CLEARING)
   - Automatic track allocation
   - Conflict detection

4. **Digital Twin Safety Verifier** (`src/digital_twin/`)
   - **Core Safety Module**
   - Virtual replica of entire system
   - Simulates all decisions before execution
   - Enforces safety rules
   - Blocks unsafe operations

5. **Signal & Gate Controllers** (`src/railway/`)
   - Signal management (RED, YELLOW, GREEN)
   - Gate management (OPEN, CLOSING, CLOSED)
   - Integrated with Digital Twin verification
   - Station Master override capability

6. **Station Master Dashboard** (`dashboard/app.py`)
   - Interactive Streamlit UI
   - Real-time monitoring
   - Manual controls
   - Event logging and audit trail

## Safety Rules

### Track Allocation
- ✅ Only one train per track
- ✅ Track must be FREE before RESERVED
- ✅ Minimum clearance time between trains

### Signal Logic
- ✅ Signal GREEN only if track RESERVED
- ✅ Signal RED if track OCCUPIED
- ✅ Default state: RED (fail-safe)

### Gate Logic
- ✅ Gate opens only if no train in danger zone (<500m)
- ✅ Auto-close when train approaches
- ✅ Default state: CLOSED (fail-safe)

### Digital Twin Verification
- ✅ All decisions simulated before execution
- ✅ Unsafe operations automatically blocked
- ✅ Complete audit trail maintained

## Technology Stack

- **Language**: Python 3.8+
- **ML Framework**: scikit-learn
- **Dashboard**: Streamlit
- **Data Processing**: NumPy, Pandas
- **Visualization**: Matplotlib, Plotly

## Project Structure

```
Digital Twin–Based Railway/
├── config/                 # Configuration and safety rules
├── src/
│   ├── simulation/        # Train simulation
│   ├── ai/                # ETA prediction
│   ├── railway/           # Track, signal, gate controllers
│   ├── digital_twin/      # Safety verifier (CORE)
│   ├── logging/           # Event logging
│   └── utils/             # Utilities
├── dashboard/             # Streamlit dashboard
├── data/
│   ├── models/            # Trained ML models
│   ├── logs/              # Event logs
│   └── datasets/          # Training data
├── tests/                 # Unit tests
├── examples/              # Demo scripts
├── docs/                  # Documentation
└── requirements.txt       # Dependencies
```

## Running the System

### 1. Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python tests/test_simulation.py
python tests/test_track_manager.py
python tests/test_digital_twin.py
```

### 3. Run Demos
```bash
# Train simulation demo
python examples/demo_simulation.py

# ETA prediction demo
python examples/demo_eta_prediction.py

# Complete integration demo
python examples/demo_integration.py
```

### 4. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

## Key Features

### 1. Software-Only Simulation
- No hardware dependencies
- Fully deterministic
- Repeatable scenarios

### 2. Explainable AI
- Linear Regression (baseline)
- Random Forest (primary)
- Feature importance analysis
- Confidence scoring

### 3. Digital Twin Architecture
- Virtual replica of entire system
- Decision simulation before execution
- Safety rule enforcement
- Conflict detection

### 4. Human-in-the-Loop
- Station Master dashboard
- Manual override capability
- Complete audit trail
- Emergency controls

## Academic Evaluation Criteria

✅ **Functional Requirements**
- Multiple train simulation
- ETA prediction with >85% accuracy
- Track conflict prevention
- 100% Digital Twin verification coverage
- Interactive dashboard

✅ **Safety Requirements**
- Zero unsafe signal changes
- Zero track conflicts
- Zero gate opening violations
- All decisions verified

✅ **Code Quality**
- Modular architecture
- Clear documentation
- Comprehensive tests
- Review-ready structure

## Development Log

See `docs/development_log.md` for complete development history with timestamps and detailed progress tracking.

## Future Enhancements (Out of Scope)

- Real railway protocol integration (ERTMS, ETCS)
- Hardware sensor integration
- Multi-station networks
- Deep learning models
- Production-scale optimization

## License

Academic Project - Educational Use Only

## Contact

For questions or academic review, refer to project documentation.
