"""
Sales Service Layer.
Handles sales orders, customer transactions, and atomic inventory reduction
in Cloud Firestore using atomic batch writes/transactions.
"""

from datetime import datetime
from firebase.firebase_config import get_db
from backend.services.product_service import get_all_products, calculate_stock_status
from backend.utils.helpers import get_current_timestamp, format_currency


def get_all_sales(search=None, category=None, status=None, limit=None):
    """Retrieves all sales records from Firestore with optional filtering."""
    db = get_db()
    sales_ref = db.collection("sales")
    docs = list(sales_ref.stream())

    results = []
    for doc in docs:
        item = doc.to_dict()
        sid = item.get("sale_id") or doc.id
        pid = item.get("product_id") or ""
        pname = item.get("product_name") or item.get("product", "Garment Item")
        cname = item.get("category_name") or item.get("category", "Casual")

        qty = int(item.get("quantity", 0))
        unit_price = float(item.get("unit_price") if "unit_price" in item else item.get("unitPrice", 0))
        total = float(item.get("total_amount") if "total_amount" in item else item.get("total", qty * unit_price))
        sdate = item.get("sale_date") or item.get("date", datetime.now().strftime("%Y-%m-%d"))

        item["sale_id"] = sid
        item["id"] = sid
        item["product_id"] = pid
        item["product_name"] = pname
        item["product"] = pname
        item["category_name"] = cname
        item["category"] = cname
        item["quantity"] = qty
        item["unit_price"] = unit_price
        item["unitPrice"] = unit_price
        item["total_amount"] = total
        item["total"] = total
        item["total_formatted"] = format_currency(total)
        item["sale_date"] = sdate
        item["date"] = sdate
        item["status"] = item.get("status", "Completed")

        # Search filter
        if search:
            q = search.lower().strip()
            if not (q in sid.lower() or q in pname.lower() or q in cname.lower()):
                continue

        # Category filter
        if category and category.lower() != "all":
            if cname.lower() != category.lower():
                continue

        # Status filter
        if status and status.lower() != "all":
            if item["status"].lower() != status.lower():
                continue

        results.append(item)

    # Sort descending by date then ID
    results.sort(key=lambda x: str(x.get("sale_date", "")) + str(x.get("sale_id", "")), reverse=True)

    if limit and isinstance(limit, int):
        results = results[:limit]

    return results


def get_sale_by_id(sale_id):
    """Retrieves a single sale transaction by ID."""
    db = get_db()
    doc = db.collection("sales").document(sale_id).get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    sid = data.get("sale_id") or doc.id
    qty = int(data.get("quantity", 0))
    unit_price = float(data.get("unit_price") if "unit_price" in data else data.get("unitPrice", 0))
    total = float(data.get("total_amount") if "total_amount" in data else data.get("total", qty * unit_price))
    pname = data.get("product_name") or data.get("product", "Garment Item")
    cname = data.get("category_name") or data.get("category", "Casual")
    sdate = data.get("sale_date") or data.get("date", datetime.now().strftime("%Y-%m-%d"))

    data["sale_id"] = sid
    data["id"] = sid
    data["product_name"] = pname
    data["product"] = pname
    data["category_name"] = cname
    data["category"] = cname
    data["quantity"] = qty
    data["unit_price"] = unit_price
    data["unitPrice"] = unit_price
    data["total_amount"] = total
    data["total"] = total
    data["total_formatted"] = format_currency(total)
    data["sale_date"] = sdate
    data["date"] = sdate
    return data


def record_sale(sale_data):
    """
    Atomically records a new garment sales transaction and deducts inventory in Cloud Firestore:
    1. Validate product.
    2. Read current inventory.
    3. Validate requested quantity.
    4. Make sure enough stock exists.
    5. Get product price.
    6. Calculate total_amount = quantity * unit_price.
    7. Create sales document.
    8. Reduce inventory.
    9. Recalculate stock status.
    10. Save updated inventory via atomic Firestore batch write.
    """
    db = get_db()

    # Step 1: Identify and validate product
    target_product_id = sale_data.get("product_id")
    product_name_input = sale_data.get("product_name") or sale_data.get("product")
    products = get_all_products()

    matched_product = None
    if target_product_id:
        for p in products:
            if p.get("product_id") == target_product_id or p.get("id") == target_product_id:
                matched_product = p
                break

    if not matched_product and product_name_input:
        for p in products:
            if p.get("product_name", "").lower() == product_name_input.lower() or p.get("name", "").lower() == product_name_input.lower():
                matched_product = p
                break

    if not matched_product:
        return None, "Product not found. Please provide a valid product ID or name."

    product_id = matched_product["product_id"]
    product_name = matched_product["product_name"]
    category_id = matched_product.get("category_id", "CAT-001")
    category_name = matched_product.get("category_name", "Casual")

    # Step 2: Read current inventory
    inv_doc_ref = db.collection("inventory").document(product_id)
    inv_doc = inv_doc_ref.get()
    
    if inv_doc.exists:
        inv_data = inv_doc.to_dict()
        current_stock = int(inv_data.get("stock_quantity", 0))
        reorder_level = int(inv_data.get("reorder_level", 20))
    else:
        current_stock = int(matched_product.get("stock_quantity", matched_product.get("stock", 0)))
        reorder_level = int(matched_product.get("reorder_level", 20))

    # Step 3: Validate requested quantity
    try:
        qty = int(sale_data.get("quantity", 1))
        if qty <= 0:
            return None, "Sale quantity must be greater than zero."
    except (ValueError, TypeError):
        return None, "Invalid sale quantity."

    # Step 4: Make sure enough stock exists
    status = sale_data.get("status", "Completed")
    if status == "Completed" and current_stock < qty:
        return None, f"Insufficient stock: Requested {qty} units, but only {current_stock} available for {product_name}."

    # Step 5: Get product price
    price_val = sale_data.get("unit_price") if "unit_price" in sale_data else sale_data.get("unitPrice", matched_product.get("price", 0))
    unit_price = float(price_val) if price_val is not None else float(matched_product.get("price", 0))

    # Step 6: Calculate total_amount
    total_amount = qty * unit_price

    # Step 7: Prepare sales document
    sales_ref = db.collection("sales")
    doc_id = sale_data.get("sale_id") or sale_data.get("id")
    if not doc_id:
        existing_sales = list(sales_ref.stream())
        doc_id = f"S{str(len(existing_sales) + 1).zfill(3)}"

    now_str = get_current_timestamp()
    sale_date = sale_data.get("sale_date") or sale_data.get("date") or datetime.now().strftime("%Y-%m-%d")

    sale_record = {
        "sale_id": doc_id,
        "id": doc_id,
        "product_id": product_id,
        "product_name": product_name,
        "product": product_name,
        "category_id": category_id,
        "category_name": category_name,
        "category": category_name,
        "quantity": qty,
        "unit_price": unit_price,
        "unitPrice": unit_price,
        "total_amount": total_amount,
        "total": total_amount,
        "total_formatted": format_currency(total_amount),
        "sale_date": sale_date,
        "date": sale_date,
        "status": status,
        "created_by": sale_data.get("created_by", "admin"),
        "created_at": now_str
    }

    # Step 8-10: Reduce inventory & recalculate stock status atomically using Firestore batch
    batch = db.batch()

    # 1. Add sale document
    sale_doc_ref = sales_ref.document(doc_id)
    batch.set(sale_doc_ref, sale_record)

    # 2. Update inventory if sale is Completed
    if status == "Completed":
        new_stock = max(0, current_stock - qty)
        new_stock_status = calculate_stock_status(new_stock, reorder_level)

        updated_inv_payload = {
            "product_id": product_id,
            "product_name": product_name,
            "category_name": category_name,
            "size": matched_product.get("size", "M"),
            "price": unit_price,
            "stock_quantity": new_stock,
            "reorder_level": reorder_level,
            "stock_status": new_stock_status,
            "last_updated": now_str
        }
        batch.set(inv_doc_ref, updated_inv_payload)

        # 3. Update products catalog doc
        prod_doc_ref = db.collection("products").document(product_id)
        prod_doc = prod_doc_ref.get()
        if prod_doc.exists:
            p_data = prod_doc.to_dict()
            p_data["stock"] = new_stock
            p_data["stock_quantity"] = new_stock
            p_data["status"] = new_stock_status
            p_data["stock_status"] = new_stock_status
            p_data["updated_at"] = now_str
            batch.set(prod_doc_ref, p_data)

    # Commit atomic batch write
    batch.commit()

    return sale_record, None


def delete_sale(sale_id):
    """Deletes a sale document by ID."""
    db = get_db()
    doc_ref = db.collection("sales").document(sale_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True
