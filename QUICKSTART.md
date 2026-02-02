# Railway Digital Twin - Premium Edition 🚂

## Quick Start Guide

### 1. Install Dependencies

```bash
# Navigate to project directory
cd "c:\Users\annap\Desktop\Projects\finished-projects\Digital Twin–Based Railway"

# Install required packages
pip install -r requirements.txt
```

### 2. Launch Premium Dashboard

```bash
# Run the new premium dashboard
streamlit run dashboard/app_premium.py
```

### 3. Upload Your Dataset

The system supports:
- ✅ **CSV files** - Train schedules, logs, tracking data
- ✅ **JSON files** - Network topology, structured data
- ✅ **Excel files** - Any railway operational data

**Sample datasets included:**
- `data/sample_indian_railways.csv` - Train schedule data
- `data/sample_network_topology.json` - Network structure

### 4. Explore Features

#### 🏠 Home
- Overview of capabilities
- Quick start guide
- Load sample datasets

#### 📊 Upload Data
- Drag & drop any railway dataset
- **Auto-detection** of trains, stations, routes
- Data quality analysis
- Column mapping

#### 🗺️ Network View
- Interactive railway network map
- Real-time visualization
- Station details
- Route connections

#### 📈 Analytics
- Performance metrics (OTP, reliability)
- Circular gauges
- Trend analysis
- Delay tracking

#### ⏱️ Time-Traveler
- Historical replay (coming soon)
- Timeline controls
- Event playback

---

## What's New in Premium Edition

### 🎨 Modern Dark Theme
- Professional control center aesthetic
- Vibrant accent colors (green, blue, orange)
- Glassmorphism effects
- Smooth animations

### 🧠 Intelligent Data Processing
- **Auto-detects** any railway dataset format
- Identifies trains, stations, routes automatically
- Validates data quality
- Provides helpful suggestions

### 🗺️ Network Visualization
- Full railway network maps
- Interactive graph visualization
- Station node analysis
- Route connections

### 📊 Advanced Analytics
- Circular performance gauges
- KPI metrics
- Trend charts
- Predictive insights

---

## Dataset Format Examples

### Schedule Format (CSV)
```csv
train_id,departure_station,arrival_station,scheduled_time,actual_time,status
T001,Mumbai,Pune,08:00,08:05,DELAYED
T002,Delhi,Agra,06:00,06:00,ON_TIME
```

### Network Topology (JSON)
```json
{
  "stations": [
    {"station_id": "S001", "station_name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777}
  ],
  "routes": [
    {"from_station": "S001", "to_station": "S002", "distance_km": 150}
  ]
}
```

### Real-Time Tracking (CSV)
```csv
timestamp,train_id,latitude,longitude,speed,status
2024-01-01 10:00,T001,19.0760,72.8777,85,RUNNING
```

---

## System Architecture

```
📊 Upload Dataset
    ↓
🧠 Smart Analyzer (Auto-detect structure)
    ↓
🔄 Data Transformer (Unified format)
    ↓
🗺️ Network Builder (Graph construction)
    ↓
📈 Premium Dashboard (Visualization)
```

---

## Key Features

✅ **Upload ANY railway dataset** - CSV, JSON, Excel  
✅ **Auto-detection** - Trains, stations, routes identified automatically  
✅ **Network visualization** - Interactive maps with real-time data  
✅ **Performance analytics** - Circular gauges, KPIs, trends  
✅ **Premium UI** - Modern dark theme, professional design  
✅ **Data quality** - Automatic validation and reporting  

---

## Troubleshooting

### Dataset not detected properly?
- Ensure column names include keywords like: `train`, `station`, `time`, `status`
- Check data format (dates should be parseable)
- Review warnings in Upload Data page

### Network not displaying?
- Verify dataset has station/route information
- Check if stations have connections
- Try sample datasets first

### Performance issues?
- Large datasets (>10,000 rows) may take time to process
- Consider filtering data by date range
- Use data sampling for initial exploration

---

## Next Steps

1. **Try sample datasets** - Load included samples to see features
2. **Upload your data** - Test with your own railway datasets
3. **Explore analytics** - Check performance metrics and trends
4. **Customize** - Modify code to add specific features

---

## Support

For issues or questions:
- Check dataset format examples above
- Review error messages in Upload Data page
- Ensure all dependencies are installed

**Version:** 2.0 Premium  
**Status:** 🟢 Production Ready
