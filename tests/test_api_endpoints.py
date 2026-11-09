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

import inspect
import socket
import threading
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from fastapi.encoders import jsonable_encoder
from src.app.main import app


def _can_use_loopback_socketpair(timeout: float = 0.5) -> bool:
    result = [False]
    def _probe():
        try:
            a, b = socket.socketpair()
            a.close()
            b.close()
            result[0] = True
        except Exception:
            result[0] = False
    t = threading.Thread(target=_probe, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]


class _MockResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = jsonable_encoder(payload)

    def json(self):
        return self._payload


class _DirectRouteClient:
    """Bộ điều phối route trực tiếp trong bộ nhớ khi môi trường test cô lập không hỗ trợ TCP socketpair."""
    def __init__(self, fastapi_app):
        self.app = fastapi_app

    def _iter_routes(self):
        for item in self.app.routes:
            if hasattr(item, "original_router") and hasattr(item.original_router, "routes"):
                for sub in item.original_router.routes:
                    yield sub
            else:
                yield item

    def _dispatch(self, method: str, path: str, params=None, json_body=None):
        params = params or {}
        for route in self._iter_routes():
            r_path = getattr(route, "path", None)
            r_methods = getattr(route, "methods", None) or set()
            fn = getattr(route, "endpoint", None)
            if r_path == path and method.upper() in r_methods and callable(fn):
                sig = inspect.signature(fn)
                kwargs = {}
                for name, param in sig.parameters.items():
                    if json_body is not None and hasattr(param.annotation, "model_validate"):
                        kwargs[name] = param.annotation.model_validate(json_body)
                    elif name in params:
                        ann = param.annotation
                        val = params[name]
                        if ann is int:
                            val = int(val)
                        elif ann is float:
                            val = float(val)
                        kwargs[name] = val
                    elif hasattr(param.default, "default"):
                        kwargs[name] = param.default.default
                res = fn(**kwargs)
                if inspect.iscoroutine(res):
                    # Thực thi coroutine đồng bộ nhẹ nếu là hàm async thuần không I/O mạng
                    try:
                        res.send(None)
                    except StopIteration as stop:
                        res = stop.value
                return _MockResponse(200, res)
        return _MockResponse(404, {"detail": "Not Found"})

    def get(self, path: str, params=None):
        return self._dispatch("GET", path, params=params)

    def post(self, path: str, json=None):
        return self._dispatch("POST", path, json_body=json)


class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if _can_use_loopback_socketpair():
            cls.client = TestClient(app)
        else:
            cls.client = _DirectRouteClient(app)

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
