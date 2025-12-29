"""
Integration demo - All modules working together.
Demonstrates complete system with Digital Twin verification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation.simulator import TrainSimulator
from src.ai.eta_predictor import ETAPredictor
from src.railway.track_manager import TrackManager
from src.railway.signal_controller import SignalController
from src.railway.gate_controller import GateController
from src.digital_twin.safety_verifier import SafetyVerifier
import time


def main():
    """Run integrated system demo."""
    print("\n" + "="*70)
    print("Railway Digital Twin - Integrated System Demo")
    print("="*70 + "\n")
    
    # Initialize all components
    print("Initializing system components...")
    simulator = TrainSimulator()
    track_manager = TrackManager(["P1", "P2", "P3"])
    safety_verifier = SafetyVerifier()
    signal_controller = SignalController(safety_verifier)
    gate_controller = GateController(safety_verifier)
    
    # Add signals and gates
    signal_controller.add_signal("S1", "P1")
    signal_controller.add_signal("S2", "P2")
    gate_controller.add_gate("G1")
    
    print("✓ System initialized\n")
    
    # Add train
    print("Adding train T001...")
    train = simulator.add_train("T001", 5.0, 80.0, "INBOUND", "STOPPING")
    print(f"✓ Train added: {train}\n")
    
    # Sync state with Digital Twin
    print("Syncing state with Digital Twin...")
    safety_verifier.sync_state(
        trains=simulator.get_all_states(),
        tracks=track_manager.get_all_states(),
        signals=signal_controller.get_all_states(),
        gates=gate_controller.get_all_states()
    )
    print("✓ State synchronized\n")
    
    print("-" * 70)
    print("SCENARIO: Train approaching station")
    print("-" * 70 + "\n")
    
    # Step 1: Allocate track
    print("STEP 1: Allocating track for T001...")
    track_id = track_manager.allocate_track("T001", 225.0)
    if track_id:
        print(f"✓ Track {track_id} allocated to T001")
        
        # Update Digital Twin
        safety_verifier.sync_state(tracks=track_manager.get_all_states())
    else:
        print("✗ Track allocation failed")
        return
    
    print()
    
    # Step 2: Change signal to GREEN
    print("STEP 2: Changing signal to GREEN...")
    success, msg = signal_controller.change_signal("S1", "GREEN")
    print(f"{'✓' if success else '✗'} {msg}\n")
    
    # Step 3: Close gate as train approaches
    print("STEP 3: Managing gate as train approaches...")
    gate_controller.update_train_proximity("G1", "T001", 5000.0)  # 5km = 5000m
    print(f"Train distance: 5000m - Gate status: {gate_controller.get_gate('G1').state.value}")
    
    gate_controller.update_train_proximity("G1", "T001", 450.0)  # Approaching danger zone
    success, msg = gate_controller.auto_close_if_needed("G1", threshold=500.0)
    if success:
        print(f"✓ {msg}")
    
    print()
    
    # Step 4: Simulate train movement
    print("STEP 4: Simulating train movement...")
    for step in range(10):
        state = simulator.run_step()
        if state['active_trains'] == 0:
            print("Train reached station!")
            break
        
        train_state = state['trains'][0]
        print(f"  Step {step + 1}: Position {train_state['position']:.2f}km @ {train_state['speed']}kmph")
        time.sleep(0.1)
    
    print()
    
    # Step 5: Occupy track
    print("STEP 5: Train occupying track...")
    track = track_manager.get_track(track_id)
    if track:
        track.occupy("T001")
        print(f"✓ Track {track_id} now OCCUPIED")
        
        # Update Digital Twin
        safety_verifier.sync_state(tracks=track_manager.get_all_states())
    
    print()
    
    # Step 6: Try to change signal to GREEN (should fail - track occupied)
    print("STEP 6: Attempting to change signal to GREEN (should fail)...")
    success, msg = signal_controller.change_signal("S1", "GREEN")
    print(f"{'✓' if success else '✗'} {msg}\n")
    
    # Step 7: Clear track
    print("STEP 7: Clearing track...")
    track.start_clearing()
    track.clear()
    print(f"✓ Track {track_id} cleared and FREE\n")
    
    # Show final statistics
    print("="*70)
    print("System Statistics")
    print("="*70)
    
    stats = safety_verifier.get_verification_stats()
    print(f"\nDigital Twin Verifications:")
    print(f"  Total: {stats['total_verifications']}")
    print(f"  Safe: {stats['safe']}")
    print(f"  Unsafe: {stats['unsafe']}")
    print(f"  Safety Rate: {stats['safety_rate']:.1f}%")
    
    print(f"\nTrack Manager:")
    print(f"  Free tracks: {track_manager.get_free_track_count()}/{len(track_manager.tracks)}")
    
    print(f"\nSignal Controller:")
    print(f"  Total signals: {len(signal_controller.signals)}")
    
    print(f"\nGate Controller:")
    print(f"  Total gates: {len(gate_controller.gates)}")
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
