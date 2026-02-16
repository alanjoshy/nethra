"""
Scoring utilities for intelligence analysis.
"""

from typing import List, Dict, Tuple, Set, Optional
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt


class ScoringUtils:
    """Utility class for intelligence scoring calculations."""
    
    # Violent tag keywords for risk assessment
    VIOLENT_TAGS = {"assault", "murder", "violent", "weapon", "armed", "battery"}
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        "LOW": (0, 5),
        "MEDIUM": (6, 10),
        "HIGH": (11, float('inf'))
    }
    
    @staticmethod
    def calculate_tag_overlap(tags1: List[str], tags2: List[str]) -> Tuple[int, List[str]]:
        """
        Calculate tag overlap between two tag lists.
        
        Args:
            tags1: First list of tags
            tags2: Second list of tags
            
        Returns:
            Tuple of (overlap_count, list_of_overlapping_tags)
        """
        set1 = set(tags1) if tags1 else set()
        set2 = set(tags2) if tags2 else set()
        overlap = set1 & set2
        return len(overlap), list(overlap)
    
    @staticmethod
    def calculate_temporal_similarity(
        datetime1: datetime,
        datetime2: datetime,
        max_days: int = 90
    ) -> float:
        """
        Calculate temporal similarity between two datetimes.
        Returns a score from 0.0 (no similarity) to 1.0 (very similar).
        
        Args:
            datetime1: First datetime
            datetime2: Second datetime
            max_days: Maximum days considered for similarity (default 90)
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not datetime1 or not datetime2:
            return 0.0
            
        time_diff = abs((datetime1 - datetime2).total_seconds())
        max_seconds = max_days * 24 * 3600
        
        # Linear decay: score decreases as time difference increases
        similarity = max(0.0, 1.0 - (time_diff / max_seconds))
        return similarity
    
    @staticmethod
    def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """
        Calculate the great circle distance in kilometers between two points
        on the earth (specified in decimal degrees).
        
        Args:
            lon1: Longitude of first point
            lat1: Latitude of first point
            lon2: Longitude of second point
            lat2: Latitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c  # Radius of earth in kilometers
        return km
    
    @staticmethod
    def calculate_weighted_score(components: Dict[str, float]) -> float:
        """
        Calculate a weighted score from multiple components.
        
        Args:
            components: Dictionary with keys as component names and values as (score, weight) tuples
                       Example: {"tag_overlap": (3, 3), "distance": (1.5, 2)}
            
        Returns:
            Weighted total score
        """
        total_score = 0.0
        for component_name, (value, weight) in components.items():
            total_score += value * weight
        return total_score
    
    @staticmethod
    def determine_risk_level(score: float) -> str:
        """
        Determine risk level based on score.
        
        Args:
            score: Risk score
            
        Returns:
            Risk level: "LOW", "MEDIUM", or "HIGH"
        """
        for level, (min_score, max_score) in ScoringUtils.RISK_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return level
        return "LOW"
    
    @staticmethod
    def extract_time_patterns(incidents: List) -> Dict[str, any]:
        """
        Extract time-based patterns from incidents.
        
        Args:
            incidents: List of incident entities with occurred_at datetime
            
        Returns:
            Dictionary with:
                - hour_distribution: Count of incidents by hour (0-23)
                - weekday_distribution: Count by weekday (0=Monday, 6=Sunday)
                - is_weekend_heavy: Boolean if weekend incidents dominate
        """
        hour_dist = {}
        weekday_dist = {}
        
        for incident in incidents:
            if not incident.occurred_at:
                continue
                
            # Parse occurred_at (might be string or datetime)
            if isinstance(incident.occurred_at, str):
                dt = datetime.fromisoformat(incident.occurred_at.replace('Z', '+00:00'))
            else:
                dt = incident.occurred_at
            
            # Hour distribution
            hour = dt.hour
            hour_dist[hour] = hour_dist.get(hour, 0) + 1
            
            # Weekday distribution
            weekday = dt.weekday()
            weekday_dist[weekday] = weekday_dist.get(weekday, 0) + 1
        
        # Check if weekend-heavy (Saturday=5, Sunday=6)
        weekend_count = weekday_dist.get(5, 0) + weekday_dist.get(6, 0)
        weekday_count = sum(weekday_dist.get(i, 0) for i in range(5))
        is_weekend_heavy = weekend_count > weekday_count if (weekend_count + weekday_count) > 0 else False
        
        return {
            "hour_distribution": hour_dist,
            "weekday_distribution": weekday_dist,
            "is_weekend_heavy": is_weekend_heavy
        }
    
    @staticmethod
    def calculate_pattern_similarity(pattern1: Dict, pattern2: Dict) -> float:
        """
        Calculate similarity between two time patterns.
        
        Args:
            pattern1: Time pattern dict from extract_time_patterns
            pattern2: Time pattern dict from extract_time_patterns
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Weekend pattern match
        weekend_match = 1.0 if pattern1.get("is_weekend_heavy") == pattern2.get("is_weekend_heavy") else 0.0
        
        # Hour distribution similarity (simplified: check overlap in top hours)
        hours1 = set(sorted(pattern1.get("hour_distribution", {}).keys(), 
                           key=lambda h: pattern1["hour_distribution"][h], reverse=True)[:3])
        hours2 = set(sorted(pattern2.get("hour_distribution", {}).keys(), 
                           key=lambda h: pattern2["hour_distribution"][h], reverse=True)[:3])
        
        hour_overlap = len(hours1 & hours2) / 3.0 if len(hours1) > 0 and len(hours2) > 0 else 0.0
        
        # Combined similarity
        return (weekend_match * 0.4) + (hour_overlap * 0.6)
    
    @staticmethod
    def count_violent_tags(tags: List[str]) -> int:
        """
        Count how many tags are considered violent.
        
        Args:
            tags: List of tag names
            
        Returns:
            Count of violent tags
        """
        tag_set = set(tag.lower() for tag in tags) if tags else set()
        return len(tag_set & ScoringUtils.VIOLENT_TAGS)
