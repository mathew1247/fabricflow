"""
Backend Analytics Package
"""
from analytics.sales_analysis import analyze_sales_overview, analyze_sales_trends, analyze_sales_by_category
from analytics.inventory_analysis import analyze_inventory_overview, analyze_stock_distribution
from analytics.product_analysis import analyze_product_performance
from analytics.demand_forecasting import compute_demand_forecast

__all__ = [
    "analyze_sales_overview",
    "analyze_sales_trends",
    "analyze_sales_by_category",
    "analyze_inventory_overview",
    "analyze_stock_distribution",
    "analyze_product_performance",
    "compute_demand_forecast"
]
