"""
Analytics service for aggregated crime reporting.
"""

from typing import Optional
from datetime import date
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.persons.entities.person_entity import Person, CasePerson
from app.modules.cases.entities.case_entity import Case
from app.modules.analytics.schemas import (
    DistrictStats,
    CrimeByLocationResponse,
    PatternStats,
    PatternFrequencyResponse,
    MonthlyData,
    MonthlyTrendsResponse,
    RepeatOffenderSummary,
    RepeatOffenderOverviewResponse,
)


class AnalyticsService:
    """Service for analytics aggregations and reporting."""
    
    @staticmethod
    async def crime_by_location(
        db: AsyncSession,
        district: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> CrimeByLocationResponse:
        """
        Aggregate incidents by district/location.
        
        Args:
            db: Database session
            district: Optional district filter
            from_date: Optional start date
            to_date: Optional end date
            
        Returns:
            CrimeByLocationResponse with district statistics
        """
        # Query incidents grouped by district
        query = (
            select(
                Incident.district,
                func.count(Incident.id).label("incident_count")
            )
            .where(Incident.district.isnot(None))
        )
        
        # Apply filters
        if district:
            query = query.where(Incident.district == district)
        if from_date:
            query = query.where(Incident.occurred_at >= from_date)
        if to_date:
            query = query.where(Incident.occurred_at <= to_date)
        
        # Group by district
        query = query.group_by(Incident.district).order_by(func.count(Incident.id).desc())
        
        result = await db.execute(query)
        district_data = result.all()
        
        districts = [
            DistrictStats(district=dist, incident_count=count)
            for dist, count in district_data
        ]
        
        return CrimeByLocationResponse(districts=districts)
    
    @staticmethod
    async def pattern_frequency(db: AsyncSession) -> PatternFrequencyResponse:
        """
        Aggregate tag occurrence frequencies.
        
        Args:
            db: Database session
            
        Returns:
            PatternFrequencyResponse with tag statistics
        """
        # Query tag occurrences
        query = (
            select(
                Tag.name,
                func.count(IncidentTag.incident_id).label("count")
            )
            .join(IncidentTag, IncidentTag.tag_id == Tag.id)
            .group_by(Tag.name)
            .order_by(func.count(IncidentTag.incident_id).desc())
        )
        
        result = await db.execute(query)
        tag_data = result.all()
        
        patterns = [
            PatternStats(tag=tag_name, count=count)
            for tag_name, count in tag_data
        ]
        
        return PatternFrequencyResponse(patterns=patterns)
    
    @staticmethod
    async def monthly_trends(db: AsyncSession, year: int) -> MonthlyTrendsResponse:
        """
        Aggregate incidents by month for a given year.
        
        Args:
            db: Database session
            year: Year to analyze
            
        Returns:
            MonthlyTrendsResponse with monthly statistics
        """
        # Month names lookup
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        # Query incidents grouped by month
        query = (
            select(
                extract('month', Incident.occurred_at).label("month"),
                func.count(Incident.id).label("incident_count")
            )
            .where(extract('year', Incident.occurred_at) == year)
            .group_by(extract('month', Incident.occurred_at))
            .order_by(extract('month', Incident.occurred_at))
        )
        
        result = await db.execute(query)
        monthly_data_raw = result.all()
        
        # Build monthly data with month names
        monthly_dict = {int(month): count for month, count in monthly_data_raw}
        
        monthly_data = [
            MonthlyData(
                month=month_names[i],
                incident_count=monthly_dict.get(i + 1, 0)
            )
            for i in range(12)
        ]
        
        return MonthlyTrendsResponse(year=year, monthly_data=monthly_data)
    
    @staticmethod
    async def repeat_offender_overview(
        db: AsyncSession,
        min_cases: int = 2,
    ) -> RepeatOffenderOverviewResponse:
        """
        Aggregate repeat offenders with case counts.
        
        Args:
            db: Database session
            min_cases: Minimum case count threshold
            
        Returns:
            RepeatOffenderOverviewResponse with offender statistics
        """
        # Query persons with multiple case involvements as suspects
        query = (
            select(
                Person.id,
                Person.name,
                func.count(func.distinct(CasePerson.case_id)).label("case_count")
            )
            .join(CasePerson, CasePerson.person_id == Person.id)
            .where(CasePerson.role == "suspect")
            .group_by(Person.id, Person.name)
            .having(func.count(func.distinct(CasePerson.case_id)) >= min_cases)
            .order_by(func.count(func.distinct(CasePerson.case_id)).desc())
        )
        
        result = await db.execute(query)
        offender_data = result.all()
        
        repeat_offenders = [
            RepeatOffenderSummary(
                person_id=str(person_id),
                name=name,
                case_count=case_count
            )
            for person_id, name, case_count in offender_data
        ]
        
        return RepeatOffenderOverviewResponse(repeat_offenders=repeat_offenders)
