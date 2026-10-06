"""
Data Processing & Transformation Utilities using Pandas & NumPy.
Converts Cloud Firestore document collections into structured Pandas DataFrames.
"""

import pandas as pd
import numpy as np


def products_to_df(products_list):
    """Converts a list of product dictionaries into a clean Pandas DataFrame."""
    if not products_list:
        return pd.DataFrame(columns=[
            "id", "name", "category", "size", "price", "cost_price",
            "supplier", "stock", "min_stock", "status"
        ])

    df = pd.DataFrame(products_list)

    # Column name normalization
    if "id" not in df.columns and "product_id" in df.columns:
        df["id"] = df["product_id"]
    if "name" not in df.columns and "product_name" in df.columns:
        df["name"] = df["product_name"]
    if "category" not in df.columns and "category_name" in df.columns:
        df["category"] = df["category_name"]
    if "stock" not in df.columns and "stock_quantity" in df.columns:
        df["stock"] = df["stock_quantity"]
    if "min_stock" not in df.columns and "reorder_level" in df.columns:
        df["min_stock"] = df["reorder_level"]
    elif "min_stock" not in df.columns and "minStock" in df.columns:
        df["min_stock"] = df["minStock"]

    # Ensure required columns exist
    for col, default in [
        ("id", ""),
        ("name", "Unnamed Garment"),
        ("category", "Casual"),
        ("size", "M"),
        ("price", 0.0),
        ("stock", 0),
        ("min_stock", 20),
        ("cost_price", 0.0)
    ]:
        if col not in df.columns:
            df[col] = default

    # Normalize numeric columns
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    df["cost_price"] = pd.to_numeric(df["cost_price"], errors="coerce").fillna(df["price"] * 0.5)
    df["cost_price"] = np.where(df["cost_price"] <= 0, df["price"] * 0.5, df["cost_price"])
    df["stock"] = pd.to_numeric(df["stock"], errors="coerce").fillna(0).astype(int)
    df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce").fillna(20).astype(int)
    
    # Calculate valuation columns
    df["inventory_value"] = df["stock"] * df["price"]
    df["cost_value"] = df["stock"] * df["cost_price"]

    # Normalize string columns
    df["category"] = df["category"].astype(str).str.strip()
    df["size"] = df["size"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()

    return df


def sales_to_df(sales_list):
    """Converts a list of sales transactions into a clean Pandas DataFrame."""
    if not sales_list:
        return pd.DataFrame(columns=[
            "id", "product", "category", "quantity", "unit_price", "total", "date", "status"
        ])

    df = pd.DataFrame(sales_list)

    # Column name mappings
    if "id" not in df.columns and "sale_id" in df.columns:
        df["id"] = df["sale_id"]
    if "product" not in df.columns and "product_name" in df.columns:
        df["product"] = df["product_name"]
    if "category" not in df.columns and "category_name" in df.columns:
        df["category"] = df["category_name"]
    if "unit_price" not in df.columns and "unitPrice" in df.columns:
        df["unit_price"] = df["unitPrice"]
    if "total" not in df.columns and "total_amount" in df.columns:
        df["total"] = df["total_amount"]
    if "date" not in df.columns and "sale_date" in df.columns:
        df["date"] = df["sale_date"]

    for col, default in [
        ("id", ""),
        ("product", "Garment Item"),
        ("category", "Casual"),
        ("quantity", 0),
        ("unit_price", 0.0),
        ("status", "Completed")
    ]:
        if col not in df.columns:
            df[col] = default

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    
    if "total" not in df.columns:
        df["total"] = df["quantity"] * df["unit_price"]
    else:
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(df["quantity"] * df["unit_price"])

    # Parse dates
    date_col = df["date"] if "date" in df.columns else pd.Timestamp.now()
    df["date"] = pd.to_datetime(date_col, errors="coerce").fillna(pd.Timestamp.now())
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    df["month"] = df["date"].dt.strftime("%b")
    df["month_year"] = df["date"].dt.strftime("%Y-%m")
    df["day_of_week"] = df["date"].dt.strftime("%a")

    df["status"] = df["status"].astype(str)
    df["category"] = df["category"].astype(str)
    df["product"] = df["product"].astype(str)

    return df


def suppliers_to_df(suppliers_list):
    """Converts a list of suppliers into a clean Pandas DataFrame."""
    if not suppliers_list:
        return pd.DataFrame(columns=[
            "id", "name", "contact", "email", "address", "products_supplied", "status"
        ])

    df = pd.DataFrame(suppliers_list)
    if "id" not in df.columns and "supplier_id" in df.columns:
        df["id"] = df["supplier_id"]
    if "name" not in df.columns and "supplier_name" in df.columns:
        df["name"] = df["supplier_name"]
    if "contact" not in df.columns and "contact_number" in df.columns:
        df["contact"] = df["contact_number"]

    for col, default in [
        ("products_supplied", 6),
        ("lead_time_days", 7)
    ]:
        if col not in df.columns:
            df[col] = default

    df["products_supplied"] = pd.to_numeric(df["products_supplied"], errors="coerce").fillna(0).astype(int)
    df["lead_time_days"] = pd.to_numeric(df["lead_time_days"], errors="coerce").fillna(7).astype(int)
    return df
