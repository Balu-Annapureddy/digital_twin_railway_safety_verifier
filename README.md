# Railway Digital Twin System - Complete Documentation

## Project Overview
**AI-Driven Digital Twin–Based Real-Time Railway Interlock and Signal Logic Verifier**

A software-first, simulation-based academic project that demonstrates safety-critical system design using Digital Twin architecture for railway operations.

### 🎉 Enhanced Version
This system now includes **real-world features** with enhanced UI/UX while maintaining 100% safety compliance.

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

### Enhanced Features (New)

7. **Real-World Data Integration** (`src/data/`)
   - Load train schedules from CSV/JSON files
   - Data validation and fallback to simulation
   - Sample realistic Indian railway data
   - Seamless integration with existing system

8. **Enhanced Station Dashboard**
   - **Station Overview Panel**: Real-time platform statistics
   - **Train Overview Panel**: Categorized trains (Incoming/On Platform/Departed)
   - **Platform Details Panel**: Color-coded platform cards
   - **Custom CSS Styling**: Professional gradient headers and improved UX

9. **Train Categorization** (`src/utils/train_categorizer.py`)
   - Automatic categorization by operational status
   - Visual status indicators with emojis
   - Tabbed interface for easy navigation

10. **2D Visual Simulation** (`dashboard/components/visual_sim.py`)
    - Interactive Plotly-based schematic view
    - Real-time train position tracking
    - Color-coded platform tracks
    - Signal and gate indicators
    - Station boundary visualization

11. **Comprehensive Documentation**
    - Complete user guide (`docs/USER_GUIDE.md`)
    - Detailed component explanations
    - Step-by-step workflows
    - Troubleshooting guide

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
│   ├── settings.py
│   ├── safety_rules.py
│   └── station_config.py  # NEW: Station metadata
├── src/
│   ├── simulation/        # Train simulation
│   ├── ai/                # ETA prediction
│   ├── railway/           # Track, signal, gate controllers
│   ├── digital_twin/      # Safety verifier (CORE)
│   ├── logging/           # Event logging
│   ├── data/              # NEW: Real-world data integration
│   └── utils/             # Utilities (includes train_categorizer)
├── dashboard/             # Streamlit dashboard
│   ├── app.py             # Enhanced with new panels
│   └── components/        # NEW: Visual simulation component
├── data/
│   ├── models/            # Trained ML models
│   ├── logs/              # Event logs
│   ├── datasets/          # Training data
│   └── schedules/         # NEW: Sample schedule files (CSV/JSON)
├── tests/                 # Unit tests
├── examples/              # Demo scripts (includes schedule loader demo)
├── docs/                  # Documentation
│   ├── development_log.md
│   └── USER_GUIDE.md      # NEW: Comprehensive user guide
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

### Core System

#### 1. Software-Only Simulation
- No hardware dependencies
- Fully deterministic
- Repeatable scenarios

#### 2. Explainable AI
- Linear Regression (baseline)
- Random Forest (primary)
- Feature importance analysis
- Confidence scoring

#### 3. Digital Twin Architecture
- Virtual replica of entire system
- Decision simulation before execution
- Safety rule enforcement
- Conflict detection

#### 4. Human-in-the-Loop
- Station Master dashboard
- Manual override capability
- Complete audit trail
- Emergency controls

### Enhanced Features

#### 5. Real-World Data Integration
- CSV/JSON schedule loading
- Data validation and fallback
- Realistic Indian railway samples
- Seamless data layer integration

#### 6. Station-Level Awareness
- Station overview with real-time metrics
- Platform occupancy statistics
- Train categorization (Incoming/On Platform/Departed)
- Enhanced visual indicators

#### 7. 2D Visual Simulation
- Interactive schematic station layout
- Real-time train position tracking
- Color-coded platform states
- Signal and gate visualization
- Hover tooltips with detailed information

#### 8. Professional UI/UX
- Gradient station headers
- Color-coded status cards
- Tabbed interfaces
- Custom CSS styling
- Responsive layout

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

## Documentation

### Available Documentation

1. **User Guide** (`docs/USER_GUIDE.md`)
   - Complete dashboard walkthrough
   - Component explanations
   - Step-by-step workflows
   - Troubleshooting guide
   - Best practices for demonstrations

2. **Development Log** (`docs/development_log.md`)
   - Complete development history
   - Timestamped progress tracking
   - Enhancement phases documented
   - Safety compliance notes

3. **README** (this file)
   - Project overview
   - Setup instructions
   - Feature list
   - Architecture overview

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
