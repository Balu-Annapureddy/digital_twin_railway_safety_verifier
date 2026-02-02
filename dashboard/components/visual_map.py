"""
Visual Map Component - Generates 2D SVG visualization of the railway station.
"""

import streamlit as st

class VisualMap:
    @staticmethod
    def render(tracks, trains, signals, gates):
        """
        Render the station layout using SVG.
        
        Args:
            tracks: List of track dictionaries.
            trains: List of train dictionaries.
            signals: Dictionary of signal states.
            gates: Dictionary of gate states.
        """
        
        # SVG Configuration
        width = 800
        height = 400
        padding = 50
        track_spacing = 100
        track_start_x = 100
        track_end_x = 700
        
        svg_elements = []
        
        # Background
        svg_elements.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f0f2f6" />')
        
        # Draw Tracks (Platforms)
        # We assume 3 tracks based on the config: P1, P2, P3
        # Map track IDs to Y positions
        track_y_map = {}
        sorted_tracks = sorted([t['track_id'] for t in tracks])
        
        for i, track_id in enumerate(sorted_tracks):
            y_pos = padding + (i + 1) * track_spacing
            track_y_map[track_id] = y_pos
            
            # Draw Track Line
            svg_elements.append(f'''
                <line x1="{track_start_x}" y1="{y_pos}" x2="{track_end_x}" y2="{y_pos}" 
                      stroke="#555" stroke-width="4" stroke-dasharray="10,5" />
                <text x="{track_start_x - 40}" y="{y_pos + 5}" fill="#333" font-family="Arial" font-weight="bold">{track_id}</text>
            ''')
            
            # Draw Platform Rectangle
            svg_elements.append(f'''
                <rect x="{track_start_x + 100}" y="{y_pos - 15}" width="400" height="30" 
                      fill="#ddd" stroke="#999" opacity="0.5" />
                <text x="{track_start_x + 280}" y="{y_pos + 5}" fill="#666" font-family="Arial" font-size="12">Platform Area</text>
            ''')

        # Draw Signals
        for signal_id, signal_data in signals.items():
            track_id = signal_data['track_id']
            if track_id in track_y_map:
                y_pos = track_y_map[track_id]
                color_map = {'RED': '#ff4b4b', 'YELLOW': '#ffc107', 'GREEN': '#09ab3b'}
                fill_color = color_map.get(signal_data['state'], '#999')
                
                # Draw Signal on left side
                svg_elements.append(f'''
                    <circle cx="{track_start_x + 50}" cy="{y_pos - 20}" r="8" fill="{fill_color}" stroke="black" />
                    <line x1="{track_start_x + 50}" y1="{y_pos - 20}" x2="{track_start_x + 50}" y2="{y_pos}" stroke="black" stroke-width="2" />
                    <text x="{track_start_x + 40}" y="{y_pos - 35}" fill="#333" font-size="10">{signal_id}</text>
                ''')

        # Draw Gates (Assuming G1 affects all tracks or is a crossing)
        # For visualization, we'll place G1 as a vertical bar crossing all tracks at the end
        gate_x = track_end_x - 100
        for gate_id, gate_data in gates.items():
            state = gate_data['state']
            # Open = distinct rects, Closed = solid bar across
            color_map = {'OPEN': '#09ab3b', 'CLOSING': '#ffc107', 'CLOSED': '#ff4b4b'}
            fill_color = color_map.get(state, '#999')
            
            # Simple representation: A crossing line
            svg_elements.append(f'''
                <line x1="{gate_x}" y1="{padding}" x2="{gate_x}" y2="{height - padding}" 
                      stroke="{fill_color}" stroke-width="10" opacity="0.6" />
                <text x="{gate_x - 10}" y="{padding}" fill="#333" font-weight="bold">{gate_id}</text>
                <text x="{gate_x + 10}" y="{padding + 20}" fill="#333" font-size="10">{state}</text>
            ''')

        # Draw Trains
        for train in trains:
            # Determine Y position
            # If train is ON_PLATFORM, we know the track_id from previous logic in app.py
            # But here `trains` might just have status/position. 
            # We need to match train to track if possible.
            
            # In our data structure from app.py:
            # display_tracks has 'allocated_to' -> train_id
            
            track_owner = None
            for t in tracks:
                if t['allocated_to'] == train['id']:
                    track_owner = t['track_id']
                    break
            
            if track_owner and track_owner in track_y_map:
                y_pos = track_y_map[track_owner]
                # If on platform, center it. If moving, use position approximation?
                # For historical replay, we often lack exact position if it's not in the CSV.
                # We'll assume center of platform if status is OCCUPIED/ON_PLATFORM
                
                train_x = track_start_x + 300 # Center of platform
                
                color = "#3b82f6" # Blue train
                
                svg_elements.append(f'''
                    <rect x="{train_x - 40}" y="{y_pos - 12}" width="80" height="24" rx="5" fill="{color}" stroke="black" />
                    <text x="{train_x}" y="{y_pos + 5}" fill="white" font-family="Arial" font-weight="bold" text-anchor="middle" font-size="12">{train['id']}</text>
                ''')
            
            # Handle incoming/departing if we had position data mapping to pixels...
            # For this version, we focus on platform occupancy visualization as that's the core data we have.

        svg_content = f'<svg width="100%" viewBox="0 0 {width} {height}">' + "".join(svg_elements) + '</svg>'
        
        st.markdown(svg_content, unsafe_allow_html=True)
