"""
Demand Forecast Service Layer.
Executes predictive demand modeling, horizon parameterization, and procurement recommendations.
"""

from backend.services.product_service import get_all_products
from backend.services.sales_service import get_all_sales
from analytics.demand_forecasting import compute_demand_forecast


def get_demand_forecast(period="30", category="all"):
    """
    Computes statistical demand forecast for specified planning horizon (7, 30, 90 days).
    """
    products = get_all_products()
    sales = get_all_sales()
    return compute_demand_forecast(products, sales, period=period, category_filter=category)
