"""
Pagination utilities for Nethra Backend.
"""

from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel, Field
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.constants import Pagination as PaginationConstants
from app.common.responses import PaginationMeta


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    
    page: int = Field(
        default=PaginationConstants.DEFAULT_PAGE,
        ge=1,
        description="Page number (1-indexed)"
    )
    page_size: int = Field(
        default=PaginationConstants.DEFAULT_PAGE_SIZE,
        ge=1,
        le=PaginationConstants.MAX_PAGE_SIZE,
        description=f"Items per page (max: {PaginationConstants.MAX_PAGE_SIZE})"
    )
    
    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get the limit for database queries."""
        return self.page_size


class PaginatedResult(Generic[T]):
    """Container for paginated results."""
    
    def __init__(
        self,
        items: Sequence[T],
        total_items: int,
        pagination_params: PaginationParams
    ):
        self.items = list(items)
        self.total_items = total_items
        self.pagination_params = pagination_params
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total_items == 0:
            return 0
        return (self.total_items + self.pagination_params.page_size - 1) // self.pagination_params.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.pagination_params.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.pagination_params.page > 1
    
    def to_meta(self) -> PaginationMeta:
        """Convert to PaginationMeta response model."""
        return PaginationMeta(
            page=self.pagination_params.page,
            page_size=self.pagination_params.page_size,
            total_items=self.total_items,
            total_pages=self.total_pages,
            has_next=self.has_next,
            has_previous=self.has_previous
        )


async def paginate(
    db: AsyncSession,
    query: Select,
    pagination_params: PaginationParams
) -> PaginatedResult:
    """
    Execute a paginated query.
    
    Args:
        db: Database session
        query: SQLAlchemy select query
        pagination_params: Pagination parameters
    
    Returns:
        PaginatedResult with items and metadata
    """
    # Get total count
    count_query = query.with_only_columns(func.count()).order_by(None)
    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0
    
    # Get paginated items
    paginated_query = query.offset(pagination_params.offset).limit(pagination_params.limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    
    return PaginatedResult(
        items=items,
        total_items=total_items,
        pagination_params=pagination_params
    )
