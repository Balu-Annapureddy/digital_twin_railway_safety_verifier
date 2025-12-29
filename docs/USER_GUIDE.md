# Railway Digital Twin - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Station Overview Panel](#station-overview-panel)
5. [Station Schematic View](#station-schematic-view)
6. [Train Overview Panel](#train-overview-panel)
7. [Platform Details Panel](#platform-details-panel)
8. [System Status](#system-status)
9. [Signals & Gates Control](#signals--gates-control)
10. [Sidebar Controls](#sidebar-controls)
11. [Event Log](#event-log)
12. [Safety Features](#safety-features)
13. [Common Workflows](#common-workflows)

---

## Introduction

The **Railway Digital Twin - Station Master Dashboard** is an interactive web application for monitoring and controlling a simulated railway station. It uses **Digital Twin technology** to verify all operations before execution, ensuring 100% safety compliance.

### Key Features
- Real-time train tracking and visualization
- AI-based ETA prediction
- Digital Twin safety verification
- Interactive signal and gate controls
- Station-level awareness with multiple panels
- Complete audit trail

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Virtual environment activated
- All dependencies installed (see `requirements.txt`)

### Launching the Dashboard

1. **Activate Virtual Environment**:
   ```bash
   venv\Scripts\activate  # Windows
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

3. **Access in Browser**:
   - The dashboard will automatically open at `http://localhost:8501`
   - If not, manually navigate to the URL shown in terminal

---

## Dashboard Overview

The dashboard is divided into several key sections:

```
┌─────────────────────────────────────────────────────┐
│          STATION HEADER (Blue Gradient)             │
├─────────────────────────────────────────────────────┤
│              Station Overview Panel                 │
├──────────────────────────┬──────────────────────────┤
│                          │                          │
│   Main Content Area      │   Sidebar Controls       │
│   - Schematic View       │   - Train Management     │
│   - Train Overview       │   - Simulation Control   │
│   - Platform Details     │   - Emergency Controls   │
│   - System Status        │                          │
│   - Signals & Gates      │                          │
│                          │                          │
├─────────────────────────────────────────────────────┤
│                  Event Log                          │
└─────────────────────────────────────────────────────┘
```

---

## Station Overview Panel

**Location**: Top of the dashboard, below the station header

**Purpose**: Provides at-a-glance statistics about the station's operational status.

### Metrics Displayed

1. **Total Platforms** (📊)
   - Shows the total number of platforms at the station
   - Default: 3 platforms (P1, P2, P3)

2. **Occupied** (🔴)
   - Number of platforms currently occupied by trains
   - Red indicator shows critical status

3. **Reserved** (🟡)
   - Number of platforms reserved for incoming trains
   - Yellow indicator shows pending status

4. **Free** (🟢)
   - Number of platforms available for allocation
   - Green indicator shows available capacity

5. **Active Trains** (🚂)
   - Total number of trains currently in the system
   - Includes both approaching and on-platform trains

### What It Tells You
- **Capacity**: How many platforms are available
- **Utilization**: How busy the station is
- **Traffic**: How many trains are being managed

---

## Station Schematic View

**Location**: Below Station Overview, full width

**Purpose**: Visual representation of the station layout showing trains, platforms, signals, and gates in real-time.

### Components

#### 1. Platform Tracks (Horizontal Lines)
- **Green Line** 🟢: Platform is FREE (available)
- **Yellow Line** 🟡: Platform is RESERVED (train incoming)
- **Red Line** 🔴: Platform is OCCUPIED (train present)
- **Gray Line** ⚪: Platform is CLEARING (train departed, cleaning in progress)

**Platform Labels**: P1, P2, P3 shown on the left side

#### 2. Train Markers
- **Blue Arrow** (→): Approaching train (moving toward station)
  - Position shows distance from station
  - Arrow points in direction of travel
- **Orange Square** (■): Train on platform (stopped)
  - Positioned at center of platform

**Train Labels**: Train ID displayed above each marker (e.g., T001)

#### 3. Signal Indicators (Diamonds ◆)
- Located at platform entrance (left side)
- **Red Diamond** 🔴: Signal is RED (stop)
- **Yellow Diamond** 🟡: Signal is YELLOW (caution)
- **Green Diamond** 🟢: Signal is GREEN (proceed)

#### 4. Gate Indicators (X Marks)
- Located below platform area
- **Red X** 🔴: Gate is CLOSED (safe)
- **Orange X** 🟠: Gate is CLOSING (in progress)
- **Green X** 🟢: Gate is OPEN (pedestrian access)

#### 5. Station Boundary
- Dashed navy blue rectangle
- Light blue background
- "STATION AREA" label at top
- Represents the physical station limits (0-20 km range)

### How to Read It
1. **X-axis**: Distance in kilometers (left = station, right = far away)
2. **Y-axis**: Platform numbers (P1 at bottom, P3 at top)
3. **Hover**: Move mouse over any element to see detailed information

### Interactive Features
- **Zoom**: Scroll to zoom in/out
- **Pan**: Click and drag to move view
- **Hover**: See train position, speed, status
- **Legend**: Shows track states on the right

---

## Train Overview Panel

**Location**: Main content area, left column

**Purpose**: Detailed information about all trains, categorized by operational status.

### Three Categories (Tabs)

#### 1. 🚂 Incoming Trains
**Criteria**: Trains approaching the station (position > 0 km)

**Information Displayed**:
- **Position**: Distance from station in kilometers
- **Speed**: Current speed in kmph
- **Type**: STOPPING or NON_STOPPING
- **ETA**: Estimated time of arrival in minutes
- **Avg Speed**: Average speed during journey
- **Status**: 🟢 Approaching

**Example**:
```
Train T001
├─ Position: 5.25 km
├─ Speed: 80 kmph
├─ Type: STOPPING
├─ ETA: ~3.9 minutes
├─ Avg Speed: 80.0 kmph
└─ Status: 🟢 Approaching
```

#### 2. 🚉 On Platform Trains
**Criteria**: Trains currently on a platform (track OCCUPIED)

**Information Displayed**:
- **Platform**: Which platform the train is on (P1, P2, P3)
- **Type**: STOPPING or NON_STOPPING
- **Status**: 🟠 On Platform
- **Speed**: 0 kmph (Stopped)

**Example**:
```
Train T002 - Platform P1
├─ Platform: P1
├─ Type: STOPPING
├─ Status: 🟠 On Platform
└─ Speed: 0 kmph (Stopped)
```

#### 3. ✅ Departed Trains
**Criteria**: Trains that have cleared the system

**Information**: Departed trains are removed from active tracking to keep the system clean.

### Detailed Train Data Table
Below the tabs, a complete data table shows all active trains with:
- Train ID
- Position
- Speed
- Direction
- Train Type
- Average Speed
- Speed History

---

## Platform Details Panel

**Location**: Main content area, below Train Overview

**Purpose**: Detailed status of each platform with color-coded visual cards.

### Platform Cards

Each platform is displayed as a colored card:

#### Card Colors
- **🟢 Green**: Platform is FREE
- **🟡 Yellow**: Platform is RESERVED
- **🔴 Red**: Platform is OCCUPIED
- **⚪ Gray**: Platform is CLEARING

#### Information Shown
1. **Platform ID**: P1, P2, or P3
2. **State**: Current state (FREE/RESERVED/OCCUPIED/CLEARING)
3. **Train**: Assigned train ID (or "None" if free)
4. **ETA**: Expected arrival time in seconds (if reserved)
5. **Clearance**: Clearance time in seconds (default 120s)

**Example Card**:
```
┌─────────────────┐
│ 🟡 P1           │
│ RESERVED        │
├─────────────────┤
│ Train: T001     │
│ ETA: 234s       │
│ Clearance: 120s │
└─────────────────┘
```

### What Each State Means

- **FREE**: Platform is available for allocation
- **RESERVED**: Platform allocated to incoming train, waiting for arrival
- **OCCUPIED**: Train is currently on the platform
- **CLEARING**: Train has departed, platform being prepared for next train

---

## System Status

**Location**: Main content area, top section

**Purpose**: Real-time system metrics and statistics.

### Metrics

1. **Active Trains**
   - Number of trains currently in the system
   - Includes incoming and on-platform trains

2. **Free Tracks**
   - Number of platforms available for allocation
   - Out of total platforms (e.g., "2/3")

3. **Safety Rate**
   - Percentage of operations verified as safe
   - Should always be close to 100%
   - Calculated from Digital Twin verifications

4. **Simulation Time**
   - Total elapsed time in the simulation
   - Measured in seconds
   - Increments with each simulation step

---

## Signals & Gates Control

**Location**: Right sidebar

**Purpose**: Manual control of signals and gates with Digital Twin verification.

### Signals Section

#### Signal Display
Each signal shows:
- **Color Indicator**: 🔴 RED, 🟡 YELLOW, or 🟢 GREEN
- **Signal ID**: S1, S2, S3
- **Track ID**: Associated platform (P1, P2, P3)
- **Current State**: RED, YELLOW, or GREEN

#### Control Buttons
Three buttons per signal:
- **🔴 Button**: Change signal to RED
- **🟡 Button**: Change signal to YELLOW
- **🟢 Button**: Change signal to GREEN

#### Signal States Explained
- **RED** 🔴: Stop - Train must not proceed
- **YELLOW** 🟡: Caution - Prepare to stop
- **GREEN** 🟢: Proceed - Safe to enter platform

**⚠️ Safety Note**: Signal changes are verified by Digital Twin. Unsafe changes will be blocked automatically.

### Gates Section

#### Gate Display
Each gate shows:
- **Gate ID**: G1
- **Status**: 🟢 OPEN, 🟡 CLOSING, or 🔴 CLOSED
- **Nearest Train**: Distance to nearest train in meters

#### Control Buttons
Two buttons per gate:
- **Open**: Open the gate (pedestrian access)
- **Close**: Close the gate (train approaching)

#### Gate States Explained
- **OPEN** 🟢: Gate is open, pedestrians can cross
- **CLOSING** 🟡: Gate is in the process of closing
- **CLOSED** 🔴: Gate is closed, safe for train passage

**⚠️ Safety Note**: Gates cannot be opened if a train is within 500m (danger zone). Digital Twin will block unsafe operations.

---

## Sidebar Controls

**Location**: Left sidebar (collapsible)

**Purpose**: System controls for train management, simulation, and emergency operations.

### 1. Train Management

**Add Train Form**:
- **Train ID**: Unique identifier (auto-generated as T000, T001, etc.)
- **Initial Position**: Starting distance from station (1-20 km)
- **Initial Speed**: Starting speed (40-120 kmph)
- **Train Type**: STOPPING or NON_STOPPING

**How to Add a Train**:
1. Fill in the form fields (or use defaults)
2. Click "➕ Add Train"
3. Train appears in the system immediately
4. Event is logged in Event Log

### 2. Simulation Control

**Run Step** (▶️):
- Advances simulation by one time step
- Updates train positions
- Recalculates ETAs
- Updates all visualizations

**Reset** (🔄):
- Clears all trains from system
- Resets simulation time to 0
- Clears event log
- Returns all platforms to FREE state

**How to Run Simulation**:
1. Add one or more trains
2. Click "▶️ Run Step" repeatedly to see trains move
3. Watch the schematic view update in real-time
4. Monitor train progress in Train Overview

### 3. Emergency Controls

**Emergency Stop All** (🚨):
- Sets ALL signals to RED immediately
- Uses Station Master override (bypasses verification)
- Logs emergency action in Event Log
- Use only in critical situations

**⚠️ Warning**: Override bypasses Digital Twin verification. Use responsibly!

---

## Event Log

**Location**: Bottom of dashboard, full width

**Purpose**: Complete audit trail of all system events.

### Information Logged

Each event shows:
- **Timestamp**: When the event occurred (ISO format)
- **Type**: Event category (TRAIN, TRACK, SIGNAL, GATE, VERIFICATION, SYSTEM)
- **Entity ID**: Which entity was affected (train ID, signal ID, etc.)
- **Action**: What action was taken
- **Result**: SUCCESS, FAILURE, or BLOCKED
- **Details**: Additional information about the event

### Event Types

1. **TRAIN**: Train added, removed, or state changed
2. **TRACK**: Track allocated, occupied, cleared
3. **SIGNAL**: Signal state changed
4. **GATE**: Gate opened or closed
5. **VERIFICATION**: Digital Twin verification result
6. **SYSTEM**: System-wide actions (emergency stop, reset)

### Example Events
```
2025-12-29T12:30:45 | TRAIN | T001 | ADDED | SUCCESS | Position: 10km, Speed: 80kmph
2025-12-29T12:31:02 | SIGNAL | S1 | CHANGE_TO_GREEN | SUCCESS | VERIFIED
2025-12-29T12:31:15 | GATE | G1 | OPEN | FAILURE | Train too close (450m < 500m danger zone)
```

### How to Use Event Log
- **Monitor Operations**: See what's happening in real-time
- **Debug Issues**: Understand why an operation failed
- **Audit Trail**: Complete history for review and analysis
- **Safety Verification**: Confirm Digital Twin is working

---

## Safety Features

### Digital Twin Safety Verifier

**What It Does**:
- Creates a virtual replica of the entire railway system
- Simulates every decision before execution
- Blocks unsafe operations automatically
- Maintains 100% safety compliance

**How It Works**:
1. User requests an action (e.g., change signal to GREEN)
2. Digital Twin creates a copy of current state
3. Simulates the proposed action
4. Checks for conflicts and safety violations
5. If SAFE → executes action
6. If UNSAFE → blocks action and logs reason

### Safety Rules Enforced

#### Track Allocation
- ✅ Only one train per track
- ✅ Track must be FREE before RESERVED
- ✅ Minimum clearance time between trains

#### Signal Logic
- ✅ Signal GREEN only if track RESERVED
- ✅ Signal RED if track OCCUPIED
- ✅ Default state: RED (fail-safe)

#### Gate Logic
- ✅ Gate opens only if no train in danger zone (<500m)
- ✅ Auto-close when train approaches
- ✅ Default state: CLOSED (fail-safe)

### Station Master Override

**When to Use**:
- Emergency situations only
- When you need to bypass verification
- Critical safety decisions

**How It Works**:
- Add `override=True` parameter to control functions
- Action executes without Digital Twin verification
- Logged with "OVERRIDE" reason in Event Log

**⚠️ Warning**: Use override sparingly and responsibly!

---

## Common Workflows

### Workflow 1: Adding and Tracking a Train

1. **Add Train**:
   - Go to sidebar → Train Management
   - Set position (e.g., 10 km)
   - Set speed (e.g., 80 kmph)
   - Click "➕ Add Train"

2. **Watch Approach**:
   - Train appears in "🚂 Incoming" tab
   - Blue arrow shows on schematic view
   - ETA is calculated automatically

3. **Allocate Platform**:
   - System automatically allocates platform when needed
   - Platform changes to RESERVED (yellow)
   - Signal can be changed to GREEN

4. **Train Arrives**:
   - Click "▶️ Run Step" multiple times
   - Watch train move on schematic
   - Train reaches platform (position = 0)
   - Moves to "🚉 On Platform" tab
   - Platform becomes OCCUPIED (red)

5. **Train Departs**:
   - Continue clicking "▶️ Run Step"
   - Train clears platform
   - Platform enters CLEARING state
   - Then returns to FREE

### Workflow 2: Controlling Signals

1. **Check Track State**:
   - Look at Platform Details panel
   - Ensure track is RESERVED (yellow)

2. **Change Signal**:
   - Go to Signals & Gates section
   - Click 🟢 button for desired signal
   - Digital Twin verifies the change

3. **If Blocked**:
   - Check Event Log for reason
   - Usually: track not in correct state
   - Fix the underlying issue first

4. **If Successful**:
   - Signal changes color
   - Event logged
   - Train can proceed

### Workflow 3: Managing Gates

1. **Check Train Distance**:
   - Look at gate display
   - See "Nearest train: XXXm"

2. **Open Gate** (if safe):
   - Click "Open" button
   - Digital Twin checks distance
   - If > 500m → opens
   - If < 500m → blocked

3. **Close Gate**:
   - Click "Close" button
   - Always allowed (safe operation)
   - Gate closes immediately

4. **Auto-Close**:
   - When train approaches (<500m)
   - System suggests auto-close
   - Can be triggered manually

### Workflow 4: Emergency Stop

1. **Identify Emergency**:
   - Multiple trains approaching
   - System malfunction
   - Safety concern

2. **Activate Emergency Stop**:
   - Go to sidebar → Emergency Controls
   - Click "🚨 Emergency Stop All"
   - Confirm action

3. **Result**:
   - ALL signals set to RED
   - All trains must stop
   - Event logged with OVERRIDE
   - System in safe state

4. **Recovery**:
   - Assess situation
   - Manually reset signals as needed
   - Resume normal operations

---

## Tips and Best Practices

### For Demonstrations

1. **Start Simple**:
   - Add one train at a time
   - Watch complete lifecycle
   - Understand each state transition

2. **Show Safety**:
   - Try to open gate with train nearby
   - Try to set signal GREEN on occupied track
   - Show how Digital Twin blocks unsafe actions

3. **Use Visualization**:
   - Point out schematic view
   - Show real-time updates
   - Explain color coding

### For Testing

1. **Test Edge Cases**:
   - Multiple trains on different platforms
   - Trains with different speeds
   - Emergency scenarios

2. **Verify Safety**:
   - Check Safety Rate stays at 100%
   - Review Event Log for blocked actions
   - Confirm no unsafe operations execute

3. **Monitor Performance**:
   - Watch simulation time
   - Check platform utilization
   - Verify ETA accuracy

### For Academic Evaluation

1. **Highlight Features**:
   - Digital Twin verification
   - Real-time visualization
   - Complete audit trail
   - Safety-first design

2. **Demonstrate Scalability**:
   - Add multiple trains
   - Show concurrent operations
   - Explain how it could scale to real stations

3. **Explain Architecture**:
   - Modular design
   - Separation of concerns
   - Safety layer integration

---

## Troubleshooting

### Dashboard Won't Load

**Problem**: `streamlit run dashboard/app.py` fails

**Solutions**:
1. Ensure virtual environment is activated
2. Check all dependencies installed: `pip install -r requirements.txt`
3. Verify Python version: `python --version` (need 3.8+)

### Trains Not Moving

**Problem**: Clicking "Run Step" doesn't update positions

**Solutions**:
1. Check if trains are actually added (see Train Overview)
2. Verify simulation time is incrementing
3. Look for errors in Event Log

### Signal Changes Blocked

**Problem**: Cannot change signal to GREEN

**Solutions**:
1. Check track state (must be RESERVED)
2. Review Event Log for specific reason
3. Ensure train is allocated to that platform

### Gate Won't Open

**Problem**: "Open" button doesn't work

**Solutions**:
1. Check nearest train distance
2. Must be > 500m for safety
3. Wait for train to pass or move further away

---

## Keyboard Shortcuts

Currently, the dashboard uses mouse/click interactions only. Keyboard shortcuts may be added in future versions.

---

## Support and Documentation

### Additional Resources

- **Development Log**: `docs/development_log.md` - Complete development history
- **README**: `README.md` - Project overview and setup
- **Code Documentation**: Inline comments in all source files
- **Enhancement Plan**: See artifacts for planned features

### Getting Help

For questions or issues:
1. Check this User Guide first
2. Review Event Log for error messages
3. Check development log for known issues
4. Refer to code comments for technical details

---

## Conclusion

The Railway Digital Twin Dashboard provides a comprehensive, safe, and interactive way to monitor and control a railway station. With its Digital Twin safety verification, real-time visualization, and complete audit trail, it demonstrates modern approaches to safety-critical system design.

**Remember**: Safety is always the top priority. The Digital Twin verifies every operation to ensure 100% compliance with safety rules.

Happy monitoring! 🚂✨
