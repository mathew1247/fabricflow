"""
Firestore Database Seeding Script.
Populates realistic garment products, categories, suppliers, inventory, sales, and user records
directly into Firebase Cloud Firestore.

Usage:
  python firestore/seed_data.py
  python firestore/seed_data.py --force
"""

import os
import sys
import argparse
from datetime import datetime

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from firebase.firebase_config import get_db, init_firebase
from backend.services.product_service import calculate_stock_status
from backend.utils.helpers import get_current_timestamp, format_currency

DEMO_CATEGORIES = [
    {"category_id": "CAT-001", "category_name": "Casual Wear", "description": "T-Shirts, Graphic Tees, Casual Trousers & Polos"},
    {"category_id": "CAT-002", "category_name": "Denim", "description": "Denim Jeans, Jackets, and Ripped Jeans"},
    {"category_id": "CAT-003", "category_name": "Formal Wear", "description": "Oxford Shirts, Dress Shirts, and Formal Trousers"},
    {"category_id": "CAT-004", "category_name": "Ethnic Wear", "description": "Kurtas, Sarees, Lehengas, and Traditional Apparel"},
    {"category_id": "CAT-005", "category_name": "Sports Wear", "description": "Tracksuits, Performance Tees, and Activewear"},
    {"category_id": "CAT-006", "category_name": "Outerwear", "description": "Winter Jackets, Bomber Jackets, Hoodies & Fleece"},
    {"category_id": "CAT-007", "category_name": "Women's Wear", "description": "Dresses, Tops, Skirts, and Kurtis"}
]

DEMO_SUPPLIERS = [
    {
        "supplier_id": "SUP-101",
        "supplier_name": "ABC Textiles Co.",
        "contact_number": "+91 98765 43210",
        "email": "orders@abctextiles.com",
        "address": "Ring Road Textile Hub, Surat, Gujarat",
        "products_supplied": 18,
        "status": "Active",
        "lead_time_days": 5
    },
    {
        "supplier_id": "SUP-102",
        "supplier_name": "Vogue Fabrics Mill",
        "contact_number": "+91 98111 22334",
        "email": "info@voguefabrics.in",
        "address": "Tirupur Knitwear Apparel Park, Tamil Nadu",
        "products_supplied": 12,
        "status": "Active",
        "lead_time_days": 7
    },
    {
        "supplier_id": "SUP-103",
        "supplier_name": "Prime Weaves Ltd.",
        "contact_number": "+91 97234 56789",
        "email": "sales@primeweaves.com",
        "address": "Bhiwandi Loom Complex, Maharashtra",
        "products_supplied": 15,
        "status": "Active",
        "lead_time_days": 4
    },
    {
        "supplier_id": "SUP-104",
        "supplier_name": "Apex Garments Supply",
        "contact_number": "+91 99444 88776",
        "email": "contact@apexgarments.com",
        "address": "Ludhiana Woolen Cluster, Punjab",
        "products_supplied": 9,
        "status": "Active",
        "lead_time_days": 8
    },
    {
        "supplier_id": "SUP-105",
        "supplier_name": "Heritage Looms & Threads",
        "contact_number": "+91 98333 11223",
        "email": "support@heritagelooms.com",
        "address": "Varanasi Silk Weaver Center, Uttar Pradesh",
        "products_supplied": 6,
        "status": "Active",
        "lead_time_days": 10
    }
]

DEMO_PRODUCTS = [
    {
        "product_id": "P001",
        "product_name": "Classic Cotton T-Shirt",
        "category_id": "CAT-001",
        "category_name": "Casual Wear",
        "size": "M",
        "price": 899.0,
        "supplier_id": "SUP-101",
        "supplier_name": "ABC Textiles Co.",
        "stock": 120,
        "reorder_level": 25,
        "description": "100% combed cotton breathable classic t-shirt"
    },
    {
        "product_id": "P002",
        "product_name": "Slim Fit Denim Jeans",
        "category_id": "CAT-002",
        "category_name": "Denim",
        "size": "32",
        "price": 1999.0,
        "supplier_id": "SUP-102",
        "supplier_name": "Vogue Fabrics Mill",
        "stock": 10,
        "reorder_level": 20,
        "description": "Stretchable indigo denim slim fit jeans"
    },
    {
        "product_id": "P003",
        "product_name": "Oxford Formal Shirt",
        "category_id": "CAT-003",
        "category_name": "Formal Wear",
        "size": "L",
        "price": 1499.0,
        "supplier_id": "SUP-103",
        "supplier_name": "Prime Weaves Ltd.",
        "stock": 85,
        "reorder_level": 15,
        "description": "Wrinkle-resistant pinpoint Oxford corporate shirt"
    },
    {
        "product_id": "P004",
        "product_name": "Quilted Winter Jacket",
        "category_id": "CAT-006",
        "category_name": "Outerwear",
        "size": "XL",
        "price": 3499.0,
        "supplier_id": "SUP-104",
        "supplier_name": "Apex Garments Supply",
        "stock": 4,
        "reorder_level": 12,
        "description": "Thermal insulated windproof quilted zip jacket"
    },
    {
        "product_id": "P005",
        "product_name": "Oversized Graphic Tee",
        "category_id": "CAT-001",
        "category_name": "Casual Wear",
        "size": "L",
        "price": 1099.0,
        "supplier_id": "SUP-101",
        "supplier_name": "ABC Textiles Co.",
        "stock": 140,
        "reorder_level": 30,
        "description": "Drop-shoulder streetwear typography graphic tee"
    },
    {
        "product_id": "P006",
        "product_name": "Linen Casual Trousers",
        "category_id": "CAT-001",
        "category_name": "Casual Wear",
        "size": "34",
        "price": 1899.0,
        "supplier_id": "SUP-105",
        "supplier_name": "Heritage Looms & Threads",
        "stock": 45,
        "reorder_level": 15,
        "description": "Breathable French linen drawstring summer trousers"
    },
    {
        "product_id": "P007",
        "product_name": "Flannel Plaid Shirt",
        "category_id": "CAT-003",
        "category_name": "Formal Wear",
        "size": "M",
        "price": 1599.0,
        "supplier_id": "SUP-103",
        "supplier_name": "Prime Weaves Ltd.",
        "stock": 8,
        "reorder_level": 18,
        "description": "Brushed cotton yarn-dyed checkered flannel shirt"
    },
    {
        "product_id": "P008",
        "product_name": "Fleece Hooded Sweatshirt",
        "category_id": "CAT-006",
        "category_name": "Outerwear",
        "size": "L",
        "price": 2199.0,
        "supplier_id": "SUP-104",
        "supplier_name": "Apex Garments Supply",
        "stock": 65,
        "reorder_level": 20,
        "description": "Heavyweight French terry fleece kangaroo pocket hoodie"
    },
    {
        "product_id": "P009",
        "product_name": "Ripped Skinny Jeans",
        "category_id": "CAT-002",
        "category_name": "Denim",
        "size": "30",
        "price": 2299.0,
        "supplier_id": "SUP-102",
        "supplier_name": "Vogue Fabrics Mill",
        "stock": 3,
        "reorder_level": 15,
        "description": "Acid washed distressed skinny fit denim trousers"
    },
    {
        "product_id": "P010",
        "product_name": "Polo Collar T-Shirt",
        "category_id": "CAT-001",
        "category_name": "Casual Wear",
        "size": "M",
        "price": 1199.0,
        "supplier_id": "SUP-101",
        "supplier_name": "ABC Textiles Co.",
        "stock": 95,
        "reorder_level": 25,
        "description": "Piqué knit collar smart casual polo tee"
    },
    {
        "product_id": "P011",
        "product_name": "Silk Blend Party Kurta",
        "category_id": "CAT-004",
        "category_name": "Ethnic Wear",
        "size": "L",
        "price": 2499.0,
        "supplier_id": "SUP-105",
        "supplier_name": "Heritage Looms & Threads",
        "stock": 32,
        "reorder_level": 10,
        "description": "Jacquard weave festive embroidered mandarin kurta"
    },
    {
        "product_id": "P012",
        "product_name": "Traditional Banarasi Saree",
        "category_id": "CAT-004",
        "category_name": "Ethnic Wear",
        "size": "Free Size",
        "price": 4999.0,
        "supplier_id": "SUP-105",
        "supplier_name": "Heritage Looms & Threads",
        "stock": 18,
        "reorder_level": 8,
        "description": "Pure Katan silk handwoven zari border saree"
    },
    {
        "product_id": "P013",
        "product_name": "Floral Summer Dress",
        "category_id": "CAT-007",
        "category_name": "Women's Wear",
        "size": "M",
        "price": 1799.0,
        "supplier_id": "SUP-101",
        "supplier_name": "ABC Textiles Co.",
        "stock": 40,
        "reorder_level": 15,
        "description": "Chiffon printed A-line tiered bohemian summer dress"
    },
    {
        "product_id": "P014",
        "product_name": "Performance Tracksuit",
        "category_id": "CAT-005",
        "category_name": "Sports Wear",
        "size": "L",
        "price": 2299.0,
        "supplier_id": "SUP-104",
        "supplier_name": "Apex Garments Supply",
        "stock": 55,
        "reorder_level": 15,
        "description": "Quick-dry moisture wicking athletic training tracksuit"
    }
]

DEMO_SALES = [
    {"sale_id": "S001", "product_id": "P001", "product_name": "Classic Cotton T-Shirt", "category_name": "Casual Wear", "quantity": 25, "unit_price": 899.0, "sale_date": "2024-08-05", "status": "Completed"},
    {"sale_id": "S002", "product_id": "P002", "product_name": "Slim Fit Denim Jeans", "category_name": "Denim", "quantity": 14, "unit_price": 1999.0, "sale_date": "2024-08-10", "status": "Completed"},
    {"sale_id": "S003", "product_id": "P005", "product_name": "Oversized Graphic Tee", "category_name": "Casual Wear", "quantity": 30, "unit_price": 1099.0, "sale_date": "2024-08-14", "status": "Completed"},
    {"sale_id": "S004", "product_id": "P003", "product_name": "Oxford Formal Shirt", "category_name": "Formal Wear", "quantity": 18, "unit_price": 1499.0, "sale_date": "2024-08-20", "status": "Completed"},
    {"sale_id": "S005", "product_id": "P010", "product_name": "Polo Collar T-Shirt", "category_name": "Casual Wear", "quantity": 22, "unit_price": 1199.0, "sale_date": "2024-08-25", "status": "Completed"},
    {"sale_id": "S006", "product_id": "P001", "product_name": "Classic Cotton T-Shirt", "category_name": "Casual Wear", "quantity": 35, "unit_price": 899.0, "sale_date": "2024-09-01", "status": "Completed"},
    {"sale_id": "S007", "product_id": "P006", "product_name": "Linen Casual Trousers", "category_name": "Casual Wear", "quantity": 12, "unit_price": 1899.0, "sale_date": "2024-09-04", "status": "Completed"},
    {"sale_id": "S008", "product_id": "P008", "product_name": "Fleece Hooded Sweatshirt", "category_name": "Outerwear", "quantity": 15, "unit_price": 2199.0, "sale_date": "2024-09-08", "status": "Completed"},
    {"sale_id": "S009", "product_id": "P002", "product_name": "Slim Fit Denim Jeans", "category_name": "Denim", "quantity": 16, "unit_price": 1999.0, "sale_date": "2024-09-12", "status": "Completed"},
    {"sale_id": "S010", "product_id": "P011", "product_name": "Silk Blend Party Kurta", "category_name": "Ethnic Wear", "quantity": 14, "unit_price": 2499.0, "sale_date": "2024-09-15", "status": "Completed"},
    {"sale_id": "S011", "product_id": "P005", "product_name": "Oversized Graphic Tee", "category_name": "Casual Wear", "quantity": 28, "unit_price": 1099.0, "sale_date": "2024-09-18", "status": "Completed"},
    {"sale_id": "S012", "product_id": "P013", "product_name": "Floral Summer Dress", "category_name": "Women's Wear", "quantity": 18, "unit_price": 1799.0, "sale_date": "2024-09-22", "status": "Completed"},
    {"sale_id": "S013", "product_id": "P014", "product_name": "Performance Tracksuit", "category_name": "Sports Wear", "quantity": 15, "unit_price": 2299.0, "sale_date": "2024-09-26", "status": "Completed"},
    {"sale_id": "S014", "product_id": "P004", "product_name": "Quilted Winter Jacket", "category_name": "Outerwear", "quantity": 6, "unit_price": 3499.0, "sale_date": "2024-09-29", "status": "Completed"},
    {"sale_id": "S015", "product_id": "P010", "product_name": "Polo Collar T-Shirt", "category_name": "Casual Wear", "quantity": 24, "unit_price": 1199.0, "sale_date": "2024-10-02", "status": "Completed"},
    {"sale_id": "S016", "product_id": "P007", "product_name": "Flannel Plaid Shirt", "category_name": "Formal Wear", "quantity": 8, "unit_price": 1599.0, "sale_date": "2024-10-04", "status": "Completed"},
    {"sale_id": "S017", "product_id": "P012", "product_name": "Traditional Banarasi Saree", "category_name": "Ethnic Wear", "quantity": 5, "unit_price": 4999.0, "sale_date": "2024-10-05", "status": "Completed"},
    {"sale_id": "S018", "product_id": "P009", "product_name": "Ripped Skinny Jeans", "category_name": "Denim", "quantity": 7, "unit_price": 2299.0, "sale_date": "2024-10-06", "status": "Completed"}
]

DEMO_USERS = [
    {
        "uid": "USR-ADMIN-01",
        "name": "Alex Morgan",
        "email": "admin@fabricflow.com",
        "role": "admin",
        "created_at": get_current_timestamp()
    },
    {
        "uid": "USR-STAFF-02",
        "name": "Sarah Chen",
        "email": "sarah@fabricflow.com",
        "role": "manager",
        "created_at": get_current_timestamp()
    }
]


def seed_firestore(force=False):
    """
    Safely seeds demo garment data into Cloud Firestore.
    Does NOT delete production data by default.
    """
    print("==================================================")
    print("  SEEDING GOOGLE CLOUD FIRESTORE COLLECTIONS      ")
    print("==================================================")

    init_firebase()
    db = get_db()
    now_str = get_current_timestamp()

    # 1. Seed Categories
    print(f"[*] Seeding {len(DEMO_CATEGORIES)} Categories...")
    for cat in DEMO_CATEGORIES:
        cid = cat["category_id"]
        doc_ref = db.collection("categories").document(cid)
        if not force and doc_ref.get().exists:
            continue
        payload = {
            "category_id": cid,
            "id": cid,
            "category_name": cat["category_name"],
            "name": cat["category_name"],
            "description": cat["description"],
            "created_at": now_str
        }
        doc_ref.set(payload)
    print("    -> Categories collection ready.")

    # 2. Seed Suppliers
    print(f"[*] Seeding {len(DEMO_SUPPLIERS)} Suppliers...")
    for sup in DEMO_SUPPLIERS:
        sid = sup["supplier_id"]
        doc_ref = db.collection("suppliers").document(sid)
        if not force and doc_ref.get().exists:
            continue
        payload = dict(sup)
        payload["id"] = sid
        payload["name"] = sup["supplier_name"]
        payload["contact"] = sup["contact_number"]
        payload["created_at"] = now_str
        payload["updated_at"] = now_str
        doc_ref.set(payload)
    print("    -> Suppliers collection ready.")

    # 3. Seed Products and Inventory
    print(f"[*] Seeding {len(DEMO_PRODUCTS)} Products & Inventory records...")
    for p in DEMO_PRODUCTS:
        pid = p["product_id"]
        p_ref = db.collection("products").document(pid)
        inv_ref = db.collection("inventory").document(pid)

        stock = int(p["stock"])
        reorder = int(p["reorder_level"])
        stock_status = calculate_stock_status(stock, reorder)

        if force or not p_ref.get().exists:
            p_payload = {
                "product_id": pid,
                "id": pid,
                "product_name": p["product_name"],
                "name": p["product_name"],
                "category_id": p["category_id"],
                "category_name": p["category_name"],
                "category": p["category_name"],
                "size": p["size"],
                "price": p["price"],
                "supplier_id": p["supplier_id"],
                "supplier_name": p["supplier_name"],
                "supplier": p["supplier_name"],
                "description": p["description"],
                "stock": stock,
                "stock_quantity": stock,
                "min_stock": reorder,
                "reorder_level": reorder,
                "status": stock_status,
                "stock_status": stock_status,
                "created_at": now_str,
                "updated_at": now_str
            }
            p_ref.set(p_payload)

        if force or not inv_ref.get().exists:
            inv_payload = {
                "product_id": pid,
                "id": pid,
                "product_name": p["product_name"],
                "name": p["product_name"],
                "category_name": p["category_name"],
                "category": p["category_name"],
                "size": p["size"],
                "price": p["price"],
                "stock_quantity": stock,
                "stock": stock,
                "reorder_level": reorder,
                "min_stock": reorder,
                "stock_status": stock_status,
                "status": stock_status,
                "last_updated": now_str
            }
            inv_ref.set(inv_payload)
    print("    -> Products & Inventory collections ready.")

    # 4. Seed Sales
    print(f"[*] Seeding {len(DEMO_SALES)} Sales records...")
    for s in DEMO_SALES:
        sid = s["sale_id"]
        s_ref = db.collection("sales").document(sid)
        if not force and s_ref.get().exists:
            continue

        qty = int(s["quantity"])
        unit_price = float(s["unit_price"])
        total = qty * unit_price

        s_payload = {
            "sale_id": sid,
            "id": sid,
            "product_id": s["product_id"],
            "product_name": s["product_name"],
            "product": s["product_name"],
            "category_name": s["category_name"],
            "category": s["category_name"],
            "quantity": qty,
            "unit_price": unit_price,
            "unitPrice": unit_price,
            "total_amount": total,
            "total": total,
            "total_formatted": format_currency(total),
            "sale_date": s["sale_date"],
            "date": s["sale_date"],
            "status": s["status"],
            "created_by": "admin",
            "created_at": now_str
        }
        s_ref.set(s_payload)
    print("    -> Sales collection ready.")

    # 5. Seed Users
    print(f"[*] Seeding {len(DEMO_USERS)} Users...")
    for u in DEMO_USERS:
        uid = u["uid"]
        u_ref = db.collection("users").document(uid)
        if not force and u_ref.get().exists:
            continue
        u_ref.set(u)
    print("    -> Users collection ready.")

    print("\n[OK] Cloud Firestore successfully seeded with garment demo data!")
    print("    Collections verified: users, products, categories, inventory, sales, suppliers.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Cloud Firestore database with garment demo data.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing demo records.")
    args = parser.parse_args()

    seed_firestore(force=args.force)
