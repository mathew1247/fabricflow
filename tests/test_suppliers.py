import unittest
from backend.services.supplier_service import (
    get_all_suppliers,
    get_supplier_by_id,
    create_supplier,
    update_supplier,
    delete_supplier
)

class TestSupplierService(unittest.TestCase):
    def test_get_suppliers(self):
        suppliers = get_all_suppliers()
        self.assertIsInstance(suppliers, list)
        self.assertGreater(len(suppliers), 0)

    def test_create_and_delete_supplier(self):
        supp_data = {
            "name": "Global Textil Inc",
            "contact": "Jane Doe",
            "email": "jane@globaltextil.com",
            "address": "123 Textile Rd, Mumbai",
            "status": "Active",
            "products_supplied": 12
        }
        created = create_supplier(supp_data)
        self.assertIsNotNone(created)
        supp_id = created.get("id")
        self.assertIsNotNone(supp_id)

        supp = get_supplier_by_id(supp_id)
        self.assertIsNotNone(supp)
        self.assertEqual(supp.get("name"), "Global Textil Inc")

        # Update
        updated = update_supplier(supp_id, {"contact": "John Doe"})
        self.assertIsNotNone(updated)
        self.assertEqual(updated.get("contact"), "John Doe")

        # Delete
        success = delete_supplier(supp_id)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
