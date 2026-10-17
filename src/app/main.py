# -*- coding: utf-8 -*-
"""
HUẾ SMART TOURISM RESTFUL API BACKEND (MAIN ENTRYPOINT)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Sinh viên thực hiện: Lê Hoàng Minh Quý | GVHD: TS. Hồ Quốc Dũng
-------------------------------------------------------------------------------------
Kiến trúc Phân lớp Modular Backend:
- schemas/: Chứa định nghĩa kiểu dữ liệu Pydantic (Request / Response)
- routes/: Chứa các file Router độc lập (chat, itinerary, kg, system)
- main.py: Khởi tạo FastAPI App, cấu hình CORS, kết nối các router qua include_router()
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.routes import system_router, chat_router, itinerary_router, kg_router

# =============================================================================
# 1. KHỞI TẠO FASTAPI APP
# =============================================================================
app = FastAPI(
    title="Huế Smart Tourism AI API",
    description=(
        "Cổng RESTful API phục vụ tích hợp vào ứng dụng đô thị thông minh Hue-S và các ứng dụng di động. "
        "Cung cấp tính năng Hỏi đáp du lịch dựa trên Đồ thị Tri thức Không gian (Spatial GraphRAG) "
        "và Tự động Gợi ý Lịch trình Tour tối ưu theo cự ly thực tế."
    ),
    version="1.0.0",
    contact={
        "name": "Lê Hoàng Minh Quý (HUET)",
        "email": "quylhm@huet.edu.vn"
    }
)

# =============================================================================
# 2. CẤU HÌNH MIDDLEWARE (CORS CHO HUE-S / WEB / MOBILE)
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# 3. NỐI CÁC ROUTE VÀO ỨNG DỤNG (INCLUDE ROUTERS)
# =============================================================================
app.include_router(system_router)
app.include_router(chat_router)
app.include_router(itinerary_router)
app.include_router(kg_router)


# =============================================================================
# 4. CHẠY TRỰC TIẾP VỚI UVICORN
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("🚀 KHỞI CHẠY HUẾ SMART TOURISM RESTFUL API BACKEND (MODULAR ARCHITECTURE)")
    print("📖 Xem tài liệu Swagger UI trực quan tại: http://localhost:8000/docs")
    print("=" * 80)
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
