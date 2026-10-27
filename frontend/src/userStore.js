// =============================================================================
// HUẾ SMART TOURISM — USER STORE (WISHLIST, CHECK-IN TRACKER & PREFERENCES)
// Quản lý Địa điểm Yêu thích, Hành trình Check-in (Hộ chiếu Cố Đô) & Gu Du lịch
// =============================================================================

import hueTopPlaces from './hue_top_places.json';

const STORAGE_FAVORITES_KEY = 'hue_user_favorites';
const STORAGE_CHECKINS_KEY = 'hue_user_checkins';
const STORAGE_PREFERENCES_KEY = 'hue_user_travel_preferences';

// Hệ thống cấp bậc Khám phá Cố Đô Huế (Phong cách Tối giản Editorial)
const EXPLORER_RANKS = [
  { min: 0, level: '01', title: 'Khách bộ hành Cố Đô', desc: 'Bắt đầu hành trình khám phá di sản và thắng cảnh' },
  { min: 3, level: '02', title: 'Lữ khách Khám phá', desc: 'Đã đặt chân đến các danh thắng biểu tượng' },
  { min: 8, level: '03', title: 'Người chu du xứ Huế', desc: 'Am tường hệ thống lăng tẩm và ẩm thực truyền thống' },
  { min: 16, level: '04', title: 'Chuyên gia Di sản Cố Đô', desc: 'Hoàn thành chặng đường tìm hiểu văn hóa lịch sử' }
];

export class UserStore {
  constructor() {
    this.totalLandmarksCount = Array.isArray(hueTopPlaces) ? hueTopPlaces.length : 158;
    this._favorites = null;
    this._favSet = new Set();
    this._checkins = null;
    this._checkinSet = new Set();
    this._preferences = null;
    this._initStore();
  }

  _initStore() {
    this._loadFavorites();
    this._loadCheckins();
    this._loadPreferences();

    // Đồng bộ nếu có thay đổi từ tab khác
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (e) => {
        if (e.key === STORAGE_FAVORITES_KEY) {
          this._loadFavorites();
          this.notifyChange('favorites_external', { list: this._favorites });
        } else if (e.key === STORAGE_CHECKINS_KEY) {
          this._loadCheckins();
          this.notifyChange('checkins_external', { list: this._checkins });
        } else if (e.key === STORAGE_PREFERENCES_KEY) {
          this._loadPreferences();
          this.notifyChange('preferences_external', { preferences: this._preferences });
        }
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 1. ĐỊA ĐIỂM YÊU THÍCH (WISHLIST / FAVORITES)
  // ---------------------------------------------------------------------------

  _loadFavorites() {
    try {
      const raw = localStorage.getItem(STORAGE_FAVORITES_KEY);
      this._favorites = raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.warn('Lỗi đọc favorites từ localStorage:', e);
      this._favorites = [];
    }
    this._rebuildFavSet();
    return this._favorites;
  }

  _rebuildFavSet() {
    this._favSet.clear();
    for (const item of (this._favorites || [])) {
      if (item.place_id) this._favSet.add(String(item.place_id).trim().toLowerCase());
      if (item.name) this._favSet.add(String(item.name).trim().toLowerCase());
    }
  }

  getFavorites() {
    if (!this._favorites) {
      this._loadFavorites();
    }
    return this._favorites;
  }

  isFavorite(placeIdOrName) {
    if (!placeIdOrName) return false;
    if (!this._favorites) this._loadFavorites();
    return this._favSet.has(String(placeIdOrName).trim().toLowerCase());
  }

  toggleFavorite(place, note = '') {
    if (!place || !place.name) return { isFav: false, list: this.getFavorites() };

    const list = this.getFavorites();
    const targetName = String(place.name).trim().toLowerCase();
    const targetId = place.place_id ? String(place.place_id).trim().toLowerCase() : null;

    const existingIndex = list.findIndex(item => 
      (targetId && item.place_id && String(item.place_id).trim().toLowerCase() === targetId) ||
      (item.name && String(item.name).trim().toLowerCase() === targetName)
    );

    let isFav = false;
    if (existingIndex >= 0) {
      // Đã có -> Xóa bỏ
      list.splice(existingIndex, 1);
      isFav = false;
    } else {
      // Chưa có -> Thêm vào đầu danh sách
      const newFav = {
        place_id: place.place_id || `fav_${Date.now()}`,
        name: place.name,
        category: place.category || place.cat || 'Attraction',
        address: place.address || place.street_address || place.desc || 'Thành phố Huế',
        latitude: place.latitude || place.lat || null,
        longitude: place.longitude || place.lng || null,
        rating_value: place.rating_value || place.rating || 4.6,
        note: note || '',
        addedAt: new Date().toISOString()
      };
      list.unshift(newFav);
      isFav = true;
    }

    this._rebuildFavSet();

    try {
      localStorage.setItem(STORAGE_FAVORITES_KEY, JSON.stringify(list));
      this.notifyChange('favorites', { isFav, place, list });
    } catch (e) {
      console.error('Lỗi lưu favorites vào localStorage:', e);
    }

    return { isFav, list };
  }

  updateFavoriteNote(placeIdOrName, note) {
    if (!placeIdOrName) return;
    const target = String(placeIdOrName).trim().toLowerCase();
    const list = this.getFavorites();
    const item = list.find(it => 
      (it.place_id && String(it.place_id).trim().toLowerCase() === target) ||
      (it.name && String(it.name).trim().toLowerCase() === target)
    );
    if (item) {
      item.note = note || '';
      item.updatedAt = new Date().toISOString();
      try {
        localStorage.setItem(STORAGE_FAVORITES_KEY, JSON.stringify(list));
        this.notifyChange('favorites_note', { item, list });
      } catch (e) {
        console.error('Lỗi lưu ghi chú:', e);
      }
    }
  }

  removeFavorite(placeIdOrName) {
    if (!placeIdOrName) return this.getFavorites();
    const target = String(placeIdOrName).trim().toLowerCase();
    let list = this.getFavorites();
    list = list.filter(it => 
      (it.place_id && String(it.place_id).trim().toLowerCase() !== target) &&
      (it.name && String(it.name).trim().toLowerCase() !== target)
    );
    this._favorites = list;
    this._rebuildFavSet();

    try {
      localStorage.setItem(STORAGE_FAVORITES_KEY, JSON.stringify(list));
      this.notifyChange('favorites', { isFav: false, list });
    } catch (e) {
      console.error('Lỗi lưu favorites sau khi xóa:', e);
    }
    return list;
  }

  // ---------------------------------------------------------------------------
  // 2. HÀNH TRÌNH CHECK-IN (VISITED PLACES & PASSPORT)
  // ---------------------------------------------------------------------------

  _loadCheckins() {
    try {
      const raw = localStorage.getItem(STORAGE_CHECKINS_KEY);
      this._checkins = raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.warn('Lỗi đọc checkins từ localStorage:', e);
      this._checkins = [];
    }
    this._rebuildCheckinSet();
    return this._checkins;
  }

  _rebuildCheckinSet() {
    this._checkinSet.clear();
    for (const item of (this._checkins || [])) {
      if (item.place_id) this._checkinSet.add(String(item.place_id).trim().toLowerCase());
      if (item.name) this._checkinSet.add(String(item.name).trim().toLowerCase());
    }
  }

  getCheckins() {
    if (!this._checkins) {
      this._loadCheckins();
    }
    return this._checkins;
  }

  isCheckedIn(placeIdOrName) {
    if (!placeIdOrName) return false;
    if (!this._checkins) this._loadCheckins();
    return this._checkinSet.has(String(placeIdOrName).trim().toLowerCase());
  }

  toggleCheckin(place) {
    if (!place || !place.name) return { isChecked: false, list: this.getCheckins() };

    const list = this.getCheckins();
    const targetName = String(place.name).trim().toLowerCase();
    const targetId = place.place_id ? String(place.place_id).trim().toLowerCase() : null;

    const existingIndex = list.findIndex(item => 
      (targetId && item.place_id && String(item.place_id).trim().toLowerCase() === targetId) ||
      (item.name && String(item.name).trim().toLowerCase() === targetName)
    );

    let isChecked = false;
    if (existingIndex >= 0) {
      // Đã check-in -> Hủy check-in
      list.splice(existingIndex, 1);
      isChecked = false;
    } else {
      // Chưa check-in -> Đánh dấu đã ghé thăm
      const newCheckin = {
        place_id: place.place_id || `checkin_${Date.now()}`,
        name: place.name,
        category: place.category || place.cat || 'Attraction',
        address: place.address || place.street_address || place.desc || 'Thành phố Huế',
        latitude: place.latitude || place.lat || null,
        longitude: place.longitude || place.lng || null,
        visitedAt: new Date().toISOString()
      };
      list.unshift(newCheckin);
      isChecked = true;
    }

    this._rebuildCheckinSet();

    try {
      localStorage.setItem(STORAGE_CHECKINS_KEY, JSON.stringify(list));
      this.notifyChange('checkins', { isChecked, place, list, stats: this.getExplorerStats() });
    } catch (e) {
      console.error('Lỗi lưu checkins vào localStorage:', e);
    }

    return { isChecked, list };
  }

  getExplorerStats() {
    const checkins = this.getCheckins();
    const count = checkins.length;
    const total = this.totalLandmarksCount || 158;
    const percentage = Math.min(100, Math.round((count / total) * 100));

    // Tìm cấp bậc hiện tại
    let currentRank = EXPLORER_RANKS[0];
    let nextRank = EXPLORER_RANKS[1];

    for (let i = EXPLORER_RANKS.length - 1; i >= 0; i--) {
      if (count >= EXPLORER_RANKS[i].min) {
        currentRank = EXPLORER_RANKS[i];
        nextRank = EXPLORER_RANKS[i + 1] || null;
        break;
      }
    }

    const remainingForNext = nextRank ? (nextRank.min - count) : 0;

    return {
      count,
      total,
      percentage,
      level: currentRank.level || '01',
      rankTitle: currentRank.title,
      rankDesc: currentRank.desc,
      nextRankTitle: nextRank ? nextRank.title : 'Đạt cấp độ tối đa',
      remainingForNext
    };
  }

  // ---------------------------------------------------------------------------
  // 3. HỒ SƠ GU DU LỊCH & KHẨU VỊ CÁ NHÂN HÓA (TRAVEL PREFERENCES)
  // ---------------------------------------------------------------------------

  getDefaultPreferences() {
    return {
      styles: ['heritage', 'foodie'], // di tích, ẩm thực
      dietary: ['Ăn cay chuẩn Huế'],
      party: 'Cặp đôi',
      transport: 'Xe máy',
      customNotes: ''
    };
  }

  _loadPreferences() {
    try {
      const raw = localStorage.getItem(STORAGE_PREFERENCES_KEY);
      this._preferences = raw ? { ...this.getDefaultPreferences(), ...JSON.parse(raw) } : this.getDefaultPreferences();
    } catch (e) {
      console.warn('Lỗi đọc preferences từ localStorage:', e);
      this._preferences = this.getDefaultPreferences();
    }
    return this._preferences;
  }

  getPreferences() {
    if (!this._preferences) {
      this._loadPreferences();
    }
    return this._preferences;
  }

  savePreferences(prefs) {
    try {
      const merged = { ...this.getPreferences(), ...prefs };
      this._preferences = merged;
      localStorage.setItem(STORAGE_PREFERENCES_KEY, JSON.stringify(merged));
      this.notifyChange('preferences', { preferences: merged });
      return merged;
    } catch (e) {
      console.error('Lỗi lưu preferences vào localStorage:', e);
      return prefs;
    }
  }

  // ---------------------------------------------------------------------------
  // 4. EVENT BROADCASTER (ĐỒNG BỘ GIAO DIỆN REACTIVE)
  // ---------------------------------------------------------------------------

  notifyChange(type, detail) {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('hue-user-store-changed', {
        detail: { type, ...detail }
      });
      window.dispatchEvent(event);
    }
  }
}

// Khởi tạo Singleton UserStore dùng toàn cục
export const userStore = new UserStore();
if (typeof window !== 'undefined') {
  window.userStore = userStore;
}
