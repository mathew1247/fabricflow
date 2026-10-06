"""
Category Service Layer.
Manages garment categories and master classification hierarchies in Cloud Firestore.
"""

from firebase.firebase_config import get_db
from backend.utils.helpers import get_current_timestamp


def get_all_categories():
    """Retrieves all garment categories from Firestore."""
    db = get_db()
    cat_ref = db.collection("categories")
    docs = list(cat_ref.stream())

    categories = []
    for doc in docs:
        item = doc.to_dict()
        cid = item.get("category_id") or doc.id
        cname = item.get("category_name") or item.get("name", "")
        item["category_id"] = cid
        item["id"] = cid
        item["category_name"] = cname
        item["name"] = cname
        categories.append(item)

    # Sort categories alphabetically
    categories.sort(key=lambda x: str(x.get("category_name", "")).lower())
    return categories


def get_category_by_id(category_id):
    """Retrieves a single category document from Firestore."""
    db = get_db()
    doc = db.collection("categories").document(category_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    cid = data.get("category_id") or doc.id
    cname = data.get("category_name") or data.get("name", "")
    data["category_id"] = cid
    data["id"] = cid
    data["category_name"] = cname
    data["name"] = cname
    return data


def create_category(data):
    """
    Creates a new category in Firestore.
    Prevents duplicate category names where practical.
    """
    db = get_db()
    categories_ref = db.collection("categories")

    name = (data.get("category_name") or data.get("name") or "").strip()
    
    # Check duplicate name
    existing = get_all_categories()
    for cat in existing:
        if cat.get("category_name", "").lower() == name.lower():
            return None, f"Category '{name}' already exists."

    doc_id = data.get("category_id") or data.get("id")
    if not doc_id:
        doc_id = f"CAT-{str(len(existing) + 1).zfill(3)}"

    now_str = get_current_timestamp()
    category_doc = {
        "category_id": doc_id,
        "id": doc_id,
        "category_name": name,
        "name": name,
        "description": data.get("description", f"{name} Garments & Apparel").strip(),
        "created_at": now_str
    }

    categories_ref.document(doc_id).set(category_doc)
    return category_doc, None


def update_category(category_id, data):
    """Updates an existing category in Firestore."""
    db = get_db()
    doc_ref = db.collection("categories").document(category_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None, f"Category with ID '{category_id}' not found."

    current = doc.to_dict()
    new_name = (data.get("category_name") or data.get("name") or "").strip()

    if new_name and new_name.lower() != (current.get("category_name") or current.get("name", "")).lower():
        # Check duplicate
        all_cats = get_all_categories()
        for cat in all_cats:
            if cat["id"] != category_id and cat.get("category_name", "").lower() == new_name.lower():
                return None, f"Category name '{new_name}' already exists."
        current["category_name"] = new_name
        current["name"] = new_name

    if "description" in data:
        current["description"] = str(data["description"]).strip()

    current["updated_at"] = get_current_timestamp()
    current["category_id"] = category_id
    current["id"] = category_id

    doc_ref.set(current)
    return current, None


def delete_category(category_id):
    """Deletes a category from Firestore."""
    db = get_db()
    doc_ref = db.collection("categories").document(category_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True
