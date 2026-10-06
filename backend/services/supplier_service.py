"""
Supplier Service Layer.
Manages textile mills, garment suppliers, contact channels, and lead times in Cloud Firestore.
"""

from firebase.firebase_config import get_db
from backend.utils.helpers import get_current_timestamp


def get_all_suppliers(search=None, status=None):
    """Retrieves all suppliers from Firestore with search and status filtering."""
    db = get_db()
    suppliers_ref = db.collection("suppliers")
    docs = list(suppliers_ref.stream())

    results = []
    for doc in docs:
        item = doc.to_dict()
        sid = item.get("supplier_id") or doc.id
        sname = item.get("supplier_name") or item.get("name", "")
        contact = item.get("contact_number") or item.get("contact", "")

        item["supplier_id"] = sid
        item["id"] = sid
        item["supplier_name"] = sname
        item["name"] = sname
        item["contact_number"] = contact
        item["contact"] = contact
        item["productsSupplied"] = item.get("products_supplied", item.get("productsSupplied", 8))
        item["products_supplied"] = item["productsSupplied"]

        if search:
            q = search.lower().strip()
            name_match = q in sname.lower()
            id_match = q in sid.lower()
            addr_match = q in str(item.get("address", "")).lower()
            if not (name_match or id_match or addr_match):
                continue

        if status and status.lower() != "all":
            if str(item.get("status", "")).lower() != status.lower():
                continue

        results.append(item)

    results.sort(key=lambda x: str(x.get("supplier_id", "")))
    return results


def get_supplier_by_id(supplier_id):
    """Retrieves a single supplier by ID."""
    db = get_db()
    doc = db.collection("suppliers").document(supplier_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    sid = data.get("supplier_id") or doc.id
    sname = data.get("supplier_name") or data.get("name", "")
    contact = data.get("contact_number") or data.get("contact", "")
    data["supplier_id"] = sid
    data["id"] = sid
    data["supplier_name"] = sname
    data["name"] = sname
    data["contact_number"] = contact
    data["contact"] = contact
    data["productsSupplied"] = data.get("products_supplied", data.get("productsSupplied", 8))
    data["products_supplied"] = data["productsSupplied"]
    return data


def create_supplier(supplier_data):
    """Adds a new supplier to Firestore."""
    db = get_db()
    suppliers_ref = db.collection("suppliers")

    doc_id = supplier_data.get("supplier_id") or supplier_data.get("id")
    if not doc_id:
        existing = list(suppliers_ref.stream())
        doc_id = f"SUP-{100 + len(existing) + 1}"

    sname = (supplier_data.get("supplier_name") or supplier_data.get("name") or "").strip()
    contact = (supplier_data.get("contact_number") or supplier_data.get("contact") or "").strip()
    now_str = get_current_timestamp()

    payload = {
        "supplier_id": doc_id,
        "id": doc_id,
        "supplier_name": sname,
        "name": sname,
        "contact_number": contact,
        "contact": contact,
        "email": supplier_data.get("email", "").strip(),
        "address": supplier_data.get("address", "").strip(),
        "products_supplied": int(supplier_data.get("products_supplied", supplier_data.get("productsSupplied", 8))),
        "productsSupplied": int(supplier_data.get("products_supplied", supplier_data.get("productsSupplied", 8))),
        "status": supplier_data.get("status", "Active"),
        "lead_time_days": int(supplier_data.get("lead_time_days", 7)),
        "created_at": now_str,
        "updated_at": now_str
    }

    suppliers_ref.document(doc_id).set(payload)
    return payload


def update_supplier(supplier_id, update_data):
    """Updates an existing supplier in Firestore."""
    db = get_db()
    doc_ref = db.collection("suppliers").document(supplier_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    current = doc.to_dict()
    if "supplier_name" in update_data or "name" in update_data:
        val = (update_data.get("supplier_name") or update_data.get("name", "")).strip()
        current["supplier_name"] = val
        current["name"] = val

    if "contact_number" in update_data or "contact" in update_data:
        val = (update_data.get("contact_number") or update_data.get("contact", "")).strip()
        current["contact_number"] = val
        current["contact"] = val

    for field in ["email", "address", "status"]:
        if field in update_data:
            current[field] = str(update_data[field]).strip()

    if "products_supplied" in update_data or "productsSupplied" in update_data:
        cnt = int(update_data.get("products_supplied", update_data.get("productsSupplied", 8)))
        current["products_supplied"] = cnt
        current["productsSupplied"] = cnt

    now_str = get_current_timestamp()
    current["updated_at"] = now_str
    current["supplier_id"] = supplier_id
    current["id"] = supplier_id

    doc_ref.set(current)
    return current


def delete_supplier(supplier_id):
    """Deletes a supplier from Firestore."""
    db = get_db()
    doc_ref = db.collection("suppliers").document(supplier_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False
    doc_ref.delete()
    return True
