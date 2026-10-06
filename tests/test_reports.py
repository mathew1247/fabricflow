import unittest
from backend.services.report_service import get_report_data, generate_csv_export

class TestReportService(unittest.TestCase):
    def test_get_report_data(self):
        report = get_report_data(report_type="inventory")
        self.assertIn("headers", report)
        self.assertIn("rows", report)
        self.assertIn("title", report)

    def test_generate_csv_export(self):
        csv_data, filename = generate_csv_export(report_type="inventory")
        self.assertIsNotNone(csv_data)
        self.assertTrue(filename.endswith(".csv"))

if __name__ == "__main__":
    unittest.main()
