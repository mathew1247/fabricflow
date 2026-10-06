import unittest
from backend.services.forecast_service import get_demand_forecast

class TestForecastService(unittest.TestCase):
    def test_get_demand_forecast(self):
        forecast = get_demand_forecast(period="30", category="all")
        self.assertIn("cards", forecast)
        self.assertIn("chart", forecast)
        self.assertIn("table", forecast)
        self.assertGreater(len(forecast["table"]), 0)

if __name__ == "__main__":
    unittest.main()
