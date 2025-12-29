"""
Visual Simulation Component - Simple 2D schematic visualization.
Displays station layout with platforms, trains, signals, and gates.

⚠️ REPRESENTATION ONLY - Does not control logic.
"""

import plotly.graph_objects as go
from typing import List, Dict


class VisualSimulation:
    """
    Creates simple 2D schematic visualization of railway station.
    
    Components:
    - Station block
    - Platform tracks
    - Train markers
    - Signal/gate indicators
    
    ⚠️ DISPLAY ONLY - Does not control operations.
    """
    
    def __init__(self, platform_ids: List[str] = None):
        """
        Initialize visual simulation.
        
        Args:
            platform_ids: List of platform IDs
        """
        if platform_ids is None:
            platform_ids = ["P1", "P2", "P3"]
        
        self.platform_ids = platform_ids
        self.num_platforms = len(platform_ids)
        
    def create_station_layout(
        self,
        train_states: List[Dict],
        track_states: List[Dict],
        signal_states: List[Dict],
        gate_states: List[Dict]
    ) -> go.Figure:
        """
        Create complete station layout visualization.
        
        Args:
            train_states: List of train states
            track_states: List of track states
            signal_states: List of signal states
            gate_states: List of gate states
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Add platform tracks
        self._add_platforms(fig, track_states)
        
        # Add trains
        self._add_trains(fig, train_states, track_states)
        
        # Add signals
        self._add_signals(fig, signal_states)
        
        # Add gates
        self._add_gates(fig, gate_states)
        
        # Add station boundary
        self._add_station_boundary(fig)
        
        # Configure layout
        fig.update_layout(
            title="Railway Station Schematic View",
            xaxis=dict(
                title="Distance (km)",
                range=[-2, 22],
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title="Platforms",
                range=[-1, self.num_platforms],
                showgrid=True,
                gridcolor='lightgray',
                tickvals=list(range(self.num_platforms)),
                ticktext=self.platform_ids
            ),
            height=400,
            showlegend=True,
            hovermode='closest',
            plot_bgcolor='#f8f9fa'
        )
        
        return fig
    
    def _add_platforms(self, fig: go.Figure, track_states: List[Dict]) -> None:
        """Add platform tracks to visualization."""
        for idx, track in enumerate(track_states):
            state = track['state']
            
            # Color based on state
            if state == 'FREE':
                color = 'green'
            elif state == 'RESERVED':
                color = 'yellow'
            elif state == 'OCCUPIED':
                color = 'red'
            else:
                color = 'gray'
            
            # Draw platform track
            fig.add_trace(go.Scatter(
                x=[0, 20],
                y=[idx, idx],
                mode='lines',
                line=dict(color=color, width=8),
                name=f"{track['track_id']} ({state})",
                hovertemplate=f"<b>{track['track_id']}</b><br>State: {state}<br>Train: {track.get('allocated_to', 'None')}<extra></extra>"
            ))
            
            # Add platform label
            fig.add_annotation(
                x=-0.5,
                y=idx,
                text=track['track_id'],
                showarrow=False,
                font=dict(size=14, color='black', family='Arial Black')
            )
    
    def _add_trains(self, fig: go.Figure, train_states: List[Dict], track_states: List[Dict]) -> None:
        """Add train markers to visualization."""
        for train in train_states:
            train_id = train['id']
            position = train['position']
            
            # Find which platform this train is on/assigned to
            platform_idx = None
            for idx, track in enumerate(track_states):
                if track.get('allocated_to') == train_id:
                    platform_idx = idx
                    break
            
            if platform_idx is None:
                # Train not yet assigned, show on first available track
                platform_idx = 0
            
            # Determine train marker
            if position > 0:
                # Train is approaching
                x_pos = 20 - position  # Convert to visual position
                marker_symbol = 'arrow-right'
                marker_color = 'blue'
                status = 'Approaching'
            else:
                # Train on platform
                x_pos = 10  # Center of platform
                marker_symbol = 'square'
                marker_color = 'orange'
                status = 'On Platform'
            
            # Add train marker
            fig.add_trace(go.Scatter(
                x=[x_pos],
                y=[platform_idx],
                mode='markers+text',
                marker=dict(
                    symbol=marker_symbol,
                    size=15,
                    color=marker_color,
                    line=dict(color='black', width=2)
                ),
                text=train_id,
                textposition='top center',
                name=train_id,
                hovertemplate=f"<b>{train_id}</b><br>Position: {position:.2f} km<br>Speed: {train['speed']} kmph<br>Status: {status}<extra></extra>"
            ))
    
    def _add_signals(self, fig: go.Figure, signal_states: List[Dict]) -> None:
        """Add signal indicators to visualization."""
        for idx, signal in enumerate(signal_states):
            state = signal['state']
            
            # Color based on signal state
            if state == 'RED':
                color = 'red'
            elif state == 'YELLOW':
                color = 'yellow'
            elif state == 'GREEN':
                color = 'green'
            else:
                color = 'gray'
            
            # Add signal marker at platform entrance
            fig.add_trace(go.Scatter(
                x=[0.5],
                y=[idx],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color=color,
                    line=dict(color='black', width=1)
                ),
                name=f"Signal {signal['signal_id']}",
                hovertemplate=f"<b>{signal['signal_id']}</b><br>State: {state}<extra></extra>",
                showlegend=False
            ))
    
    def _add_gates(self, fig: go.Figure, gate_states: List[Dict]) -> None:
        """Add gate indicators to visualization."""
        for idx, gate in enumerate(gate_states):
            state = gate['state']
            
            # Color based on gate state
            if state == 'OPEN':
                color = 'green'
            elif state == 'CLOSING':
                color = 'orange'
            elif state == 'CLOSED':
                color = 'red'
            else:
                color = 'gray'
            
            # Add gate marker
            y_pos = -0.5  # Below platforms
            x_pos = 15 + (idx * 2)  # Spread gates horizontally
            
            fig.add_trace(go.Scatter(
                x=[x_pos],
                y=[y_pos],
                mode='markers+text',
                marker=dict(
                    symbol='x',
                    size=15,
                    color=color,
                    line=dict(color='black', width=2)
                ),
                text=gate['gate_id'],
                textposition='bottom center',
                name=f"Gate {gate['gate_id']}",
                hovertemplate=f"<b>{gate['gate_id']}</b><br>State: {state}<br>Distance: {gate.get('distance', 0):.0f}m<extra></extra>",
                showlegend=False
            ))
    
    def _add_station_boundary(self, fig: go.Figure) -> None:
        """Add station boundary box."""
        # Station boundary rectangle
        fig.add_shape(
            type="rect",
            x0=0, y0=-0.8,
            x1=20, y1=self.num_platforms - 0.2,
            line=dict(color="navy", width=3, dash="dash"),
            fillcolor="rgba(173, 216, 230, 0.1)"
        )
        
        # Station label
        fig.add_annotation(
            x=10,
            y=self.num_platforms - 0.5,
            text="STATION AREA",
            showarrow=False,
            font=dict(size=16, color='navy', family='Arial Black')
        )


if __name__ == "__main__":
    # Test visualization
    print("\nVisual Simulation Test\n")
    
    # Sample data
    trains = [
        {'id': 'T001', 'position': 5.0, 'speed': 80},
        {'id': 'T002', 'position': 0.0, 'speed': 0}
    ]
    
    tracks = [
        {'track_id': 'P1', 'state': 'RESERVED', 'allocated_to': 'T001'},
        {'track_id': 'P2', 'state': 'OCCUPIED', 'allocated_to': 'T002'},
        {'track_id': 'P3', 'state': 'FREE', 'allocated_to': None}
    ]
    
    signals = [
        {'signal_id': 'S1', 'state': 'YELLOW'},
        {'signal_id': 'S2', 'state': 'RED'},
        {'signal_id': 'S3', 'state': 'GREEN'}
    ]
    
    gates = [
        {'gate_id': 'G1', 'state': 'CLOSED', 'distance': 450}
    ]
    
    vis = VisualSimulation()
    fig = vis.create_station_layout(trains, tracks, signals, gates)
    
    print("✓ Visualization created")
    print("  Use fig.show() to display in browser")
