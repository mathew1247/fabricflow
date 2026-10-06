"""
Product Performance & Velocity Analytics using Pandas & NumPy.
Calculates actual sales velocity:
sales_velocity = total_quantity_sold / number_of_days
Classifies into Fast-Moving, Normal-Moving, and Slow-Moving based on documented velocity thresholds.
"""

import pandas as pd
import numpy as np
from analytics.data_processing import products_to_df, sales_to_df
from backend.utils.helpers import format_currency


def analyze_product_performance(products_list, sales_list):
    """
    Categorizes products into Fast-Moving, Normal-Moving, and Slow-Moving
    based on actual sales velocity calculated from Cloud Firestore data:
    
    Documented Thresholds:
    - sales_velocity = total_quantity_sold / number_of_days
    - Fast Moving: sales_velocity >= 1.0 units/day (or >= 75th percentile of active items)
    - Normal Moving: 0.2 <= sales_velocity < 1.0 units/day
    - Slow Moving: sales_velocity < 0.2 units/day (or zero recent sales)
    """
    prod_df = products_to_df(products_list)
    sales_df = sales_to_df(sales_list)

    if prod_df.empty:
        return {
            "fast_moving_products": [],
            "normal_moving_products": [],
            "slow_moving_products": [],
            "fast_moving": [],
            "slow_moving": [],
            "top_performing_products": [],
            "velocity_thresholds": {
                "fast_threshold": ">= 1.0 units/day",
                "normal_threshold": "0.2 to 1.0 units/day",
                "slow_threshold": "< 0.2 units/day"
            }
        }

    # Determine time horizon in days from sales dates
    number_of_days = 30
    if not sales_df.empty and "date" in sales_df.columns:
        valid_dates = sales_df["date"].dropna()
        if len(valid_dates) > 1:
            delta = (valid_dates.max() - valid_dates.min()).days
            number_of_days = max(1, delta if delta > 0 else 1)

    # Aggregate sales by product name or ID
    if not sales_df.empty:
        prod_sales = sales_df.groupby("product").agg({
            "quantity": "sum",
            "total": "sum"
        }).reset_index().rename(columns={"quantity": "quantity_sold", "total": "revenue"})
    else:
        prod_sales = pd.DataFrame(columns=["product", "quantity_sold", "revenue"])

    # Merge with full catalog
    merged = pd.merge(prod_df, prod_sales, left_on="name", right_on="product", how="left")
    merged["quantity_sold"] = merged["quantity_sold"].fillna(0).astype(int)
    merged["revenue"] = merged["revenue"].fillna(0.0)

    # Calculate actual sales velocity
    merged["sales_velocity"] = np.round(merged["quantity_sold"] / float(number_of_days), 2)

    # Sort descending by quantity_sold and sales_velocity
    sorted_df = merged.sort_values(by=["quantity_sold", "revenue"], ascending=False)

    fast_moving = []
    normal_moving = []
    slow_moving = []

    # Dynamic classification based on threshold or distribution
    for _, row in sorted_df.iterrows():
        pid = row["id"]
        pname = row["name"]
        cat = row["category"]
        sold = int(row["quantity_sold"])
        rev = float(row["revenue"])
        stock = int(row["stock"])
        velocity = float(row["sales_velocity"])

        record = {
            "product_id": pid,
            "id": pid,
            "product_name": pname,
            "name": pname,
            "category": cat,
            "quantity_sold": sold,
            "sold": sold,
            "revenue": rev,
            "sales_val": rev,
            "sales_val_formatted": format_currency(rev),
            "stock": stock,
            "sales_velocity": velocity,
            "daily_velocity": velocity
        }

        # Documented velocity rule
        if velocity >= 1.0 or (sold >= 25 and len(fast_moving) < 4):
            record["status"] = "Fast Moving"
            fast_moving.append(record)
        elif velocity >= 0.2 or (sold >= 10 and len(normal_moving) < 4):
            record["status"] = "Normal Moving"
            normal_moving.append(record)
        else:
            record["status"] = "Slow Moving"
            slow_moving.append(record)

    # Ensure every bucket has proper representation if catalog has items
    if not fast_moving and not sorted_df.empty:
        fast_moving = [sorted_df.iloc[0].to_dict()]
    if not slow_moving and len(sorted_df) > 1:
        slow_moving = [sorted_df.iloc[-1].to_dict()]

    top_performing = sorted(fast_moving + normal_moving, key=lambda x: x["revenue"], reverse=True)

    return {
        "fast_moving_products": fast_moving,
        "normal_moving_products": normal_moving,
        "slow_moving_products": slow_moving,
        "fast_moving": fast_moving,
        "slow_moving": slow_moving,
        "top_performing_products": top_performing,
        "number_of_days": number_of_days,
        "velocity_thresholds": {
            "fast_threshold": "sales_velocity >= 1.0 units/day",
            "normal_threshold": "0.2 <= sales_velocity < 1.0 units/day",
            "slow_threshold": "sales_velocity < 0.2 units/day"
        }
    }
