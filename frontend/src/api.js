// =============================================================================
// HUẾ SMART TOURISM — API CLIENT (FastAPI Gateway Connector)
// Kết nối trực tiếp đến Modular Backend: src/app/main.py
// =============================================================================

const API_BASE_URL = 'http://localhost:8000';

export class TourismApiClient {
  /**
   * Kiểm tra tình trạng kết nối Backend & Đồ thị Tri thức
   */
  static async checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('Backend connection warning:', err);
      return { status: 'offline', error: err.message };
    }
  }

  /**
   * Gọi API Lập Lịch Trình Du Lịch Tối Ưu (Spatial Itinerary Planner)
   * @param {number} numDays - Số ngày (1, 2, 3)
   * @param {string[]} preferredDishes - Danh sách món ăn ưu tiên
   * @param {string} tripType - Phong cách: Couples, Family, Friends, Solo
   */
  static async generateItinerary(numDays = 2, preferredDishes = [], tripType = 'Couples') {
    const res = await fetch(`${API_BASE_URL}/api/v1/itinerary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        num_days: parseInt(numDays, 10),
        preferred_dishes: preferredDishes,
        trip_type: tripType
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Lỗi khi lập lịch trình (HTTP ${res.status})`);
    }

    return await res.json();
  }

  /**
   * Gửi câu hỏi đến Trợ lý Du lịch Thông minh (Spatial Agentic RAG)
   * @param {string} query - Câu hỏi tự nhiên
   * @param {string} locality - Vùng địa lý ("Thành phố Huế")
   * @param {number|null} userLat - Vĩ độ GPS người dùng
   * @param {number|null} userLng - Kinh độ GPS người dùng
   */
  static async askAssistant(query, locality = 'Thành phố Huế', userLat = null, userLng = null) {
    const payload = {
      query: query,
      locality: locality
    };
    if (userLat !== null && userLng !== null) {
      payload.user_lat = userLat;
      payload.user_lng = userLng;
    }

    const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Lỗi khi xử lý câu hỏi (HTTP ${res.status})`);
    }

    return await res.json();
  }

  /**
   * Tra cứu quán ăn theo món đặc sản qua cạnh SERVES trong Đồ thị
   */
  static async searchPlacesByDish(dishName, limit = 5) {
    const params = new URLSearchParams({
      dish_name: dishName,
      limit: limit.toString()
    });
    const res = await fetch(`${API_BASE_URL}/api/v1/kg/dishes/search?${params.toString()}`);
    if (!res.ok) throw new Error(`Lỗi tra cứu món ăn (HTTP ${res.status})`);
    return await res.json();
  }

  /**
   * Tra cứu địa điểm lân cận qua cạnh NEAR_BY trong Đồ thị
   */
  static async getNearbyPlaces(placeId, maxDistanceKm = 1.5, limit = 5) {
    const params = new URLSearchParams({
      place_id: placeId,
      max_distance_km: maxDistanceKm.toString(),
      limit: limit.toString()
    });
    const res = await fetch(`${API_BASE_URL}/api/v1/kg/places/nearby?${params.toString()}`);
    if (!res.ok) throw new Error(`Lỗi tra cứu lân cận (HTTP ${res.status})`);
    return await res.json();
  }

  /**
   * Tra cứu hồ sơ chi tiết chuyên sâu của địa điểm (POI Deep-dive: Rating, Reviews, Cạnh SERVES, Cạnh NEAR_BY)
   * @param {string} name - Tên địa điểm
   * @param {string} [placeId] - ID địa điểm
   */
  static async getPlaceDetail(name, placeId = null) {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (placeId) params.append('place_id', placeId);

    const res = await fetch(`${API_BASE_URL}/api/v1/kg/places/detail?${params.toString()}`);
    if (!res.ok) throw new Error(`Lỗi tra cứu chi tiết địa điểm (HTTP ${res.status})`);
    return await res.json();
  }
}
