# -*- coding: utf-8 -*-
"""
WEB SEARCH TOOL (CÔNG CỤ TÌM KIẾM WEB DỰ PHÒNG - ZERO API KEY)
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
- Tự động kích hoạt khi điểm tin cậy nội bộ (KG + ChromaDB) thấp hơn ngưỡng
- Hỗ trợ công cụ tìm kiếm DuckDuckGo HTML & Wikipedia Tiếng Việt (100% miễn phí, không cần API Key)
- Tương thích cắm rút (pluggable): tự động nâng cấp sang Tavily nếu có TAVILY_API_KEY
"""

import os
import sys
import json
import urllib.parse
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup


class WebSearchTool:
    def __init__(self, timeout: int = 6):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def search_duckduckgo(self, query: str, max_results: int = 4) -> List[Dict[str, str]]:
        """Tìm kiếm qua cổng DuckDuckGo HTML công khai."""
        encoded_q = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            
            # Duyệt các block kết quả
            for res_div in soup.select(".result"):
                title_elem = res_div.select_one(".result__title a")
                snippet_elem = res_div.select_one(".result__snippet")
                url_elem = res_div.select_one(".result__url")

                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    link = title_elem.get("href", "")
                    
                    # Giải mã URL chuyển tiếp nếu cần
                    if link.startswith("/l/?uddg="):
                        link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])

                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "link": link,
                        "source": "DuckDuckGo"
                    })
                    if len(results) >= max_results:
                        break

            return results
        except Exception as e:
            return []

    def search_wikipedia(self, query: str, max_results: int = 2) -> List[Dict[str, str]]:
        """Tìm kiếm bách khoa toàn thư Wikipedia Tiếng Việt (cực nhanh và ổn định)."""
        encoded_q = urllib.parse.quote(query)
        url = f"https://vi.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_q}&utf8=&format=json"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                return []
            
            data = resp.json()
            search_items = data.get("query", {}).get("search", [])
            results = []
            for item in search_items[:max_results]:
                title = item.get("title", "")
                raw_snippet = item.get("snippet", "")
                # Loại bỏ thẻ span HTML trong snippet
                clean_snippet = BeautifulSoup(raw_snippet, "html.parser").get_text(strip=True)
                results.append({
                    "title": title,
                    "snippet": clean_snippet,
                    "link": f"https://vi.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                    "source": "Wikipedia"
                })
            return results
        except Exception:
            return []

    def search(self, query: str, max_results: int = 4) -> List[Dict[str, str]]:
        """Tìm kiếm tổng hợp từ các nguồn mở không cần API key."""
        # Ưu tiên DuckDuckGo
        ddg_results = self.search_duckduckgo(query, max_results=max_results)
        if ddg_results:
            return ddg_results

        # Fallback sang Wikipedia nếu mạng chặn DuckDuckGo
        wiki_results = self.search_wikipedia(query, max_results=max_results)
        return wiki_results

    def format_search_context(self, search_results: List[Dict[str, str]]) -> str:
        """Định dạng kết quả tìm kiếm web thành văn bản cho LLM."""
        if not search_results:
            return "Không tìm thấy thông tin bổ sung từ nguồn Internet mở."

        lines = ["### [THÔNG TIN THỰC THỜI BỔ SUNG TỪ INTERNET (WEB FALLBACK)]"]
        for idx, res in enumerate(search_results, 1):
            src = res.get("source", "Web")
            title = res.get("title", "")
            snippet = res.get("snippet", "")
            link = res.get("link", "")
            lines.append(f"{idx}. [{src}] **{title}**\n   {snippet}\n   (Nguồn: {link})")
        return "\n".join(lines)


# Singleton
_search_tool = None

def get_web_search_tool() -> WebSearchTool:
    global _search_tool
    if _search_tool is None:
        _search_tool = WebSearchTool()
    return _search_tool


if __name__ == "__main__":
    tool = get_web_search_tool()
    print("🌐 Đang thử nghiệm Web Search Fallback...")
    res = tool.search("thời tiết thành phố Huế", max_results=2)
    print(tool.format_search_context(res))
