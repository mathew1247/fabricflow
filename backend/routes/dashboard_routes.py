"""
Dashboard Overview API Endpoints.
Aggregates summary KPIs, charts, category velocity, and recent transactions.
"""

from flask import Blueprint, request
from backend.services.dashboard_service import get_dashboard_metrics
from backend.utils.helpers import success_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
def dashboard_overview():
    """Returns all data needed for the main overview dashboard."""
    period = request.args.get("period", "monthly")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    data = get_dashboard_metrics(period=period, start_date=start_date, end_date=end_date)
    return success_response(data=data)
