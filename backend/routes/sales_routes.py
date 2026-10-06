"""
Sales REST API Endpoints.
Handles order logs, receipt generation, and atomic sales recording with automatic stock deduction.
"""

from flask import Blueprint, request
from backend.services.sales_service import (
    get_all_sales,
    get_sale_by_id,
    record_sale,
    delete_sale
)
from backend.utils.validation import validate_sale_payload
from backend.utils.response import success_response, error_response
from backend.utils.auth import require_auth

sales_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@sales_bp.route("", methods=["GET"])
def list_sales():
    """Returns list of sales transactions with optional filters."""
    search = request.args.get("search")
    category = request.args.get("category")
    status = request.args.get("status")
    limit_param = request.args.get("limit")
    limit = int(limit_param) if limit_param and limit_param.isdigit() else None

    sales = get_all_sales(search=search, category=category, status=status, limit=limit)
    return success_response(data=sales, pagination={"total": len(sales)})


@sales_bp.route("/<sale_id>", methods=["GET"])
def get_sale(sale_id):
    """Returns single sale transaction details."""
    sale = get_sale_by_id(sale_id)
    if not sale:
        return error_response(f"Sale transaction '{sale_id}' not found.", status_code=404)
    return success_response(data=sale)


@sales_bp.route("", methods=["POST"])
@require_auth()
def create_sale():
    """Records a new garment sales transaction and atomically reduces stock."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid JSON request body.", status_code=400)

    is_valid, errors = validate_sale_payload(data)
    if not is_valid:
        return error_response(errors[0] if errors else "Validation failed.", status_code=400, errors=errors)

    recorded, err = record_sale(data)
    if err:
        status_code = 404 if "not found" in err.lower() else 400
        return error_response(err, status_code=status_code)

    return success_response(data=recorded, message="Sale recorded successfully.", status_code=201)


@sales_bp.route("/<sale_id>", methods=["DELETE"])
@require_auth(allowed_roles=["admin"])
def remove_sale(sale_id):
    """Deletes a sale transaction."""
    deleted = delete_sale(sale_id)
    if not deleted:
        return error_response(f"Sale transaction '{sale_id}' not found.", status_code=404)
    return success_response(message="Sale transaction deleted successfully.")
