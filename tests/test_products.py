import unittest
from backend.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    calculate_stock_status
)

class TestProductService(unittest.TestCase):
    def test_get_all_products(self):
        products = get_all_products()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)

    def test_stock_status_calculation(self):
        self.assertEqual(calculate_stock_status(0, 15), "Critical")
        self.assertEqual(calculate_stock_status(-2, 15), "Critical")
        self.assertEqual(calculate_stock_status(12, 15), "Low")
        self.assertEqual(calculate_stock_status(50, 15), "Normal")

    def test_product_crud_flow(self):
        new_prod_data = {
            "name": "Test Cotton Shirt",
            "category": "Shirts",
            "size": "L",
            "price": 29.99,
            "cost_price": 14.50,
            "stock": 50,
            "min_stock": 10,
            "supplier": "Test Supplier"
        }
        created = create_product(new_prod_data)
        self.assertIsNotNone(created)
        prod_id = created.get("id")
        self.assertIsNotNone(prod_id)

        # Fetch
        prod = get_product_by_id(prod_id)
        self.assertIsNotNone(prod)
        self.assertEqual(prod.get("name"), "Test Cotton Shirt")

        # Update
        updated = update_product(prod_id, {"price": 34.99})
        self.assertIsNotNone(updated)
        self.assertEqual(updated.get("price"), 34.99)

        # Delete
        success = delete_product(prod_id)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
