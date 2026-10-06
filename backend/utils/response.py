"""
API Response Formatting Utility.
Standardizes all JSON success and error payloads.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200, pagination=None, meta=None):
    """Formats standard JSON success payload."""
    payload = {
        "success": True,
        "status": "success",
        "message": message,
        "data": data if data is not None else {}
    }
    if pagination is not None:
        payload["pagination"] = pagination
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Formats standard JSON error payload."""
    payload = {
        "success": False,
        "status": "error",
        "message": message
    }
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code
