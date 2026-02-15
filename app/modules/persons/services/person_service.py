"""
Person service - Business logic for person management.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.persons.entities.person_entity import Person, CasePerson, PersonRole
from app.modules.persons.repositories.person_repository import PersonRepository
from app.shared.exceptions import NotFoundError, ValidationError


class PersonService:
    """
    Person service.
    Handles business logic for person operations.
    """
    
    @staticmethod
    async def create_person(
        db: AsyncSession,
        name: str,
        date_of_birth: Optional[date] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        identification_number: Optional[str] = None,
    ) -> Person:
        """Create a new person."""
        # Check if identification number exists if provided
        if identification_number:
            # TODO: Add check for existing ID number if needed (unique constraint handles it but cleaner to check)
            pass

        person = Person(
            name=name,
            date_of_birth=date_of_birth,
            phone=phone,
            address=address,
            identification_number=identification_number,
        )
        return await PersonRepository.create(db, person)
    
    @staticmethod
    async def list_persons(db: AsyncSession) -> list[Person]:
        """Get all persons."""
        return await PersonRepository.get_all(db)
    
    @staticmethod
    async def get_person(db: AsyncSession, person_id: UUID) -> Person:
        """Get a person by ID."""
        person = await PersonRepository.get_by_id(db, person_id)
        if not person:
            raise NotFoundError(resource="Person", identifier=person_id)
        return person
    
    @staticmethod
    async def update_person(
        db: AsyncSession,
        person_id: UUID,
        name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        identification_number: Optional[str] = None,
    ) -> Person:
        """Update a person."""
        person = await PersonService.get_person(db, person_id)
        
        if name is not None:
            person.name = name
        if date_of_birth is not None:
            person.date_of_birth = date_of_birth
        if phone is not None:
            person.phone = phone
        if address is not None:
            person.address = address
        if identification_number is not None:
            person.identification_number = identification_number
        
        return await PersonRepository.save(db, person)
    
    @staticmethod
    async def delete_person(db: AsyncSession, person_id: UUID) -> None:
        """Delete a person."""
        person = await PersonService.get_person(db, person_id)
        await PersonRepository.delete(db, person)

    @staticmethod
    async def link_person_to_case(
        db: AsyncSession,
        case_id: UUID,
        person_id: UUID,
        role: PersonRole
    ) -> CasePerson:
        """Link a person to a case."""
        # Verify person exists
        await PersonService.get_person(db, person_id)
        
        # Check if link already exists
        existing_link = await PersonRepository.get_case_person(db, case_id, person_id)
        if existing_link:
            raise ValidationError(message=f"Person {person_id} is already linked to case {case_id}")

        link = CasePerson(
            case_id=case_id,
            person_id=person_id,
            role=role
        )
        return await PersonRepository.link_to_case(db, link)

    @staticmethod
    async def get_persons_for_case(
        db: AsyncSession,
        case_id: UUID
    ) -> list[CasePerson]:
        """Get all persons linked to a case."""
        return await PersonRepository.get_persons_by_case(db, case_id)

    @staticmethod
    async def remove_person_from_case(
        db: AsyncSession,
        case_id: UUID,
        person_id: UUID
    ) -> None:
        """Remove a person from a case."""
        link = await PersonRepository.get_case_person(db, case_id, person_id)
        if not link:
            raise NotFoundError(resource="CasePersonLink", identifier=f"{case_id}-{person_id}")
        
        await PersonRepository.remove_link(db, link)
