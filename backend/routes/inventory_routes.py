"""
Inventory Management REST API Endpoints.
Handles stock balance retrieval, single item inspection, update, summary KPIs, and stock level adjustment operations.
"""

from flask import Blueprint, request
from backend.services.inventory_service import (
    get_all_inventory,
    get_inventory_by_id,
    update_inventory,
    adjust_stock,
    get_inventory_summary
)
from backend.utils.validation import validate_stock_adjustment_payload
from backend.utils.response import success_response, error_response
from backend.utils.auth import require_auth

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


@inventory_bp.route("", methods=["GET"])
def list_inventory():
    """Returns inventory table records with optional filters."""
    search = request.args.get("search")
    category = request.args.get("category")
    status = request.args.get("status")

    inventory_items = get_all_inventory(search=search, category=category, status=status)
    return success_response(data=inventory_items, pagination={"total": len(inventory_items)})


@inventory_bp.route("/summary", methods=["GET"])
def inventory_summary():
    """Returns top summary metrics (total stock, normal, low, critical, valuation)."""
    summary = get_inventory_summary()
    return success_response(data=summary)


@inventory_bp.route("/<product_id>", methods=["GET"])
def get_inventory_item(product_id):
    """Returns inventory document for a single product."""
    item = get_inventory_by_id(product_id)
    if not item:
        return error_response(f"Inventory record for product '{product_id}' not found.", status_code=404)
    return success_response(data=item)


@inventory_bp.route("/<product_id>", methods=["PUT", "PATCH"])
@require_auth(allowed_roles=["admin", "manager"])
def update_inventory_item(product_id):
    """Updates stock quantity and/or reorder level for an inventory document."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    updated, err = update_inventory(product_id, data)
    if err:
        return error_response(err, status_code=404 if "not found" in err.lower() else 400)

    return success_response(data=updated, message="Inventory updated successfully.")


@inventory_bp.route("/<product_id>/adjust", methods=["POST"])
@require_auth(allowed_roles=["admin", "manager"])
def adjust_inventory_level(product_id):
    """Adjusts stock level (add inflow, deduct outflow, set exact count)."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_stock_adjustment_payload(data)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    adj_type = data.get("type", "set")
    qty = int(data.get("quantity") if "quantity" in data else data.get("stock_quantity", data.get("qty", 0)))
    reason = data.get("reason", "")

    updated_inv, err = adjust_stock(product_id, adj_type, qty, reason)
    if err:
        status_code = 404 if "not found" in err.lower() else 400
        return error_response(err, status_code=status_code)

    return success_response(data=updated_inv, message="Stock level adjusted successfully.")
