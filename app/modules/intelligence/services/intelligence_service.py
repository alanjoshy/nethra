"""
Intelligence service - Business logic for Phase 1 intelligence analysis.
"""

from typing import Optional, List, Dict, Tuple
from uuid import UUID
from datetime import datetime, timedelta, date
from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_AsText
from geoalchemy2.elements import WKTElement
from collections import Counter

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.cases.entities.case_entity import Case
from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.persons.entities.person_entity import Person, CasePerson, PersonRole
from app.modules.intelligence.utils.scoring import ScoringUtils
from app.modules.intelligence.schemas import (
    RelatedCaseResult,
    RelatedCasesResponse,
    RepeatOffenderResult,
    RepeatOffendersResponse,
    TagCorrelation,
    SuspectPattern,
    PatternCorrelationResponse,
    BehaviorSimilarityResult,
    BehaviorSimilarityResponse,
    RiskBreakdown,
    RiskScoreResponse,
)
from app.common.exceptions import NotFoundError


class IntelligenceService:
    """Intelligence service for Phase 1 analysis."""
    
    @staticmethod
    async def find_related_cases(
        db: AsyncSession,
        case_id: UUID,
        radius_km: float = 5.0,
        days_range: int = 90,
        limit: int = 10,
    ) -> RelatedCasesResponse:
        """
        Find cases related to a reference case using multi-dimensional scoring.
        
        Scoring components:
        - Tag overlap (weight: 3)
        - Suspect overlap (weight: 4)
        - Geographic proximity (weight: 2)
        - Time similarity (weight: 1)
        """
        # 1. Fetch reference case and its incident
        ref_case_query = select(Case).where(Case.id == case_id)
        ref_case_result = await db.execute(ref_case_query)
        ref_case = ref_case_result.scalar_one_or_none()
        
        if not ref_case:
            raise NotFoundError(f"Case {case_id} not found")
        
        ref_incident_query = select(Incident).where(Incident.id == ref_case.primary_incident_id)
        ref_incident_result = await db.execute(ref_incident_query)
        ref_incident = ref_incident_result.scalar_one_or_none()
        
        if not ref_incident:
            raise NotFoundError(f"Incident for case {case_id} not found")
        
        # 2. Get reference case tags
        ref_tags_query = (
            select(Tag.name)
            .join(IncidentTag, IncidentTag.tag_id == Tag.id)
            .where(IncidentTag.incident_id == ref_incident.id)
        )
        ref_tags_result = await db.execute(ref_tags_query)
        ref_tags = [row[0] for row in ref_tags_result.all()]
        
        # 3. Get reference case suspects
        ref_suspects_query = (
            select(Person.id)
            .join(CasePerson, CasePerson.person_id == Person.id)
            .where(
                CasePerson.case_id == case_id,
                CasePerson.role == PersonRole.SUSPECT
            )
        )
        ref_suspects_result = await db.execute(ref_suspects_query)
        ref_suspect_ids = {row[0] for row in ref_suspects_result.all()}
        
        # 4. Find candidate cases within radius and time range
        radius_meters = radius_km * 1000
        time_cutoff = ref_incident.occurred_at - timedelta(days=days_range)
        
        candidates_query = (
            select(
                Case.id,
                Incident.id.label("incident_id"),
                Incident.location,
                Incident.occurred_at,
                ST_Distance(Incident.location, ref_incident.location).label("distance_meters")
            )
            .join(Case, Case.primary_incident_id == Incident.id)
            .where(
                and_(
                    Case.id != case_id,  # Exclude reference case itself
                    ST_DWithin(Incident.location, ref_incident.location, radius_meters),
                    Incident.occurred_at >= time_cutoff
                )
            )
            .limit(limit * 3)  # Get more candidates for scoring
        )
        
        candidates_result = await db.execute(candidates_query)
        candidates = candidates_result.all()
        
        # 5. Score each candidate
        scored_results = []
        
        for candidate in candidates:
            candidate_case_id = candidate.id
            candidate_incident_id = candidate.incident_id
            distance_meters = float(candidate.distance_meters) if candidate.distance_meters else 0.0
            distance_km = distance_meters / 1000.0
            
            # Get candidate tags
            candidate_tags_query = (
                select(Tag.name)
                .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                .where(IncidentTag.incident_id == candidate_incident_id)
            )
            candidate_tags_result = await db.execute(candidate_tags_query)
            candidate_tags = [row[0] for row in candidate_tags_result.all()]
            
            # Calculate tag overlap
            tag_overlap_count, _ = ScoringUtils.calculate_tag_overlap(ref_tags, candidate_tags)
            
            # Get candidate suspects
            candidate_suspects_query = (
                select(Person.id)
                .join(CasePerson, CasePerson.person_id == Person.id)
                .where(
                    CasePerson.case_id == candidate_case_id,
                    CasePerson.role == PersonRole.SUSPECT
                )
            )
            candidate_suspects_result = await db.execute(candidate_suspects_query)
            candidate_suspect_ids = {row[0] for row in candidate_suspects_result.all()}
            
            # Calculate suspect overlap
            suspect_overlap_count = len(ref_suspect_ids & candidate_suspect_ids)
            
            # Calculate time similarity
            time_similarity = ScoringUtils.calculate_temporal_similarity(
                ref_incident.occurred_at,
                candidate.occurred_at,
                max_days=days_range
            )
            
            # Calculate geographic score (inverse distance, max at 1km)
            geo_score = max(0, 1.0 - (distance_km / radius_km))
            
            # Calculate weighted composite score
            components = {
                "tag_overlap": (tag_overlap_count, 3),
                "suspect_overlap": (suspect_overlap_count, 4),
                "geo_proximity": (geo_score, 2),
                "time_similarity": (time_similarity, 1),
            }
            composite_score = ScoringUtils.calculate_weighted_score(components)
            
            scored_results.append(
                RelatedCaseResult(
                    case_id=str(candidate_case_id),
                    score=round(composite_score, 2),
                    distance_km=round(distance_km, 2),
                    tag_overlap_count=tag_overlap_count,
                    suspect_overlap_count=suspect_overlap_count,
                )
            )
        
        # 6. Sort by score descending and limit
        scored_results.sort(key=lambda x: x.score, reverse=True)
        scored_results = scored_results[:limit]
        
        return RelatedCasesResponse(
            reference_case_id=str(case_id),
            results=scored_results
        )
    
    @staticmethod
    async def find_repeat_offenders(
        db: AsyncSession,
        tags: Optional[List[str]] = None,
        radius_km: Optional[float] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        min_cases: int = 2,
    ) -> RepeatOffendersResponse:
        """
        Find persons involved in multiple cases with optional filtering.
        """
        # Base query: persons with case links
        query = (
            select(
                Person.id,
                Person.name,
                func.count(distinct(CasePerson.case_id)).label("case_count"),
                func.max(Incident.occurred_at).label("last_seen")
            )
            .join(CasePerson, CasePerson.person_id == Person.id)
            .join(Case, Case.id == CasePerson.case_id)
            .join(Incident, Incident.id == Case.primary_incident_id)
            .where(CasePerson.role == PersonRole.SUSPECT)
        )
        
        # Apply date filters
        if from_date:
            query = query.where(Incident.occurred_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.where(Incident.occurred_at <= datetime.combine(to_date, datetime.max.time()))
        
        # Apply tag filter
        if tags:
            query = query.join(IncidentTag, IncidentTag.incident_id == Incident.id)
            query = query.join(Tag, Tag.id == IncidentTag.tag_id)
            query = query.where(Tag.name.in_(tags))
        
        # Group and filter by min_cases
        query = query.group_by(Person.id, Person.name)
        query = query.having(func.count(distinct(CasePerson.case_id)) >= min_cases)
        
        result = await db.execute(query)
        offenders = result.all()
        
        # Calculate pattern matches for each offender
        results = []
        for offender in offenders:
            person_id = offender.id
            
            # Get all cases for this person
            person_cases_query = (
                select(Case.id)
                .join(CasePerson, CasePerson.case_id == Case.id)
                .where(
                    CasePerson.person_id == person_id,
                    CasePerson.role == PersonRole.SUSPECT
                )
            )
            person_cases_result = await db.execute(person_cases_query)
            person_case_ids = [row[0] for row in person_cases_result.all()]
            
            # Get tag patterns for these cases
            tag_patterns = []
            for case_id in person_case_ids:
                incident_query = select(Incident.id).join(Case).where(Case.id == case_id)
                incident_result = await db.execute(incident_query)
                incident_id = incident_result.scalar()
                
                tags_query = (
                    select(Tag.name)
                    .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                    .where(IncidentTag.incident_id == incident_id)
                )
                tags_result = await db.execute(tags_query)
                case_tags = sorted([row[0] for row in tags_result.all()])
                tag_patterns.append(tuple(case_tags))
            
            # Count pattern matches (cases with identical tag sets)
            pattern_counter = Counter(tag_patterns)
            pattern_match_count = sum(1 for count in pattern_counter.values() if count > 1)
            
            results.append(
                RepeatOffenderResult(
                    person_id=str(person_id),
                    name=offender.name,
                    case_count=offender.case_count,
                    pattern_match_count=pattern_match_count,
                    last_seen_date=offender.last_seen
                )
            )
        
        # Sort by case count descending
        results.sort(key=lambda x: x.case_count, reverse=True)
        
        return RepeatOffendersResponse(results=results)
    
    @staticmethod
    async def analyze_pattern_correlation(
        db: AsyncSession,
        case_id: Optional[UUID] = None,
        min_occurrence: int = 2,
    ) -> PatternCorrelationResponse:
        """
        Analyze tag co-occurrence patterns and suspect-to-pattern mappings.
        """
        # Get all incident-tag relationships
        tag_query = (
            select(IncidentTag.incident_id, Tag.name)
            .join(Tag, Tag.id == IncidentTag.tag_id)
        )
        
        # If case_id provided, filter to related incidents
        if case_id:
            # This is simplified - could expand to related cases within radius
            tag_query = tag_query.join(Incident).join(Case, Case.primary_incident_id == Incident.id)
            tag_query = tag_query.where(Case.id == case_id)
        
        tag_result = await db.execute(tag_query)
        incident_tags_raw = tag_result.all()
        
        # Group tags by incident
        incident_tags_map = {}
        for incident_id, tag_name in incident_tags_raw:
            if incident_id not in incident_tags_map:
                incident_tags_map[incident_id] = []
            incident_tags_map[incident_id].append(tag_name)
        
        # Find tag combinations (pairs and triplets)
        tag_combinations = []
        for incident_id, tags in incident_tags_map.items():
            sorted_tags = sorted(tags)
            if len(sorted_tags) >= 2:
                tag_combinations.append(tuple(sorted_tags))
        
        # Count occurrences
        combination_counter = Counter(tag_combinations)
        
        # Filter by min_occurrence
        tag_correlations = [
            TagCorrelation(
                tag_combination=list(combo),
                occurrence_count=count
            )
            for combo, count in combination_counter.items()
            if count >= min_occurrence
        ]
        
        # Sort by occurrence count descending
        tag_correlations.sort(key=lambda x: x.occurrence_count, reverse=True)
        
        # Suspect pattern mapping
        suspect_pattern_query = (
            select(
                Person.id,
                func.count(distinct(CasePerson.case_id)).label("pattern_frequency")
            )
            .join(CasePerson, CasePerson.person_id == Person.id)
            .where(CasePerson.role == PersonRole.SUSPECT)
            .group_by(Person.id)
            .having(func.count(distinct(CasePerson.case_id)) >= min_occurrence)
        )
        
        suspect_result = await db.execute(suspect_pattern_query)
        suspects = suspect_result.all()
        
        suspect_patterns = [
            SuspectPattern(
                person_id=str(suspect.id),
                pattern_score=float(suspect.pattern_frequency)
            )
            for suspect in suspects
        ]
        
        # Sort by pattern score descending
        suspect_patterns.sort(key=lambda x: x.pattern_score, reverse=True)
        
        return PatternCorrelationResponse(
            tag_correlations=tag_correlations,
            suspect_pattern_map=suspect_patterns
        )
    
    @staticmethod
    async def find_similar_cases_behavioral(
        db: AsyncSession,
        case_id: UUID,
        limit: int = 10,
    ) -> BehaviorSimilarityResponse:
        """
        Find cases with similar behavioral patterns.
        """
        # Get reference case
        ref_case_query = select(Case).where(Case.id == case_id)
        ref_case_result = await db.execute(ref_case_query)
        ref_case = ref_case_result.scalar_one_or_none()
        
        if not ref_case:
            raise NotFoundError(f"Case {case_id} not found")
        
        ref_incident_query = select(Incident).where(Incident.id == ref_case.primary_incident_id)
        ref_incident_result = await db.execute(ref_incident_query)
        ref_incident = ref_incident_result.scalar_one_or_none()
        
        # Get reference tags
        ref_tags_query = (
            select(Tag.name)
            .join(IncidentTag, IncidentTag.tag_id == Tag.id)
            .where(IncidentTag.incident_id == ref_incident.id)
        )
        ref_tags_result = await db.execute(ref_tags_query)
        ref_tags = [row[0] for row in ref_tags_result.all()]
        
        # Extract reference time patterns
        ref_patterns = ScoringUtils.extract_time_patterns([ref_incident])
        
        # Get all other cases
        all_cases_query = (
            select(Case.id, Incident)
            .join(Incident, Incident.id == Case.primary_incident_id)
            .where(Case.id != case_id)
        )
        all_cases_result = await db.execute(all_cases_query)
        all_cases = all_cases_result.all()
        
        # Score each case
        scored_results = []
        
        for other_case_id, other_incident in all_cases:
            # Get tags
            other_tags_query = (
                select(Tag.name)
                .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                .where(IncidentTag.incident_id == other_incident.id)
            )
            other_tags_result = await db.execute(other_tags_query)
            other_tags = [row[0] for row in other_tags_result.all()]
            
            # Calculate tag similarity
            tag_overlap_count, _ = ScoringUtils.calculate_tag_overlap(ref_tags, other_tags)
            tag_similarity = tag_overlap_count / max(len(ref_tags), len(other_tags)) if (ref_tags or other_tags) else 0.0
            
            # Calculate time pattern similarity
            other_patterns = ScoringUtils.extract_time_patterns([other_incident])
            time_similarity = ScoringUtils.calculate_pattern_similarity(ref_patterns, other_patterns)
            
            # Composite behavior score
            behavior_score = (tag_similarity * 0.6) + (time_similarity * 0.4)
            
            scored_results.append(
                BehaviorSimilarityResult(
                    case_id=str(other_case_id),
                    behavior_score=round(behavior_score, 3),
                    time_similarity=round(time_similarity, 3),
                    tag_similarity=round(tag_similarity, 3),
                )
            )
        
        # Sort by behavior score descending
        scored_results.sort(key=lambda x: x.behavior_score, reverse=True)
        scored_results = scored_results[:limit]
        
        return BehaviorSimilarityResponse(
            reference_case_id=str(case_id),
            behavior_similarity_results=scored_results
        )
    
    @staticmethod
    async def calculate_person_risk_score(
        db: AsyncSession,
        person_id: UUID,
    ) -> RiskScoreResponse:
        """
        Calculate dynamic risk score for a person.
        
        Risk formula:
        - Repeat offense count (weight: 3)
        - Violent tag frequency (weight: 4)
        - Pattern consistency (weight: 2)
        - Proximity to active cases (weight: 2)
        """
        # Check person exists
        person_query = select(Person).where(Person.id == person_id)
        person_result = await db.execute(person_query)
        person = person_result.scalar_one_or_none()
        
        if not person:
            raise NotFoundError(f"Person {person_id} not found")
        
        # 1. Count repeat offenses
        repeat_offense_query = (
            select(func.count(distinct(CasePerson.case_id)))
            .where(
                CasePerson.person_id == person_id,
                CasePerson.role == PersonRole.SUSPECT
            )
        )
        repeat_offense_result = await db.execute(repeat_offense_query)
        repeat_offense_count = repeat_offense_result.scalar() or 0
        
        # 2. Count violent tags
        violent_tags_query = (
            select(Tag.name)
            .join(IncidentTag, IncidentTag.tag_id == Tag.id)
            .join(Incident, Incident.id == IncidentTag.incident_id)
            .join(Case, Case.primary_incident_id == Incident.id)
            .join(CasePerson, CasePerson.case_id == Case.id)
            .where(
                CasePerson.person_id == person_id,
                CasePerson.role == PersonRole.SUSPECT
            )
        )
        violent_tags_result = await db.execute(violent_tags_query)
        all_tags = [row[0] for row in violent_tags_result.all()]
        violent_tag_frequency = ScoringUtils.count_violent_tags(all_tags)
        
        # 3. Calculate pattern consistency
        # Get all cases for this person and their tag patterns
        person_cases_query = (
            select(Case.id, Incident.id)
            .join(CasePerson, CasePerson.case_id == Case.id)
            .join(Incident, Incident.id == Case.primary_incident_id)
            .where(
                CasePerson.person_id == person_id,
                CasePerson.role == PersonRole.SUSPECT
            )
        )
        person_cases_result = await db.execute(person_cases_query)
        person_cases = person_cases_result.all()
        
        tag_patterns = []
        for case_id, incident_id in person_cases:
            tags_query = (
                select(Tag.name)
                .join(IncidentTag, IncidentTag.tag_id == Tag.id)
                .where(IncidentTag.incident_id == incident_id)
            )
            tags_result = await db.execute(tags_query)
            case_tags = sorted([row[0] for row in tags_result.all()])
            tag_patterns.append(tuple(case_tags))
        
        # Pattern consistency: ratio of most common pattern to total cases
        if tag_patterns:
            pattern_counter = Counter(tag_patterns)
            most_common_count = pattern_counter.most_common(1)[0][1]
            pattern_consistency = most_common_count / len(tag_patterns)
        else:
            pattern_consistency = 0.0
        
        # 4. Calculate proximity to active cases
        # Count active/pending cases within 10km of any of this person's incident locations
        proximity_count = 0
        for case_id, incident_id in person_cases:
            # Get location of this incident
            loc_query = select(Incident.location).where(Incident.id == incident_id)
            loc_result = await db.execute(loc_query)
            location = loc_result.scalar()
            
            if location:
                # Count nearby active cases
                nearby_active_query = (
                    select(func.count(Case.id))
                    .join(Incident, Incident.id == Case.primary_incident_id)
                    .where(
                        and_(
                            Case.status.in_(["pending", "under_investigation"]),
                            ST_DWithin(Incident.location, location, 10000)  # 10km
                        )
                    )
                )
                nearby_result = await db.execute(nearby_active_query)
                nearby_count = nearby_result.scalar() or 0
                proximity_count = max(proximity_count, nearby_count)
        
        proximity_factor = min(proximity_count / 5.0, 2.0)  # Cap at 2.0
        
        # Calculate weighted risk score
        components = {
            "repeat_offense": (repeat_offense_count, 3),
            "violent_tags": (violent_tag_frequency, 4),
            "pattern_consistency": (pattern_consistency, 2),
            "proximity": (proximity_factor, 2),
        }
        risk_score = ScoringUtils.calculate_weighted_score(components)
        
        # Determine risk level
        risk_level = ScoringUtils.determine_risk_level(risk_score)
        
        return RiskScoreResponse(
            person_id=str(person_id),
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            breakdown=RiskBreakdown(
                repeat_offense_count=repeat_offense_count,
                violent_tag_frequency=violent_tag_frequency,
                pattern_consistency=round(pattern_consistency, 3),
                proximity_factor=round(proximity_factor, 2),
            )
        )
