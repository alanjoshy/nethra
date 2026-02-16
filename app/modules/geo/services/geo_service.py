"""
Geospatial service layer - heatmap and cluster detection.
"""

from typing import Optional, List
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_MakeEnvelope, ST_Within, ST_X, ST_Y, ST_Centroid, ST_Collect
from geoalchemy2.elements import WKTElement

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.geo.schemas import (
    HeatmapCell,
    HeatmapResponse,
    ClusterResult,
    ClustersResponse,
)
from app.modules.geo.utils import SpatialUtils


class GeoService:
    """Service for geospatial intelligence operations."""
    
    @staticmethod
    async def generate_heatmap(
        db: AsyncSession,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        tags: Optional[List[str]] = None,
        grid_size_meters: int = 250,
    ) -> HeatmapResponse:
        """
        Generate crime density heatmap using spatial grid.
        
        Args:
            db: Database session
            min_lat: Bounding box minimum latitude
            min_lng: Bounding box minimum longitude
            max_lat: Bounding box maximum latitude
            max_lng: Bounding box maximum longitude
            from_date: Optional start date filter
            to_date: Optional end date filter
            tags: Optional tag filters
            grid_size_meters: Grid cell size in meters
            
        Returns:
            HeatmapResponse with grid cells and density levels
        """
        # Validate bounding box
        SpatialUtils.validate_bounding_box(min_lat, min_lng, max_lat, max_lng)
        
        # Generate grid cells
        grid_cells = SpatialUtils.create_grid_cells(
            min_lat, min_lng, max_lat, max_lng, grid_size_meters
        )
        
        # Base query with bounding box filter
        query = select(Incident).where(
            ST_Within(
                Incident.location,
                ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
            )
        )
        
        # Apply date filters
        if from_date:
            query = query.where(Incident.occurred_at >= from_date)
        if to_date:
            query = query.where(Incident.occurred_at <= to_date)
        
        # Apply tag filters if provided
        if tags:
            query = (
                query
                .join(IncidentTag, IncidentTag.incident_id == Incident.id)
                .join(Tag, Tag.id == IncidentTag.tag_id)
                .where(Tag.name.in_(tags))
            )
        
        # Execute query to get all incidents in bounds
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        # Convert incidents to lat/lng coordinates
        incident_coords = []
        for incident in incidents:
            if incident.location:
                # Extract lat/lng from Geography point
                lat_result = await db.execute(select(ST_Y(incident.location)))
                lng_result = await db.execute(select(ST_X(incident.location)))
                lat = lat_result.scalar()
                lng = lng_result.scalar()
                if lat is not None and lng is not None:
                    incident_coords.append((lat, lng))
        
        # Count incidents in each grid cell
        cell_counts = {}
        max_count = 0
        
        for cell_idx, (cell_min_lat, cell_min_lng, cell_max_lat, cell_max_lng, center_lat, center_lng) in enumerate(grid_cells):
            count = 0
            for lat, lng in incident_coords:
                if cell_min_lat <= lat <= cell_max_lat and cell_min_lng <= lng <= cell_max_lng:
                    count += 1
            
            cell_counts[cell_idx] = count
            max_count = max(max_count, count)
        
        # Build response cells
        heatmap_cells = []
        for cell_idx, (_, _, _, _, center_lat, center_lng) in enumerate(grid_cells):
            count = cell_counts.get(cell_idx, 0)
            if count > 0:  # Only include cells with incidents
                density_level = SpatialUtils.determine_density_level(count, max_count)
                heatmap_cells.append(
                    HeatmapCell(
                        center_lat=center_lat,
                        center_lng=center_lng,
                        incident_count=count,
                        density_level=density_level,
                    )
                )
        
        return HeatmapResponse(
            grid_size_meters=grid_size_meters,
            total_incidents=len(incident_coords),
            cells=heatmap_cells,
        )
    
    @staticmethod
    async def detect_clusters(
        db: AsyncSession,
        radius_meters: int = 500,
        min_points: int = 3,
        from_date: Optional[date] = None,
        tags: Optional[List[str]] = None,
    ) -> ClustersResponse:
        """
        Detect spatial crime clusters using DBSCAN.
        
        Args:
            db: Database session
            radius_meters: Clustering radius in meters
            min_points: Minimum points to form a cluster
            from_date: Optional date filter
            tags: Optional tag filters
            
        Returns:
            ClustersResponse with detected clusters
        """
        # Note: ST_ClusterDBSCAN requires PostGIS 2.3+
        # For now, implement a simplified version without window functions
        # In production, would use:
        # ST_ClusterDBSCAN(location, eps := radius, minpoints := min_points) OVER ()
        
        # Query incidents with filters
        query = select(
            Incident.id,
            ST_X(Incident.location).label("lng"),
            ST_Y(Incident.location).label("lat"),
        ).where(Incident.location.isnot(None))
        
        if from_date:
            query = query.where(Incident.occurred_at >= from_date)
        
        if tags:
            query = (
                query
                .join(IncidentTag, IncidentTag.incident_id == Incident.id)
                .join(Tag, Tag.id == IncidentTag.tag_id)
                .where(Tag.name.in_(tags))
            )
        
        result = await db.execute(query)
        incidents_data = result.all()
        
        if not incidents_data:
            return ClustersResponse(
                radius_meters=radius_meters,
                min_points=min_points,
                clusters=[],
            )
        
        # Simple clustering algorithm (density-based grouping)
        # Group incidents that are within radius of each other
        clusters_dict = {}
        cluster_id = 0
        assigned = set()
        
        for i, (inc_id, lng, lat) in enumerate(incidents_data):
            if inc_id in assigned:
                continue
            
            # Find all incidents within radius
            cluster_members = [(inc_id, lng, lat)]
            
            for j, (other_id, other_lng, other_lat) in enumerate(incidents_data):
                if other_id == inc_id or other_id in assigned:
                    continue
                
                # Calculate distance (simplified haversine)
                from math import radians, sin, cos, sqrt, atan2
                
                R = 6371000  # Earth radius in meters
                lat1, lng1 = radians(lat), radians(lng)
                lat2, lng2 = radians(other_lat), radians(other_lng)
                
                dlat = lat2 - lat1
                dlng = lng2 - lng1
                
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                distance = R * c
                
                if distance <= radius_meters:
                    cluster_members.append((other_id, other_lng, other_lat))
                    assigned.add(other_id)
            
            # Only form cluster if meets min_points threshold
            if len(cluster_members) >= min_points:
                assigned.add(inc_id)
                clusters_dict[cluster_id] = cluster_members
                cluster_id += 1
        
        # Build cluster results with centroids
        cluster_results = []
        for cid, members in clusters_dict.items():
            avg_lat = sum(m[2] for m in members) / len(members)
            avg_lng = sum(m[1] for m in members) / len(members)
            
            cluster_results.append(
                ClusterResult(
                    cluster_id=cid,
                    incident_count=len(members),
                    centroid={"lat": avg_lat, "lng": avg_lng},
                )
            )
        
        return ClustersResponse(
            radius_meters=radius_meters,
            min_points=min_points,
            clusters=cluster_results,
        )
