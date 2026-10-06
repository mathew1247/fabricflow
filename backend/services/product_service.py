"""
Product Service Layer.
Manages garment catalog and CRUD operations with Firebase Cloud Firestore.
Synchronizes with the inventory collection.
"""

from firebase.firebase_config import get_db
from backend.utils.helpers import get_current_timestamp
from config import Config


def calculate_stock_status(stock_quantity, reorder_level=None):
    """
    Computes garment stock status according to specification:
    if stock_quantity <= 0: Critical
    elif stock_quantity <= reorder_level: Low
    else: Normal
    """
    try:
        qty = int(stock_quantity)
    except (ValueError, TypeError):
        qty = 0

    if reorder_level is None:
        reorder_level = Config.DEFAULT_LOW_STOCK_THRESHOLD

    try:
        reorder = int(reorder_level)
    except (ValueError, TypeError):
        reorder = 20

    if qty <= 0:
        return "Critical"
    elif qty <= reorder:
        return "Low"
    return "Normal"


def get_all_products(search=None, category=None, size=None, status=None, limit=None, offset=None):
    """
    Fetches all products from Firestore products collection,
    merging real-time stock levels from the inventory collection.
    """
    db = get_db()
    products_ref = db.collection("products")
    prod_docs = list(products_ref.stream())

    # Map inventory records by product_id
    inventory_ref = db.collection("inventory")
    inv_docs = list(inventory_ref.stream())
    inv_map = {doc.id: doc.to_dict() for doc in inv_docs}

    results = []
    for doc in prod_docs:
        item = doc.to_dict()
        pid = item.get("product_id") or doc.id
        item["product_id"] = pid
        item["id"] = pid

        # Merge inventory data
        inv = inv_map.get(pid, {})
        stock_qty = inv.get("stock_quantity") if "stock_quantity" in inv else item.get("stock", 0)
        reorder = inv.get("reorder_level") if "reorder_level" in inv else item.get("min_stock", item.get("minStock", 20))
        stock_status = calculate_stock_status(stock_qty, reorder)

        item["stock_quantity"] = int(stock_qty)
        item["stock"] = int(stock_qty)
        item["reorder_level"] = int(reorder)
        item["min_stock"] = int(reorder)
        item["minStock"] = int(reorder)
        item["stock_status"] = stock_status
        item["status"] = stock_status

        # Standardize name / category / supplier
        pname = item.get("product_name") or item.get("name", "Unnamed Garment")
        cname = item.get("category_name") or item.get("category", "Casual")
        sname = item.get("supplier_name") or item.get("supplier", "ABC Textiles")

        item["product_name"] = pname
        item["name"] = pname
        item["category_name"] = cname
        item["category"] = cname
        item["supplier_name"] = sname
        item["supplier"] = sname
        item["price"] = float(item.get("price", 0))

        # Search filter
        if search:
            q = search.lower().strip()
            name_match = q in pname.lower()
            id_match = q in pid.lower()
            sup_match = q in sname.lower()
            cat_match = q in cname.lower()
            if not (name_match or id_match or sup_match or cat_match):
                continue

        # Category filter
        if category and category.lower() != "all":
            if cname.lower() != category.lower():
                continue

        # Size filter
        if size and size.lower() != "all":
            if str(item.get("size", "")).lower() != size.lower():
                continue

        # Stock Status filter
        if status and status.lower() != "all":
            if stock_status.lower() != status.lower():
                continue

        results.append(item)

    # Sort by ID or creation date
    results.sort(key=lambda x: str(x.get("product_id", "")), reverse=False)

    if offset and isinstance(offset, int):
        results = results[offset:]
    if limit and isinstance(limit, int):
        results = results[:limit]

    return results


def get_product_by_id(product_id):
    """Retrieves a single product from Firestore with its inventory status."""
    db = get_db()
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    data["product_id"] = doc.id
    data["id"] = doc.id

    # Check inventory doc
    inv_doc = db.collection("inventory").document(product_id).get()
    if inv_doc.exists:
        inv = inv_doc.to_dict()
        stock = inv.get("stock_quantity", 0)
        reorder = inv.get("reorder_level", 20)
    else:
        stock = data.get("stock", 0)
        reorder = data.get("min_stock", data.get("minStock", 20))

    stock_status = calculate_stock_status(stock, reorder)
    data["stock_quantity"] = int(stock)
    data["stock"] = int(stock)
    data["reorder_level"] = int(reorder)
    data["min_stock"] = int(reorder)
    data["stock_status"] = stock_status
    data["status"] = stock_status
    data["product_name"] = data.get("product_name") or data.get("name", "")
    data["name"] = data["product_name"]
    data["category_name"] = data.get("category_name") or data.get("category", "")
    data["category"] = data["category_name"]
    data["supplier_name"] = data.get("supplier_name") or data.get("supplier", "")
    data["supplier"] = data["supplier_name"]
    data["price"] = float(data.get("price", 0))

    return data


def create_product(product_data):
    """
    Creates a new product document in Firestore products collection,
    and automatically creates the corresponding inventory document.
    """
    db = get_db()
    products_ref = db.collection("products")
    inventory_ref = db.collection("inventory")

    # Generate custom SKU if not provided
    doc_id = product_data.get("product_id") or product_data.get("id")
    if not doc_id:
        existing_docs = list(products_ref.stream())
        doc_id = f"P{str(len(existing_docs) + 1).zfill(3)}"

    pname = (product_data.get("product_name") or product_data.get("name") or "").strip()
    cname = (product_data.get("category_name") or product_data.get("category") or "Casual").strip()
    cid = product_data.get("category_id") or f"CAT-{cname.lower()[:3].upper()}"
    sname = (product_data.get("supplier_name") or product_data.get("supplier") or "ABC Textiles").strip()
    sid = product_data.get("supplier_id") or f"SUP-{sname.lower()[:3].upper()}"
    size = str(product_data.get("size", "M")).strip()
    price = float(product_data.get("price", 0))
    desc = product_data.get("description", f"{pname} in {cname} collection")
    
    stock_qty = max(0, int(product_data.get("stock_quantity", product_data.get("stock", 0))))
    reorder = max(0, int(product_data.get("reorder_level", product_data.get("min_stock", product_data.get("minStock", 20)))))
    stock_status = calculate_stock_status(stock_qty, reorder)
    now_str = get_current_timestamp()

    product_payload = {
        "product_id": doc_id,
        "id": doc_id,
        "product_name": pname,
        "name": pname,
        "category_id": cid,
        "category_name": cname,
        "category": cname,
        "size": size,
        "price": price,
        "supplier_id": sid,
        "supplier_name": sname,
        "supplier": sname,
        "description": desc,
        "created_at": now_str,
        "updated_at": now_str,
        "stock": stock_qty,
        "stock_quantity": stock_qty,
        "min_stock": reorder,
        "reorder_level": reorder,
        "status": stock_status,
        "stock_status": stock_status
    }

    # Inventory document payload
    inventory_payload = {
        "product_id": doc_id,
        "product_name": pname,
        "category_name": cname,
        "size": size,
        "price": price,
        "stock_quantity": stock_qty,
        "reorder_level": reorder,
        "stock_status": stock_status,
        "last_updated": now_str
    }

    # Store product and corresponding inventory document
    products_ref.document(doc_id).set(product_payload)
    inventory_ref.document(doc_id).set(inventory_payload)

    return product_payload


def update_product(product_id, update_data):
    """Updates product document and synchronizes updated inventory fields."""
    db = get_db()
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    current = doc.to_dict()
    now_str = get_current_timestamp()

    # Update product fields
    if "product_name" in update_data or "name" in update_data:
        val = (update_data.get("product_name") or update_data.get("name", "")).strip()
        current["product_name"] = val
        current["name"] = val

    if "category_name" in update_data or "category" in update_data:
        val = (update_data.get("category_name") or update_data.get("category", "")).strip()
        current["category_name"] = val
        current["category"] = val

    if "category_id" in update_data:
        current["category_id"] = str(update_data["category_id"]).strip()

    if "size" in update_data:
        current["size"] = str(update_data["size"]).strip()

    if "price" in update_data:
        current["price"] = float(update_data["price"])

    if "supplier_name" in update_data or "supplier" in update_data:
        val = (update_data.get("supplier_name") or update_data.get("supplier", "")).strip()
        current["supplier_name"] = val
        current["supplier"] = val

    if "supplier_id" in update_data:
        current["supplier_id"] = str(update_data["supplier_id"]).strip()

    if "description" in update_data:
        current["description"] = str(update_data["description"]).strip()

    # Check if stock/reorder updated
    inv_doc_ref = db.collection("inventory").document(product_id)
    inv_doc = inv_doc_ref.get()
    inv_data = inv_doc.to_dict() if inv_doc.exists else {}

    stock_val = update_data.get("stock_quantity") if "stock_quantity" in update_data else update_data.get("stock")
    if stock_val is not None:
        new_stock = max(0, int(stock_val))
    else:
        new_stock = inv_data.get("stock_quantity", current.get("stock", 0))

    reorder_val = update_data.get("reorder_level") if "reorder_level" in update_data else update_data.get("min_stock", update_data.get("minStock"))
    if reorder_val is not None:
        new_reorder = max(0, int(reorder_val))
    else:
        new_reorder = inv_data.get("reorder_level", current.get("min_stock", 20))

    new_status = calculate_stock_status(new_stock, new_reorder)

    current["stock"] = new_stock
    current["stock_quantity"] = new_stock
    current["min_stock"] = new_reorder
    current["reorder_level"] = new_reorder
    current["status"] = new_status
    current["stock_status"] = new_status
    current["updated_at"] = now_str
    current["product_id"] = product_id
    current["id"] = product_id

    doc_ref.set(current)

    # Sync inventory doc
    inv_data["product_id"] = product_id
    inv_data["product_name"] = current["product_name"]
    inv_data["category_name"] = current["category_name"]
    inv_data["size"] = current.get("size", "M")
    inv_data["price"] = current.get("price", 0)
    inv_data["stock_quantity"] = new_stock
    inv_data["reorder_level"] = new_reorder
    inv_data["stock_status"] = new_status
    inv_data["last_updated"] = now_str
    inv_doc_ref.set(inv_data)

    return current


def delete_product(product_id):
    """
    Safely deletes a product and its inventory record from Firestore.
    Does NOT delete sales transactions to preserve financial audit history.
    """
    db = get_db()
    prod_ref = db.collection("products").document(product_id)
    prod_doc = prod_ref.get()
    if not prod_doc.exists:
        return False

    # Delete product document
    prod_ref.delete()

    # Delete corresponding inventory record
    inv_ref = db.collection("inventory").document(product_id)
    if inv_ref.get().exists:
        inv_ref.delete()

    return True
