"""
DateTime Utilities for RetroEarthERP
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Header


def get_utc_now() -> datetime:
    """
    Get current UTC timestamp with timezone info.
    Use this instead of datetime.utcnow() or datetime.now()
    """
    return datetime.now(timezone.utc)
