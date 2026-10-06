"""
Category API Endpoints.
Full Firestore CRUD for garment categories.
"""

from flask import Blueprint, request
from backend.services.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)
from backend.utils.validation import validate_category_payload
from backend.utils.response import success_response, error_response
from backend.utils.auth import require_auth

category_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@category_bp.route("", methods=["GET"])
def list_categories():
    """Returns list of garment categories and item counts."""
    categories = get_all_categories()
    return success_response(data=categories, pagination={"total": len(categories)})


@category_bp.route("/<category_id>", methods=["GET"])
def get_category(category_id):
    """Returns single category details."""
    cat = get_category_by_id(category_id)
    if not cat:
        return error_response(f"Category with ID '{category_id}' not found.", status_code=404)
    return success_response(data=cat)


@category_bp.route("", methods=["POST"])
@require_auth(allowed_roles=["admin", "manager"])
def add_category():
    """Creates a new category in Firestore."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_category_payload(data, is_update=False)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    created, err = create_category(data)
    if err:
        return error_response(err, status_code=409)

    return success_response(data=created, message="Category created successfully.", status_code=201)


@category_bp.route("/<category_id>", methods=["PUT", "PATCH"])
@require_auth(allowed_roles=["admin", "manager"])
def edit_category(category_id):
    """Updates an existing category in Firestore."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_category_payload(data, is_update=True)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    updated, err = update_category(category_id, data)
    if err:
        status_code = 404 if "not found" in err.lower() else 409
        return error_response(err, status_code=status_code)

    return success_response(data=updated, message="Category updated successfully.")


@category_bp.route("/<category_id>", methods=["DELETE"])
@require_auth(allowed_roles=["admin"])
def remove_category(category_id):
    """Deletes a category from Firestore."""
    deleted = delete_category(category_id)
    if not deleted:
        return error_response(f"Category with ID '{category_id}' not found.", status_code=404)

    return success_response(message="Category deleted successfully.")
