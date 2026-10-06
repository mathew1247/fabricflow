"""
Inventory Service Layer.
Manages stock levels, reorder buffers, stock status updates, and audit adjustments
in the Cloud Firestore inventory collection.
"""

from firebase.firebase_config import get_db
from backend.services.product_service import calculate_stock_status
from backend.utils.helpers import get_current_timestamp
from analytics.inventory_analysis import analyze_inventory_overview


def get_all_inventory(search=None, category=None, status=None):
    """
    Retrieves inventory records from Firestore, merged with product details.
    """
    db = get_db()
    inv_docs = list(db.collection("inventory").stream())
    prod_docs = list(db.collection("products").stream())
    prod_map = {doc.id: doc.to_dict() for doc in prod_docs}

    results = []
    # If inventory collection is empty but products exist, backfill
    if not inv_docs and prod_docs:
        for p_doc in prod_docs:
            p_data = p_doc.to_dict()
            pid = p_data.get("product_id") or p_doc.id
            stock = max(0, int(p_data.get("stock", 0)))
            reorder = max(0, int(p_data.get("min_stock", 20)))
            st = calculate_stock_status(stock, reorder)
            now_str = get_current_timestamp()
            inv_entry = {
                "product_id": pid,
                "id": pid,
                "product_name": p_data.get("product_name") or p_data.get("name", "Garment"),
                "name": p_data.get("product_name") or p_data.get("name", "Garment"),
                "category_name": p_data.get("category_name") or p_data.get("category", "Casual"),
                "category": p_data.get("category_name") or p_data.get("category", "Casual"),
                "size": p_data.get("size", "M"),
                "price": float(p_data.get("price", 0)),
                "stock_quantity": stock,
                "stock": stock,
                "reorder_level": reorder,
                "min_stock": reorder,
                "stock_status": st,
                "status": st,
                "last_updated": now_str
            }
            db.collection("inventory").document(pid).set(inv_entry)
            results.append(inv_entry)
    else:
        for doc in inv_docs:
            inv = doc.to_dict()
            pid = inv.get("product_id") or doc.id
            p_data = prod_map.get(pid, {})

            stock = max(0, int(inv.get("stock_quantity", p_data.get("stock", 0))))
            reorder = max(0, int(inv.get("reorder_level", p_data.get("min_stock", 20))))
            st = calculate_stock_status(stock, reorder)

            pname = inv.get("product_name") or p_data.get("product_name") or p_data.get("name", "Garment")
            cname = inv.get("category_name") or p_data.get("category_name") or p_data.get("category", "Casual")
            size = inv.get("size") or p_data.get("size", "M")
            price = float(inv.get("price") if "price" in inv else p_data.get("price", 0))

            item = {
                "product_id": pid,
                "id": pid,
                "product_name": pname,
                "name": pname,
                "category_name": cname,
                "category": cname,
                "size": size,
                "price": price,
                "stock_quantity": stock,
                "stock": stock,
                "reorder_level": reorder,
                "min_stock": reorder,
                "stock_status": st,
                "status": st,
                "last_updated": inv.get("last_updated", get_current_timestamp())
            }

            # Search filter
            if search:
                q = search.lower().strip()
                if not (q in pid.lower() or q in pname.lower() or q in cname.lower()):
                    continue

            # Category filter
            if category and category.lower() != "all":
                if cname.lower() != category.lower():
                    continue

            # Status filter
            if status and status.lower() != "all":
                if st.lower() != status.lower():
                    continue

            results.append(item)

    results.sort(key=lambda x: str(x.get("product_id", "")))
    return results


def get_inventory_by_id(product_id):
    """Retrieves an inventory document by product_id."""
    db = get_db()
    inv_doc = db.collection("inventory").document(product_id).get()
    p_doc = db.collection("products").document(product_id).get()

    if not inv_doc.exists and not p_doc.exists:
        return None

    inv = inv_doc.to_dict() if inv_doc.exists else {}
    p_data = p_doc.to_dict() if p_doc.exists else {}

    stock = max(0, int(inv.get("stock_quantity", p_data.get("stock", 0))))
    reorder = max(0, int(inv.get("reorder_level", p_data.get("min_stock", 20))))
    st = calculate_stock_status(stock, reorder)
    pname = inv.get("product_name") or p_data.get("product_name") or p_data.get("name", "Garment")
    cname = inv.get("category_name") or p_data.get("category_name") or p_data.get("category", "Casual")

    return {
        "product_id": product_id,
        "id": product_id,
        "product_name": pname,
        "name": pname,
        "category_name": cname,
        "category": cname,
        "size": inv.get("size") or p_data.get("size", "M"),
        "price": float(inv.get("price") if "price" in inv else p_data.get("price", 0)),
        "stock_quantity": stock,
        "stock": stock,
        "reorder_level": reorder,
        "min_stock": reorder,
        "stock_status": st,
        "status": st,
        "last_updated": inv.get("last_updated", get_current_timestamp())
    }


def update_inventory(product_id, update_data):
    """
    Updates inventory document in Firestore.
    Recalculates stock_status and ensures stock_quantity >= 0.
    """
    db = get_db()
    inv_ref = db.collection("inventory").document(product_id)
    inv_doc = inv_ref.get()

    prod_ref = db.collection("products").document(product_id)
    prod_doc = prod_ref.get()

    if not inv_doc.exists and not prod_doc.exists:
        return None, f"Inventory record for product '{product_id}' not found."

    current_inv = inv_doc.to_dict() if inv_doc.exists else {}
    p_data = prod_doc.to_dict() if prod_doc.exists else {}

    # Extract new stock
    stock_val = update_data.get("stock_quantity") if "stock_quantity" in update_data else update_data.get("stock")
    if stock_val is not None:
        stock = int(stock_val)
        if stock < 0:
            return None, "Stock quantity cannot be negative."
    else:
        stock = max(0, int(current_inv.get("stock_quantity", p_data.get("stock", 0))))

    reorder_val = update_data.get("reorder_level") if "reorder_level" in update_data else update_data.get("min_stock", update_data.get("minStock"))
    if reorder_val is not None:
        reorder = int(reorder_val)
        if reorder < 0:
            return None, "Reorder level cannot be negative."
    else:
        reorder = max(0, int(current_inv.get("reorder_level", p_data.get("min_stock", 20))))

    stock_status = calculate_stock_status(stock, reorder)
    now_str = get_current_timestamp()
    pname = current_inv.get("product_name") or p_data.get("product_name") or p_data.get("name", "Garment")
    cname = current_inv.get("category_name") or p_data.get("category_name") or p_data.get("category", "Casual")

    inv_payload = {
        "product_id": product_id,
        "id": product_id,
        "product_name": pname,
        "name": pname,
        "category_name": cname,
        "category": cname,
        "size": current_inv.get("size") or p_data.get("size", "M"),
        "price": float(current_inv.get("price") if "price" in current_inv else p_data.get("price", 0)),
        "stock_quantity": stock,
        "stock": stock,
        "reorder_level": reorder,
        "min_stock": reorder,
        "stock_status": stock_status,
        "status": stock_status,
        "last_updated": now_str
    }

    inv_ref.set(inv_payload)

    # Sync to products document
    if prod_doc.exists:
        p_data["stock"] = stock
        p_data["stock_quantity"] = stock
        p_data["min_stock"] = reorder
        p_data["reorder_level"] = reorder
        p_data["status"] = stock_status
        p_data["stock_status"] = stock_status
        p_data["updated_at"] = now_str
        prod_ref.set(p_data)

    return inv_payload, None


def adjust_stock(product_id, adjustment_type, quantity, reason=""):
    """
    Adjusts stock level:
    - 'add': new_stock = current_stock + qty
    - 'deduct': new_stock = current_stock - qty (rejects if current_stock < qty)
    - 'set': new_stock = qty (rejects if qty < 0)
    - 'adjust': new_stock = current_stock + qty (rejects if current_stock + qty < 0)
    Recalculates stock_status and ensures stock_quantity cannot be negative.
    """
    db = get_db()
    current_inv = get_inventory_by_id(product_id)
    if not current_inv:
        return None, f"Product '{product_id}' not found in inventory."

    current_stock = int(current_inv.get("stock_quantity", 0))
    qty = int(quantity)

    if adjustment_type == "add":
        if qty < 0:
            return None, "Add quantity cannot be negative."
        new_stock = current_stock + qty
    elif adjustment_type == "deduct":
        if qty < 0:
            return None, "Deduct quantity cannot be negative."
        if current_stock < qty:
            return None, f"Insufficient stock: cannot deduct {qty} units from current stock of {current_stock}."
        new_stock = current_stock - qty
    elif adjustment_type == "set":
        if qty < 0:
            return None, "Stock quantity cannot be negative."
        new_stock = qty
    elif adjustment_type == "adjust":
        if current_stock + qty < 0:
            return None, f"Insufficient stock: adjustment of {qty} would result in negative stock."
        new_stock = current_stock + qty
    else:
        if current_stock + qty < 0:
            return None, f"Insufficient stock: adjustment of {qty} would result in negative stock."
        new_stock = current_stock + qty

    reorder = int(current_inv.get("reorder_level", 20))
    new_status = calculate_stock_status(new_stock, reorder)
    now_str = get_current_timestamp()

    # Save to inventory doc
    inv_doc_ref = db.collection("inventory").document(product_id)
    current_inv["stock_quantity"] = new_stock
    current_inv["stock"] = new_stock
    current_inv["stock_status"] = new_status
    current_inv["status"] = new_status
    current_inv["last_updated"] = now_str
    inv_doc_ref.set(current_inv)

    # Sync to products collection
    prod_ref = db.collection("products").document(product_id)
    prod_doc = prod_ref.get()
    if prod_doc.exists:
        p_data = prod_doc.to_dict()
        p_data["stock"] = new_stock
        p_data["stock_quantity"] = new_stock
        p_data["status"] = new_status
        p_data["stock_status"] = new_status
        p_data["updated_at"] = now_str
        prod_ref.set(p_data)

    # Audit log
    audit_log = {
        "product_id": product_id,
        "product_name": current_inv.get("product_name"),
        "previous_stock": current_stock,
        "new_stock": new_stock,
        "adjustment_type": adjustment_type,
        "quantity_changed": qty,
        "reason": reason or "Stock adjustment",
        "timestamp": now_str
    }
    try:
        db.collection("inventory_logs").add(audit_log)
    except Exception:
        pass

    return current_inv, None


def get_inventory_summary():
    """Computes comprehensive inventory metrics via Pandas."""
    items = get_all_inventory()
    return analyze_inventory_overview(items)


# Alias for backwards compatibility
get_inventory_list = get_all_inventory

