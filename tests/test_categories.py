import unittest
from backend.services.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)

class TestCategoryService(unittest.TestCase):
    def test_get_categories(self):
        cats = get_all_categories()
        self.assertIsInstance(cats, list)
        self.assertGreater(len(cats), 0)
        self.assertTrue("name" in cats[0] or "category_name" in cats[0])

    def test_category_crud_and_duplicate(self):
        test_cat_data = {
            "category_name": "Test Activewear Category",
            "description": "Active sportswear testing category"
        }
        created, err = create_category(test_cat_data)
        self.assertIsNone(err)
        self.assertIsNotNone(created)
        cat_id = created["category_id"]

        # Duplicate check
        dup_created, dup_err = create_category(test_cat_data)
        self.assertIsNotNone(dup_err)

        # Get
        cat = get_category_by_id(cat_id)
        self.assertIsNotNone(cat)
        self.assertEqual(cat["category_name"], "Test Activewear Category")

        # Update
        updated, u_err = update_category(cat_id, {"description": "Updated activewear description"})
        self.assertIsNone(u_err)
        self.assertEqual(updated["description"], "Updated activewear description")

        # Delete
        success = delete_category(cat_id)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
