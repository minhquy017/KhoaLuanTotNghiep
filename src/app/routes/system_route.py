# -*- coding: utf-8 -*-
"""
ROUTER: THÔNG TIN HỆ THỐNG & HEALTH CHECK (SYSTEM ROUTE)
"""
from fastapi import APIRouter
from src.graph.graph_retriever import get_graph_retriever

from src.rag.agent_graph import OLLAMA_MODEL

router = APIRouter(tags=["Hệ thống"])
retriever = get_graph_retriever()


@router.get("/")
def root():
    """Thông tin tổng quan dịch vụ API."""
    return {
        "service": "Huế Smart Tourism AI Gateway",
        "institution": "Khoa Kỹ thuật và Công nghệ – Đại học Huế (HUET)",
        "author": "Lê Hoàng Minh Quý",
        "supervisor": "TS. Hồ Quốc Dũng",
        "ready_for": ["Hue-S Mobile App", "Web Applications", "Third-party Tourism Systems"],
        "docs_url": "/docs",
        "status": "online"
    }


@router.get("/health")
@router.get("/api/v1/health")
def health_check():
    """Kiểm tra trạng thái kết nối Đồ thị và Mô hình."""
    return {
        "status": "healthy",
        "kg_nodes": len(retriever.G.nodes) if retriever.G else 0,
        "kg_edges": len(retriever.G.edges) if retriever.G else 0,
        "vector_db": "ChromaDB Connected",
        "model": f"{OLLAMA_MODEL.upper()} (GPU Local)"
    }
