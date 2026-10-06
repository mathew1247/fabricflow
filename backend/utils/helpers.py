"""
Helper utilities for API responses, serialization, and date formatting.
"""

from datetime import datetime, timezone
from backend.utils.response import success_response, error_response


def format_currency(amount):
    """Formats currency in INR style."""
    try:
        val = float(amount)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹{amount}"


def get_current_timestamp():
    """Returns ISO format UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()
