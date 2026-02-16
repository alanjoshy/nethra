"""
Search service for unified advanced search across cases.
"""

from typing import Optional, List
from datetime import date
from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_X, ST_Y
from geoalchemy2.elements import WKTElement

from app.modules.cases.entities.case_entity import Case
from app.modules.incidents.entities.incident_entity import Incident
from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.persons.entities.person_entity import Person, CasePerson
from app.modules.search.schemas import SearchResultItem, SearchResponse


class SearchService:
    """Service for unified case search with multiple filters."""
    
    @staticmethod
    async def unified_search(
        db: AsyncSession,
        radius_km: Optional[float] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        tags: Optional[List[str]] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        suspect_name: Optional[str] = None,
        status: Optional[str] = None,
        assigned_officer: Optional[UUID] = None,
        limit: int = 20,
    ) -> SearchResponse:
        """
        Unified search with performance-first filtering strategy.
        
        Filter order:
        1. Bounding box/radius filter (if provided)
        2. Date range filter
        3. Status filter
        4. Tag join (if tags provided)
        5. Suspect join (if suspect_name provided)
        6. Officer filter
        7. Pagination
        
        Args:
            db: Database session
            radius_km: Geographic radius filter
            lat: Latitude (required with radius_km)
            lng: Longitude (required with radius_km)
            tags: Tag filters
            from_date: Start date
            to_date: End date
            suspect_name: Partial suspect name match
            status: Case status
            assigned_officer:Officer UUID
            limit: Maximum results
            
        Returns:
            SearchResponse with matching cases
        """
        # Build base query
        query = (
            select(Case, Incident)
            .join(Incident, Incident.id == Case.primary_incident_id)
        )
        
        # 1. Geospatial filter (if radius provided)
        if radius_km and lat is not None and lng is not None:
            radius_meters = radius_km * 1000
            point = WKTElement(f'POINT({lng} {lat})', srid=4326)
            query = query.where(
                ST_DWithin(Incident.location, point, radius_meters, use_spheroid=True)
            )
        
        # 2. Date range filter
        if from_date:
            query = query.where(Incident.occurred_at >= from_date)
        if to_date:
            query = query.where(Incident.occurred_at <= to_date)
        
        # 3. Status filter
        if status:
            query = query.where(Case.status == status)
        
        # 4. Tag filter (if provided)
        if tags:
            query = (
                query
                .join(IncidentTag, IncidentTag.incident_id == Incident.id)
                .join(Tag, Tag.id == IncidentTag.tag_id)
                .where(Tag.name.in_(tags))
            )
        
        # 5. Suspect name filter (if provided)
        if suspect_name:
            query = (
                query
                .join(CasePerson, CasePerson.case_id == Case.id)
                .join(Person, Person.id == CasePerson.person_id)
                .where(Person.name.ilike(f"%{suspect_name}%"))
            )
        
        # 6. Officer filter
        if assigned_officer:
            query = query.where(Case.assigned_to == assigned_officer)
        
        # Add limit
        query = query.limit(limit)
        
        # Execute query
        result = await db.execute(query)
        case_incident_pairs = result.all()
        
        # Build results
        search_results = []
        for case, incident in case_incident_pairs:
            # Fetch tags for incident
            tags_query = (
                select(Tag.name)
                .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                .where(IncidentTag.incident_id == incident.id)
            )
            tags_result = await db.execute(tags_query)
            incident_tags = [tag for tag, in tags_result.all()]
            
            # Fetch suspects for case
            suspects_query = (
                select(Person.name)
                .join(CasePerson, CasePerson.person_id == Person.id)
                .where(
                    and_(
                        CasePerson.case_id == case.id,
                        CasePerson.role == "suspect"
                    )
                )
            )
            suspects_result = await db.execute(suspects_query)
            suspect_names = [name for name, in suspects_result.all()]
            
            # Extract location coords
            lat_val = None
            lng_val = None
            if incident.location:
                lat_result = await db.execute(select(ST_Y(incident.location)))
                lng_result = await db.execute(select(ST_X(incident.location)))
                lat_val = lat_result.scalar()
                lng_val = lng_result.scalar()
            
            search_results.append(
                SearchResultItem(
                    case_id=str(case.id),
                    incident_type=incident.type,
                    occurred_at=incident.occurred_at,
                    location={"lat": lat_val or 0.0, "lng": lng_val or 0.0},
                    tags=incident_tags,
                    suspects=suspect_names,
                    status=case.status,
                )
            )
        
        return SearchResponse(
            total_results=len(search_results),
            results=search_results,
        )
