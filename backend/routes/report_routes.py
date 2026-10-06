"""
Reports REST API Endpoints.
Provides structured report data and CSV downloads for:
- inventory
- sales
- products
- low-stock
- forecast
"""

from flask import Blueprint, request, Response
from backend.services.report_service import get_report_data, generate_csv_export
from backend.utils.response import success_response

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _respond_report(report_type):
    """Helper to return JSON or direct CSV based on format parameter."""
    fmt = request.args.get("format", "").lower()
    if fmt == "csv":
        csv_text, filename = generate_csv_export(report_type)
        response = Response(csv_text, mimetype="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    data = get_report_data(report_type)
    return success_response(data=data)


@report_bp.route("/inventory", methods=["GET"])
def report_inventory():
    """Returns inventory report or downloads CSV with ?format=csv."""
    return _respond_report("inventory")


@report_bp.route("/sales", methods=["GET"])
def report_sales():
    """Returns sales report or downloads CSV with ?format=csv."""
    return _respond_report("sales")


@report_bp.route("/products", methods=["GET"])
def report_products():
    """Returns products report or downloads CSV with ?format=csv."""
    return _respond_report("products")


@report_bp.route("/low-stock", methods=["GET"])
def report_low_stock():
    """Returns low-stock report or downloads CSV with ?format=csv."""
    return _respond_report("lowstock")


@report_bp.route("/forecast", methods=["GET"])
def report_forecast():
    """Returns forecast report or downloads CSV with ?format=csv."""
    return _respond_report("forecast")


@report_bp.route("/preview", methods=["GET"])
def preview_report():
    """Returns tabular preview of selected report type for frontend."""
    report_type = request.args.get("type", "inventory")
    data = get_report_data(report_type=report_type)
    return success_response(data=data)


@report_bp.route("/export/csv", methods=["GET"])
def export_csv():
    """Generates and downloads CSV file for selected report type."""
    report_type = request.args.get("type", "inventory")
    csv_text, filename = generate_csv_export(report_type=report_type)

    response = Response(csv_text, mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
