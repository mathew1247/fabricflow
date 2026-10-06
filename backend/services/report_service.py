"""
Report Service Layer.
Generates tabular data and CSV file exports for:
- inventory
- sales
- products
- low-stock
- forecast
Directly generated from live Google Cloud Firestore data.
"""

import os
import io
import csv
from datetime import datetime
from config import Config
from backend.services.product_service import get_all_products
from backend.services.sales_service import get_all_sales
from backend.services.forecast_service import get_demand_forecast


def get_report_data(report_type="inventory"):
    """
    Returns structured table headers and rows for report preview or CSV export.
    Supports: inventory, sales, products, low-stock, forecast.
    """
    rtype = report_type.lower().replace("-", "").replace("_", "")

    products = get_all_products()
    sales = get_all_sales()

    if rtype == "sales":
        headers = ["Sale ID", "Product", "Category", "Quantity", "Unit Price", "Total Amount", "Date", "Status"]
        rows = []
        for s in sales:
            rows.append({
                "id": s.get("sale_id", s.get("id")),
                "product": s.get("product_name", s.get("product", "")),
                "category": s.get("category_name", s.get("category", "")),
                "quantity": s.get("quantity", 0),
                "unit_price": f"₹{float(s.get('unit_price', 0)):,.2f}",
                "total": f"₹{float(s.get('total_amount', s.get('total', 0))):,.2f}",
                "date": s.get("sale_date", s.get("date", "")),
                "status": s.get("status", "Completed")
            })
        return {
            "title": "Sales Summary Report",
            "type": "sales",
            "count": len(rows),
            "headers": headers,
            "rows": rows
        }

    elif rtype in ["lowstock", "low_stock"]:
        headers = ["Product ID", "Product Name", "Category", "Current Stock", "Reorder Level", "Deficit", "Supplier", "Risk Status"]
        low_items = [p for p in products if p.get("stock_status") in ["Low", "Critical"] or int(p.get("stock_quantity", p.get("stock", 0))) <= int(p.get("reorder_level", p.get("min_stock", 20)))]
        rows = []
        for p in low_items:
            stock = int(p.get("stock_quantity", p.get("stock", 0)))
            reorder = int(p.get("reorder_level", p.get("min_stock", 20)))
            deficit = max(0, reorder - stock)
            rows.append({
                "id": p.get("product_id", p.get("id")),
                "product": p.get("product_name", p.get("name")),
                "category": p.get("category_name", p.get("category")),
                "stock": f"{stock} pcs",
                "min_stock": f"{reorder} pcs",
                "deficit": f"{deficit} pcs",
                "supplier": p.get("supplier_name", p.get("supplier")),
                "status": p.get("stock_status", p.get("status", "Low"))
            })
        return {
            "title": "Low Stock & Risk Report",
            "type": "low-stock",
            "count": len(rows),
            "headers": headers,
            "rows": rows
        }

    elif rtype == "products":
        headers = ["Product ID", "Product Name", "Category", "Size", "Price", "Stock", "Supplier", "Created At"]
        rows = []
        for p in products:
            rows.append({
                "id": p.get("product_id", p.get("id")),
                "name": p.get("product_name", p.get("name")),
                "category": p.get("category_name", p.get("category")),
                "size": p.get("size", "M"),
                "price": f"₹{float(p.get('price', 0)):,.2f}",
                "stock": f"{p.get('stock_quantity', p.get('stock', 0))} pcs",
                "supplier": p.get("supplier_name", p.get("supplier")),
                "created_at": str(p.get("created_at", "")).split("T")[0]
            })
        return {
            "title": "Products Catalog Report",
            "type": "products",
            "count": len(rows),
            "headers": headers,
            "rows": rows
        }

    elif rtype == "forecast":
        headers = ["Product ID", "Product Name", "Category", "Current Stock", "Predicted 30D Demand", "Recommended Stock", "Forecast Status", "Recommendation"]
        fc = get_demand_forecast("30", "all")
        rows = []
        for item in fc.get("table", []):
            rows.append({
                "id": item.get("product_id", item.get("id")),
                "product": item.get("product_name", item.get("name")),
                "category": item.get("category"),
                "stock": f"{item.get('stock', 0)} pcs",
                "predicted": f"{item.get('predicted', 0)} pcs",
                "recommended": f"{item.get('recommended', 0)} pcs",
                "status": item.get("status", "Maintain Stock"),
                "reason": item.get("reason", "")
            })
        return {
            "title": "Demand Forecast Report",
            "type": "forecast",
            "count": len(rows),
            "headers": headers,
            "rows": rows
        }

    else:
        # Default: Inventory Valuation Report
        headers = ["Product ID", "Product Name", "Category", "Size", "Price", "Stock Units", "Valuation", "Stock Status"]
        rows = []
        for p in products:
            price = float(p.get("price", 0))
            stock = int(p.get("stock_quantity", p.get("stock", 0)))
            val = price * stock
            rows.append({
                "id": p.get("product_id", p.get("id")),
                "name": p.get("product_name", p.get("name")),
                "category": p.get("category_name", p.get("category")),
                "size": p.get("size", "M"),
                "price": f"₹{price:,.2f}",
                "stock": f"{stock} pcs",
                "stock_units": stock,
                "valuation": f"₹{val:,.2f}",
                "status": p.get("stock_status", p.get("status", "Normal"))
            })
        return {
            "title": "Inventory Valuation Report",
            "type": "inventory",
            "count": len(rows),
            "headers": headers,
            "rows": rows
        }


def generate_csv_export(report_type="inventory"):
    """
    Generates and returns raw CSV text and timestamped filename for client download.
    """
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    report_data = get_report_data(report_type)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Headers
    writer.writerow(report_data["headers"])

    # Write Rows
    for row in report_data["rows"]:
        writer.writerow(list(row.values()))

    csv_text = output.getvalue()
    output.close()

    # Save local copy
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(Config.REPORTS_DIR, f"fabricflow_{report_type}_{timestamp}.csv")
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            f.write(csv_text)
    except Exception:
        pass

    return csv_text, f"fabricflow_{report_type}_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
