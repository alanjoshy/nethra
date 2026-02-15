"""
Person repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.persons.entities.person_entity import Person, CasePerson


class PersonRepository:
    """
    Repository for Person entity.
    Handles all database operations for persons and case links.
    """
    
    @staticmethod
    async def create(
        db: AsyncSession,
        person: Person
    ) -> Person:
        """Create a new person."""
        db.add(person)
        await db.commit()
        await db.refresh(person)
        return person
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        person_id: UUID
    ) -> Optional[Person]:
        """Get a person by ID."""
        result = await db.execute(
            select(Person).where(Person.id == person_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Person]:
        """Get all persons."""
        result = await db.execute(select(Person))
        return list(result.scalars().all())
    
    @staticmethod
    async def save(db: AsyncSession, person: Person) -> Person:
        """Update an existing person."""
        await db.commit()
        await db.refresh(person)
        return person
    
    @staticmethod
    async def delete(db: AsyncSession, person: Person) -> None:
        """Delete a person."""
        await db.delete(person)
        await db.commit()

    @staticmethod
    async def link_to_case(
        db: AsyncSession,
        case_person: CasePerson
    ) -> CasePerson:
        """Link a person to a case."""
        db.add(case_person)
        await db.commit()
        await db.refresh(case_person)
        return case_person

    @staticmethod
    async def get_case_person(
        db: AsyncSession,
        case_id: UUID,
        person_id: UUID
    ) -> Optional[CasePerson]:
        """Get a case-person link."""
        result = await db.execute(
            select(CasePerson).where(
                CasePerson.case_id == case_id,
                CasePerson.person_id == person_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_persons_by_case(
        db: AsyncSession,
        case_id: UUID
    ) -> list[CasePerson]:
        """Get all persons linked to a case."""
        result = await db.execute(
            select(CasePerson)
            .where(CasePerson.case_id == case_id)
            .options(selectinload(CasePerson.person))
        )
        return list(result.scalars().all())

    @staticmethod
    async def remove_link(
        db: AsyncSession,
        case_person: CasePerson
    ) -> None:
        """Remove a link between a person and a case."""
        await db.delete(case_person)
        await db.commit()
