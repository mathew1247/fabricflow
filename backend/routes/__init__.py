from .auth_routes import auth_bp
from .product_routes import product_bp
from .category_routes import category_bp
from .inventory_routes import inventory_bp
from .sales_routes import sales_bp
from .supplier_routes import supplier_bp
from .dashboard_routes import dashboard_bp
from .analytics_routes import analytics_bp
from .forecast_routes import forecast_bp
from .report_routes import report_bp

__all__ = [
    "auth_bp",
    "product_bp",
    "category_bp",
    "inventory_bp",
    "sales_bp",
    "supplier_bp",
    "dashboard_bp",
    "analytics_bp",
    "forecast_bp",
    "report_bp"
]
