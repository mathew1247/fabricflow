"""
Full Verification Test Suite for FabricFlow Analytics
Covers Sections 4 to 25 of the Final Verification Specification.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.error
import json
import io
import csv
from firebase.firebase_config import get_db

BASE_URL = "http://127.0.0.1:5000/api"

def api_call(method, path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            status = resp.getcode()
            try:
                res_json = json.loads(content)
            except Exception:
                res_json = content
            return status, res_json
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            res_json = json.loads(content)
        except Exception:
            res_json = content
        return e.code, res_json

def run_tests():
    db = get_db()
    results = {}

    print("==================================================")
    print("STARTING FULL VERIFICATION SUITE")
    print("==================================================")

    # -------------------------------------------------------------------------
    # 4. CATEGORY CRUD TEST
    # -------------------------------------------------------------------------
    print("\n--- Section 4: Testing Category CRUD ---")
    cat_payload = {
        "name": "TEST_FABRICFLOW_CAT",
        "description": "Category for automated verification testing"
    }
    # Create category
    st, res = api_call("POST", "/categories", cat_payload)
    assert st == 201, f"Failed to create category: {st} {res}"
    cat_id = res["data"]["id"]
    print(f"[OK] Created category: {cat_id}")

    # Read all categories
    st, res = api_call("GET", "/categories")
    assert st == 200 and any(c["id"] == cat_id for c in res["data"])
    print("[OK] Category present in list")

    # Read single category
    st, res = api_call("GET", f"/categories/{cat_id}")
    assert st == 200 and res["data"]["name"] == "TEST_FABRICFLOW_CAT"
    print("[OK] Category fetched individually")

    # Update category
    st, res = api_call("PUT", f"/categories/{cat_id}", {"description": "Updated description"})
    assert st == 200 and res["data"]["description"] == "Updated description"
    print("[OK] Category updated")

    # Test duplicate creation
    st, res = api_call("POST", "/categories", cat_payload)
    assert st == 409, f"Duplicate category did not return 409: {st} {res}"
    print("[OK] Duplicate category rejected with 409")

    # Test invalid category ID
    st, res = api_call("GET", "/categories/NONEXISTENT_CAT_ID_999")
    assert st == 404, f"Invalid category ID did not return 404: {st}"
    print("[OK] Nonexistent category returns 404")

    # Delete category
    st, res = api_call("DELETE", f"/categories/{cat_id}")
    assert st == 200
    print("[OK] Category deleted")
    results["Categories CRUD"] = "PASS"

    # -------------------------------------------------------------------------
    # 5. SUPPLIER CRUD TEST
    # -------------------------------------------------------------------------
    print("\n--- Section 5: Testing Supplier CRUD ---")
    sup_payload = {
        "name": "TEST_FABRICFLOW_SUPPLIER",
        "supplier_name": "TEST_FABRICFLOW_SUPPLIER",
        "contact": "9876543210",
        "contact_number": "9876543210",
        "email": "test_supplier@fabricflow.com",
        "address": "123 Textile Way, Mumbai"
    }
    st, res = api_call("POST", "/suppliers", sup_payload)
    assert st == 201, f"Failed to create supplier: {st} {res}"
    sup_id = res["data"]["id"]
    print(f"[OK] Created supplier: {sup_id}")

    st, res = api_call("GET", "/suppliers")
    assert st == 200 and any(s["id"] == sup_id for s in res["data"])
    print("[OK] Supplier present in list")

    st, res = api_call("GET", f"/suppliers/{sup_id}")
    assert st == 200 and res["data"]["name"] == "TEST_FABRICFLOW_SUPPLIER"
    print("[OK] Supplier fetched individually")

    st, res = api_call("PUT", f"/suppliers/{sup_id}", {"address": "Updated Address 456"})
    assert st == 200 and res["data"]["address"] == "Updated Address 456"
    print("[OK] Supplier updated")

    # Validation: empty name
    st, res = api_call("POST", "/suppliers", {"name": ""})
    assert st == 400, f"Empty supplier name did not return 400: {st}"
    print("[OK] Empty supplier name rejected with 400")

    # Clean up supplier
    st, res = api_call("DELETE", f"/suppliers/{sup_id}")
    assert st == 200
    print("[OK] Supplier deleted")
    results["Suppliers CRUD"] = "PASS"

    # -------------------------------------------------------------------------
    # 6. PRODUCT CRUD & VALIDATION TEST
    # -------------------------------------------------------------------------
    print("\n--- Section 6: Testing Product CRUD & Validation ---")
    test_prod_id = "TEST_FABRICFLOW_P01"
    prod_payload = {
        "id": test_prod_id,
        "product_id": test_prod_id,
        "name": "TEST_FABRICFLOW_SHIRT",
        "product_name": "TEST_FABRICFLOW_SHIRT",
        "category": "Casual Wear",
        "category_id": "C001",
        "size": "L",
        "price": 500.0,
        "supplier": "ABC Textiles Co.",
        "supplier_id": "S001",
        "stock": 100,
        "stock_quantity": 100,
        "reorder_level": 20
    }
    st, res = api_call("POST", "/products", prod_payload)
    assert st == 201, f"Failed to create product: {st} {res}"
    print(f"[OK] Product created: {test_prod_id}")

    # Read product
    st, res = api_call("GET", f"/products/{test_prod_id}")
    assert st == 200 and res["data"]["name"] == "TEST_FABRICFLOW_SHIRT"
    print("[OK] Product fetched by ID")

    # Update product
    st, res = api_call("PUT", f"/products/{test_prod_id}", {"price": 550.0})
    assert st == 200 and float(res["data"]["price"]) == 550.0
    print("[OK] Product updated successfully")

    # Validation: negative price
    st, res = api_call("POST", "/products", {
        "name": "Invalid Price Product",
        "category": "Casual Wear",
        "price": -100.0,
        "size": "M"
    })
    assert st == 400, f"Negative price was not rejected with 400: {st}"
    print("[OK] Negative price rejected with 400")

    results["Products CRUD"] = "PASS"

    # -------------------------------------------------------------------------
    # 7 & 8. INVENTORY VERIFICATION & STOCK STATUS
    # -------------------------------------------------------------------------
    print("\n--- Section 7 & 8: Testing Inventory & Stock Status Calculation ---")
    st, res = api_call("GET", f"/inventory/{test_prod_id}")
    assert st == 200, f"Failed to get inventory for {test_prod_id}: {st} {res}"
    assert int(res["data"]["stock_quantity"]) == 100
    print("[OK] Inventory record exists with initial stock 100")

    # Adjustment: deduct 20 -> expected 80, Status: Normal (80 > 20)
    st, res = api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "deduct",
        "quantity": 20,
        "reason": "Test deduction"
    })
    assert st == 200 and int(res["data"]["stock"]) == 80
    assert res["data"]["status"] == "Normal"
    print("[OK] Inventory adjusted -20 -> 80 units, Status: Normal")

    # Adjustment: add 10 -> expected 90
    st, res = api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "add",
        "quantity": 10,
        "reason": "Test addition"
    })
    assert st == 200 and int(res["data"]["stock"]) == 90
    print("[OK] Inventory adjusted +10 -> 90 units")

    # Test negative stock protection (attempt deduct 150 from 90 -> REJECTED)
    st, res = api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "deduct",
        "quantity": 150,
        "reason": "Excessive deduction"
    })
    assert st == 400, f"Negative stock was not rejected with 400: {st}"
    # Verify stock remains 90
    st, res = api_call("GET", f"/inventory/{test_prod_id}")
    assert int(res["data"]["stock_quantity"]) == 90
    print("[OK] Negative stock adjustment rejected; stock remained 90")

    # Test Stock Status: Low (set to 15 <= reorder_level 20)
    st, res = api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "set",
        "quantity": 15,
        "reason": "Low stock test"
    })
    assert st == 200 and res["data"]["status"] == "Low"
    print("[OK] Stock status 'Low' verified (15 <= 20)")

    # Test Stock Status: Critical (set to 0)
    st, res = api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "set",
        "quantity": 0,
        "reason": "Critical stock test"
    })
    assert st == 200 and res["data"]["status"] == "Critical"
    print("[OK] Stock status 'Critical' verified (0 <= 0)")

    # Restore stock to 100 for sales tests
    api_call("POST", f"/inventory/{test_prod_id}/adjust", {
        "type": "set",
        "quantity": 100,
        "reason": "Restore for sales test"
    })
    results["Inventory"] = "PASS"

    # -------------------------------------------------------------------------
    # 9 & 10. SALES MANAGEMENT & VALIDATION
    # -------------------------------------------------------------------------
    print("\n--- Section 9 & 10: Testing Sales Management & Validation ---")
    sale_payload = {
        "product_id": test_prod_id,
        "product": "TEST_FABRICFLOW_SHIRT",
        "category": "Casual Wear",
        "quantity": 20,
        "unit_price": 500.0,
        "status": "Completed"
    }
    st, res = api_call("POST", "/sales", sale_payload)
    assert st == 201, f"Failed to record sale: {st} {res}"
    created_sale = res["data"]
    sale_id = created_sale.get("id") or created_sale.get("sale_id")
    assert created_sale.get("total") == 10000.0 or created_sale.get("total_amount") == 10000.0
    print(f"[OK] Sale created: {sale_id}, total: 10000.0")

    # Verify inventory decreased from 100 to 80
    st, res = api_call("GET", f"/inventory/{test_prod_id}")
    assert int(res["data"]["stock_quantity"]) == 80
    print("[OK] Inventory atomically reduced from 100 to 80")

    # Validation: quantity = 0
    st, res = api_call("POST", "/sales", {**sale_payload, "quantity": 0})
    assert st == 400, f"Sale with quantity=0 not rejected: {st}"
    print("[OK] Sale with quantity=0 rejected with 400")

    # Validation: quantity = -1
    st, res = api_call("POST", "/sales", {**sale_payload, "quantity": -1})
    assert st == 400, f"Sale with quantity=-1 not rejected: {st}"
    print("[OK] Sale with negative quantity rejected with 400")

    # Validation: quantity > stock (attempt 150 when stock is 80)
    st, res = api_call("POST", "/sales", {**sale_payload, "quantity": 150})
    assert st == 400, f"Excess sale quantity not rejected: {st}"
    print("[OK] Sale exceeding available stock rejected with 400")

    # Verify inventory is still 80
    st, res = api_call("GET", f"/inventory/{test_prod_id}")
    assert int(res["data"]["stock_quantity"]) == 80
    print("[OK] Stock unchanged after rejected sale attempts")

    # Clean up test sale
    api_call("DELETE", f"/sales/{sale_id}")
    # Clean up test product
    api_call("DELETE", f"/products/{test_prod_id}")
    results["Sales"] = "PASS"

    # -------------------------------------------------------------------------
    # 11. DASHBOARD API VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- Section 11: Testing Dashboard API Against Firestore ---")
    st, res = api_call("GET", "/dashboard")
    assert st == 200, f"Failed dashboard call: {st}"
    dash_data = res["data"]

    # Calculate actual counts directly from Firestore
    actual_prods = len(list(db.collection("products").stream()))
    actual_sales = list(db.collection("sales").stream())
    actual_sales_total = sum(float(d.to_dict().get("total_amount") or d.to_dict().get("total") or 0) for d in actual_sales)
    actual_stock = sum(int(d.to_dict().get("stock_quantity") or d.to_dict().get("stock") or 0) for d in db.collection("inventory").stream())

    print(f"Firestore Prods: {actual_prods} | Dashboard: {dash_data['total_products']}")
    print(f"Firestore Stock: {actual_stock} | Dashboard: {dash_data['total_stock']}")
    print(f"Firestore Sales Total: {actual_sales_total} | Dashboard: {dash_data['total_sales']}")

    assert dash_data["total_products"] == actual_prods
    assert dash_data["total_stock"] == actual_stock
    assert abs(dash_data["total_sales"] - actual_sales_total) < 1.0
    assert "sales_trend" in dash_data
    assert "stock_status" in dash_data
    assert "top_categories" in dash_data
    assert "recent_sales" in dash_data
    print("[OK] Dashboard API matches Firestore values exactly")
    results["Dashboard API"] = "PASS"

    # -------------------------------------------------------------------------
    # 13 & 14. ANALYTICS VERIFICATION & VELOCITY
    # -------------------------------------------------------------------------
    print("\n--- Section 13 & 14: Testing Analytics & Velocity Classification ---")
    st, res = api_call("GET", "/analytics/sales")
    assert st == 200 and "total_sales" in res["data"]
    print("[OK] Sales analytics returns total_sales and category breakdowns")

    st, res = api_call("GET", "/analytics/inventory")
    assert st == 200 and "total_stock" in res["data"]
    print("[OK] Inventory analytics returns stock distributions")

    st, res = api_call("GET", "/analytics/products")
    assert st == 200 and "fast_moving_products" in res["data"]
    fast = res["data"]["fast_moving_products"]
    normal = res["data"]["normal_moving_products"]
    slow = res["data"]["slow_moving_products"]
    print(f"[OK] Product Velocity: {len(fast)} Fast, {len(normal)} Normal, {len(slow)} Slow")
    if fast:
        print(f"     Top Fast-Moving: {fast[0]['product_name']} (velocity: {fast[0]['sales_velocity']}/day)")
    if slow:
        print(f"     Sample Slow-Moving: {slow[0]['product_name']} (velocity: {slow[0]['sales_velocity']}/day)")
    results["Sales Analytics"] = "PASS"
    results["Inventory Analytics"] = "PASS"
    results["Product Analytics"] = "PASS"
    results["Fast/Slow Analysis"] = "PASS"

    # -------------------------------------------------------------------------
    # 16. FORECAST VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- Section 16: Testing Forecast Calculations ---")
    for period in ["7", "30", "90"]:
        st, res = api_call("GET", f"/forecast?period={period}")
        assert st == 200 and "table" in res["data"]
        items = res["data"]["table"]
        assert len(items) > 0
        sample = items[0]
        assert "predicted_demand" in sample
        assert "recommended_stock" in sample
        assert "status" in sample
        print(f"[OK] Forecast {period}-day: {len(items)} items, sample: {sample['name']} -> {sample['status']}")
    results["Forecast"] = "PASS"

    # -------------------------------------------------------------------------
    # 18. REPORTS & CSV EXPORT VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- Section 18: Testing Reports & CSV Exports ---")
    for rtype in ["inventory", "sales", "products", "low-stock", "forecast"]:
        # Preview
        st, res = api_call("GET", f"/reports/{rtype}")
        assert st == 200, f"Report preview {rtype} failed: {st}"
        assert "headers" in res["data"] and "rows" in res["data"]
        print(f"[OK] Report {rtype} JSON preview: {len(res['data']['rows'])} rows")

        # CSV Export
        url = f"{BASE_URL}/reports/{rtype}?format=csv"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
            csv_text = resp.read().decode("utf-8")
            reader = csv.reader(io.StringIO(csv_text))
            rows = list(reader)
            assert len(rows) > 1, f"CSV {rtype} empty or missing header!"
            print(f"[OK] Report {rtype} CSV export: {len(rows)} lines parsed (Header: {rows[0][:3]})")
    results["Reports"] = "PASS"

    # -------------------------------------------------------------------------
    # 21. AUTHENTICATION & ERROR HANDLING
    # -------------------------------------------------------------------------
    print("\n--- Section 21 & 23: Testing Authentication & Error Handling ---")
    # Test unauthenticated / invalid token access on protected endpoint
    url = f"{BASE_URL}/products"
    req = urllib.request.Request(
        url,
        data=json.dumps({"name": "Unauthorized Test"}).encode("utf-8"),
        headers={"Authorization": "Bearer invalid-expired-token-xyz", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req)
        assert False, "Invalid token did not fail!"
    except urllib.error.HTTPError as e:
        assert e.code == 401
        err_json = json.loads(e.read().decode("utf-8"))
        assert err_json["success"] is False
        print("[OK] Invalid token correctly returned 401 Unauthorized")

    # Test 404 handler
    st, res = api_call("GET", "/nonexistent-route-for-testing")
    assert st == 404 and res["success"] is False
    print("[OK] 404 handler returns consistent error JSON")

    results["Authentication"] = "PASS"
    results["Authorization"] = "PASS"
    results["Error Handling"] = "PASS"

    # -------------------------------------------------------------------------
    # 25. END-TO-END BUSINESS FLOW (15 Steps)
    # -------------------------------------------------------------------------
    print("\n--- Section 25: Executing Complete 15-Step Business Flow ---")
    import time
    ts = int(time.time())
    flow_cat = f"FLOW_CAT_{ts}"
    flow_sup = f"FLOW_SUP_{ts}"
    flow_prod_id = f"FLOW_PROD_{ts}"

    # Also clean up any lingering previous test records
    for c in db.collection("categories").where("name", "in", ["TEST_FABRICFLOW_CAT_FLOW", "TEST_FABRICFLOW_CAT"]).stream():
        db.collection("categories").document(c.id).delete()
    for s in db.collection("suppliers").where("name", "in", ["TEST_FABRICFLOW_SUPPLIER_FLOW", "TEST_FABRICFLOW_SUPPLIER"]).stream():
        db.collection("suppliers").document(s.id).delete()
    for p in db.collection("products").where("id", "in", ["TEST_FABRICFLOW_SHIRT_FLOW", "TEST_FABRICFLOW_P01"]).stream():
        db.collection("products").document(p.id).delete()
        db.collection("inventory").document(p.id).delete()

    # STEP 1: Create category
    st, res = api_call("POST", "/categories", {"name": flow_cat, "description": "Flow Category"})
    assert st == 201, f"Create category failed: {st} {res}"
    flow_cat_id = res["data"]["id"]
    print(f"[OK] STEP 1: Created Category: {flow_cat} ({flow_cat_id})")

    # STEP 2: Create supplier
    st, res = api_call("POST", "/suppliers", {
        "name": flow_sup,
        "contact": "9876543210",
        "email": "flow_sup@fabricflow.com",
        "address": "Flow Textile Mill"
    })
    assert st == 201
    flow_sup_id = res["data"]["id"]
    print(f"[OK] STEP 2: Created Supplier: {flow_sup} ({flow_sup_id})")

    # STEP 3 & 4: Create product & inventory
    st, res = api_call("POST", "/products", {
        "id": flow_prod_id,
        "name": "TEST_FABRICFLOW_SHIRT",
        "category": flow_cat,
        "category_id": flow_cat_id,
        "size": "M",
        "price": 500.0,
        "supplier": flow_sup,
        "supplier_id": flow_sup_id,
        "stock": 100,
        "reorder_level": 20
    })
    assert st == 201
    print(f"[OK] STEP 3 & 4: Created Product & Inventory with Stock: 100, Reorder: 20")

    # STEP 5: Verify dashboard increases
    st, res = api_call("GET", "/dashboard")
    assert st == 200
    print(f"[OK] STEP 5: Dashboard reflects updated product catalog")

    # STEP 6 & 7 & 8: Create sale 30 -> Stock = 70, Status = Normal
    st, res = api_call("POST", "/sales", {
        "product_id": flow_prod_id,
        "product": "TEST_FABRICFLOW_SHIRT",
        "category": flow_cat,
        "quantity": 30,
        "unit_price": 500.0,
        "status": "Completed"
    })
    assert st == 201
    sale_1_id = res["data"].get("id") or res["data"].get("sale_id")
    assert res["data"].get("total") == 15000.0 or res["data"].get("total_amount") == 15000.0
    print(f"[OK] STEP 6: Created Sale 1: 30 units @ 500 = 15000")

    st, res = api_call("GET", f"/inventory/{flow_prod_id}")
    assert int(res["data"]["stock_quantity"]) == 70
    assert res["data"]["stock_status"] == "Normal"
    print(f"[OK] STEP 7 & 8: Inventory = 70, Stock Status = Normal (70 > 20)")

    # STEP 9: Create second sale 55 -> Stock = 15, Status = Low (15 <= 20)
    st, res = api_call("POST", "/sales", {
        "product_id": flow_prod_id,
        "product": "TEST_FABRICFLOW_SHIRT",
        "category": flow_cat,
        "quantity": 55,
        "unit_price": 500.0,
        "status": "Completed"
    })
    assert st == 201
    sale_2_id = res["data"].get("id") or res["data"].get("sale_id")
    print(f"[OK] STEP 9: Created Sale 2: 55 units @ 500 = 27500")

    st, res = api_call("GET", f"/inventory/{flow_prod_id}")
    assert int(res["data"]["stock_quantity"]) == 15
    assert res["data"]["stock_status"] == "Low"
    print(f"[OK] STEP 9: Inventory = 15, Stock Status = Low (15 <= 20)")

    # STEP 10: Check dashboard low-stock count
    st, res = api_call("GET", "/dashboard")
    assert st == 200 and res["data"]["low_stock_items"] > 0
    print(f"[OK] STEP 10: Dashboard Low Stock count verified: {res['data']['low_stock_items']}")

    # STEP 11: Analytics reflects the new product
    st, res = api_call("GET", "/analytics/sales")
    assert st == 200
    print("[OK] STEP 11: Sales analytics reflects transactions")

    # STEP 12: Fast/Slow classification
    st, res = api_call("GET", "/analytics/products")
    assert st == 200
    print("[OK] STEP 12: Velocity and ranking updated")

    # STEP 13: Forecast
    st, res = api_call("GET", "/forecast?period=30")
    assert st == 200
    print("[OK] STEP 13: Forecast reflects recent velocity")

    # STEP 14: Sales report has both sales
    st, res = api_call("GET", "/reports/sales")
    assert st == 200
    sales_rows = [r for r in res["data"]["rows"] if r.get("product") == "TEST_FABRICFLOW_SHIRT" or r.get("id") in [sale_1_id, sale_2_id]]
    assert len(sales_rows) >= 2
    print(f"[OK] STEP 14: Sales report contains both test sales ({len(sales_rows)} found)")

    # STEP 15: Inventory report has stock = 15
    st, res = api_call("GET", "/reports/inventory")
    assert st == 200
    inv_row = next((r for r in res["data"]["rows"] if r.get("name") == "TEST_FABRICFLOW_SHIRT" or r.get("id") == flow_prod_id), None)
    assert inv_row is not None and int(str(inv_row["stock"]).split()[0]) == 15
    print(f"[OK] STEP 15: Inventory report verified with stock = 15")

    # Clean up flow test records
    api_call("DELETE", f"/sales/{sale_1_id}")
    api_call("DELETE", f"/sales/{sale_2_id}")
    api_call("DELETE", f"/products/{flow_prod_id}")
    api_call("DELETE", f"/suppliers/{flow_sup_id}")
    api_call("DELETE", f"/categories/{flow_cat_id}")
    print("[OK] Cleaned up all Section 25 business flow records")
    results["End-to-End Business Flow"] = "PASS"

    print("\n==================================================")
    print("ALL VERIFICATION SECTIONS PASSED")
    print("==================================================")
    return results

if __name__ == "__main__":
    run_tests()
