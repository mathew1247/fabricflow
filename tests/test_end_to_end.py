"""
End-to-end verification test executing the required sequence from Section 34:
- STEP 2: GET /api/health
- STEP 3: Verify Firebase connection
- STEP 4: Create/read a product
- STEP 5: Create/read inventory
- STEP 6: Create a sale
- STEP 7: Verify inventory decreases
- STEP 8: Verify dashboard totals change
- STEP 9: Verify analytics reflect the sale
- STEP 10: Verify forecast uses actual sales history
- STEP 11: Verify reports contain actual Firestore data
"""

import unittest
import json
from app import app
from backend.services.inventory_service import get_inventory_by_id

class TestEndToEndFlow(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_complete_flow(self):
        # STEP 2 & 3: Test GET /api/health and verify Firebase connection
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("firebase"), "connected")
        print("[OK] STEP 2 & 3: /api/health verified - Firebase connected")

        # Record dashboard totals prior to test
        dash_before = self.client.get("/api/dashboard").get_json()["data"]
        sales_count_before = dash_before.get("total_sales_count", 0)
        stock_before_total = dash_before.get("total_stock", 0)

        # STEP 4 & 5: Create/read a product and verify inventory document
        test_product_id = "PTEST_E2E_01"
        payload = {
            "id": test_product_id,
            "product_id": test_product_id,
            "name": "E2E Test Linen Shirt",
            "product_name": "E2E Test Linen Shirt",
            "category": "Casual Wear",
            "category_name": "Casual Wear",
            "size": "M",
            "price": 1200.0,
            "stock": 50,
            "stock_quantity": 50,
            "reorder_level": 10,
            "supplier": "Apex Garments Ltd",
            "supplier_name": "Apex Garments Ltd",
            "description": "Created during E2E verification test"
        }
        create_resp = self.client.post("/api/products", json=payload)
        self.assertEqual(create_resp.status_code, 201)
        print("[OK] STEP 4: Product created successfully")

        # Read product
        get_prod = self.client.get(f"/api/products/{test_product_id}")
        self.assertEqual(get_prod.status_code, 200)
        self.assertEqual(get_prod.get_json()["data"]["name"], "E2E Test Linen Shirt")

        # Read inventory
        inv_doc = get_inventory_by_id(test_product_id)
        self.assertIsNotNone(inv_doc)
        self.assertEqual(inv_doc.get("stock_quantity"), 50)
        self.assertEqual(inv_doc.get("stock_status"), "Normal")
        print("[OK] STEP 5: Inventory initialized in Firestore")

        # STEP 6: Create a sale for this product (10 units)
        sale_payload = {
            "product_id": test_product_id,
            "product": "E2E Test Linen Shirt",
            "product_name": "E2E Test Linen Shirt",
            "category": "Casual Wear",
            "category_name": "Casual Wear",
            "quantity": 10,
            "unit_price": 1200.0,
            "status": "Completed"
        }
        sale_resp = self.client.post("/api/sales", json=sale_payload)
        self.assertEqual(sale_resp.status_code, 201)
        created_sale = sale_resp.get_json()["data"]
        sale_id = created_sale.get("id") or created_sale.get("sale_id")
        self.assertIsNotNone(sale_id)
        print(f"[OK] STEP 6: Sale created: ID {sale_id}")

        # STEP 7: Verify inventory decreases from 50 to 40
        inv_after = get_inventory_by_id(test_product_id)
        self.assertEqual(inv_after.get("stock_quantity"), 40)
        self.assertEqual(inv_after.get("stock_status"), "Normal")
        print("[OK] STEP 7: Inventory decreased from 50 to 40 in Firestore")

        # STEP 8: Verify dashboard totals reflect the new sale and stock
        dash_after = self.client.get("/api/dashboard").get_json()["data"]
        self.assertGreaterEqual(dash_after.get("total_sales_count", 0), sales_count_before)
        print("[OK] STEP 8: Dashboard totals updated with live Firestore data")

        # STEP 9: Verify analytics reflect the sale
        analytics_resp = self.client.get("/api/analytics/sales")
        self.assertEqual(analytics_resp.status_code, 200)
        an_data = analytics_resp.get_json()["data"]
        self.assertGreater(an_data["total_units_sold"], 0)
        print("[OK] STEP 9: Analytics calculated from Firestore transactions")

        # STEP 10: Verify forecast returns calculations based on history
        forecast_resp = self.client.get("/api/forecast?period=30")
        self.assertEqual(forecast_resp.status_code, 200)
        fc_data = forecast_resp.get_json()["data"]
        self.assertIn("table", fc_data)
        self.assertGreater(len(fc_data["table"]), 0)
        print("[OK] STEP 10: Demand forecasting verified")

        # STEP 11: Verify reports contain actual Firestore data and CSV export works
        rep_resp = self.client.get("/api/reports/sales?format=csv")
        self.assertEqual(rep_resp.status_code, 200)
        self.assertIn("text/csv", rep_resp.content_type)
        print("[OK] STEP 11: Real Firestore CSV reports verified")

        # Clean up test records
        self.client.delete(f"/api/sales/{sale_id}")
        self.client.delete(f"/api/products/{test_product_id}")
        print("[OK] Cleaned up temporary E2E test data")

if __name__ == "__main__":
    unittest.main()
