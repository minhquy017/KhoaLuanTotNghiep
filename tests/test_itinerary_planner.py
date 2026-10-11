# -*- coding: utf-8 -*-
"""
UNIT TEST: SPATIAL ITINERARY PLANNER
Kiểm thử thuật toán lập lịch trình 1 - 3 ngày, ràng buộc cự ly quán ăn và phân cụm không gian.
"""
import unittest
from src.planner.itinerary_planner import get_itinerary_planner


class TestItineraryPlanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planner = get_itinerary_planner()

    def test_plan_itinerary_1_day(self):
        """Kiểm thử lập lịch trình 1 ngày: phải có đủ các chặng sáng/trưa/chiều/tối."""
        plan = self.planner.plan_itinerary(num_days=1, preferred_dishes=["Bún bò Huế"], trip_type="Couples")
        self.assertIsInstance(plan, dict)
        self.assertIn("days", plan)
        self.assertEqual(len(plan["days"]), 1)

        day1 = plan["days"][0]
        self.assertEqual(day1["day_number"], 1)
        self.assertIn("theme", day1)
        self.assertIn("slots", day1)
        self.assertGreaterEqual(len(day1["slots"]), 4, "Lịch trình 1 ngày phải có ít nhất 4 chặng")

        # Kiểm tra tính hợp lệ của tọa độ GPS trong từng chặng
        for slot in day1["slots"]:
            self.assertIn("latitude", slot)
            self.assertIn("longitude", slot)
            self.assertGreater(slot["latitude"], 16.0)
            self.assertGreater(slot["longitude"], 107.0)

    def test_lunch_proximity_constraint(self):
        """Quán ăn trưa phải được ghép nối lân cận điểm tham quan sáng (< 2.5 km)."""
        plan = self.planner.plan_itinerary(num_days=1, preferred_dishes=["Bún bò Huế"], trip_type="Couples")
        day1 = plan["days"][0]
        
        # Tìm chặng trưa
        lunch_slot = None
        for s in day1["slots"]:
            if "Trưa" in s.get("slot_name", "") or "Ẩm thực" in s.get("activity_type", ""):
                lunch_slot = s
                break
        
        self.assertIsNotNone(lunch_slot, "Không tìm thấy chặng ăn trưa")
        dist_to_prev = lunch_slot.get("distance_from_prev_km", 0.0)
        self.assertLessEqual(dist_to_prev, 2.5, f"Quán ăn trưa quá xa điểm tham quan: {dist_to_prev} km")

    def test_plan_itinerary_3_days(self):
        """Kiểm thử lập lịch trình 3 ngày hoàn chỉnh."""
        plan = self.planner.plan_itinerary(num_days=3, preferred_dishes=["Bún bò Huế", "Cơm hến"], trip_type="Friends")
        self.assertEqual(len(plan["days"]), 3)
        for i, d in enumerate(plan["days"], start=1):
            self.assertEqual(d["day_number"], i)
            self.assertGreater(d.get("total_distance_km", 0), 0)

    def test_format_itinerary_markdown(self):
        """Xuất bản lịch trình dạng Markdown rõ ràng cho người dùng."""
        plan = self.planner.plan_itinerary(num_days=1, trip_type="Solo")
        md_text = self.planner.format_itinerary_markdown(plan)
        self.assertIsInstance(md_text, str)
        self.assertIn("NGÀY 1", md_text.upper())
        self.assertIn("KM", md_text.upper())


if __name__ == "__main__":
    unittest.main()
