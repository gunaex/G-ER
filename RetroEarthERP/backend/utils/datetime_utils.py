"""
DateTime Utilities for RetroEarthERP
All timestamps are stored in UTC with timezone information.
Frontend should send client timezone offset in 'X-Client-Timezone-Offset' header.

Usage:
- Backend stores all dates in UTC
- Frontend sends timezone offset (minutes from UTC) in header
- Frontend converts UTC to local time for display

Header Format: X-Client-Timezone-Offset: 420 (for UTC+7)
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Header


def get_utc_now() -> datetime:
    """
    Get current UTC timestamp with timezone info.
    Always use this instead of datetime.now() or datetime.utcnow()
    """
    return datetime.now(timezone.utc)


def get_utc_from_offset(offset_minutes: int = 0) -> datetime:
    """
    Get current UTC timestamp, useful when client provides offset.
    offset_minutes: Client's timezone offset from UTC (e.g., +420 for UTC+7)
    """
    return datetime.now(timezone.utc)


def parse_client_datetime(dt_string: str, offset_minutes: Optional[int] = None) -> datetime:
    """
    Parse a datetime string from client and convert to UTC.
    Supports ISO 8601 format with timezone info.
    
    Args:
        dt_string: DateTime string (ISO 8601 format preferred)
        offset_minutes: Client's timezone offset if not in string
    
    Returns:
        Timezone-aware datetime in UTC
    """
    if not dt_string:
        return get_utc_now()
    
    # Try parsing ISO format with timezone
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        # Convert to UTC if it has timezone info
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc)
        # If no timezone, assume it's UTC
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    
    # Try parsing common formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_string, fmt)
            # Apply offset if provided
            if offset_minutes is not None:
                client_tz = timezone(timedelta(minutes=offset_minutes))
                dt = dt.replace(tzinfo=client_tz)
                return dt.astimezone(timezone.utc)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    # If all parsing fails, return current UTC
    return get_utc_now()


def format_datetime_utc(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 string with UTC timezone.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def format_datetime_with_offset(dt: datetime, offset_minutes: int) -> str:
    """
    Format datetime to ISO 8601 string with client's timezone.
    
    Args:
        dt: The datetime to format (should be UTC)
        offset_minutes: Client's timezone offset from UTC
    
    Returns:
        ISO 8601 formatted string in client's timezone
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    client_tz = timezone(timedelta(minutes=offset_minutes))
    return dt.astimezone(client_tz).isoformat()


# Thailand timezone (UTC+7)
TZ_BANGKOK = timezone(timedelta(hours=7))

def get_thailand_now() -> datetime:
    """Get current time in Thailand timezone"""
    return datetime.now(TZ_BANGKOK)

def utc_to_thailand(dt: datetime) -> datetime:
    """Convert UTC datetime to Thailand timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_BANGKOK)


async def get_client_timezone_offset(
    x_client_timezone_offset: Optional[str] = Header(None, alias="X-Client-Timezone-Offset")
) -> int:
    """
    FastAPI dependency to get client's timezone offset from header.
    Returns offset in minutes from UTC.
    Default: 420 (UTC+7 Thailand)
    """
    if x_client_timezone_offset:
        try:
            return int(x_client_timezone_offset)
        except ValueError:
            pass
    return 420  # Default to Thailand timezone (UTC+7)


def get_client_datetime(offset_minutes: int) -> datetime:
    """
    Get current datetime in client's timezone (with timezone info).
    For document numbers, we often want client's local date.
    """
    utc_now = get_utc_now()
    client_tz = timezone(timedelta(minutes=offset_minutes))
    return utc_now.astimezone(client_tz)

