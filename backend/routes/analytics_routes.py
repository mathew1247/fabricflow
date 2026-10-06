"""
Analytics REST API Endpoints.
Provides dedicated data streams for Sales Analytics, Inventory Analytics, and Product Performance.
"""

from flask import Blueprint
from backend.services.analytics_service import (
    get_sales_analytics,
    get_inventory_analytics,
    get_product_performance_analytics,
    get_consolidated_analytics
)
from backend.utils.response import success_response

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("", methods=["GET"])
def composite_analytics():
    """Returns composite analytics payload for all tabs."""
    return success_response(data=get_consolidated_analytics())


@analytics_bp.route("/sales", methods=["GET"])
def sales_analytics():
    """Returns sales analytics breakdown."""
    data = get_sales_analytics()
    return success_response(data=data)


@analytics_bp.route("/inventory", methods=["GET"])
def inventory_analytics():
    """Returns inventory analytics breakdown."""
    data = get_inventory_analytics()
    return success_response(data=data)


@analytics_bp.route("/products", methods=["GET"])
def product_analytics():
    """Returns product velocity and performance breakdown."""
    data = get_product_performance_analytics()
    return success_response(data=data)


@analytics_bp.route("/performance", methods=["GET"])
def performance_analytics():
    """Returns fast and slow moving product tables."""
    data = get_product_performance_analytics()
    return success_response(data=data)
