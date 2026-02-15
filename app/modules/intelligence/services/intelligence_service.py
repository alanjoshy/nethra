"""
Intelligence service - Business logic for geospatial and pattern search.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, and_, or_, cast
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_Distance
from geoalchemy2.elements import WKTElement

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.cases.entities.case_entity import Case
from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.persons.entities.person_entity import Person, CasePerson, PersonRole
from app.modules.intelligence.schemas import (
    RelatedCaseResponse,
    SuspectedPersonResponse,
    IntelligenceResponse,
)


class IntelligenceService:
    """
    Intelligence service.
    Handles advanced search and correlation logic.
    """
    
    @staticmethod
    async def find_related_cases(
        db: AsyncSession,
        lat: float,
        lon: float,
        radius_meters: float,
        tags: Optional[List[str]] = None,
    ) -> IntelligenceResponse:
        """
        Find related cases based on location, distance, and optional tags.
        """
        # Create point from lat/lon
        point = WKTElement(f"POINT({lon} {lat})", srid=4326)

        # 1. Base query: Find incidents within radius
        # We join with Case to ensure we only get incidents linked to cases
        query = (
            select(
                Case.id.label("case_id"),
                Incident.id.label("incident_id"),
                ST_Distance(Incident.location, point).label("distance_meters"),
            )
            .join(Case, Case.primary_incident_id == Incident.id)
            .where(
                ST_DWithin(Incident.location, point, radius_meters)
            )
        )

        # 2. Execute query to get basic matches
        result = await db.execute(query)
        matches = result.all()

        related_cases = []
        suspects_map = {}

        for match in matches:
            case_id = match.case_id
            incident_id = match.incident_id
            distance = match.distance_meters

            # Fetch tags for this incident
            tags_query = (
                select(Tag.name)
                .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                .where(IncidentTag.incident_id == incident_id)
            )
            tags_result = await db.execute(tags_query)
            incident_tags = [row[0] for row in tags_result.all()]

            # Filter by tags if provided
            matched_tags = []
            if tags:
                matched_tags = list(set(incident_tags) & set(tags))
                if not matched_tags:
                    continue # Skip if no matching tags and tags were requested? 
                    # Requirement says "Tags (optional)", usually implies filtering if present.
                    # Logic: If tags provided, MUST match at least one? Or just boost score?
                    # "Search cases by ... Pattern tags" -> implies filtering.
                    # Strict filtering:
                    # continue 
            else:
                matched_tags = incident_tags

            # Add to related cases
            related_cases.append(
                RelatedCaseResponse(
                    case_id=str(case_id),
                    incident_id=str(incident_id),
                    distance_meters=float(distance) if distance else 0.0,
                    matched_tags=matched_tags,
                )
            )

            # 3. Fetch Suspects for this case
            suspects_query = (
                select(Person)
                .join(CasePerson, CasePerson.person_id == Person.id)
                .where(
                    CasePerson.case_id == case_id,
                    CasePerson.role == PersonRole.SUSPECT
                )
            )
            suspects_result = await db.execute(suspects_query)
            suspects = suspects_result.scalars().all()

            for suspect in suspects:
                if suspect.id not in suspects_map:
                    suspects_map[suspect.id] = {
                        "person": suspect,
                        "cases_count": 0,
                        "matched_tags": set(),
                    }
                
                suspect_data = suspects_map[suspect.id]
                suspect_data["cases_count"] += 1
                suspect_data["matched_tags"].update(matched_tags)

        # 4. Format Suspects Response
        formatted_suspects = []
        for person_id, data in suspects_map.items():
            person = data["person"]
            matched_tags_list = list(data["matched_tags"])
            
            # Simple scoring logic
            # Score = (Tag Matches * 2) + (Case Count * 5)
            # This is a basic placeholder for "Scoring based on..."
            match_score = (len(matched_tags_list) * 2.0) + (data["cases_count"] * 5.0)

            formatted_suspects.append(
                SuspectedPersonResponse(
                    person_id=str(person.id),
                    name=person.name,
                    match_score=match_score,
                    cases_count=data["cases_count"],
                    matched_tags=matched_tags_list,
                )
            )

        # Sort suspects by score descending
        formatted_suspects.sort(key=lambda x: x.match_score, reverse=True)
        # Sort cases by distance ascending
        related_cases.sort(key=lambda x: x.distance_meters)

        return IntelligenceResponse(
            related_cases=related_cases,
            suspected_persons=formatted_suspects,
        )
