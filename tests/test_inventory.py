import unittest
from backend.services.inventory_service import get_inventory_summary, get_inventory_list, adjust_stock

class TestInventoryService(unittest.TestCase):
    def test_get_inventory_summary(self):
        summary = get_inventory_summary()
        self.assertIn("total_products_count", summary)
        self.assertIn("total_stock_units", summary)
        self.assertIn("low_stock_count", summary)

    def test_get_inventory_list(self):
        inv_list = get_inventory_list()
        self.assertIsInstance(inv_list, list)
        self.assertGreater(len(inv_list), 0)

    def test_adjust_stock(self):
        # Test add stock
        product, err = adjust_stock("P001", "add", 10, "Stock replenishment")
        self.assertIsNone(err)
        self.assertIsNotNone(product)

if __name__ == "__main__":
    unittest.main()
