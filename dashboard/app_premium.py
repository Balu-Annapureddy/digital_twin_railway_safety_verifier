"""
Premium Railway Digital Twin Dashboard
Modern, dark-themed control center with network visualization and analytics.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.intelligence.dataset_analyzer import SmartDatasetAnalyzer
from src.intelligence.data_transformer import DataTransformer
from src.network.network_builder import NetworkBuilder


# ============================================================================
# HELPER FUNCTIONS - Define before use
# ============================================================================

def create_network_visualization(network_builder):
    """Create interactive network visualization using Plotly."""
    graph = network_builder.graph
    layout = network_builder.layout
    
    # Create edge traces
    edge_trace = []
    for edge in graph.edges():
        x0, y0 = layout[edge[0]]
        x1, y1 = layout[edge[1]]
        
        edge_trace.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=2, color='#4ecdc4'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    
    for node in graph.nodes():
        x, y = layout[node]
        node_x.append(x)
        node_y.append(y)
        station_info = network_builder.get_station_info(node)
        node_text.append(f"{station_info['name']}<br>Connections: {station_info['degree']}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[network_builder.stations[n].name for n in graph.nodes()],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            size=20,
            color='#00ff88',
            line=dict(width=2, color='#ffffff')
        ),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_trace + [node_trace])
    
    fig.update_layout(
        title="Railway Network Map",
        showlegend=False,
        hovermode='closest',
        template="plotly_dark",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='#0a0e1a',
        paper_bgcolor='#0a0e1a'
    )
    
    return fig


def create_circular_gauge(value, title, color):
    """Create circular gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14, 'color': '#e0e0e0'}},
        number={'suffix': "%", 'font': {'size': 24, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#4a5568'},
            'bar': {'color': color},
            'bgcolor': '#1a1f2e',
            'borderwidth': 2,
            'bordercolor': '#2a3f5f',
            'steps': [
                {'range': [0, 50], 'color': '#2d3748'},
                {'range': [50, 75], 'color': '#1a202c'},
                {'range': [75, 100], 'color': '#0f1419'}
            ],
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e0e0e0'}
    )
    
    return fig

# ============================================================================
# END HELPER FUNCTIONS
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="Railway Digital Twin Control Center",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0e1a;
        color: #e0e0e0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1419;
        border-right: 1px solid #1e2936;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00ff88;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 100%);
        border: 1px solid #2a3f5f;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Accent colors */
    .accent-green { color: #00ff88; }
    .accent-blue { color: #4ecdc4; }
    .accent-orange { color: #ff6b35; }
    .accent-purple { color: #a78bfa; }
    
    /* Upload area */
    [data-testid="stFileUploader"] {
        background-color: #1a1f2e;
        border: 2px dashed #4ecdc4;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00ff88 0%, #00d4aa 100%);
        color: #0a0e1a;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1f2e;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8b92a8;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00ff88;
        border-bottom-color: #00ff88;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: #1a2f1a;
        border-left: 4px solid #00ff88;
    }
    
    .stInfo {
        background-color: #1a2a3a;
        border-left: 4px solid #4ecdc4;
    }
    
    .stWarning {
        background-color: #3a2a1a;
        border-left: 4px solid #ff6b35;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dataset_loaded' not in st.session_state:
    st.session_state.dataset_loaded = False
    st.session_state.analysis_result = None
    st.session_state.unified_model = None
    st.session_state.network = None
    st.session_state.current_page = "Home"

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🚂 Railway Digital Twin")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 Upload Data", "🗺️ Network View", "📈 Analytics", "⏱️ Time-Traveler"],
        label_visibility="collapsed"
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # Quick Stats (if data loaded)
    if st.session_state.dataset_loaded:
        st.markdown("### Quick Stats")
        if st.session_state.analysis_result:
            st.metric("Trains", st.session_state.analysis_result.train_count)
            st.metric("Stations", st.session_state.analysis_result.station_count)
            st.metric("Data Quality", f"{st.session_state.analysis_result.data_quality:.0f}%")
    else:
        st.info("📤 Upload a dataset to get started")
    
    st.markdown("---")
    st.markdown("**Version:** 2.0 Premium")
    st.markdown("**Status:** 🟢 Online")

# Main Content Area
if page == "🏠 Home":
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 40px 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 10px;'>🚂 Railway Digital Twin</h1>
        <p style='font-size: 1.2rem; color: #8b92a8;'>Advanced Control Center & Network Visualization Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3 class='accent-green'>📊 Smart Analysis</h3>
            <p>Upload any railway dataset (CSV/JSON/Excel) and our AI automatically detects trains, stations, and routes.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3 class='accent-blue'>🗺️ Network View</h3>
            <p>Visualize entire railway networks with real-time train tracking and interactive maps.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3 class='accent-orange'>📈 Analytics</h3>
            <p>Advanced performance metrics, delay prediction, and comprehensive reporting.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting Started
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    
    st.markdown("""
    1. **Upload Dataset** - Go to 📊 Upload Data and drop your railway dataset
    2. **Auto-Analysis** - System automatically detects structure and validates data
    3. **Visualize** - Explore network map, analytics, and time-traveler features
    4. **Analyze** - Get insights, predictions, and performance metrics
    """)
    
    # Sample Datasets
    st.markdown("---")
    st.markdown("### 📁 Sample Datasets")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Load Sample Schedule Data"):
            st.info("Sample schedule data would be loaded here")
    
    with col2:
        if st.button("🔄 Load Sample Network Data"):
            st.info("Sample network data would be loaded here")

elif page == "📊 Upload Data":
    st.title("📊 Dataset Upload & Analysis")
    
    st.markdown("""
    Upload your railway dataset in **CSV**, **JSON**, or **Excel** format.  
    Our intelligent analyzer will automatically detect:
    - 🚂 Train IDs and schedules
    - 🏢 Stations and locations
    - 🛤️ Routes and connections
    - ⏰ Time ranges and events
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'json', 'xlsx', 'xls'],
        help="Supported formats: CSV, JSON, Excel"
    )
    
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing dataset..."):
            try:
                # Read file based on type
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Analyze
                analyzer = SmartDatasetAnalyzer()
                result = analyzer.analyze(dataframe=df)
                
                st.session_state.analysis_result = result
                
                # Transform
                transformer = DataTransformer(result)
                unified = transformer.transform()
                st.session_state.unified_model = unified
                
                # PERSIST RAW DATAFRAME FOR CALCULATOR
                st.session_state.raw_df = df
                
                
                # Build network
                builder = NetworkBuilder(unified)
                graph = builder.build_topology()
                st.session_state.network = builder
                
                st.session_state.dataset_loaded = True
                
                st.success("✅ Dataset analyzed successfully!")
                
                # Display results
                st.markdown("---")
                st.markdown("### 📋 Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Format", result.file_format)
                with col2:
                    st.metric("Dataset Type", result.dataset_type)
                with col3:
                    st.metric("Total Rows", f"{result.total_rows:,}")
                with col4:
                    st.metric("Data Quality", f"{result.data_quality:.0f}%")
                
                # Entities detected
                st.markdown("### 🎯 Detected Entities")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🚂 Trains", result.train_count)
                with col2:
                    st.metric("🏢 Stations", result.station_count)
                with col3:
                    st.metric("🛤️ Routes", result.route_count)
                
                # Column detection
                st.markdown("### 🔍 Detected Columns")
                cols_detected = []
                if result.train_id_column:
                    cols_detected.append(f"✅ Train ID: `{result.train_id_column}`")
                if result.timestamp_column:
                    cols_detected.append(f"✅ Timestamp: `{result.timestamp_column}`")
                if result.station_column:
                    cols_detected.append(f"✅ Station: `{result.station_column}`")
                if result.speed_column:
                    cols_detected.append(f"✅ Speed: `{result.speed_column}`")
                if result.status_column:
                    cols_detected.append(f"✅ Status: `{result.status_column}`")
                
                for col_info in cols_detected:
                    st.markdown(col_info)
                
                # Issues & Warnings
                if result.issues:
                    st.markdown("### ❌ Issues")
                    for issue in result.issues:
                        st.warning(issue)
                
                if result.warnings:
                    st.markdown("### ⚠️ Warnings")
                    for warning in result.warnings:
                        st.info(warning)
                
                # Data preview
                st.markdown("### 👀 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error analyzing dataset: {str(e)}")
                st.exception(e)

elif page == "🗺️ Network View":
    st.title("🗺️ Railway Network Visualization")
    
    if not st.session_state.dataset_loaded:
        st.warning("⚠️ Please upload a dataset first from the 📊 Upload Data page")
    else:
        # Network statistics
        col1, col2, col3, col4 = st.columns(4)
        
        stats = st.session_state.network.get_network_stats()
        
        with col1:
            st.metric("🏢 Stations", stats['total_stations'])
        with col2:
            st.metric("🛤️ Routes", stats['total_routes'])
        with col3:
            st.metric("🔗 Connections", stats['total_connections'])
        with col4:
            st.metric("📊 Avg Degree", f"{stats['average_degree']:.1f}")
        
        st.markdown("---")
        
        # Create network visualization
        fig = create_network_visualization(st.session_state.network)
        st.plotly_chart(fig, use_container_width=True)
        
        # Station details
        st.markdown("### 🏢 Station Details")
        station_ids = list(st.session_state.network.stations.keys())
        selected_station = st.selectbox("Select Station", station_ids)
        
        if selected_station:
            station_info = st.session_state.network.get_station_info(selected_station)
            if station_info:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {station_info['name']}")
                    st.write(f"**Connections:** {station_info['degree']}")
                with col2:
                    st.write(f"**Connected To:** {', '.join(station_info['neighbors'])}")

elif page == "📈 Analytics":
    st.title("📈 Performance Analytics")
    
    if not st.session_state.dataset_loaded:
        st.warning("⚠️ Please upload a dataset first")
    else:
        # KPI Metrics
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Circular gauge for OTP
            fig_otp = create_circular_gauge(88, "On-Time Performance", "#00ff88")
            st.plotly_chart(fig_otp, use_container_width=True)
        
        with col2:
            fig_reliability = create_circular_gauge(78, "Engine Reliability", "#4ecdc4")
            st.plotly_chart(fig_reliability, use_container_width=True)
        
        with col3:
            st.metric("Active Trains", st.session_state.analysis_result.train_count, "+3")
        
        with col4:
            st.metric("Total Delays", "12", "-5")
        
        # Charts
        st.markdown("---")
        st.markdown("### 📉 Trends & Insights")
        
        # Sample trend chart
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        delays = np.random.randint(5, 25, 30)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=dates, y=delays,
            mode='lines+markers',
            name='Daily Delays',
            line=dict(color='#ff6b35', width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            title="Delay Trends (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Number of Delays",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)

    # ============================================================================
    # TIME TRAVELER / HISTORICAL REPLAY LOGIC
    # ============================================================================
    
    st.title("⏱️ Time-Traveler & Historical Replay")
    
    if not st.session_state.dataset_loaded:
        st.warning("⚠️ Please upload a dataset to enable Time-Traveler features.")
        st.info("Tip: Upload a CSV with schedule data to visualize track occupancy over time.")
    else:
        # Initialize Backend Components if not already done
        if 'track_calculator' not in st.session_state:
            with st.spinner("Initializing Historical Engine..."):
                try:
                    from src.railway.station_manager import StationManager
                    from src.utils.track_occupancy_calculator import TrackOccupancyCalculator
                    
                    # 1. Initialize Station Manager (Topology)
                    # Try to look for topology file in standard location
                    topo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_network_topology.json')
                    if os.path.exists(topo_path):
                        st.session_state.station_manager = StationManager(topology_file=topo_path)
                    else:
                        st.warning("Topology file not found. Using default 3-platform config.")
                        st.session_state.station_manager = StationManager(network_topology={'stations': []}) # fallback or need better default
                    
                    # 2. Initialize Track Calculator (Schedule)
                    # We use the dataframe that was uploaded/analyzed
                    # Need to retrieve the dataframe from the analyzer result if stored, 
                    # OR we just re-use the df if we kept it. 
                    # NOTE: app_premium.py current state doesn't persist the raw df in session_state explicitly 
                    # outside the local scope of "Upload Data". 
                    # We should probably persist it in "Upload Data" section.
                    # For now, let's assume we can't get it unless we re-upload or if we modified Upload section to save it.
                    # Let's Modify the Upload Section to save `st.session_state.raw_df` first.
                    
                    # WAIT: I cannot modify the Upload Section in this replace_block easily without replacing the whole file 
                    # or doing a multi_replace.
                    # Let's assume for this block that st.session_state.raw_df EXISTS. 
                    # If not, we show an error asking to re-upload.
                    
                    if 'raw_df' in st.session_state:
                         st.session_state.track_calculator = TrackOccupancyCalculator(
                            st.session_state.raw_df, 
                            st.session_state.station_manager.topology
                        )
                    else:
                        st.error("Dataframe not found in memory. Please re-upload the dataset.")
                
                except Exception as e:
                    st.error(f"Failed to initialize engine: {e}")
        
        # --- UI CONTROLS ---
        
        if 'track_calculator' in st.session_state:
            calc = st.session_state.track_calculator
            mgr = st.session_state.station_manager
            
            # 1. Station Selector
            st.markdown("### 1. Select Station")
            station_names = mgr.get_station_names()
            if not station_names:
                station_names = ["Default Station"] # Fallback
            
            selected_station_name = st.selectbox("Choose Station to Monitor", station_names)
            
            # Get Station Details
            station_summary = mgr.get_station_summary(selected_station_name)
            if station_summary:
                st.write(f"**{selected_station_name}** | Platforms: {station_summary['total_platforms']} | Zone: {station_summary.get('zone', 'N/A')}")
            
            st.markdown("---")
            
            # 2. Time Control
            st.markdown("### 2. Time Travel")
            
            # Get time range from calculator
            min_time, max_time = calc.get_time_range()
            if not min_time:
                # Fallback if no time data
                min_time = datetime(2024, 1, 1, 0, 0)
                max_time = datetime(2024, 1, 1, 23, 59)
            
            # Slider
            min_ts = min_time.timestamp()
            max_ts = max_time.timestamp()
            
            selected_ts = st.slider(
                "Select Time",
                min_value=min_ts,
                max_value=max_ts,
                value=min_ts,
                step=60.0, # 1 minute steps
                format=""
            )
            
            current_dt = datetime.fromtimestamp(selected_ts)
            st.markdown(f"#### 🕒 Current Time: `{current_dt.strftime('%Y-%m-%d %H:%M')}`")
            
            st.markdown("---")
            
            # 3. Occupancy Grid View
            st.markdown("### 3. Track Occupancy Status")
            
            # Get occupancy data
            occupancy = calc.get_occupancy_at_time(selected_station_name, current_dt)
            
            # Summary Metrics for this time
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Occupied Tracks", occupancy['occupied_count'])
            with c2:
                st.metric("Free Tracks", occupancy['free_count'])
            with c3:
                utilization = (occupancy['occupied_count'] / occupancy['total_platforms']) * 100 if occupancy['total_platforms'] > 0 else 0
                st.metric("Utilization", f"{utilization:.1f}%")
            
            # Grid Visual
            # We'll use columns to create a grid layout
            
            platforms = occupancy['platforms']
            # Sort by platform ID
            sorted_p_ids = sorted(platforms.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
            
            # Create interactive grid
            st.markdown("#### Platform Status Grid")
            
            # Define CSS for grid
            st.markdown("""
            <style>
            .plat-card {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                text-align: center;
                border: 1px solid #333;
            }
            .occupied {
                background-color: #3b2a2a; /* Dark Redish */
                border-color: #ff4b4b;
            }
            .free {
                background-color: #1a2f1a; /* Dark Greenish */
                border-color: #00ff88;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Iterate and display
            cols = st.columns(4) # 4 columns grid
            for idx, pid in enumerate(sorted_p_ids):
                p_data = platforms[pid]
                status = p_data['status']
                col_idx = idx % 4
                
                with cols[col_idx]:
                    if status == 'OCCUPIED':
                        card_class = "occupied"
                        icon = "🔴"
                        train_txt = f"**{p_data['train_id']}**"
                        sub_txt = f"Dep: {p_data['departure_time'].strftime('%H:%M') if p_data['departure_time'] else '?'}"
                    else:
                        card_class = "free"
                        icon = "🟢"
                        train_txt = "*Empty*"
                        sub_txt = "Available"
                    
                    st.markdown(f"""
                    <div class="plat-card {card_class}">
                        <h4 style="margin:0">{icon} {pid}</h4>
                        <p style="font-size:1.2em; margin:5px 0;">{train_txt}</p>
                        <small>{sub_txt}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Detailed Table
            with st.expander("📝 View Detailed Schedule for this Station"):
                # Filter schedule for this station
                # This is a bit computationally expensive if done every rerun on full df, 
                # but valid for prototype.
                if 'raw_df' in st.session_state:
                    df = st.session_state.raw_df
                    # Simple filter for station name in dep/arr
                    # This depends on exact column names from analyzer
                    # Analyzer standardizes to 'departure_station', 'arrival_station'
                    
                    station_filter = (df['departure_station'] == selected_station_name) | (df['arrival_station'] == selected_station_name)
                    st.dataframe(df[station_filter], use_container_width=True)


if __name__ == "__main__":
    pass
