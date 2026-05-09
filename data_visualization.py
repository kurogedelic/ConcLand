"""
Advanced Data Visualization for ConcLand
Real-time charts, graphs, and data displays for city statistics
"""

import pyxel
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

class ChartType(Enum):
    LINE = "line"
    AREA = "area"
    BAR = "bar"
    STACKED_BAR = "stacked_bar"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    RADAR = "radar"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    CANDLESTICK = "candlestick"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"

@dataclass
class DataSeries:
    """Data series for charts"""
    name: str
    values: List[float]
    color: int
    style: str = "solid"  # solid, dashed, dotted
    marker: str = "circle"  # circle, square, triangle, none
    visible: bool = True

@dataclass
class ChartConfig:
    """Configuration for charts"""
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    show_grid: bool = True
    show_legend: bool = True
    show_values: bool = False
    animation: bool = True
    interactive: bool = True
    
    # Axes
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    auto_scale: bool = True
    
    # Style
    bg_color: int = 0
    fg_color: int = 7
    grid_color: int = 5
    text_color: int = 7
    
    # Layout
    margin_top: int = 20
    margin_bottom: int = 20
    margin_left: int = 30
    margin_right: int = 20

class Chart:
    """Base chart class"""
    
    def __init__(self, x: int, y: int, width: int, height: int, config: ChartConfig):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.config = config
        self.data_series: List[DataSeries] = []
        
        # Animation state
        self.animation_progress = 0.0
        self.animation_speed = 0.05
        
        # Interaction state
        self.hover_point = None
        self.selected_series = None
        
        # Calculate plot area
        self.plot_x = x + config.margin_left
        self.plot_y = y + config.margin_top
        self.plot_width = width - config.margin_left - config.margin_right
        self.plot_height = height - config.margin_top - config.margin_bottom
    
    def add_series(self, series: DataSeries):
        """Add a data series"""
        self.data_series.append(series)
    
    def update(self):
        """Update chart animation"""
        if self.config.animation and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
    
    def draw(self):
        """Draw the chart"""
        # Draw background
        pyxel.rect(self.x, self.y, self.width, self.height, self.config.bg_color)
        
        # Draw title
        if self.config.title:
            title_x = self.x + self.width // 2 - len(self.config.title) * 2
            title_y = self.y + 5
            pyxel.text(title_x, title_y, self.config.title, self.config.text_color)
        
        # Draw grid
        if self.config.show_grid:
            self._draw_grid()
        
        # Draw axes
        self._draw_axes()
        
        # Draw data (implemented by subclasses)
        self._draw_data()
        
        # Draw legend
        if self.config.show_legend and self.data_series:
            self._draw_legend()
    
    def _draw_grid(self):
        """Draw grid lines"""
        # Vertical grid lines
        grid_x_step = self.plot_width // 10
        for i in range(11):
            x = self.plot_x + i * grid_x_step
            pyxel.line(x, self.plot_y, x, self.plot_y + self.plot_height, self.config.grid_color)
        
        # Horizontal grid lines
        grid_y_step = self.plot_height // 10
        for i in range(11):
            y = self.plot_y + i * grid_y_step
            pyxel.line(self.plot_x, y, self.plot_x + self.plot_width, y, self.config.grid_color)
    
    def _draw_axes(self):
        """Draw chart axes"""
        # X axis
        pyxel.line(self.plot_x, self.plot_y + self.plot_height,
                  self.plot_x + self.plot_width, self.plot_y + self.plot_height,
                  self.config.fg_color)
        
        # Y axis
        pyxel.line(self.plot_x, self.plot_y,
                  self.plot_x, self.plot_y + self.plot_height,
                  self.config.fg_color)
        
        # X label
        if self.config.x_label:
            label_x = self.plot_x + self.plot_width // 2 - len(self.config.x_label) * 2
            label_y = self.y + self.height - 5
            pyxel.text(label_x, label_y, self.config.x_label, self.config.text_color)
        
        # Y label (rotated - simplified)
        if self.config.y_label:
            label_x = self.x + 2
            label_y = self.plot_y + self.plot_height // 2
            pyxel.text(label_x, label_y, self.config.y_label, self.config.text_color)
    
    def _draw_legend(self):
        """Draw chart legend"""
        legend_x = self.plot_x + self.plot_width + 5
        legend_y = self.plot_y
        
        for i, series in enumerate(self.data_series):
            if not series.visible:
                continue
            
            # Color box
            pyxel.rect(legend_x, legend_y + i * 10, 8, 6, series.color)
            
            # Series name
            pyxel.text(legend_x + 10, legend_y + i * 10, series.name[:8], self.config.text_color)
    
    def _draw_data(self):
        """Draw chart data (override in subclasses)"""
        pass

class LineChart(Chart):
    """Line chart implementation"""
    
    def _draw_data(self):
        """Draw line chart data"""
        for series in self.data_series:
            if not series.visible or not series.values:
                continue
            
            # Calculate points
            points = []
            x_step = self.plot_width / (len(series.values) - 1) if len(series.values) > 1 else 0
            
            # Find data range
            y_min = min(series.values)
            y_max = max(series.values)
            y_range = y_max - y_min if y_max != y_min else 1
            
            for i, value in enumerate(series.values):
                x = self.plot_x + i * x_step
                y_normalized = (value - y_min) / y_range
                
                # Apply animation
                if self.config.animation:
                    y_normalized *= self.animation_progress
                
                y = self.plot_y + self.plot_height - y_normalized * self.plot_height
                points.append((int(x), int(y)))
            
            # Draw lines
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                
                if series.style == "dashed" and i % 2 == 0:
                    continue
                elif series.style == "dotted" and i % 3 != 0:
                    continue
                
                pyxel.line(x1, y1, x2, y2, series.color)
            
            # Draw markers
            if series.marker != "none":
                for x, y in points:
                    if series.marker == "circle":
                        pyxel.circ(x, y, 2, series.color)
                    elif series.marker == "square":
                        pyxel.rect(x - 2, y - 2, 4, 4, series.color)
                    elif series.marker == "triangle":
                        pyxel.tri(x, y - 2, x - 2, y + 2, x + 2, y + 2, series.color)
            
            # Draw values
            if self.config.show_values:
                for i, (x, y) in enumerate(points):
                    value_text = f"{series.values[i]:.0f}"
                    pyxel.text(x - len(value_text) * 2, y - 8, value_text, self.config.text_color)

class BarChart(Chart):
    """Bar chart implementation"""
    
    def _draw_data(self):
        """Draw bar chart data"""
        if not self.data_series:
            return
        
        num_series = len([s for s in self.data_series if s.visible])
        if num_series == 0:
            return
        
        # Calculate bar dimensions
        total_bars = sum(len(s.values) for s in self.data_series if s.visible)
        bar_width = self.plot_width // (total_bars + num_series)
        bar_spacing = 2
        
        x_offset = self.plot_x
        
        for series in self.data_series:
            if not series.visible or not series.values:
                continue
            
            # Find data range
            y_max = max(max(series.values), 1)
            
            for i, value in enumerate(series.values):
                # Calculate bar height
                bar_height = (value / y_max) * self.plot_height
                
                # Apply animation
                if self.config.animation:
                    bar_height *= self.animation_progress
                
                bar_x = x_offset
                bar_y = self.plot_y + self.plot_height - bar_height
                
                # Draw bar
                pyxel.rect(bar_x, bar_y, bar_width - bar_spacing, bar_height, series.color)
                
                # Draw value
                if self.config.show_values:
                    value_text = f"{value:.0f}"
                    text_x = bar_x + (bar_width - bar_spacing) // 2 - len(value_text) * 2
                    text_y = bar_y - 8
                    pyxel.text(text_x, text_y, value_text, self.config.text_color)
                
                x_offset += bar_width
            
            x_offset += bar_spacing * 2

class PieChart(Chart):
    """Pie chart implementation"""
    
    def _draw_data(self):
        """Draw pie chart data"""
        if not self.data_series or not self.data_series[0].values:
            return
        
        values = self.data_series[0].values
        total = sum(values)
        if total == 0:
            return
        
        # Center and radius
        cx = self.plot_x + self.plot_width // 2
        cy = self.plot_y + self.plot_height // 2
        radius = min(self.plot_width, self.plot_height) // 3
        
        # Apply animation to radius
        if self.config.animation:
            radius = int(radius * self.animation_progress)
        
        # Draw slices
        start_angle = 0
        colors = [8, 10, 11, 12, 14, 2, 3, 4, 5, 6]  # Default color palette
        
        for i, value in enumerate(values):
            # Calculate slice angle
            slice_angle = (value / total) * 360
            end_angle = start_angle + slice_angle
            
            # Draw slice (simplified using lines from center)
            color = colors[i % len(colors)]
            
            for angle in range(int(start_angle), int(end_angle)):
                rad = math.radians(angle)
                x = cx + int(radius * math.cos(rad))
                y = cy + int(radius * math.sin(rad))
                pyxel.line(cx, cy, x, y, color)
            
            # Draw percentage
            if self.config.show_values and slice_angle > 20:  # Only show for large slices
                mid_angle = start_angle + slice_angle / 2
                rad = math.radians(mid_angle)
                text_x = cx + int(radius * 0.7 * math.cos(rad))
                text_y = cy + int(radius * 0.7 * math.sin(rad))
                percentage = f"{value/total*100:.0f}%"
                pyxel.text(text_x - len(percentage) * 2, text_y - 3, percentage, 7)
            
            start_angle = end_angle

class RadarChart(Chart):
    """Radar/Spider chart implementation"""
    
    def _draw_data(self):
        """Draw radar chart data"""
        if not self.data_series:
            return
        
        # Center and radius
        cx = self.plot_x + self.plot_width // 2
        cy = self.plot_y + self.plot_height // 2
        radius = min(self.plot_width, self.plot_height) // 3
        
        # Apply animation
        if self.config.animation:
            radius = int(radius * self.animation_progress)
        
        # Draw grid circles
        for i in range(1, 6):
            r = radius * i // 5
            pyxel.circb(cx, cy, r, self.config.grid_color)
        
        # Draw axes
        num_axes = len(self.data_series[0].values) if self.data_series and self.data_series[0].values else 0
        if num_axes < 3:
            return
        
        angle_step = 360 / num_axes
        
        for i in range(num_axes):
            angle = math.radians(i * angle_step - 90)
            x = cx + int(radius * math.cos(angle))
            y = cy + int(radius * math.sin(angle))
            pyxel.line(cx, cy, x, y, self.config.grid_color)
        
        # Draw data
        for series in self.data_series:
            if not series.visible or not series.values:
                continue
            
            # Normalize values
            max_value = max(series.values) if series.values else 1
            
            # Calculate points
            points = []
            for i, value in enumerate(series.values):
                angle = math.radians(i * angle_step - 90)
                r = radius * (value / max_value)
                
                # Apply animation
                if self.config.animation:
                    r *= self.animation_progress
                
                x = cx + int(r * math.cos(angle))
                y = cy + int(r * math.sin(angle))
                points.append((x, y))
            
            # Draw polygon
            if len(points) >= 3:
                for i in range(len(points)):
                    x1, y1 = points[i]
                    x2, y2 = points[(i + 1) % len(points)]
                    pyxel.line(x1, y1, x2, y2, series.color)
                
                # Draw points
                for x, y in points:
                    pyxel.circ(x, y, 2, series.color)

class HeatMap(Chart):
    """Heat map implementation"""
    
    def __init__(self, x: int, y: int, width: int, height: int, config: ChartConfig):
        super().__init__(x, y, width, height, config)
        self.data_matrix: List[List[float]] = []
        self.color_scale = self._create_color_scale()
    
    def _create_color_scale(self) -> List[int]:
        """Create color scale for heat map"""
        # Blue -> Green -> Yellow -> Red
        return [1, 5, 3, 11, 10, 9, 8]
    
    def set_data(self, data: List[List[float]]):
        """Set heat map data"""
        self.data_matrix = data
    
    def _draw_data(self):
        """Draw heat map data"""
        if not self.data_matrix:
            return
        
        rows = len(self.data_matrix)
        cols = len(self.data_matrix[0]) if rows > 0 else 0
        
        if rows == 0 or cols == 0:
            return
        
        # Calculate cell size
        cell_width = self.plot_width // cols
        cell_height = self.plot_height // rows
        
        # Find data range
        flat_data = [val for row in self.data_matrix for val in row]
        min_val = min(flat_data) if flat_data else 0
        max_val = max(flat_data) if flat_data else 1
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Draw cells
        for row in range(rows):
            for col in range(cols):
                value = self.data_matrix[row][col]
                
                # Normalize value
                norm_value = (value - min_val) / val_range
                
                # Apply animation
                if self.config.animation:
                    norm_value *= self.animation_progress
                
                # Map to color
                color_idx = int(norm_value * (len(self.color_scale) - 1))
                color = self.color_scale[color_idx]
                
                # Draw cell
                cell_x = self.plot_x + col * cell_width
                cell_y = self.plot_y + row * cell_height
                pyxel.rect(cell_x, cell_y, cell_width - 1, cell_height - 1, color)
                
                # Draw value
                if self.config.show_values and cell_width > 15 and cell_height > 10:
                    value_text = f"{value:.0f}"
                    text_x = cell_x + cell_width // 2 - len(value_text) * 2
                    text_y = cell_y + cell_height // 2 - 3
                    pyxel.text(text_x, text_y, value_text, 7)

class RealTimeChart:
    """Real-time scrolling chart"""
    
    def __init__(self, x: int, y: int, width: int, height: int, max_points: int = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_points = max_points
        
        # Data buffers
        self.data_buffers: Dict[str, deque] = {}
        self.series_colors: Dict[str, int] = {}
        self.series_visible: Dict[str, bool] = {}
        
        # Display range
        self.y_min = 0
        self.y_max = 100
        self.auto_scale = True
        
        # Grid
        self.show_grid = True
        self.grid_color = 5
        
        # Update counter
        self.update_counter = 0
    
    def add_series(self, name: str, color: int):
        """Add a data series"""
        self.data_buffers[name] = deque(maxlen=self.max_points)
        self.series_colors[name] = color
        self.series_visible[name] = True
    
    def add_point(self, series_name: str, value: float):
        """Add a data point to a series"""
        if series_name in self.data_buffers:
            self.data_buffers[series_name].append(value)
            
            # Auto-scale if enabled
            if self.auto_scale:
                all_values = [v for buffer in self.data_buffers.values() for v in buffer]
                if all_values:
                    self.y_min = min(all_values) * 0.9
                    self.y_max = max(all_values) * 1.1
    
    def draw(self):
        """Draw the real-time chart"""
        # Draw background
        pyxel.rect(self.x, self.y, self.width, self.height, 0)
        pyxel.rectb(self.x, self.y, self.width, self.height, 7)
        
        # Draw grid
        if self.show_grid:
            # Horizontal lines
            for i in range(5):
                y = self.y + i * self.height // 4
                pyxel.line(self.x, y, self.x + self.width, y, self.grid_color)
        
        # Draw data
        for series_name, buffer in self.data_buffers.items():
            if not self.series_visible[series_name] or len(buffer) < 2:
                continue
            
            color = self.series_colors[series_name]
            x_step = self.width / self.max_points
            
            # Draw lines
            for i in range(len(buffer) - 1):
                # Calculate positions
                x1 = self.x + i * x_step
                x2 = self.x + (i + 1) * x_step
                
                # Normalize values
                y_range = self.y_max - self.y_min if self.y_max != self.y_min else 1
                y1_norm = (buffer[i] - self.y_min) / y_range
                y2_norm = (buffer[i + 1] - self.y_min) / y_range
                
                y1 = self.y + self.height - y1_norm * self.height
                y2 = self.y + self.height - y2_norm * self.height
                
                pyxel.line(int(x1), int(y1), int(x2), int(y2), color)
        
        # Draw current values
        y_offset = self.y + 2
        for series_name, buffer in self.data_buffers.items():
            if buffer and self.series_visible[series_name]:
                current_value = buffer[-1]
                color = self.series_colors[series_name]
                text = f"{series_name}: {current_value:.1f}"
                pyxel.text(self.x + 2, y_offset, text, color)
                y_offset += 8

# Dashboard class combining multiple visualizations
class Dashboard:
    """Dashboard combining multiple charts"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Create charts
        self.charts = {}
        self._create_default_layout()
    
    def _create_default_layout(self):
        """Create default dashboard layout"""
        # Quarter sections
        quarter_w = self.width // 2
        quarter_h = self.height // 2
        
        # Top left - Line chart
        config1 = ChartConfig(title="Population Trend", show_legend=True)
        self.charts["population"] = LineChart(
            self.x, self.y, quarter_w - 2, quarter_h - 2, config1
        )
        
        # Top right - Bar chart
        config2 = ChartConfig(title="Zone Distribution", show_values=True)
        self.charts["zones"] = BarChart(
            self.x + quarter_w, self.y, quarter_w - 2, quarter_h - 2, config2
        )
        
        # Bottom left - Pie chart
        config3 = ChartConfig(title="Budget Breakdown", show_values=True)
        self.charts["budget"] = PieChart(
            self.x, self.y + quarter_h, quarter_w - 2, quarter_h - 2, config3
        )
        
        # Bottom right - Real-time chart
        self.charts["realtime"] = RealTimeChart(
            self.x + quarter_w, self.y + quarter_h, 
            quarter_w - 2, quarter_h - 2, 50
        )
    
    def update(self):
        """Update all charts"""
        for chart in self.charts.values():
            if hasattr(chart, 'update'):
                chart.update()
    
    def draw(self):
        """Draw the dashboard"""
        # Draw background
        pyxel.rect(self.x, self.y, self.width, self.height, 1)
        
        # Draw all charts
        for chart in self.charts.values():
            chart.draw()

# Test function
def test_visualization():
    """Test data visualization"""
    pyxel.init(400, 300, title="Data Visualization Test")
    
    # Create dashboard
    dashboard = Dashboard(5, 5, 390, 290)
    
    # Add sample data
    # Population trend
    pop_series = DataSeries("Population", 
                           [100, 150, 200, 280, 350, 420, 500, 580, 650, 700],
                           12)
    dashboard.charts["population"].add_series(pop_series)
    
    # Zone distribution
    zone_series = DataSeries("Zones", [30, 45, 25, 60, 40], 10)
    dashboard.charts["zones"].add_series(zone_series)
    
    # Budget
    budget_series = DataSeries("Budget", [3000, 2000, 1500, 1000, 500], 8)
    dashboard.charts["budget"].add_series(budget_series)
    
    # Real-time data
    dashboard.charts["realtime"].add_series("Traffic", 10)
    dashboard.charts["realtime"].add_series("Power", 11)
    
    frame_count = 0
    
    def update():
        nonlocal frame_count
        frame_count += 1
        
        dashboard.update()
        
        # Add real-time data
        if frame_count % 10 == 0:
            import random
            dashboard.charts["realtime"].add_point("Traffic", 
                                                   50 + random.randint(-20, 20))
            dashboard.charts["realtime"].add_point("Power", 
                                                   70 + random.randint(-15, 15))
    
    def draw():
        pyxel.cls(0)
        dashboard.draw()
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_visualization()