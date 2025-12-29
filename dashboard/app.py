"""
Station Master Dashboard - Main Streamlit Application
Interactive UI for monitoring and controlling the railway system.

ENHANCED VERSION with:
- Station Overview Panel
- Train Overview Panel with route information
- Platform Details Panel
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulation.simulator import TrainSimulator
from src.railway.track_manager import TrackManager
from src.railway.signal_controller import SignalController
from src.railway.gate_controller import GateController
from src.digital_twin.safety_verifier import SafetyVerifier
from src.logging.event_logger import EventLogger
from src.data.schedule_loader import ScheduleLoader
from src.utils.train_categorizer import TrainCategorizer
from config.station_config import get_station_info
from dashboard.components.visual_sim import VisualSimulation
import pandas as pd
import time

# Page configuration
st.set_page_config(
    page_title="Railway Digital Twin - Station Master Dashboard",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .station-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.simulator = TrainSimulator()
    st.session_state.track_manager = TrackManager(["P1", "P2", "P3"])
    st.session_state.safety_verifier = SafetyVerifier()
    st.session_state.signal_controller = SignalController(st.session_state.safety_verifier)
    st.session_state.gate_controller = GateController(st.session_state.safety_verifier)
    st.session_state.event_logger = EventLogger()
    
    # Add initial signals and gates
    st.session_state.signal_controller.add_signal("S1", "P1")
    st.session_state.signal_controller.add_signal("S2", "P2")
    st.session_state.signal_controller.add_signal("S3", "P3")
    st.session_state.gate_controller.add_gate("G1")
    
    st.session_state.initialized = True
    st.session_state.simulation_running = False
    st.session_state.step_count = 0

# Station Header with Overview
station_info = get_station_info()

st.markdown(f"""
<div class="station-header">
    <h1>🚂 {station_info['station_name']}</h1>
    <p style="font-size: 18px; margin: 0;">Station Code: {station_info['station_code']} | Zone: {station_info['zone']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("**AI-Driven Real-Time Railway Interlock and Signal Logic Verifier**")

# Station Overview Panel
st.header("🏢 Station Overview")

overview_col1, overview_col2, overview_col3, overview_col4, overview_col5 = st.columns(5)

# Get current track states
tracks = st.session_state.track_manager.get_all_states()
occupied_count = sum(1 for t in tracks if t['state'] == 'OCCUPIED')
reserved_count = sum(1 for t in tracks if t['state'] == 'RESERVED')
free_count = sum(1 for t in tracks if t['state'] == 'FREE')

with overview_col1:
    st.metric("Total Platforms", station_info['total_platforms'])

with overview_col2:
    st.metric("Occupied", occupied_count, delta=None, delta_color="inverse")

with overview_col3:
    st.metric("Reserved", reserved_count, delta=None)

with overview_col4:
    st.metric("Free", free_count, delta=None, delta_color="normal")

with overview_col5:
    st.metric("Active Trains", st.session_state.simulator.get_active_train_count())

st.markdown("---")

# Sidebar - Controls
with st.sidebar:
    st.header("⚙️ System Controls")
    
    st.subheader("Train Management")
    
    with st.form("add_train_form"):
        train_id = st.text_input("Train ID", value=f"T{st.session_state.step_count:03d}")
        position = st.slider("Initial Position (km)", 1.0, 20.0, 10.0, 0.5)
        speed = st.slider("Initial Speed (kmph)", 40, 120, 80, 5)
        train_type = st.selectbox("Train Type", ["STOPPING", "NON_STOPPING"])
        
        if st.form_submit_button("➕ Add Train"):
            st.session_state.simulator.add_train(train_id, position, speed, "INBOUND", train_type)
            st.session_state.event_logger.log_event("TRAIN", train_id, "ADDED", "SUCCESS", f"Position: {position}km, Speed: {speed}kmph")
            st.success(f"Train {train_id} added!")
    
    st.markdown("---")
    
    st.subheader("Simulation Control")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Run Step"):
            st.session_state.simulator.run_step()
            st.session_state.step_count += 1
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset"):
            st.session_state.simulator.reset()
            st.session_state.step_count = 0
            st.session_state.event_logger.clear_events()
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Emergency Controls")
    st.warning("⚠️ Override bypasses Digital Twin verification")
    
    if st.button("🚨 Emergency Stop All", type="primary"):
        # Set all signals to RED
        for signal_id in st.session_state.signal_controller.signals.keys():
            st.session_state.signal_controller.change_signal(signal_id, "RED", override=True)
        st.session_state.event_logger.log_event("SYSTEM", "ALL", "EMERGENCY_STOP", "SUCCESS", "All signals set to RED")
        st.error("Emergency stop activated!")
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 System Status")
    
    # Metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Active Trains", st.session_state.simulator.get_active_train_count())
    
    with metric_col2:
        st.metric("Free Tracks", st.session_state.track_manager.get_free_track_count())
    
    with metric_col3:
        stats = st.session_state.safety_verifier.get_verification_stats()
        st.metric("Safety Rate", f"{stats.get('safety_rate', 0):.1f}%")
    
    with metric_col4:
        st.metric("Simulation Time", f"{st.session_state.simulator.simulation_time:.0f}s")
    
    st.markdown("---")
    
    # Train Overview Panel
    st.subheader("🚆 Train Overview")
    
    trains = st.session_state.simulator.get_all_states()
    tracks = st.session_state.track_manager.get_all_states()
    
    if trains:
        # Categorize trains
        categories = TrainCategorizer.categorize_all_trains(trains, tracks)
        
        # Create tabs for each category
        tab1, tab2, tab3 = st.tabs([
            f"🚂 Incoming ({len(categories['INCOMING'])})",
            f"🚉 On Platform ({len(categories['ON_PLATFORM'])})",
            f"✅ Departed ({len(categories['DEPARTED'])})"
        ])
        
        with tab1:
            if categories['INCOMING']:
                for train in categories['INCOMING']:
                    with st.expander(f"Train {train['id']}", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Position:** {train['position']:.2f} km")
                            st.write(f"**Speed:** {train['speed']} kmph")
                            st.write(f"**Type:** {train.get('train_type', 'STOPPING')}")
                        with col_b:
                            # Calculate ETA
                            if train['speed'] > 0:
                                eta_hours = train['position'] / train['speed']
                                eta_minutes = eta_hours * 60
                                st.write(f"**ETA:** ~{eta_minutes:.1f} minutes")
                            st.write(f"**Avg Speed:** {train.get('avg_speed', train['speed']):.1f} kmph")
                            st.write(f"**Status:** 🟢 Approaching")
            else:
                st.info("No incoming trains")
        
        with tab2:
            if categories['ON_PLATFORM']:
                for train in categories['ON_PLATFORM']:
                    # Find which platform
                    platform = "Unknown"
                    for track in tracks:
                        if track.get('allocated_to') == train['id']:
                            platform = track['track_id']
                            break
                    
                    with st.expander(f"Train {train['id']} - Platform {platform}", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Platform:** {platform}")
                            st.write(f"**Type:** {train.get('train_type', 'STOPPING')}")
                        with col_b:
                            st.write(f"**Status:** 🟠 On Platform")
                            st.write(f"**Speed:** {train['speed']} kmph (Stopped)")
            else:
                st.info("No trains on platform")
        
        with tab3:
            st.info("Departed trains are removed from active tracking")
    else:
        st.info("No active trains in the system")
    
    st.markdown("---")
    
    # Active Trains Table (Detailed View)
    st.subheader("📊 Detailed Train Data")
    
    if trains:
        train_df = pd.DataFrame(trains)
        st.dataframe(train_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active trains")
    
    st.markdown("---")
    
    # Platform Details Panel
    st.subheader("🛤️ Platform Details")
    
    tracks = st.session_state.track_manager.get_all_states()
    
    # Create columns for each platform
    platform_cols = st.columns(len(tracks))
    
    for idx, track in enumerate(tracks):
        with platform_cols[idx]:
            # Platform card
            state = track['state']
            
            # Color coding
            if state == 'FREE':
                color = "#90EE90"
                icon = "🟢"
            elif state == 'RESERVED':
                color = "#FFD700"
                icon = "🟡"
            elif state == 'OCCUPIED':
                color = "#FF6B6B"
                icon = "🔴"
            else:
                color = "#D3D3D3"
                icon = "⚪"
            
            st.markdown(f"""
            <div style="background-color: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <h3 style="margin: 0;">{icon} {track['track_id']}</h3>
                <p style="margin: 5px 0; font-size: 18px;"><strong>{state}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            if track['allocated_to']:
                st.write(f"**Train:** {track['allocated_to']}")
                if track.get('expected_arrival'):
                    st.write(f"**ETA:** {track['expected_arrival']:.0f}s")
            else:
                st.write("**Train:** None")
            
            st.write(f"**Clearance:** {track.get('clearance_time', 120)}s")

with col2:
    st.header("🚦 Signals & Gates")
    
    # Signals
    st.subheader("Signals")
    
    for signal_id, signal in st.session_state.signal_controller.signals.items():
        state = signal.get_state()
        
        # Color indicator
        if state['state'] == 'RED':
            color = "🔴"
        elif state['state'] == 'YELLOW':
            color = "🟡"
        else:
            color = "🟢"
        
        st.write(f"{color} **{signal_id}** ({state['track_id']}): {state['state']}")
        
        # Control buttons
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🔴", key=f"red_{signal_id}"):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "RED")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_RED", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
        with col_b:
            if st.button("🟡", key=f"yellow_{signal_id}"):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "YELLOW")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_YELLOW", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
        with col_c:
            if st.button("🟢", key=f"green_{signal_id}"):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "GREEN")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_GREEN", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
    
    st.markdown("---")
    
    # Gates
    st.subheader("Gates")
    
    for gate_id, gate in st.session_state.gate_controller.gates.items():
        state = gate.get_state()
        
        # Status indicator
        if state['state'] == 'OPEN':
            status = "🟢 OPEN"
        elif state['state'] == 'CLOSING':
            status = "🟡 CLOSING"
        else:
            status = "🔴 CLOSED"
        
        st.write(f"**{gate_id}**: {status}")
        st.write(f"Nearest train: {state['distance']:.0f}m")
        
        # Control buttons
        col_x, col_y = st.columns(2)
        with col_x:
            if st.button("Open", key=f"open_{gate_id}"):
                success, msg = st.session_state.gate_controller.change_gate(gate_id, "OPEN")
                st.session_state.event_logger.log_event("GATE", gate_id, "OPEN", "SUCCESS" if success else "FAILURE", msg)
                if not success:
                    st.error(msg)
                st.rerun()
        with col_y:
            if st.button("Close", key=f"close_{gate_id}"):
                success, msg = st.session_state.gate_controller.change_gate(gate_id, "CLOSED")
                st.session_state.event_logger.log_event("GATE", gate_id, "CLOSE", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()

# Bottom section - Event Log
st.markdown("---")
st.header("📋 Event Log")

events = st.session_state.event_logger.get_recent_events(20)
if events:
    event_df = pd.DataFrame(events)
    st.dataframe(event_df, use_container_width=True, hide_index=True)
else:
    st.info("No events logged yet")

# Footer
st.markdown("---")
st.markdown("**Railway Digital Twin System** | Academic Project | Safety-First Design")
