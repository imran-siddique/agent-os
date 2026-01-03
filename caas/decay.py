"""
Time-based decay function for relevance scoring.

Implements "The Half-Life of Truth" - mathematical gravity that pulls old data down.
Formula: Score = Similarity * (1 / Time_Elapsed)
"""

from datetime import datetime
from typing import Optional


def calculate_decay_factor(
    ingestion_timestamp: Optional[str],
    reference_time: Optional[datetime] = None,
    decay_rate: float = 1.0
) -> float:
    """
    Calculate time-based decay factor for document relevance.
    
    The decay function prioritizes recent documents over older ones:
    - A document from Yesterday with 80% match beats a document from Last Year with 95% match
    - We don't "cut off" old data (history is useful for debugging)
    - We apply mathematical "Gravity" that pulls old data down
    
    Formula: decay_factor = 1 / (1 + time_elapsed_in_days * decay_rate)
    
    Args:
        ingestion_timestamp: ISO format timestamp of document ingestion
        reference_time: Time to calculate decay from (defaults to now)
        decay_rate: Rate of decay (default 1.0). Higher values mean faster decay.
                   - 1.0: Yesterday ~0.5x, Week ago ~0.13x, Year ago ~0.003x
                   - 0.1: Yesterday ~0.91x, Week ago ~0.59x, Year ago ~0.03x
    
    Returns:
        Decay factor between 0 and 1 (1 = no decay, lower = more decay)
    
    Examples:
        >>> # Document from yesterday
        >>> calculate_decay_factor("2024-01-02T12:00:00", 
        ...                        datetime(2024, 1, 3, 12, 0, 0))
        0.5
        
        >>> # Document from a week ago
        >>> calculate_decay_factor("2024-01-01T12:00:00",
        ...                        datetime(2024, 1, 8, 12, 0, 0))
        0.125
    """
    if not ingestion_timestamp:
        # No timestamp means we can't apply decay - treat as very old
        # but not zero (history is still useful)
        return 0.1
    
    try:
        # Parse timestamp
        ingestion_dt = datetime.fromisoformat(ingestion_timestamp.replace('Z', '+00:00'))
        
        # Use reference time or current time
        if reference_time is None:
            reference_time = datetime.utcnow()
        
        # Calculate time elapsed in days
        time_delta = reference_time - ingestion_dt
        days_elapsed = time_delta.total_seconds() / (24 * 3600)
        
        # Prevent negative values (future timestamps shouldn't happen but handle gracefully)
        if days_elapsed < 0:
            days_elapsed = 0
        
        # Calculate decay factor: 1 / (1 + days_elapsed * decay_rate)
        # This gives:
        # - Day 0 (today): 1.0 (no decay)
        # - Day 1 (yesterday): 0.5
        # - Day 7 (week ago): 0.125
        # - Day 365 (year ago): 0.0027
        decay_factor = 1.0 / (1.0 + days_elapsed * decay_rate)
        
        return decay_factor
    
    except (ValueError, AttributeError) as e:
        # Invalid timestamp format - treat as old but not zero
        return 0.1


def apply_decay_to_score(base_score: float, decay_factor: float) -> float:
    """
    Apply decay factor to a base relevance score.
    
    Args:
        base_score: Base relevance score (e.g., similarity or weight)
        decay_factor: Decay factor from calculate_decay_factor (0-1)
    
    Returns:
        Decayed score
    """
    return base_score * decay_factor


def get_time_weighted_score(
    base_score: float,
    ingestion_timestamp: Optional[str],
    reference_time: Optional[datetime] = None,
    decay_rate: float = 1.0
) -> float:
    """
    Convenience function to calculate time-weighted score in one call.
    
    Args:
        base_score: Base relevance score
        ingestion_timestamp: Document ingestion timestamp
        reference_time: Reference time for decay calculation
        decay_rate: Rate of decay
    
    Returns:
        Time-weighted score
    """
    decay_factor = calculate_decay_factor(ingestion_timestamp, reference_time, decay_rate)
    return apply_decay_to_score(base_score, decay_factor)
