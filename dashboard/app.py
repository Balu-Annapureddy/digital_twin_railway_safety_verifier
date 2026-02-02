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
from src.data.historical_loader import HistoricalDataLoader
from config.station_config import get_station_info
from src.utils.train_categorizer import TrainCategorizer
from dashboard.components.visual_sim import VisualSimulation
from dashboard.components.visual_map import VisualMap
from src.digital_twin.safety_checker import HistoricalSafetyChecker
from src.ai.analytics import calculate_kpis, get_hourly_risk
from src.ai.ml_models import AnomalyDetector, RiskScorer
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go

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
    
    # Loaders & Analytics
    st.session_state.historical_loader = HistoricalDataLoader(os.path.join(os.path.dirname(__file__), '../data'))
    st.session_state.historical_loaded = st.session_state.historical_loader.load_data()
    
    # Pre-compute Safety & ML if data loaded
    st.session_state.violations_df = pd.DataFrame()
    st.session_state.ml_features = pd.DataFrame()
    st.session_state.kpis = {}
    st.session_state.hourly_risk = pd.DataFrame()
    
    if st.session_state.historical_loaded:
        merged_df = st.session_state.historical_loader.get_merged_data()
        checker = HistoricalSafetyChecker()
        st.session_state.violations_df = checker.detect_violations(merged_df)
        
        st.session_state.kpis = calculate_kpis(merged_df, st.session_state.violations_df)
        st.session_state.hourly_risk = get_hourly_risk(st.session_state.violations_df)
        
        detector = AnomalyDetector()
        st.session_state.ml_features = detector.train_and_predict(merged_df, st.session_state.violations_df)
        
        scorer = RiskScorer()
        # Simple aggregated risk for now, or per-minute in the ML tab
    
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

# --- Simulation Mode Selection ---
mode = st.sidebar.radio("Simulation Mode", ["Live Simulation", "Historical Replay"])

current_time_display = "Live"
active_train_count = 0
free_track_count = 0
safety_rate = 100.0

# Containers for data to be displayed
display_trains = []
display_tracks = []
display_signals = {} # Dict format for signals
display_gates = {}   # Dict format for gates

if mode == "Historical Replay":
    if not st.session_state.historical_loaded:
        st.error("Historical data not found in 'data/' directory.")
    else:
        st.sidebar.success("Historical Data Loaded")
        min_time, max_time = st.session_state.historical_loader.get_time_range()
        
        # --- FILTERS ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Replay Filters")
        
        # Platform Filter
        all_platforms = ["All", "P1", "P2", "P3"] # Could key this off data if needed
        selected_platform = st.sidebar.selectbox("Filter Platform", all_platforms)
        
        # Train Filter (Get all unique trains from data if possible, or simple list)
        # For strictness, let's get unique trains from the 'platform_status' dataframe if available to populate list
        all_trains = ["All"]
        if st.session_state.historical_loader.platform_df is not None:
            unique_trains = st.session_state.historical_loader.platform_df['train_id'].dropna().unique().tolist()
            all_trains.extend(sorted(unique_trains))
        
        selected_train = st.sidebar.selectbox("Filter Train", all_trains)
        
        if min_time and max_time:
            # Slider for time selection
            min_ts = min_time.timestamp()
            max_ts = max_time.timestamp()
            
            selected_ts = st.sidebar.slider(
                "Replay Time",
                min_value=min_ts,
                max_value=max_ts,
                value=min_ts,
                step=1.0,
                format=""
            )
            
            selected_dt = pd.to_datetime(selected_ts, unit='s')
            st.sidebar.info(f"Time: {selected_dt}")
            current_time_display = str(selected_dt)
            
            # Fetch State
            state = st.session_state.historical_loader.get_state_at_time(selected_dt)
            
            # Map Tracks/Platforms
            # Historical keys: platform_id, status, train_id, clearance_time
            # UI expects: track_id, state, allocated_to, clearance_time
            raw_platforms = state.get('platforms', [])
            
            # 1. Platform Filtering Logic
            display_tracks = []
            for p in raw_platforms:
                # Filter by Platform ID
                if selected_platform != "All" and p['platform_id'] != selected_platform:
                    continue
                
                display_tracks.append({
                    'track_id': p['platform_id'],
                    'state': p['status'],
                    'allocated_to': p['train_id'] if pd.notna(p['train_id']) else None,
                    'clearance_time': p['clearance_time']
                })
            display_tracks.sort(key=lambda x: x['track_id'])
            
            # 2. Train Logic (Strictly Derived from Filtered Platforms)
            display_trains = []
            for t in display_tracks:
                train_id = t['allocated_to']
                if train_id:
                    # Filter by Train ID
                    if selected_train != "All" and train_id != selected_train:
                        # If train is filtered out, we DO NOT show it, 
                        # BUT we show the platform as occupied? 
                        # Academic req: "Selecting T101 shows only T101". 
                        # So we essentially hide the train object, but platform state remains true from CSV.
                        continue

                    display_trains.append({
                        'id': train_id,
                        'position': 0.0, 
                        'speed': 0.0,
                        'train_type': 'STOPPING',
                        'status': 'ON_PLATFORM'
                    })
            
            # Note: display_trains is now populated strictly from the loop above.
            # No synthetic data generation allowed.
            
            # Map Signals
            # Historical: signal_id, platform, color, mode
            # UI expects: Dict[signal_id, {state, track_id}]
            raw_signals = state.get('signals', [])
            for s in raw_signals:
                display_signals[s['signal_id']] = {
                    'state': s['color'],
                    'track_id': s['platform']
                }
                
            # Map Gates
            # Historical: gate_id, status, nearest_train_m
            # UI expects: Dict[gate_id, {state, distance}]
            raw_gates = state.get('gates', [])
            for g in raw_gates:
                display_gates[g['gate_id']] = {
                    'state': g['status'],
                    'distance': g['nearest_train_m']
                }

            # Check for violations at this timestamp
            current_violations = []
            if not st.session_state.violations_df.empty:
                # Violations strictly AT this timestamp? Or within a window?
                # Data is precise. Let's check exact match or strict inequality if using windows.
                # Simplest: Violation timestamp == selected_dt
                # But slide might be 1s steps.
                v_df = st.session_state.violations_df
                current_violations = v_df[v_df['timestamp'] == selected_dt].to_dict('records')
            
            if current_violations:
                st.error(f"⚠️ SAFETY VIOLATION DETECTED: {len(current_violations)} active")
                for v in current_violations:
                    st.write(f"**{v['violation_type']}**: {v['description']}")

            active_train_count = len(display_trains)
            free_track_count = sum(1 for t in display_tracks if t['state'] == 'FREE')
            safety_rate = 100.0 
            if current_violations:
                safety_rate = 0.0 # Drop to 0 if violation active
            

else:
    # --- LIVE MODE --- 
    # Get current track states from Simulator/Managers
    display_tracks = st.session_state.track_manager.get_all_states()
    display_trains = st.session_state.simulator.get_all_states()
    
    # Map Signals from Controller
    for signal_id, signal in st.session_state.signal_controller.signals.items():
        display_signals[signal_id] = signal.get_state()
        
    # Map Gates from Controller
    for gate_id, gate in st.session_state.gate_controller.gates.items():
        display_gates[gate_id] = gate.get_state()

    active_train_count = st.session_state.simulator.get_active_train_count()
    free_track_count = st.session_state.track_manager.get_free_track_count()
    
    stats = st.session_state.safety_verifier.get_verification_stats()
    safety_rate = stats.get('safety_rate', 0)
    current_time_display = f"{st.session_state.simulator.simulation_time:.0f}s"

# Station Overview Panel
st.header("🏢 Station Overview")

overview_col1, overview_col2, overview_col3, overview_col4, overview_col5 = st.columns(5)

# Calculate metrics from DISPLAY data (responsive to mode)
occupied_count = sum(1 for t in display_tracks if t['state'] == 'OCCUPIED')
reserved_count = sum(1 for t in display_tracks if t['state'] == 'RESERVED')
free_count = sum(1 for t in display_tracks if t['state'] == 'FREE')

with overview_col1:
    st.metric("Total Platforms", station_info['total_platforms'])

with overview_col2:
    st.metric("Occupied", occupied_count, delta=None, delta_color="inverse")

with overview_col3:
    st.metric("Reserved", reserved_count, delta=None)

with overview_col4:
    st.metric("Free", free_count, delta=None, delta_color="normal")

with overview_col5:
    st.metric("Active Trains", active_train_count)

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
        
        if st.form_submit_button("➕ Add Train", disabled=(mode=="Historical Replay")):
            if mode == "Historical Replay":
                 st.error("Cannot add trains in Replay Mode")
            else:
                st.session_state.simulator.add_train(train_id, position, speed, "INBOUND", train_type)
                st.session_state.event_logger.log_event("TRAIN", train_id, "ADDED", "SUCCESS", f"Position: {position}km, Speed: {speed}kmph")
                st.success(f"Train {train_id} added!")
    
    st.markdown("---")
    
    st.subheader("Simulation Control")
    
    col1, col2 = st.columns(2)
    with col1:

        if st.button("▶️ Run Step", disabled=(mode=="Historical Replay")):
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
    
    if st.button("🚨 Emergency Stop All", type="primary", disabled=(mode=="Historical Replay")):
        # Set all signals to RED
        for signal_id in st.session_state.signal_controller.signals.keys():
            st.session_state.signal_controller.change_signal(signal_id, "RED", override=True)
        st.session_state.event_logger.log_event("SYSTEM", "ALL", "EMERGENCY_STOP", "SUCCESS", "All signals set to RED")
        st.error("Emergency stop activated!")
        st.rerun()

# --- MAIN CONTENT TABS ---
tab_overview, tab_visual, tab_safety, tab_ml, tab_analytics = st.tabs(["🏢 Overview", "🗺️ Visual Twin", "🛡️ Safety Violations", "🧠 ML Insights", "📈 Analytics"])

with tab_overview:
    # Main content area
    col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 System Status")
    
    # Metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:

        st.metric("Active Trains", active_train_count)
    
    with metric_col2:
        st.metric("Free Tracks", free_track_count)
    
    with metric_col3:
        st.metric("Safety Rate", f"{safety_rate:.1f}%")
    
    with metric_col4:
        st.metric("Simulation Time", current_time_display)
    
    st.markdown("---")
    
    # Train Overview Panel
    st.subheader("🚆 Train Overview")
    
    st.subheader("🚆 Train Overview")
    
    # Use display variables instead of direct session state 
    trains = display_trains
    tracks = display_tracks
    
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
    

    
    # Use display variable
    tracks = display_tracks
    
    # Create columns for each platform
    if tracks:
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
    
    # Signals
    st.subheader("Signals")
    
    for signal_id, state in display_signals.items():
        # state is now a dict {state: 'RED', track_id: 'P1'} from our map loop
        
        # Color indicator
        if state['state'] == 'RED':
            color = "🔴"
        elif state['state'] == 'YELLOW':
            color = "🟡"
        else:
            color = "🟢"
        
        st.write(f"{color} **{signal_id}** ({state['track_id']}): {state['state']}")
        
        st.write(f"{color} **{signal_id}** ({state['track_id']}): {state['state']}")
        
        # Control buttons
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🔴", key=f"red_{signal_id}", disabled=(mode=="Historical Replay")):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "RED")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_RED", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
        with col_b:
            if st.button("🟡", key=f"yellow_{signal_id}", disabled=(mode=="Historical Replay")):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "YELLOW")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_YELLOW", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
        with col_c:
            if st.button("🟢", key=f"green_{signal_id}", disabled=(mode=="Historical Replay")):
                success, msg = st.session_state.signal_controller.change_signal(signal_id, "GREEN")
                st.session_state.event_logger.log_event("SIGNAL", signal_id, "CHANGE_TO_GREEN", "SUCCESS" if success else "FAILURE", msg)
                st.rerun()
    
    st.markdown("---")
    
    # Gates
    st.subheader("Gates")
    
    # Gates
    st.subheader("Gates")
    
    for gate_id, state in display_gates.items():
        # state is dict {state: .., distance: ..}
        
        # Status indicator
        if state['state'] == 'OPEN':
            status = "🟢 OPEN"
        elif state['state'] == 'CLOSING':
            status = "🟡 CLOSING"
        else:
            status = "🔴 CLOSED"
        
        st.write(f"**{gate_id}**: {status}")
        st.write(f"Nearest train: {state['distance']:.0f}m")
        
        st.write(f"**{gate_id}**: {status}")
        st.write(f"Nearest train: {state['distance']:.0f}m")
        
        # Control buttons
        col_x, col_y = st.columns(2)
        with col_x:
            if st.button("Open", key=f"open_{gate_id}", disabled=(mode=="Historical Replay")):
                success, msg = st.session_state.gate_controller.change_gate(gate_id, "OPEN")
                st.session_state.event_logger.log_event("GATE", gate_id, "OPEN", "SUCCESS" if success else "FAILURE", msg)
                if not success:
                    st.error(msg)
                st.rerun()
        with col_y:
            if st.button("Close", key=f"close_{gate_id}", disabled=(mode=="Historical Replay")):
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

with tab_visual:
    st.header("🗺️ Digital Twin Visual Map")
    st.write("2D Schematic visualization of the station, tracks, and signals.")
    
    # Use the VisualMap component
    VisualMap.render(
        tracks=display_tracks,
        trains=display_trains,
        signals=display_signals,
        gates=display_gates
    )

with tab_safety:
    st.header("🛡️ Safety Rule Verification Engine")
    
    if st.session_state.violations_df.empty:
        st.success("No safety violations detected in the dataset (or data not loaded).")
    else:
        st.warning(f"Detected {len(st.session_state.violations_df)} safety violations.")
        
        # Filter
        severity_filter = st.multiselect("Filter by Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], default=["HIGH", "CRITICAL"])
        
        filtered_df = st.session_state.violations_df[st.session_state.violations_df['severity'].isin(severity_filter)]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Heatmap of violations over time
        if not filtered_df.empty:
            st.subheader("Violation Distribution")
            fig_viol = px.histogram(filtered_df, x="timestamp", color="violation_type", title="Violations over Time")
            st.plotly_chart(fig_viol, use_container_width=True)

with tab_ml:
    st.header("🧠 Intelligent Analytics & Risk")
    
    if st.session_state.ml_features.empty:
        st.info("ML analysis available in Historical Mode with data.")
    else:
        col_ml1, col_ml2 = st.columns(2)
        
        with col_ml1:
            st.subheader("Anomaly Detection (Isolation Forest)")
            st.write("Detects unusual system behavior (e.g., sudden spikes in events or violations).")
            
            ml_data = st.session_state.ml_features
            
            # Line chart of Anomaly Score
            fig_anom = px.line(ml_data, x='datetime', y='ui_score', title="System Anomaly Score (0=Normal, 100=Anomaly)")
            
            # Highlight anomalies
            anomalies = ml_data[ml_data['is_anomaly'] == -1]
            if not anomalies.empty:
                fig_anom.add_trace(go.Scatter(
                    x=anomalies['datetime'], y=anomalies['ui_score'],
                    mode='markers', name='Anomaly Detected',
                    marker=dict(color='red', size=10, symbol='x')
                ))
            
            st.plotly_chart(fig_anom, use_container_width=True)
            
        with col_ml2:
            st.subheader("Operational Risk Score")
            st.write("Real-time risk assessment based on violations and congestion.")
            
            # Calculate a total risk score? Or show hourly?
            # Let's show the Hourly Risk Profile
            if not st.session_state.hourly_risk.empty:
                fig_risk = px.bar(
                    st.session_state.hourly_risk, 
                    x='hour', y='risk_score',
                    color='risk_score',
                    color_continuous_scale='Reds',
                    title="Hourly Risk Profile"
                )
                st.plotly_chart(fig_risk, use_container_width=True)
            else:
                st.info("No risk data available.")
        
        st.subheader("Explainable ML Factors")
        st.markdown("""
        **Risk Score Weights:**
        - **Signal Violations:** High Impact (Weight 20)
        - **Gate Violations:** Medium Impact (Weight 15)
        - **Congestion:** Low Impact (Weight 10)
        
        **Anomaly Detection:**
        - Uses **Isolation Forest** (Unsupervised Learning)
        - Features: Event Frequency, Violation Count, Active Trains
        """)

with tab_analytics:
    st.header("📈 Performance Analytics")
    
    if mode == "Historical Replay" and st.session_state.historical_loaded:
        loader = st.session_state.historical_loader
        
        # 1. Platform Utilization
        if loader.platform_df is not None:
            st.subheader("Platform Utilization")
            df_plat = loader.platform_df
            # Count occurences of OCCUPIED per platform
            occ_counts = df_plat[df_plat['status'] == 'OCCUPIED']['platform_id'].value_counts().reset_index()
            occ_counts.columns = ['Platform', 'Occupied Count']
            
            fig_plat = px.bar(occ_counts, x='Platform', y='Occupied Count', title="Occupancy Frequency by Platform", color='Platform')
            st.plotly_chart(fig_plat, use_container_width=True)
            
        # 2. Gate Status Over Time
        if loader.gate_df is not None:
            st.subheader("Gate Status Timeline")
            df_gate = loader.gate_df
            fig_gate = px.scatter(df_gate, x='timestamp', y='gate_id', color='status', title="Gate Status Changes")
            st.plotly_chart(fig_gate, use_container_width=True)
            
        # 3. Signal State Distribution
        if loader.signal_df is not None:
            st.subheader("Signal State Distribution")
            df_sig = loader.signal_df
            sig_counts = df_sig['color'].value_counts().reset_index()
            sig_counts.columns = ['State', 'Count']
            color_map = {'GREEN': '#00CC00', 'RED': '#CC0000', 'YELLOW': '#CCCC00'}
            fig_sig = px.pie(sig_counts, values='Count', names='State', title="Signal State Distribution", color='State', color_discrete_map=color_map)
            st.plotly_chart(fig_sig, use_container_width=True)
            
    else:
        st.info("Analytics are available in 'Historical Replay' mode when data is loaded.")

# Footer
st.markdown("---")
st.markdown("**Railway Digital Twin System** | Academic Project | Safety-First Design")
