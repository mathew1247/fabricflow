"""
Product Catalog REST API Endpoints.
Provides complete CRUD, filtering, searching, and pagination for garment styles.
"""

from flask import Blueprint, request
from backend.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
from backend.utils.validation import validate_product_payload
from backend.utils.response import success_response, error_response
from backend.utils.auth import require_auth

product_bp = Blueprint("products", __name__, url_prefix="/api/products")


@product_bp.route("", methods=["GET"])
def list_products():
    """Returns list of products with optional search, category, size, and status filters."""
    search = request.args.get("search")
    category = request.args.get("category")
    size = request.args.get("size")
    status = request.args.get("status")
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int)

    products = get_all_products(search=search, category=category, size=size, status=status, limit=limit, offset=offset)
    return success_response(data=products, pagination={"total": len(products), "limit": limit, "offset": offset})


@product_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    """Returns product details for a given SKU ID."""
    product = get_product_by_id(product_id)
    if not product:
        return error_response(f"Product with ID '{product_id}' not found.", status_code=404)
    return success_response(data=product)


@product_bp.route("", methods=["POST"])
@require_auth(allowed_roles=["admin", "manager"])
def add_product():
    """Creates a new garment product in Firestore."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_product_payload(data, is_update=False)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    created = create_product(data)
    return success_response(data=created, message="Product created successfully.", status_code=201)


@product_bp.route("/<product_id>", methods=["PUT", "PATCH"])
@require_auth(allowed_roles=["admin", "manager"])
def edit_product(product_id):
    """Updates an existing garment product in Firestore."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_product_payload(data, is_update=True)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    updated = update_product(product_id, data)
    if not updated:
        return error_response(f"Product with ID '{product_id}' not found.", status_code=404)

    return success_response(data=updated, message="Product updated successfully.")


@product_bp.route("/<product_id>", methods=["DELETE"])
@require_auth(allowed_roles=["admin"])
def remove_product(product_id):
    """Deletes a garment product from Firestore."""
    deleted = delete_product(product_id)
    if not deleted:
        return error_response(f"Product with ID '{product_id}' not found.", status_code=404)

    return success_response(message="Product deleted successfully.")
