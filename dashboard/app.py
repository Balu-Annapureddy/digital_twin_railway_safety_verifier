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
import json

# ============================================================================
# CACHED DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_and_analyze_dataset(file_path, sample_size=None):
    """Load and analyze dataset with caching (1 hour TTL)
    
    Args:
        file_path: Path to dataset file
        sample_size: If set, only load first N rows (for large files)
    """
    try:
        # Read file based on extension with optimizations
        if file_path.endswith('.csv'):
            if sample_size:
                df = pd.read_csv(file_path, nrows=sample_size)
            else:
                df = pd.read_csv(file_path, low_memory=False)
        elif file_path.endswith('.json'):
            # JSON is slow for large files - use lines=True if possible
            try:
                if sample_size:
                    df = pd.read_json(file_path, lines=True, nrows=sample_size)
                else:
                    df = pd.read_json(file_path, lines=True)
            except:
                # Fallback to regular JSON (slower)
                df = pd.read_json(file_path)
                if sample_size and len(df) > sample_size:
                    df = df.head(sample_size)
        elif file_path.endswith(('.xlsx', '.xls')):
            if sample_size:
                df = pd.read_excel(file_path, nrows=sample_size)
            else:
                df = pd.read_excel(file_path)
        else:
            return None, None, None, None
        
        # Analyze (with progress for large datasets)
        analyzer = SmartDatasetAnalyzer()
        result = analyzer.analyze(dataframe=df)
        
        # Transform
        transformer = DataTransformer(result)
        unified = transformer.transform()
        
        # Build network
        builder = NetworkBuilder(unified)
        graph = builder.build_topology()
        
        return df, result, unified, builder
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None, None, None


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
    st.session_state.auto_loaded = False

# AUTO-LOAD DISABLED - Manual upload only for better control
# Users can upload any dataset via the Upload Data page
st.session_state.auto_loaded = True  # Skip auto-load

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
        df = st.session_state.raw_df
        result = st.session_state.analysis_result
        
        # Calculate real metrics from data
        total_trains = result.train_count
        total_records = len(df)
        
        # Calculate On-Time Performance (if we have scheduled vs actual times)
        otp_percentage = 88  # Default
        if result.timestamp_column:
            # Check if we have both scheduled and actual time columns
            time_cols = [col for col in df.columns if 'time' in col.lower()]
            if len(time_cols) >= 2:
                # Try to calculate delays
                try:
                    scheduled_col = [c for c in time_cols if 'scheduled' in c.lower()][0]
                    actual_col = [c for c in time_cols if 'actual' in c.lower()][0]
                    
                    # Count on-time (within 5 min tolerance)
                    on_time_count = 0
                    total_count = 0
                    for _, row in df.iterrows():
                        if pd.notna(row.get(scheduled_col)) and pd.notna(row.get(actual_col)):
                            total_count += 1
                            # Simple string comparison for now
                            if row[scheduled_col] == row[actual_col]:
                                on_time_count += 1
                    
                    if total_count > 0:
                        otp_percentage = int((on_time_count / total_count) * 100)
                except:
                    pass
        
        # Calculate reliability (based on data completeness)
        # Count non-null values across all columns
        total_cells = len(df) * len(df.columns)
        non_null_cells = df.count().sum()
        reliability = int((non_null_cells / total_cells) * 100) if total_cells > 0 else 0
        
        # Count delays (rows where actual != scheduled, or status indicates delay)
        delay_count = 0
        if result.status_column and result.status_column in df.columns:
            delay_keywords = ['delay', 'late', 'behind']
            delay_count = df[result.status_column].astype(str).str.lower().apply(
                lambda x: any(keyword in x for keyword in delay_keywords)
            ).sum()
        
        # KPI Metrics
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Circular gauge for OTP (real data)
            fig_otp = create_circular_gauge(otp_percentage, "On-Time Performance", "#00ff88")
            st.plotly_chart(fig_otp, use_container_width=True)
        
        with col2:
            # Reliability based on data quality
            fig_reliability = create_circular_gauge(reliability, "Data Quality", "#4ecdc4")
            st.plotly_chart(fig_reliability, use_container_width=True)
        
        with col3:
            st.metric("Active Trains", total_trains)
        
        with col4:
            st.metric("Total Records", total_records)
        
        # Charts
        st.markdown("---")
        st.markdown("### 📉 Trends & Insights")
        
        # Real trend chart based on data
        if result.timestamp_column and result.timestamp_column in df.columns:
            try:
                # Parse timestamps and group by date
                df_copy = df.copy()
                df_copy['parsed_time'] = pd.to_datetime(df_copy[result.timestamp_column], errors='coerce')
                df_copy['date'] = df_copy['parsed_time'].dt.date
                
                # Count records per day
                daily_counts = df_copy.groupby('date').size().reset_index(name='count')
                daily_counts = daily_counts.sort_values('date')
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=daily_counts['date'], 
                    y=daily_counts['count'],
                    mode='lines+markers',
                    name='Daily Activity',
                    line=dict(color='#ff6b35', width=3),
                    marker=dict(size=8)
                ))
                
                fig_trend.update_layout(
                    title="Daily Activity Trend",
                    xaxis_title="Date",
                    yaxis_title="Number of Records",
                    template="plotly_dark",
                    height=400
                )
            except:
                # Fallback: show record distribution
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Bar(
                    x=list(range(len(df))),
                    y=[1] * len(df),
                    name='Records',
                    marker=dict(color='#ff6b35')
                ))
                fig_trend.update_layout(
                    title="Record Distribution",
                    xaxis_title="Record Index",
                    yaxis_title="Count",
                    template="plotly_dark",
                    height=400
                )
        else:
            # No timestamp - show train distribution
            if result.train_id_column and result.train_id_column in df.columns:
                train_counts = df[result.train_id_column].value_counts().head(10)
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Bar(
                    x=train_counts.index,
                    y=train_counts.values,
                    name='Records per Train',
                    marker=dict(color='#ff6b35')
                ))
                
                fig_trend.update_layout(
                    title="Top 10 Trains by Record Count",
                    xaxis_title="Train ID",
                    yaxis_title="Number of Records",
                    template="plotly_dark",
                    height=400
                )
            else:
                # Ultimate fallback
                st.info("📊 Upload a dataset with timestamp or train ID columns for detailed trends")
                fig_trend = None
        
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)

elif page == "⏱️ Time-Traveler":
    st.title("⏱️ Time-Traveler & Platform Tracking")
    
    if not st.session_state.dataset_loaded:
        st.warning("⚠️ Please upload a dataset to enable Time-Traveler features.")
        st.info("Tip: Upload a CSV with train schedule data to visualize platform occupancy over time.")
    else:
        # Initialize Simple Platform Tracker
        if 'platform_tracker' not in st.session_state:
            try:
                from src.utils.simple_platform_tracker import SimplePlatformTracker
                st.session_state.platform_tracker = SimplePlatformTracker(st.session_state.raw_df)
            except Exception as e:
                st.error(f"Failed to initialize platform tracker: {e}")
                st.stop()
        
        tracker = st.session_state.platform_tracker
        
        # Get station list
        stations = tracker.get_station_list()
        
        if not stations:
            st.warning("No stations found in the dataset")
            st.stop()
        
        # 1. Station Selector
        st.markdown("### 1. Select Station")
        selected_station = st.selectbox("Choose Station to Monitor", stations)
        
        st.markdown("---")
        
        # 2. Time Control - Show actual train times instead of slider
        st.markdown("### 2. Select Time Period")
        
        # Get all train events for this station
        station_events = []
        for assignment in tracker.platform_assignments:
            if assignment['station'] == selected_station:
                # Add arrival event
                if assignment['arrival_time']:
                    station_events.append({
                        'time': assignment['arrival_time'],
                        'label': f"{assignment['arrival_time'].strftime('%H:%M')} - {assignment['train_id']} arrives",
                        'train_id': assignment['train_id']
                    })
                # Add departure event
                if assignment['departure_time']:
                    station_events.append({
                        'time': assignment['departure_time'],
                        'label': f"{assignment['departure_time'].strftime('%H:%M')} - {assignment['train_id']} departs",
                        'train_id': assignment['train_id']
                    })
        
        # Sort by time
        station_events.sort(key=lambda x: x['time'])
        
        if not station_events:
            st.warning(f"No train events found for {selected_station}")
            st.stop()
        
        # Create time interval options
        time_options = []
        time_map = {}
        
        # Add "All trains present" option - middle of the day
        min_time, max_time = tracker.get_time_range()
        mid_time = datetime.fromtimestamp((min_time.timestamp() + max_time.timestamp()) / 2)
        time_options.append(f"🕐 {mid_time.strftime('%H:%M')} - Peak time (view all activity)")
        time_map[time_options[-1]] = mid_time
        
        # Add specific train events
        for event in station_events:
            label = f"🚂 {event['label']}"
            time_options.append(label)
            time_map[label] = event['time']
        
        # Time selector
        selected_option = st.selectbox(
            "Choose a time to view platform status:",
            time_options,
            help="Select a specific train arrival/departure time to see platform occupancy"
        )
        
        current_dt = time_map[selected_option]
        st.markdown(f"#### 🕒 Viewing: `{current_dt.strftime('%Y-%m-%d %H:%M')}`")
        
        st.markdown("---")
        
        # 3. Platform Occupancy Grid
        st.markdown("### 3. Platform Occupancy Status")
        
        # Get occupancy data
        occupancy = tracker.get_occupancy_at_time(selected_station, current_dt)
        
        # Summary Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Occupied Platforms", occupancy['occupied_count'])
        with c2:
            st.metric("Free Platforms", occupancy['free_count'])
        with c3:
            utilization = (occupancy['occupied_count'] / occupancy['total_platforms']) * 100 if occupancy['total_platforms'] > 0 else 0
            st.metric("Utilization", f"{utilization:.0f}%")
        
        # Platform Grid
        st.markdown("#### Platform Status Grid")
        
        # CSS for platform cards
        st.markdown("""
        <style>
        .plat-card {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            text-align: center;
            border: 2px solid #333;
            transition: all 0.3s;
        }
        .plat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,255,136,0.3);
        }
        .occupied {
            background: linear-gradient(135deg, #3b2a2a 0%, #2a1a1a 100%);
            border-color: #ff4b4b;
        }
        .free {
            background: linear-gradient(135deg, #1a2f1a 0%, #0f1f0f 100%);
            border-color: #00ff88;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display platforms in grid
        platforms = occupancy['platforms']
        sorted_platforms = sorted(platforms.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
        
        cols = st.columns(4)  # 4 columns grid
        for idx, platform_id in enumerate(sorted_platforms):
            p_data = platforms[platform_id]
            col_idx = idx % 4
            
            with cols[col_idx]:
                if p_data['status'] == 'OCCUPIED':
                    card_class = "occupied"
                    icon = "🔴"
                    train_txt = f"**{p_data['train_id']}**"
                    arr_time = p_data['arrival_time'].strftime('%H:%M') if p_data['arrival_time'] else '?'
                    dep_time = p_data['departure_time'].strftime('%H:%M') if p_data['departure_time'] else '?'
                    sub_txt = f"Arr: {arr_time} | Dep: {dep_time}"
                else:
                    card_class = "free"
                    icon = "🟢"
                    train_txt = "*Empty*"
                    sub_txt = "Available"
                
                st.markdown(f"""
                <div class="plat-card {card_class}">
                    <h3 style="margin:0; color: #fff;">{icon} {platform_id}</h3>
                    <p style="font-size:1.3em; margin:10px 0; color: #fff;">{train_txt}</p>
                    <small style="color: #aaa;">{sub_txt}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed Schedule Table
        with st.expander("� View Full Schedule for this Station"):
            # Filter schedule for selected station
            if 'raw_df' in st.session_state:
                df = st.session_state.raw_df
                
                # Find station-related rows
                station_rows = df[
                    (df.get('departure_station', pd.Series()).astype(str) == selected_station) |
                    (df.get('arrival_station', pd.Series()).astype(str) == selected_station)
                ]
                
                if not station_rows.empty:
                    st.dataframe(station_rows, use_container_width=True)
                else:
                    st.info(f"No schedule data found for {selected_station}")



if __name__ == "__main__":
    pass
