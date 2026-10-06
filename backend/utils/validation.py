"""
Validation helpers for FabricFlow Entities:
Products, Categories, Suppliers, Inventory, and Sales.
"""

from datetime import datetime

VALID_SIZES = ["XS", "S", "M", "L", "XL", "XXL", "28", "30", "32", "34", "36", "38", "Free Size"]
VALID_STOCK_STATUSES = ["Normal", "Low", "Critical"]
VALID_ORDER_STATUSES = ["Completed", "Pending", "Cancelled"]


def validate_product_payload(data, is_update=False):
    """
    Validates product payload.
    Checks product_name, category, size, price, stock_quantity, reorder_level, supplier.
    """
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    errors = []

    # Name validation
    name = data.get("product_name") or data.get("name")
    if not is_update or ("product_name" in data or "name" in data):
        if not name or not str(name).strip():
            errors.append("Product name is required and cannot be empty.")

    # Category validation
    category = data.get("category_name") or data.get("category")
    if not is_update or ("category_name" in data or "category" in data):
        if not category or not str(category).strip():
            errors.append("Category is required and cannot be empty.")

    # Size validation
    if "size" in data or not is_update:
        size = data.get("size")
        if size is not None and not str(size).strip():
            errors.append("Size cannot be empty.")

    # Price validation
    if "price" in data or not is_update:
        try:
            price = float(data.get("price", 0))
            if price < 0:
                errors.append("Price cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Price must be a valid numeric value.")

    # Stock quantity validation
    stock_val = data.get("stock_quantity") if "stock_quantity" in data else data.get("stock")
    if stock_val is not None or not is_update:
        try:
            stock = int(stock_val if stock_val is not None else 0)
            if stock < 0:
                errors.append("Stock quantity cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Stock quantity must be a valid integer.")

    # Reorder level validation
    reorder_val = data.get("reorder_level") if "reorder_level" in data else data.get("min_stock")
    if reorder_val is not None:
        try:
            reorder = int(reorder_val)
            if reorder < 0:
                errors.append("Reorder level cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Reorder level must be a valid integer.")

    # Supplier validation
    supplier = data.get("supplier_name") or data.get("supplier")
    if not is_update or ("supplier_name" in data or "supplier" in data):
        if supplier is not None and not str(supplier).strip():
            errors.append("Supplier cannot be empty.")

    return len(errors) == 0, errors


def validate_category_payload(data, is_update=False):
    """Validates category creation/update payload."""
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    errors = []
    name = data.get("category_name") or data.get("name")
    if not is_update or ("category_name" in data or "name" in data):
        if not name or not str(name).strip():
            errors.append("Category name is required.")

    return len(errors) == 0, errors


def validate_supplier_payload(data, is_update=False):
    """Validates supplier creation/update payload."""
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    errors = []
    name = data.get("supplier_name") or data.get("name")
    if not is_update or ("supplier_name" in data or "name" in data):
        if not name or not str(name).strip():
            errors.append("Supplier name is required.")

    contact = data.get("contact_number") or data.get("contact")
    if not is_update or ("contact_number" in data or "contact" in data):
        if not contact or not str(contact).strip():
            errors.append("Contact number is required.")

    return len(errors) == 0, errors


def validate_sale_payload(data):
    """Validates sale transaction payload."""
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    errors = []
    product = data.get("product_name") or data.get("product") or data.get("product_id")
    if not product or not str(product).strip():
        errors.append("Product name or ID is required.")

    # Quantity validation: must be > 0
    try:
        qty = int(data.get("quantity", 0))
        if qty <= 0:
            errors.append("Quantity must be greater than 0.")
    except (ValueError, TypeError):
        errors.append("Quantity must be a valid positive integer.")

    # Unit price validation
    if "unit_price" in data or "unitPrice" in data or "price" in data:
        try:
            unit_price = float(data.get("unit_price", data.get("unitPrice", data.get("price", 0))))
            if unit_price < 0:
                errors.append("Unit price cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Unit price must be a valid number.")

    # Sale date validation
    sale_date = data.get("sale_date") or data.get("date")
    if sale_date:
        try:
            # Check ISO format YYYY-MM-DD
            datetime.strptime(str(sale_date).split("T")[0], "%Y-%m-%d")
        except ValueError:
            errors.append("Sale date must be in YYYY-MM-DD format.")

    return len(errors) == 0, errors


def validate_stock_adjustment_payload(data):
    """Validates inventory stock adjustment."""
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    errors = []
    action_type = data.get("type", "set")
    if action_type not in ["add", "deduct", "set"]:
        errors.append("Invalid adjustment type. Must be 'add', 'deduct', or 'set'.")

    qty_val = data.get("quantity") if "quantity" in data else data.get("stock_quantity", data.get("qty"))
    try:
        qty = int(qty_val if qty_val is not None else 0)
        if qty < 0:
            errors.append("Stock quantity cannot be negative.")
    except (ValueError, TypeError):
        errors.append("Adjustment quantity must be an integer.")

    return len(errors) == 0, errors
