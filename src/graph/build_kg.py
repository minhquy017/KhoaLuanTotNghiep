# -*- coding: utf-8 -*-
"""
KNOWLEDGE GRAPH BUILDER (XÂY DỰNG ĐỒ THỊ TRI THỨC DU LỊCH KHÔNG GIAN)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn dữ liệu:
  + data/processed/tourism_vietnam.db (Bảng `places`, `dishes`, `restaurant_dishes`)
  + data/processed/vietnam_provinces_gazetteer.json (Danh mục Tỉnh/Thành chuẩn hóa)
- Đầu ra:
  + data/processed/knowledge_graph.pkl (Đối tượng NetworkX MultiDiGraph nạp cực nhanh)
  + data/processed/knowledge_graph.graphml (Chuẩn GraphML phục vụ trực quan hóa Gephi/Cytoscape)
  + data/processed/kg_statistics.json (Thống kê số liệu học thuật cho chương thực nghiệm)
"""

import os
import sys
import json
import time
import pickle
import sqlite3
import networkx as nx
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
PROVINCES_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "vietnam_provinces_gazetteer.json")

OUTPUT_PKL = os.path.join(PROJECT_ROOT, "data", "processed", "knowledge_graph.pkl")
OUTPUT_GRAPHML = os.path.join(PROJECT_ROOT, "data", "processed", "knowledge_graph.graphml")
OUTPUT_STATS = os.path.join(PROJECT_ROOT, "data", "processed", "kg_statistics.json")

from spatial_indexer import compute_spatial_edges


def normalize_province_name(raw_name: str) -> str:
    """Chuẩn hóa tên tỉnh/thành để ánh xạ đồng nhất."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    if "huế" in name.lower() or "thừa thiên" in name.lower() or name == "Hue":
        return "Thành phố Huế"
    if "hà nội" in name.lower() or "hanoi" in name.lower():
        return "Thủ Đô Hà Nội"
    if "hồ chí minh" in name.lower() or "sài gòn" in name.lower() or "ho chi minh" in name.lower():
        return "Thành phố Hồ Chí Minh"
    if "đà nẵng" in name.lower() or "da nang" in name.lower():
        return "Thành phố Đà Nẵng"
    return name


def build_knowledge_graph():
    start_time = time.time()
    print("=" * 80)
    print("🌐 BẮT ĐẦU XÂY DỰNG ĐỒ THỊ TRI THỨC DU LỊCH KHÔNG GIAN (SPATIAL TOURISM KG)")
    print("=" * 80)

    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy CSDL SQLite tại: {DB_PATH}")
        return

    # Khởi tạo MultiDiGraph (Đồ thị có hướng đa cạnh)
    G = nx.MultiDiGraph()
    G.graph["name"] = "Vietnam Spatial Tourism Knowledge Graph"
    G.graph["case_study"] = "Thừa Thiên Huế"
    G.graph["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # =========================================================================
    # 1. NẠP NODES: PROVINCES (TỈNH / THÀNH PHỐ)
    # =========================================================================
    print("\n[1/4] Đang khởi tạo các đỉnh Địa giới Hành chính (Provinces)...")
    province_nodes = {}
    if os.path.exists(PROVINCES_PATH):
        with open(PROVINCES_PATH, "r", encoding="utf-8") as f:
            prov_data = json.load(f).get("provinces", {})
            for p_name, meta in prov_data.items():
                node_id = f"prov_{p_name}"
                province_nodes[p_name] = node_id
                G.add_node(
                    node_id,
                    node_type="Province",
                    name=p_name,
                    region=meta.get("region", ""),
                    is_central_city=meta.get("is_central_city", False)
                )

    # Đảm bảo Thành phố Huế luôn có mặt
    if "Thành phố Huế" not in province_nodes:
        hue_id = "prov_Thành phố Huế"
        province_nodes["Thành phố Huế"] = hue_id
        G.add_node(hue_id, node_type="Province", name="Thành phố Huế", region="Bắc Trung Bộ", is_central_city=True)

    print(f"-> Đã tạo {len(province_nodes)} đỉnh Tỉnh/Thành phố.")

    # =========================================================================
    # 2. NẠP NODES: DISHES (MÓN ĂN ĐẶC SẢN) & CẠNH ORIGINATED_FROM
    # =========================================================================
    print("\n[2/4] Đang khởi tạo các đỉnh Món ăn Đặc sản (Dishes)...")
    cur.execute("SELECT dish_id, canonical_name, category, region_origin FROM dishes")
    dish_rows = cur.fetchall()
    
    originated_edges_count = 0
    for dish_id, cname, cat, region in dish_rows:
        d_node_id = f"dish_{dish_id}"
        G.add_node(
            d_node_id,
            node_type="Dish",
            dish_id=dish_id,
            name=cname,
            category=cat or "",
            region_origin=region or ""
        )

        # Cạnh ORIGINATED_FROM: Món ăn -> Tỉnh thành xuất xứ
        if region:
            norm_region = normalize_province_name(region)
            if norm_region in province_nodes:
                G.add_edge(d_node_id, province_nodes[norm_region], key="ORIGINATED_FROM", relation="ORIGINATED_FROM")
                originated_edges_count += 1

    print(f"-> Đã tạo {len(dish_rows):,} đỉnh Món ăn và {originated_edges_count} cạnh xuất xứ (ORIGINATED_FROM).")

    # =========================================================================
    # 3. NẠP NODES: PLACES (ĐỊA ĐIỂM DU LỊCH) & CẠNH LOCATED_IN
    # =========================================================================
    print("\n[3/4] Đang khởi tạo các đỉnh Địa điểm du lịch (Places: Attractions, Restaurants, Hotels)...")
    cur.execute("""
        SELECT place_id, url, name, category, latitude, longitude,
               street_address, district, locality, rating_value, review_count,
               cuisines, price_range, image_url, is_hue
        FROM places
    """)
    place_rows = cur.fetchall()

    place_dict_list = []
    url_to_node_id = {}
    located_in_count = 0
    hue_places_count = 0

    cat_counts = Counter()

    for r in place_rows:
        (pid, url, name, cat, lat, lon, street, dist, loc, rating, rev_cnt,
         cuisines, price, img, is_hue) = r

        node_id = f"place_{pid}"
        url_to_node_id[url] = node_id
        cat_clean = (cat or "place").lower()
        cat_counts[cat_clean] += 1

        if is_hue:
            hue_places_count += 1

        lat_val = float(lat) if lat is not None else 0.0
        lon_val = float(lon) if lon is not None else 0.0
        rating_val = float(rating) if rating is not None else 0.0
        rev_cnt_val = int(rev_cnt) if rev_cnt is not None else 0

        G.add_node(
            node_id,
            node_type=cat_clean.capitalize(),
            place_id=pid,
            name=name or "",
            category=cat_clean,
            latitude=lat_val,
            longitude=lon_val,
            rating_value=rating_val,
            review_count=rev_cnt_val,
            street_address=street or "",
            district=dist or "",
            locality=loc or "",
            cuisines=cuisines or "[]",
            price_range=price or "",
            image_url=img or "",
            url=url or "",
            is_hue=int(is_hue or 0)
        )

        place_dict_list.append({
            "id": node_id,
            "latitude": lat_val,
            "longitude": lon_val,
            "locality": loc or "",
            "is_hue": is_hue
        })

        # Cạnh LOCATED_IN: Place -> Province
        std_prov = normalize_province_name(loc)
        if std_prov in province_nodes:
            G.add_edge(node_id, province_nodes[std_prov], key="LOCATED_IN", relation="LOCATED_IN")
            located_in_count += 1

    print(f"-> Đã tạo {len(place_rows):,} đỉnh Địa điểm:")
    for c_name, c_cnt in cat_counts.items():
        print(f"   • {c_name.capitalize():<15}: {c_cnt:>6,} địa điểm")
    print(f"   • Riêng Thừa Thiên Huế : {hue_places_count:>6,} địa điểm (Case Study)")
    print(f"-> Đã tạo {located_in_count:,} cạnh phân cấp hành chính (LOCATED_IN).")

    # =========================================================================
    # 4. NẠP CẠNH: SERVES (NHÀ HÀNG -> MÓN ĂN ĐẶC SẢN)
    # =========================================================================
    print("\n[4/4] Đang thiết lập các cạnh Thực đơn ngầm (SERVES) từ kết quả Khai phá NER...")
    cur.execute("""
        SELECT rd.place_url, rd.dish_id, rd.mention_count, rd.avg_rating, rd.sentiment_score, p.is_hue
        FROM restaurant_dishes rd
        JOIN places p ON rd.place_url = p.url
    """)
    serves_rows = cur.fetchall()
    
    serves_count = 0
    hue_serves_count = 0

    for purl, dish_id, m_cnt, avg_r, sent, is_hue in serves_rows:
        rest_node_id = url_to_node_id.get(purl)
        dish_node_id = f"dish_{dish_id}"

        if rest_node_id and G.has_node(rest_node_id) and G.has_node(dish_node_id):
            edge_attrs = {
                "relation": "SERVES",
                "mention_count": int(m_cnt or 0),
                "avg_rating": float(avg_r or 4.0),
                "sentiment_score": float(sent or 0.0)
            }
            G.add_edge(rest_node_id, dish_node_id, key="SERVES", **edge_attrs)
            serves_count += 1
            if is_hue:
                hue_serves_count += 1

    print(f"-> Đã tạo {serves_count:,} cạnh phục vụ món ăn (SERVES).")
    print(f"   • Riêng tại Thừa Thiên Huế: {hue_serves_count} cạnh món đặc sản Cố đô!")

    # =========================================================================
    # 5. NẠP CẠNH KHÔNG GIAN: NEAR_BY (SPATIAL PROXIMITY)
    # =========================================================================
    print("\n[5/4] Đang tính toán ma trận khoảng cách không gian (cKDTree Haversine)...")
    print("   • Bán kính lân cận: <= 1.2 km (khoảng cách đi bộ/xe máy đô thị)")
    
    spatial_edges = compute_spatial_edges(place_dict_list, max_distance_km=1.2, max_neighbors_per_node=8)
    
    nearby_count = 0
    hue_nearby_count = 0

    for u, v, e_data in spatial_edges:
        if G.has_node(u) and G.has_node(v):
            G.add_edge(u, v, key="NEAR_BY", **e_data)
            nearby_count += 1
            if G.nodes[u].get("is_hue") and G.nodes[v].get("is_hue"):
                hue_nearby_count += 1

    print(f"-> Đã tạo {nearby_count:,} cạnh lân cận không gian (NEAR_BY).")
    print(f"   • Riêng cụm địa điểm Huế: {hue_nearby_count:,} cạnh không gian!")

    conn.close()

    # =========================================================================
    # 6. TÍNH TOÁN CHỈ SỐ HỌC THUẬT & XUẤT FILE
    # =========================================================================
    print("\n" + "=" * 80)
    print("📊 BÁO CÁO THỐNG KÊ CẤU TRÚC ĐỒ THỊ TRI THỨC (GRAPH METRICS):")
    print("=" * 80)

    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()

    # Đếm node theo loại
    node_type_counts = Counter(data.get("node_type", "Unknown") for _, data in G.nodes(data=True))
    edge_type_counts = Counter(data.get("relation", "Unknown") for _, _, data in G.edges(data=True))

    print(f"• TỔNG SỐ ĐỈNH (NODES)    : {total_nodes:>7,}")
    for ntype, cnt in node_type_counts.most_common():
        print(f"  + {ntype:<15}: {cnt:>6,} nodes ({cnt/total_nodes*100:5.1f}%)")

    print(f"\n• TỔNG SỐ CẠNH (EDGES)    : {total_edges:>7,}")
    for etype, cnt in edge_type_counts.most_common():
        print(f"  + {etype:<15}: {cnt:>6,} edges ({cnt/total_edges*100:5.1f}%)")

    # Thống kê riêng cho Case Study Huế
    hue_sub_nodes = [n for n, d in G.nodes(data=True) if d.get("is_hue") == 1]
    print(f"\n• TRỌNG TÂM CASE STUDY CỐ ĐÔ HUẾ:")
    print(f"  + Số địa điểm du lịch Huế : {len(hue_sub_nodes):,} địa điểm")
    print(f"  + Cạnh phục vụ món ăn Huế : {hue_serves_count} cạnh")
    print(f"  + Cạnh lân cận không gian : {hue_nearby_count:,} cạnh")

    # Xuất file Pickle (dành cho RAG load siêu tốc)
    print(f"\n💾 Đang lưu đồ thị sang file Pickle: {OUTPUT_PKL}...")
    with open(OUTPUT_PKL, "wb") as f:
        pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Xuất file GraphML (chuẩn mở cho Gephi / Cytoscape)
    print(f"💾 Đang xuất đồ thị chuẩn GraphML: {OUTPUT_GRAPHML}...")
    # GraphML yêu cầu tất cả thuộc tính phải là primitive types (int, float, str, bool)
    G_clean = G.copy()
    for _, data in G_clean.nodes(data=True):
        if "cuisines" in data and isinstance(data["cuisines"], list):
            data["cuisines"] = json.dumps(data["cuisines"], ensure_ascii=False)
    nx.write_graphml(G_clean, OUTPUT_GRAPHML)

    # Xuất file thống kê JSON
    stats_data = {
        "graph_name": G.graph.get("name"),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "node_type_distribution": dict(node_type_counts),
        "edge_type_distribution": dict(edge_type_counts),
        "hue_case_study": {
            "total_places": len(hue_sub_nodes),
            "serves_edges": hue_serves_count,
            "nearby_edges": hue_nearby_count
        },
        "build_duration_seconds": round(time.time() - start_time, 2)
    }
    with open(OUTPUT_STATS, "w", encoding="utf-8") as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🎉 XÂY DỰNG ĐỒ THỊ TRI THỨC HOÀN TẤT THÀNH CÔNG RỰC RỠ! ({elapsed:.2f}s)")
    print(f"👉 File nạp RAG (Pickle) : {OUTPUT_PKL} ({os.path.getsize(OUTPUT_PKL)/(1024*1024):.1f} MB)")
    print(f"👉 File trực quan (GraphML): {OUTPUT_GRAPHML} ({os.path.getsize(OUTPUT_GRAPHML)/(1024*1024):.1f} MB)")
    print(f"👉 File thống kê (JSON)   : {OUTPUT_STATS}")
    print("=" * 80)


if __name__ == "__main__":
    build_knowledge_graph()
