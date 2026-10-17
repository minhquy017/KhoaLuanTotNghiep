# -*- coding: utf-8 -*-
"""
UNIT TEST: RESTFUL API ENDPOINTS (FASTAPI TESTCLIENT)
Kiểm thử toàn bộ các endpoint nghiệp vụ theo kiến trúc Modular:
- GET /health & GET /api/v1/health
- GET /
- GET /api/v1/kg/places/nearby
- GET /api/v1/kg/dishes/search
- POST /api/v1/itinerary
"""
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from fastapi.testclient import TestClient
from src.app.main import app


class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """Endpoint GET / trả về thông tin đồ án và tác giả."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("Lê Hoàng Minh Quý", data.get("author", ""))

    def test_health_endpoints(self):
        """Endpoint GET /health và GET /api/v1/health xác nhận trạng thái đồ thị."""
        for path in ["/health", "/api/v1/health"]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"Health check failed on {path}")
            data = resp.json()
            self.assertEqual(data.get("status"), "healthy")
            self.assertGreater(data.get("kg_nodes", 0), 9000)
            self.assertGreater(data.get("kg_edges", 0), 80000)

    def test_nearby_places_endpoint(self):
        """Endpoint GET /api/v1/kg/places/nearby tra cứu các điểm lân cận."""
        resp = self.client.get(
            "/api/v1/kg/places/nearby", 
            params={"place_id": "place_8875", "max_distance_km": 1.5, "limit": 3}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("nearby_places", data)
        self.assertGreater(len(data["nearby_places"]), 0)

    def test_dish_search_endpoint(self):
        """Endpoint GET /api/v1/kg/dishes/search tra cứu quán theo món ăn."""
        resp = self.client.get(
            "/api/v1/kg/dishes/search", 
            params={"dish_name": "Bún bò Huế", "limit": 3}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("places", data)
        self.assertGreater(len(data["places"]), 0)

    def test_generate_itinerary_endpoint(self):
        """Endpoint POST /api/v1/itinerary tạo lịch trình tour có cấu trúc."""
        resp = self.client.post(
            "/api/v1/itinerary", 
            json={"num_days": 1, "trip_type": "Couples", "preferred_dishes": ["Bún bò Huế"]}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "success")
        itin = data.get("itinerary_data", {})
        self.assertEqual(len(itin.get("days", [])), 1)
        self.assertIn("formatted_markdown", data)


if __name__ == "__main__":
    unittest.main()
