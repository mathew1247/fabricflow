import unittest
import json
from app import create_app

class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_login_success(self):
        response = self.client.post("/api/auth/login", json={
            "email": "admin@fabricflow.com",
            "password": "fabricflow2024"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)["data"]
        self.assertIn("token", data)
        self.assertEqual(data["email"], "admin@fabricflow.com")

    def test_login_missing_fields(self):
        response = self.client.post("/api/auth/login", json={"email": ""})
        self.assertEqual(response.status_code, 400)

    def test_get_profile(self):
        response = self.client.get("/api/auth/me", headers={
            "Authorization": "Bearer fabricflow2024"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)["data"]
        self.assertEqual(data["role"], "admin")

if __name__ == "__main__":
    unittest.main()
