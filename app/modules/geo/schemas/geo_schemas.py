"""
Geospatial schemas for heatmap and cluster detection.
"""

from typing import List, Optional, Dict
from datetime import date
from pydantic import BaseModel, Field


# ============================================================================
# Heatmap Schemas
# ============================================================================

class HeatmapCell(BaseModel):
    """Individual heatmap grid cell."""
    
    center_lat: float = Field(description="Cell center latitude")
    center_lng: float = Field(description="Cell center longitude")
    incident_count: int = Field(description="Number of incidents in cell")
    density_level: str = Field(description="Density level: NONE, LOW, MEDIUM, HIGH")


class HeatmapResponse(BaseModel):
    """Crime heatmap response."""
    
    grid_size_meters: int = Field(description="Grid cell size in meters")
    total_incidents: int = Field(description="Total incidents in bounds")
    cells: List[HeatmapCell] = Field(default_factory=list)


# ============================================================================
# Cluster Detection Schemas
# ============================================================================

class ClusterResult(BaseModel):
    """Individual crime cluster result."""
    
    cluster_id: int = Field(description="Cluster identifier")
    incident_count: int = Field(description="Number of incidents in cluster")
    centroid: Dict[str, float] = Field(description="Cluster centroid {lat, lng}")


class ClustersResponse(BaseModel):
    """Crime clusters response."""
    
    radius_meters: int = Field(description="Search radius used for clustering")
    min_points: int = Field(description="Minimum points threshold")
    clusters: List[ClusterResult] = Field(default_factory=list)
