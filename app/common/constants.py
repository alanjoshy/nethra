"""
Application-wide constants for Nethra Backend.
"""

# User Roles
class UserRole:
    ADMIN = "admin"
    OFFICER = "officer"
    ANALYST = "analyst"
    
    ALL_ROLES = [ADMIN, OFFICER, ANALYST]


# Case Status
class CaseStatus:
    PENDING = "pending"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"
    
    ALL_STATUSES = [PENDING, UNDER_INVESTIGATION, RESOLVED, CLOSED, REJECTED]


# Incident Types
class IncidentType:
    THEFT = "theft"
    ASSAULT = "assault"
    FRAUD = "fraud"
    CYBER_CRIME = "cyber_crime"
    TRAFFIC_VIOLATION = "traffic_violation"
    MISSING_PERSON = "missing_person"
    OTHER = "other"
    
    ALL_TYPES = [THEFT, ASSAULT, FRAUD, CYBER_CRIME, TRAFFIC_VIOLATION, MISSING_PERSON, OTHER]


# Incident Priority
class IncidentPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    ALL_PRIORITIES = [LOW, MEDIUM, HIGH, CRITICAL]


# Media Types
class MediaType:
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    
    ALL_TYPES = [IMAGE, VIDEO, AUDIO, DOCUMENT]


# Pagination
class Pagination:
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


# JWT/Auth
class Auth:
    TOKEN_TYPE = "bearer"
    TOKEN_TTL_MINUTES = 60
