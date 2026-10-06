import unittest
from backend.services.analytics_service import (
    get_sales_analytics,
    get_inventory_analytics,
    get_product_performance_analytics
)
from analytics.data_processing import products_to_df, sales_to_df
from backend.services.product_service import get_all_products
from backend.services.sales_service import get_all_sales

class TestAnalytics(unittest.TestCase):
    def test_sales_analytics(self):
        res = get_sales_analytics()
        self.assertIn("overview", res)
        self.assertIn("trends", res)
        self.assertIn("category_sales", res)

    def test_inventory_analytics(self):
        res = get_inventory_analytics()
        self.assertIn("overview", res)
        self.assertIn("stock_distribution", res)

    def test_product_performance(self):
        res = get_product_performance_analytics()
        self.assertIn("fast_moving", res)
        self.assertIn("slow_moving", res)

    def test_dataframes(self):
        sales = get_all_sales()
        products = get_all_products()
        sales_df = sales_to_df(sales)
        prod_df = products_to_df(products)
        self.assertFalse(sales_df.empty)
        self.assertFalse(prod_df.empty)

if __name__ == "__main__":
    unittest.main()
