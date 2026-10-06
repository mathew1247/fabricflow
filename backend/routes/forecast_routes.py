"""
Demand Forecast REST API Endpoints.
Predictive demand analytics across customizable planning horizons (7, 30, 90 days).
"""

from flask import Blueprint, request
from backend.services.forecast_service import get_demand_forecast
from backend.utils.response import success_response

forecast_bp = Blueprint("forecast", __name__, url_prefix="/api/forecast")


@forecast_bp.route("", methods=["GET", "POST"])
def demand_forecast():
    """
    Returns predictive demand metrics, trajectory chart coordinates, and procurement advice
    for 7, 30, or 90 days forecast horizon.
    """
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        period = str(payload.get("period", payload.get("forecast_days", "30")))
        category = str(payload.get("category", "all"))
    else:
        period = request.args.get("period", "30")
        category = request.args.get("category", "all")

    data = get_demand_forecast(period=period, category=category)
    return success_response(data=data)
