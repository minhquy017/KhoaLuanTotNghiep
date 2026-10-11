# -*- coding: utf-8 -*-
"""
ONTOLOGY & SCHEMA ĐỒ THỊ TRI THỨC DU LỊCH KHÔNG GIAN (SPATIAL TOURISM KG)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
Xác định cấu trúc bản thể (Ontology):
1. Các loại Thực thể (Node Types):
   - Place (Attraction, Restaurant, Hotel)
   - Dish (Món ăn đặc sản)
   - Province (Tỉnh / Thành phố)
2. Các loại Quan hệ (Relationship / Edge Types):
   - LOCATED_IN: Place -> Province
   - SERVES: Restaurant -> Dish (kèm mention_count, avg_rating, sentiment_score)
   - ORIGINATED_FROM: Dish -> Province
   - NEAR_BY: Place -> Place (kèm distance_km, walk_time_min, drive_time_min)
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class NodeType(str, Enum):
    PLACE = "Place"
    ATTRACTION = "Attraction"
    RESTAURANT = "Restaurant"
    HOTEL = "Hotel"
    DISH = "Dish"
    PROVINCE = "Province"


class EdgeType(str, Enum):
    LOCATED_IN = "LOCATED_IN"          # (Place) -[:LOCATED_IN]-> (Province)
    SERVES = "SERVES"                  # (Restaurant) -[:SERVES]-> (Dish)
    ORIGINATED_FROM = "ORIGINATED_FROM"# (Dish) -[:ORIGINATED_FROM]-> (Province)
    NEAR_BY = "NEAR_BY"                # (Place) -[:NEAR_BY]-> (Place)


@dataclass
class PlaceNode:
    id: str
    name: str
    category: str                      # attraction, restaurant, hotel
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating_value: Optional[float] = None
    review_count: int = 0
    street_address: str = ""
    district: str = ""
    locality: str = ""
    cuisines: str = ""
    price_range: str = ""
    image_url: str = ""
    url: str = ""
    is_hue: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.category.capitalize() if self.category else NodeType.PLACE.value,
            "name": self.name,
            "category": self.category,
            "latitude": self.latitude if self.latitude is not None else 0.0,
            "longitude": self.longitude if self.longitude is not None else 0.0,
            "rating_value": self.rating_value if self.rating_value is not None else 0.0,
            "review_count": self.review_count,
            "street_address": self.street_address,
            "district": self.district,
            "locality": self.locality,
            "cuisines": self.cuisines,
            "price_range": self.price_range,
            "image_url": self.image_url,
            "url": self.url,
            "is_hue": self.is_hue
        }


@dataclass
class DishNode:
    dish_id: str
    canonical_name: str
    category: str
    region_origin: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": NodeType.DISH.value,
            "name": self.canonical_name,
            "dish_id": self.dish_id,
            "category": self.category,
            "region_origin": self.region_origin
        }


@dataclass
class ProvinceNode:
    name: str
    region: str = ""
    is_central_city: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": NodeType.PROVINCE.value,
            "name": self.name,
            "region": self.region,
            "is_central_city": self.is_central_city
        }
