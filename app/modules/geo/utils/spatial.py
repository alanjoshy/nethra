"""
Spatial utilities for geospatial operations.
"""

from typing import List, Tuple
from math import radians, sin, cos, sqrt, atan2


class SpatialUtils:
    """Utilities for geospatial calculations and grid operations."""
    
    @staticmethod
    def validate_bounding_box(
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float
    ) -> None:
        """
        Validate bounding box coordinates.
        
        Args:
            min_lat: Minimum latitude
            min_lng: Minimum longitude
            max_lat: Maximum latitude
            max_lng: Maximum longitude
            
        Raises:
            ValueError: If coordinates are invalid
        """
        if not (-90 <= min_lat <= 90):
            raise ValueError(f"Invalid min_lat: {min_lat}. Must be between -90 and 90")
        if not (-90 <= max_lat <= 90):
            raise ValueError(f"Invalid max_lat: {max_lat}. Must be between -90 and 90")
        if not (-180 <= min_lng <= 180):
            raise ValueError(f"Invalid min_lng: {min_lng}. Must be between -180 and 180")
        if not (-180 <= max_lng <= 180):
            raise ValueError(f"Invalid max_lng: {max_lng}. Must be between -180 and 180")
        
        if min_lat >= max_lat:
            raise ValueError(f"min_lat ({min_lat}) must be less than max_lat ({max_lat})")
        if min_lng >= max_lng:
            raise ValueError(f"min_lng ({min_lng}) must be less than max_lng ({max_lng})")
    
    @staticmethod
    def calculate_grid_dimensions(
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        grid_size_meters: int = 250
    ) -> Tuple[int, int, float, float]:
        """
        Calculate grid dimensions for heatmap.
        
        Args:
            min_lat: Minimum latitude
            min_lng: Minimum longitude
            max_lat: Maximum latitude
            max_lng: Maximum longitude
            grid_size_meters: Grid cell size in meters
            
        Returns:
            Tuple of (rows, cols, lat_step, lng_step)
        """
        # Approximate conversion: 1 degree latitude ~ 111km
        # 1 degree longitude varies by latitude, using average
        avg_lat = (min_lat + max_lat) / 2
        lat_per_meter = 1 / 111000  # degrees per meter for latitude
        lng_per_meter = 1 / (111000 * cos(radians(avg_lat)))  # degrees per meter for longitude
        
        lat_step = grid_size_meters * lat_per_meter
        lng_step = grid_size_meters * lng_per_meter
        
        lat_range = max_lat - min_lat
        lng_range = max_lng - min_lng
        
        rows = max(1, int(lat_range / lat_step))
        cols = max(1, int(lng_range / lng_step))
        
        # Limit grid size to prevent excessive computation
        max_cells = 100
        if rows * cols > max_cells:
            # Scale down grid
            scale = sqrt(max_cells / (rows * cols))
            rows = max(1, int(rows * scale))
            cols = max(1, int(cols * scale))
            lat_step = lat_range / rows
            lng_step = lng_range / cols
        
        return rows, cols, lat_step, lng_step
    
    @staticmethod
    def create_grid_cells(
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        grid_size_meters: int = 250
    ) -> List[Tuple[float, float, float, float, float, float]]:
        """
        Generate grid cells for heatmap.
        
        Args:
            min_lat: Minimum latitude
            min_lng: Minimum longitude
            max_lat: Maximum latitude
            max_lng: Maximum longitude
            grid_size_meters: Grid cell size in meters
            
        Returns:
            List of tuples: (cell_min_lat, cell_min_lng, cell_max_lat, cell_max_lng, center_lat, center_lng)
        """
        rows, cols, lat_step, lng_step = SpatialUtils.calculate_grid_dimensions(
            min_lat, min_lng, max_lat, max_lng, grid_size_meters
        )
        
        cells = []
        for row in range(rows):
            for col in range(cols):
                cell_min_lat = min_lat + (row * lat_step)
                cell_max_lat = min(min_lat + ((row + 1) * lat_step), max_lat)
                cell_min_lng = min_lng + (col * lng_step)
                cell_max_lng = min(min_lng + ((col + 1) * lng_step), max_lng)
                
                center_lat = (cell_min_lat + cell_max_lat) / 2
                center_lng = (cell_min_lng + cell_max_lng) / 2
                
                cells.append((
                    cell_min_lat,
                    cell_min_lng,
                    cell_max_lat,
                    cell_max_lng,
                    center_lat,
                    center_lng
                ))
        
        return cells
    
    @staticmethod
    def determine_density_level(count: int, max_count: int) -> str:
        """
        Determine density level based on count distribution.
        
        Args:
            count: Incident count in cell
            max_count: Maximum count across all cells
            
        Returns:
            Density level: LOW, MEDIUM, HIGH
        """
        if count == 0:
            return "NONE"
        
        if max_count == 0:
            return "LOW"
        
        ratio = count / max_count
        
        if ratio >= 0.6:
            return "HIGH"
        elif ratio >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
