"""
Supplier REST API Endpoints.
CRUD operations for textile mills and garment suppliers.
"""

from flask import Blueprint, request
from backend.services.supplier_service import (
    get_all_suppliers,
    get_supplier_by_id,
    create_supplier,
    update_supplier,
    delete_supplier
)
from backend.utils.validation import validate_supplier_payload
from backend.utils.response import success_response, error_response
from backend.utils.auth import require_auth

supplier_bp = Blueprint("suppliers", __name__, url_prefix="/api/suppliers")


@supplier_bp.route("", methods=["GET"])
def list_suppliers():
    """Returns suppliers directory."""
    search = request.args.get("search")
    status = request.args.get("status")
    suppliers = get_all_suppliers(search=search, status=status)
    return success_response(data=suppliers, pagination={"total": len(suppliers)})


@supplier_bp.route("/<supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    """Returns details of a specific supplier."""
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        return error_response(f"Supplier '{supplier_id}' not found.", status_code=404)
    return success_response(data=supplier)


@supplier_bp.route("", methods=["POST"])
@require_auth(allowed_roles=["admin", "manager"])
def add_supplier():
    """Creates a new supplier."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_supplier_payload(data, is_update=False)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    created = create_supplier(data)
    return success_response(data=created, message="Supplier added successfully.", status_code=201)


@supplier_bp.route("/<supplier_id>", methods=["PUT", "PATCH"])
@require_auth(allowed_roles=["admin", "manager"])
def edit_supplier(supplier_id):
    """Updates supplier information."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_supplier_payload(data, is_update=True)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    updated = update_supplier(supplier_id, data)
    if not updated:
        return error_response(f"Supplier '{supplier_id}' not found.", status_code=404)

    return success_response(data=updated, message="Supplier updated successfully.")


@supplier_bp.route("/<supplier_id>", methods=["DELETE"])
@require_auth(allowed_roles=["admin"])
def remove_supplier(supplier_id):
    """Removes a supplier."""
    deleted = delete_supplier(supplier_id)
    if not deleted:
        return error_response(f"Supplier '{supplier_id}' not found.", status_code=404)
    return success_response(message="Supplier deleted successfully.")
