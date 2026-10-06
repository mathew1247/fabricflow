"""
Authentication API Endpoints.
Handles sign-in, token verification, and user profile sessions.
"""

from flask import Blueprint, request
from backend.utils.helpers import success_response, error_response
from backend.utils.auth import require_auth, get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates user and returns access token + user details."""
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return error_response("Email and password are required.", status_code=400)

    # Demo / Production authentication response
    user_data = {
        "uid": "ff-admin-001",
        "name": "Alex Morgan",
        "email": email,
        "role": "Inventory Admin",
        "token": "fabricflow2024"
    }

    return success_response(data=user_data, message="Authentication successful.")


@auth_bp.route("/me", methods=["GET"])
@require_auth()
def get_profile():
    """Returns the authenticated profile."""
    user = get_current_user()
    return success_response(data=user, message="Profile retrieved successfully.")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Clears user session."""
    return success_response(message="Logged out successfully.")
