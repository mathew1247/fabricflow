import unittest
from backend.services.sales_service import get_all_sales, get_sale_by_id, record_sale, delete_sale
from backend.services.inventory_service import get_inventory_by_id

class TestSalesService(unittest.TestCase):
    def test_get_all_sales(self):
        sales = get_all_sales()
        self.assertIsInstance(sales, list)
        self.assertGreater(len(sales), 0)

    def test_record_sale_and_inventory_reduction(self):
        # 1. Read current inventory for P001
        inv_before = get_inventory_by_id("P001")
        self.assertIsNotNone(inv_before)
        stock_before = int(inv_before.get("stock_quantity", 0))

        # 2. Record sale of 2 units
        sale_data = {
            "product_id": "P001",
            "product": "Classic Cotton T-Shirt",
            "category": "Casual Wear",
            "quantity": 2,
            "unit_price": 899.0,
            "status": "Completed"
        }
        created, err = record_sale(sale_data)
        self.assertIsNone(err)
        self.assertIsNotNone(created)
        self.assertIn("id", created)
        sale_id = created["id"]

        # 3. Verify sale retrieval
        sale = get_sale_by_id(sale_id)
        self.assertIsNotNone(sale)
        self.assertEqual(sale.get("quantity"), 2)

        # 4. Verify inventory reduction in Firestore
        inv_after = get_inventory_by_id("P001")
        stock_after = int(inv_after.get("stock_quantity", 0))
        self.assertEqual(stock_after, stock_before - 2)

        # 5. Clean up test sale
        delete_sale(sale_id)

if __name__ == "__main__":
    unittest.main()
