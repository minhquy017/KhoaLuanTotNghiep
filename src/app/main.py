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

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.routes import system_router, chat_router, itinerary_router, kg_router
from src.rag.agent_graph import OLLAMA_MODEL

def ensure_ollama_service():
    """Tự động kiểm tra và khởi chạy dịch vụ Ollama ngầm nếu chưa chạy."""
    import urllib.request
    import subprocess
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=1.0) as resp:
            if resp.status == 200:
                print(f"✅ [Ollama] Dịch vụ Local LLM ({OLLAMA_MODEL}) đang hoạt động sẵn sàng.")
                return
    except Exception:
        pass

    print("⚡ [Ollama] Chưa phát hiện dịch vụ Ollama. Đang tự động khởi chạy ngầm...")
    try:
        creation_flags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags
        )
        print("🚀 [Ollama] Đã tự động kích hoạt tiến trình 'ollama serve' thành công!")
    except Exception as e:
        print(f"⚠️ [Ollama] Không thể tự khởi động Ollama: {e}")

def warmup_llm_service():
    """Tự động nạp trước (warm-up) mô hình vào VRAM GPU và giữ thường trực."""
    import time
    time.sleep(1.0)
    print(f"🔥 [Ollama Warm-up] Đang nạp trước mô hình {OLLAMA_MODEL} vào GPU VRAM...")
    try:
        from src.rag.agent_graph import llm
        from langchain_core.messages import HumanMessage
        llm.invoke([HumanMessage(content="hi")])
        print(f"⚡ [Ollama Warm-up] ĐÃ NẠP THÀNH CÔNG {OLLAMA_MODEL} VÀO GPU VRAM! Sẵn sàng phản hồi tức thì.")
    except Exception as e:
        print(f"⚠️ [Ollama Warm-up] Thông báo: {e}")

def unload_llm_service():
    """Tự động giải phóng hoàn toàn VRAM khi tắt server Backend (ollama stop)."""
    import subprocess
    try:
        creation_flags = 0x08000000 if sys.platform == "win32" else 0
        subprocess.run(
            ["ollama", "stop", OLLAMA_MODEL],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
            timeout=5.0
        )
        print(f"🧹 [Ollama] Đã giải phóng hoàn toàn VRAM của {OLLAMA_MODEL} trả về cho hệ thống!")
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    ensure_ollama_service()
    threading.Thread(target=warmup_llm_service, daemon=True).start()
    yield
    unload_llm_service()

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
    lifespan=lifespan,
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
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "src")]
    )
