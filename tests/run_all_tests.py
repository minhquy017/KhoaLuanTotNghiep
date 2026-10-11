# -*- coding: utf-8 -*-
"""
MASTER TEST RUNNER: TOÀN BỘ HỆ THỐNG HUẾ SMART TOURISM
Chạy tất cả các test suites kiểm thử đơn vị & tích hợp (Unit & Integration Tests):
1. Spatial Indexer (Haversine & cKDTree)
2. Knowledge Graph Retriever (NetworkX)
3. Spatial Itinerary Planner (Tối ưu hóa Tour 1-3 ngày)
4. Vector Retriever & Agentic RAG (ChromaDB & LangGraph)
5. RESTful API Endpoints (FastAPI Modular Backend)
"""
import os
import sys
import time
import unittest
from pathlib import Path

# Đảm bảo import được các module từ thư mục gốc
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Import các test suites
from tests.test_spatial_indexer import TestSpatialIndexer
from tests.test_graph_retriever import TestGraphRetriever
from tests.test_itinerary_planner import TestItineraryPlanner
from tests.test_vector_and_rag import TestVectorAndRag
from tests.test_api_endpoints import TestApiEndpoints


def run_comprehensive_test_suite():
    print("=" * 85)
    print("🚀 BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG HUẾ SMART TOURISM (SPATIAL GRAPHRAG)")
    print(f"📍 Thư mục dự án: {ROOT_DIR}")
    print("=" * 85)

    suites = [
        ("1. Không Gian & Haversine (cKDTree)", unittest.TestLoader().loadTestsFromTestCase(TestSpatialIndexer)),
        ("2. Đồ Thị Tri Thức (NetworkX KG)", unittest.TestLoader().loadTestsFromTestCase(TestGraphRetriever)),
        ("3. Lập Lịch Trình (Spatial Planner)", unittest.TestLoader().loadTestsFromTestCase(TestItineraryPlanner)),
        ("4. Vector & Agentic RAG (ChromaDB)", unittest.TestLoader().loadTestsFromTestCase(TestVectorAndRag)),
        ("5. RESTful API Gateway (FastAPI)", unittest.TestLoader().loadTestsFromTestCase(TestApiEndpoints)),
    ]

    total_tests = 0
    total_failures = 0
    total_errors = 0
    start_time_all = time.time()
    results_summary = []

    for suite_name, suite in suites:
        print(f"\n🔍 Đang chạy kiểm thử: {suite_name} ({suite.countTestCases()} test cases)...")
        suite_start = time.time()
        
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        suite_duration = time.time() - suite_start
        passed = result.testsRun - len(result.failures) - len(result.errors)
        status = "PASSED ✅" if (len(result.failures) == 0 and len(result.errors) == 0) else "FAILED ❌"

        results_summary.append({
            "name": suite_name,
            "total": result.testsRun,
            "passed": passed,
            "failed": len(result.failures) + len(result.errors),
            "time": suite_duration,
            "status": status
        })

        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)

    total_duration = time.time() - start_time_all

    print("\n" + "=" * 85)
    print("📊 BẢNG TỔNG HỢP KẾT QUẢ KIỂM THỬ TOÀN BỘ HỆ THỐNG")
    print("=" * 85)
    print(f"{'Phân hệ / Test Suite':<40} | {'Tổng':<6} | {'Đạt':<6} | {'Lỗi':<6} | {'Thời gian':<10} | {'Trạng thái'}")
    print("-" * 85)

    for item in results_summary:
        print(
            f"{item['name']:<40} | "
            f"{item['total']:<6} | "
            f"{item['passed']:<6} | "
            f"{item['failed']:<6} | "
            f"{item['time']:<8.2f}s | "
            f"{item['status']}"
        )

    print("-" * 85)
    print(f"Tổng số ca kiểm thử: {total_tests} | Vượt qua: {total_tests - total_failures - total_errors} | Thất bại: {total_failures + total_errors}")
    print(f"Tổng thời gian thực thi: {total_duration:.2f} giây")
    print("=" * 85)

    if total_failures == 0 and total_errors == 0:
        print("🎉 TẤT CẢ 100% CÁC TEST CASES ĐỀU VƯỢT QUA XUẤT SẮC! HỆ THỐNG HOÀN TOÀN ỔN ĐỊNH. ✅\n")
        return 0
    else:
        print("⚠️ CÓ TEST CASE BỊ THẤT BẠI. VUI LÒNG KIỂM TRA LẠI CHI TIẾT LỖI Ở TRÊN. ❌\n")
        return 1


if __name__ == "__main__":
    exit_code = run_comprehensive_test_suite()
    sys.exit(exit_code)
