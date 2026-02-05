# 🧹 Project Cleanup Instructions

## ✅ Good News: JSON Already Converted!
The `schedules_optimized.csv` (32MB) already exists in the `data/` folder!

---

## Files to Delete (Safe to Remove)

### 1. Delete Entire `tests/` Folder
**Location:** `C:\Users\annap\Desktop\Projects\finished-projects\Digital Twin–Based Railway\tests`

This folder contains 9 test files that are no longer needed:
- test_digital_twin.py
- test_loader.py
- test_safety_logic.py
- test_simulation.py
- test_station_manager.py
- test_track_manager.py
- test_track_occupancy.py
- verify_fixes.py
- __init__.py

**Action:** Right-click the `tests` folder → Delete

---

### 2. Delete `examples/` Folder
**Location:** `C:\Users\annap\Desktop\Projects\finished-projects\Digital Twin–Based Railway\examples`

This folder contains 4 old demo scripts (not used by the dashboard):
- demo_eta_prediction.py
- demo_integration.py
- demo_schedule_loader.py
- demo_simulation.py

**Action:** Right-click the `examples` folder → Delete

---

### 3. Delete Old Data Files (in `data/` folder)

**Navigate to:** `data/` folder

**DELETE these 4 CSV files:**
- `event_log.csv` (117 bytes)
- `gate_status.csv` (12 KB)
- `platform_status.csv` (38 KB)
- `signal_state.csv` (39 KB)

**DELETE this folder:**
- `schedules.json/` (entire folder - 80MB!)

**KEEP these files:**
- `sample_indian_railways.csv` ✅
- `schedules_optimized.csv` ✅
- `sample_network_topology.json` ✅

---

### 4. Delete Old Documentation File

**DELETE:**
- `CLEANUP_COMMANDS.md` (in project root)

---

### 5. Delete __pycache__ Folders

Search for and delete all `__pycache__` folders:
- `src/__pycache__/`
- `dashboard/__pycache__/`
- `config/__pycache__/`
- Any others you find

**Tip:** In File Explorer, search for `__pycache__` in the project folder and delete all results.

---

## Quick Summary - Delete These:

```
✗ tests/ (entire folder)
✗ examples/ (entire folder)
✗ data/event_log.csv
✗ data/gate_status.csv
✗ data/platform_status.csv
✗ data/signal_state.csv
✗ data/schedules.json/ (entire folder - 80MB!)
✗ CLEANUP_COMMANDS.md
✗ All __pycache__ folders
```

## Space You'll Save: ~85-90 MB! 🎉

---

## After Cleanup

Your project will be:
- ✅ Clean and production-ready
- ✅ ~85-90 MB smaller
- ✅ Ready for Git push
- ✅ Only essential files remaining
