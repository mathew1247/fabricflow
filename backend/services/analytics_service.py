"""
Analytics Service Layer using Pandas & NumPy.
Calculates sales performance, inventory distributions, and velocity classification
directly from Cloud Firestore documents.
"""

from backend.services.product_service import get_all_products
from backend.services.sales_service import get_all_sales
from analytics.sales_analysis import (
    analyze_sales_overview,
    analyze_sales_trends,
    analyze_sales_by_category,
    analyze_monthly_sales_vs_target,
    analyze_daily_sales_distribution
)
from analytics.inventory_analysis import (
    analyze_inventory_overview,
    analyze_stock_distribution,
    analyze_inventory_movement
)
from analytics.product_analysis import analyze_product_performance
from analytics.data_processing import sales_to_df


def get_sales_analytics():
    """
    Computes comprehensive sales analysis:
    total sales, total units sold, sales by day, sales by month,
    sales by category, sales by product, sales growth.
    """
    sales = get_all_sales()
    sales_overview = analyze_sales_overview(sales)
    sales_trends = analyze_sales_trends(sales, period="monthly")
    category_breakdown = analyze_sales_by_category(sales)
    daily_dist = analyze_daily_sales_distribution(sales)
    monthly_targets = analyze_monthly_sales_vs_target(sales)

    # Sales by product
    df = sales_to_df(sales)
    sales_by_product = []
    if not df.empty:
        prod_grp = df.groupby(["product", "category"]).agg({"total": "sum", "quantity": "sum"}).reset_index()
        prod_grp.sort_values(by="total", ascending=False, inplace=True)
        for _, row in prod_grp.iterrows():
            sales_by_product.append({
                "product": row["product"],
                "category": row["category"],
                "revenue": float(row["total"]),
                "units_sold": int(row["quantity"])
            })

    return {
        "overview": sales_overview,
        "trends": sales_trends,
        "category_sales": category_breakdown,
        "total_sales": sales_overview["total_sales"],
        "total_sales_formatted": sales_overview["total_sales_formatted"],
        "total_units_sold": sales_overview["total_units_sold"],
        "sales_growth": sales_overview["growth_rate_pct"],
        "avg_order_value": sales_overview["avg_order_value"],
        "sales_by_day": daily_dist,
        "sales_by_month": sales_trends,
        "sales_by_category": category_breakdown,
        "sales_by_product": sales_by_product,
        "monthly_targets": monthly_targets
    }


def get_inventory_analytics():
    """
    Computes inventory analysis:
    total stock, normal stock, low stock, critical stock,
    stock by category, inventory movement.
    """
    products = get_all_products()
    inv_overview = analyze_inventory_overview(products)
    stock_dist = analyze_stock_distribution(products)
    movement = analyze_inventory_movement()

    return {
        "overview": inv_overview,
        "stock_distribution": stock_dist,
        "total_stock": inv_overview["total_stock_units"],
        "total_valuation": inv_overview["total_valuation"],
        "total_valuation_formatted": inv_overview["total_valuation_formatted"],
        "normal_stock": inv_overview["normal_units"],
        "normal_pct": inv_overview["normal_pct"],
        "low_stock": inv_overview["low_units"],
        "low_pct": inv_overview["low_pct"],
        "critical_stock": inv_overview["critical_units"],
        "critical_pct": inv_overview["critical_pct"],
        "stock_by_category": stock_dist,
        "inventory_movement": movement
    }


def get_product_performance_analytics():
    """
    Computes product analysis:
    sales velocity, top-performing products, fast-moving products,
    normal-moving products, slow-moving products based on actual sales data.
    """
    products = get_all_products()
    sales = get_all_sales()
    return analyze_product_performance(products, sales)


def get_consolidated_analytics():
    """
    Consolidates sales, inventory, and product metrics for frontend analytics dashboard.
    """
    sales_data = get_sales_analytics()
    inventory_data = get_inventory_analytics()
    product_data = get_product_performance_analytics()

    return {
        "sales": sales_data,
        "inventory": inventory_data,
        "products": product_data,
        "performance": {
            "fast_moving": product_data["fast_moving_products"],
            "slow_moving": product_data["slow_moving_products"]
        }
    }
