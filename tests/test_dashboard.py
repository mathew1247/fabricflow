import unittest
from backend.services.dashboard_service import get_dashboard_metrics

class TestDashboardService(unittest.TestCase):
    def test_dashboard_metrics(self):
        metrics = get_dashboard_metrics()
        self.assertIn("total_products", metrics)
        self.assertIn("total_stock", metrics)
        self.assertIn("total_sales", metrics)
        self.assertIn("low_stock_items", metrics)
        self.assertIn("critical_stock_items", metrics)
        self.assertIn("sales_growth", metrics)
        self.assertIn("stock_growth", metrics)
        self.assertIn("product_growth", metrics)
        self.assertIn("sales_trend", metrics)
        self.assertIn("stock_status", metrics)
        self.assertIn("top_categories", metrics)
        self.assertIn("recent_sales", metrics)
        self.assertIn("kpi", metrics)
        self.assertGreater(metrics["total_products"], 0)
        self.assertGreater(metrics["total_stock"], 0)
        self.assertGreater(metrics["total_sales"], 0)

if __name__ == "__main__":
    unittest.main()
