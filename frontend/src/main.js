// =============================================================================
// HUẾ SMART TOURISM — MAIN APPLICATION CONTROLLER
// Trực quan hóa Kiến trúc Spatial GraphRAG theo chuẩn Hallmark Editorial
// =============================================================================

import './style.css';
import { TourismApiClient } from './api.js';
import { SpatialMapStudio } from './map.js';
import { AuthController } from './auth.js';
import { userStore } from './userStore.js';
import {
  saveItinerary,
  saveChatSession,
  getUserChatSessions,
  deleteChatSession,
  submitAiFeedback,
  onAuthChange,
  logoutUser,
  loginWithDemoUser
} from './firebase.js';
import { HueWeatherService } from './weather.js';
import { budgetEstimator } from './budgetEstimator.js';
import { i18n } from './i18n.js';

document.addEventListener('DOMContentLoaded', async () => {
  const escapeHtml = (str) => String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const inferContextFromPlace = (place) => {
    const cat = String(place?.category || '').toLowerCase();
    const isFood = cat.includes('restaurant') || cat.includes('cafe') || cat.includes('ẩm thực') || cat.includes('quán');
    const isHotel = cat.includes('hotel') || cat.includes('khách sạn') || cat.includes('homestay') || cat.includes('resort');
    return {
      anchor_place_id: place?.place_id || place?.node_id || null,
      anchor_place_label: place?.name || '',
      anchor_place_kind: isFood ? 'food' : (isHotel ? 'lodging' : 'site'),
      topic_domain: isFood ? 'culinary' : 'heritage',
      turn_count: 1
    };
  };

  // Khởi tạo công cụ Dự toán Ngân sách Du lịch Cố Đô Huế
  budgetEstimator.init();
  window.budgetEstimator = budgetEstimator;
  // 0. KHỞI TẠO HỆ THỐNG XÁC THỰC (AUTH CONTROLLER - GOOGLE GMAIL & EMAIL)
  const authController = new AuthController();
  authController.init();
  window.authController = authController;

  // 1. KHỞI TẠO BẢN ĐỒ KHÔNG GIAN
  const mapStudio = new SpatialMapStudio('map-container');
  mapStudio.init();
  window.mapStudio = mapStudio;

  // 2. KIỂM TRA TRẠNG THÁI FASTAPI BACKEND (CHẠY NGẦM, KHÔNG ÉP HIỂN THỊ PILL)
  const statusPill = document.getElementById('system-status-pill');
  const statusLabel = document.getElementById('status-label');
  const statusDot = statusPill?.querySelector('.status-dot');

  async function checkBackendStatus() {
    try {
      const health = await TourismApiClient.checkHealth();
      if (health.status === 'healthy') {
        if (statusDot) statusDot.className = 'status-dot pulse';
        if (statusLabel) statusLabel.textContent = i18n.t('online', 'Trực tuyến');
        if (statusPill) statusPill.title = i18n.t('systemOperating', 'Hệ thống đang hoạt động');
      } else {
        throw new Error('Offline');
      }
    } catch {
      if (statusDot) statusDot.className = 'status-dot error';
      if (statusLabel) statusLabel.textContent = i18n.t('offline', 'Ngoại tuyến');
      if (statusPill) statusPill.title = i18n.t('cannotConnectServer', 'Không thể kết nối máy chủ');
    }
  }
  await checkBackendStatus();

  // ===========================================================================
  // 2.5 HƯỚNG 1: BẢN ĐỒ THÍCH ỨNG THEO NGỮ CẢNH (CONTEXT-AWARE DYNAMIC MAP)
  // Chatbot là trung tâm chính (Hero), Bản đồ tự động mở khi có câu hỏi/tác vụ không gian
  // ===========================================================================
  const studioLayout = document.querySelector('.studio-layout');
  const btnHeaderToggleMap = document.getElementById('btn-header-toggle-map');
  const headerMapToggleLabel = document.getElementById('header-map-toggle-label');
  const btnWorkbenchToggleMap = document.getElementById('btn-workbench-toggle-map');
  const btnCloseMapPanel = document.getElementById('btn-close-map-panel');

  function updateMapToggleUI(isOpen) {
    if (btnHeaderToggleMap) {
      btnHeaderToggleMap.classList.toggle('active', isOpen);
      btnHeaderToggleMap.title = isOpen ? i18n.t('mapToggleClose', 'Thu gọn Bản đồ') : i18n.t('mapToggleOpen', 'Mở Bản đồ');
      if (headerMapToggleLabel) {
        headerMapToggleLabel.textContent = isOpen ? i18n.t('mapToggleClose', 'Thu gọn Bản đồ') : i18n.t('mapToggleOpen', 'Mở Bản đồ');
      }
    }
    if (btnWorkbenchToggleMap) {
      btnWorkbenchToggleMap.classList.toggle('active', isOpen);
      btnWorkbenchToggleMap.title = isOpen ? i18n.t('mapToggleClose', 'Thu gọn bản đồ') : i18n.t('mapToggleOpen', 'Mở bản đồ');
    }
  }

  function showMapPanel(animate = true) {
    if (!studioLayout) return;
    if (studioLayout.classList.contains('map-collapsed')) {
      studioLayout.classList.remove('map-collapsed');
      updateMapToggleUI(true);
      setTimeout(() => {
        if (mapStudio && mapStudio.map) {
          mapStudio.map.invalidateSize({ animate });
        }
      }, 380);
    } else {
      // Đã mở, vẫn đảm bảo kích thước canvas luôn chuẩn xác
      if (mapStudio && mapStudio.map) {
        mapStudio.map.invalidateSize({ animate: false });
      }
    }
  }

  function hideMapPanel() {
    if (!studioLayout) return;
    if (!studioLayout.classList.contains('map-collapsed')) {
      studioLayout.classList.add('map-collapsed');
      updateMapToggleUI(false);
    }
  }

  function toggleMapPanel() {
    if (!studioLayout) return;
    if (studioLayout.classList.contains('map-collapsed')) {
      showMapPanel(true);
    } else {
      hideMapPanel();
    }
  }

  btnHeaderToggleMap?.addEventListener('click', toggleMapPanel);
  btnWorkbenchToggleMap?.addEventListener('click', toggleMapPanel);
  btnCloseMapPanel?.addEventListener('click', hideMapPanel);

  // Tự động căn chỉnh kích thước bản đồ khi xoay điện thoại hoặc thay đổi kích thước cửa sổ
  window.addEventListener('resize', () => {
    if (mapStudio && mapStudio.map) {
      mapStudio.map.invalidateSize({ animate: false });
    }
  }, { passive: true });

  // Khởi tạo trạng thái nút toggle theo layout ban đầu
  const isInitiallyMapOpen = !studioLayout?.classList.contains('map-collapsed');
  updateMapToggleUI(isInitiallyMapOpen);

  // 3. BỘ ĐIỀU KHIỂN TÁC VỤ AI (QUICK PLANNER COLLAPSIBLE & CHAT SYNC)
  const quickPlannerCard = document.getElementById('quick-planner-card');
  const btnTogglePlanner = document.getElementById('btn-toggle-planner');
  const btnClosePlanner = document.getElementById('btn-close-planner');
  const chipPlan2Days = document.getElementById('chip-plan-2days');

  function updatePlannerOriginDisplay() {
    const originEl = document.getElementById('planner-origin-name');
    if (!originEl) return;
    if (mapStudio.userLocation && mapStudio.userLocation.name) {
      const locName = mapStudio.userLocation.name;
      if (locName.includes('Vị trí') || locName.toLowerCase().includes('your location')) {
        originEl.textContent = i18n.t('userLocationHere', 'Vị trí hiện tại của bạn');
      } else {
        originEl.textContent = locName;
      }
    } else {
      originEl.textContent = i18n.t('userLocationHere', 'Vị trí hiện tại của bạn');
    }
  }

  function togglePlanner(show) {
    if (!quickPlannerCard) return;
    const isHidden = quickPlannerCard.hasAttribute('hidden');
    const shouldShow = typeof show === 'boolean' ? show : isHidden;

    if (shouldShow) {
      showMapPanel(true); // Tự động mở bản đồ khi bắt đầu tạo lịch trình
      updatePlannerOriginDisplay();
      quickPlannerCard.removeAttribute('hidden');
      btnTogglePlanner?.classList.add('active');
      btnTogglePlanner?.setAttribute('aria-expanded', 'true');
      quickPlannerCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      quickPlannerCard.setAttribute('hidden', '');
      btnTogglePlanner?.classList.remove('active');
      btnTogglePlanner?.setAttribute('aria-expanded', 'false');
    }
  }

  btnTogglePlanner?.addEventListener('click', () => togglePlanner());
  btnClosePlanner?.addEventListener('click', () => togglePlanner(false));
  chipPlan2Days?.addEventListener('click', () => {
    togglePlanner(true);
    const selDays = document.getElementById('select-days');
    if (selDays) selDays.value = '2';
  });

  const btnRefreshOrigin = document.getElementById('btn-refresh-origin');
  btnRefreshOrigin?.addEventListener('click', () => {
    locateUserPosition(false);
  });

  // 4. MAP STUDIO TOOLBAR, SEARCH & FILTER CONTROLS
  const btnResetMap = document.getElementById('btn-reset-map');
  const btnLocateUser = document.getElementById('btn-locate-user');
  const selectMapStyle = document.getElementById('select-map-style');
  const mapActiveMeta = document.getElementById('map-active-meta');
  const filterChips = document.querySelectorAll('.filter-chip');
  const mapSearchInput = document.getElementById('map-search-input');
  const mapSearchDropdown = document.getElementById('map-search-dropdown');
  const btnClearSearch = document.getElementById('btn-clear-search');

  // Định vị GPS người dùng (HTML5 Geolocation với Fallback Cầu Tràng Tiền)
  function locateUserPosition(silent = false) {
    if (!navigator.geolocation) {
      if (!silent) {
        alert(i18n.t('geoNotSupported', 'Trình duyệt của bạn không hỗ trợ Geolocation API.'));
      }
      return;
    }

    if (!silent) {
      btnLocateUser?.classList.add('loading');
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        btnLocateUser?.classList.remove('loading');
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        // Kiểm tra xem vị trí có nằm trong hoặc gần tỉnh Thừa Thiên Huế (15.8 - 16.8 N, 107.0 - 108.3 E)
        const isNearHue = (lat >= 15.8 && lat <= 16.8 && lng >= 107.0 && lng <= 108.3);
        const locName = isNearHue ? i18n.t('userLocationHere', 'Vị trí hiện tại của bạn') : i18n.t('userLocationOutside', 'Vị trí của bạn (Ngoài Huế)');

        mapStudio.setUserLocation(lat, lng, locName);
        updatePlannerOriginDisplay();
        if (!silent) {
          mapStudio.panTo(lat, lng, 16);
          btnLocateUser?.classList.add('active');
        }
        btnLocateUser.title = `${i18n.t('gpsBadge', 'Đã định vị')}: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
      },
      (err) => {
        btnLocateUser?.classList.remove('loading');
        console.warn('Geolocation error or denied:', err);
        const defaultHueLat = 16.4674;
        const defaultHueLng = 107.5905;
        mapStudio.setUserLocation(defaultHueLat, defaultHueLng, i18n.t('defaultHueCenter', 'Cầu Tràng Tiền (Trung tâm Huế)'));
        updatePlannerOriginDisplay();

        if (!silent) {
          mapStudio.panTo(defaultHueLat, defaultHueLng, 16);
          btnLocateUser?.classList.add('active');
          btnLocateUser.title = `${i18n.t('defaultHueCenter', 'Cầu Tràng Tiền, Huế')}`;
          alert(i18n.t('geoDenied', 'Không thể lấy vị trí thực tế của bạn (trình duyệt chặn hoặc chưa cấp quyền). Hệ thống đã đặt vị trí xuất phát mặc định tại Cầu Tràng Tiền, trung tâm Huế!'));
        }
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
    );
  }

  btnLocateUser?.addEventListener('click', () => {
    locateUserPosition(false);
  });

  // Tự động định vị vị trí người dùng ở chế độ im lặng khi vừa vào ứng dụng (không di chuyển map hoặc highlight nút)
  setTimeout(() => {
    locateUserPosition(true);
  }, 1200);

  // Đổi phong cách bản đồ (Google Maps / Vệ Tinh)
  selectMapStyle?.addEventListener('change', (e) => {
    mapStudio.setMapStyle(e.target.value);
  });

  function getCategoryTitle(cat) {
    const isEn = typeof i18n !== 'undefined' && i18n.currentLang === 'en';
    const titles = {
      all: isEn ? 'Heritage Map' : 'Bản đồ Di sản',
      attraction: isEn ? 'Imperial Monuments' : 'Di tích Cố đô',
      restaurant: isEn ? 'Hue Cuisine' : 'Ẩm thực Cố đô',
      cafe: isEn ? 'Cafe & Sunset' : 'Cà phê & Sunset',
      hotel: isEn ? 'Hotels & Resorts' : 'Khách sạn & Resort'
    };
    return titles[cat] || (isEn ? 'Imperial Locations' : 'Địa điểm Cố đô');
  }

  // Xử lý click chọn bộ lọc danh mục
  filterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.category;
      filterChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      mapStudio.filterByCategory(cat);
      if (mapActiveMeta) {
        const title = getCategoryTitle(cat);
        mapActiveMeta.textContent = title;
        mapActiveMeta.title = title;
      }
    });
  });

  // Đặt lại góc nhìn bản đồ trung tâm và khôi phục bộ lọc
  btnResetMap?.addEventListener('click', () => {
    mapStudio.resetView();
    filterChips.forEach(c => {
      if (c.dataset.category === 'all') c.classList.add('active');
      else c.classList.remove('active');
    });
    if (mapActiveMeta) {
      const title = getCategoryTitle('all');
      mapActiveMeta.textContent = title;
      mapActiveMeta.title = title;
    }
    btnLocateUser?.classList.remove('active');
    if (mapSearchInput) {
      mapSearchInput.value = '';
      if (btnClearSearch) btnClearSearch.style.display = 'none';
    }
    if (mapSearchDropdown) mapSearchDropdown.style.display = 'none';
  });

  // Bật/tắt chế độ Bản đồ Toàn cảnh (Thu gọn / Mở rộng bảng điều khiển bên phải)
  const btnToggleWorkbench = document.getElementById('btn-toggle-workbench');
  const workbenchToggleText = document.getElementById('workbench-toggle-text');

  btnToggleWorkbench?.addEventListener('click', () => {
    if (!studioLayout) return;
    const isCollapsed = studioLayout.classList.toggle('workbench-collapsed');
    btnToggleWorkbench.classList.toggle('active', isCollapsed);
    const isEn = typeof i18n !== 'undefined' && i18n.currentLang === 'en';
    if (workbenchToggleText) {
      workbenchToggleText.textContent = isCollapsed
        ? (isEn ? 'Show Assistant' : 'Hiện trợ lý')
        : (isEn ? 'Overview' : 'Toàn cảnh');
    }
    btnToggleWorkbench.title = isCollapsed
      ? (isEn ? 'Reopen assistant & itinerary panel' : 'Mở lại bảng trợ lý & lịch trình bên phải')
      : (isEn ? 'Collapse assistant panel for full map' : 'Thu gọn bảng trợ lý để xem bản đồ toàn cảnh');

    // Đợi transition CSS kết thúc rồi cập nhật lại Leaflet Map Viewport
    setTimeout(() => {
      if (mapStudio && mapStudio.map) {
        mapStudio.map.invalidateSize({ animate: true });
      }
    }, 360);
  });

  // Xử lý ô Tìm kiếm nhanh với Autocomplete Dropdown
  function renderSearchResults(results) {
    if (!mapSearchDropdown) return;
    const isEn = typeof i18n !== 'undefined' && i18n.currentLang === 'en';
    if (results.length === 0) {
      const emptyText = typeof i18n !== 'undefined'
        ? i18n.t('mapNoSearchResult', 'Không tìm thấy địa điểm phù hợp với từ khóa')
        : 'Không tìm thấy địa điểm phù hợp với từ khóa';
      mapSearchDropdown.innerHTML = `
        <div class="search-empty-item">
          ${emptyText}
        </div>
      `;
      mapSearchDropdown.style.display = 'block';
      return;
    }

    const iconMap = {
      attraction: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/></svg>`,
      restaurant: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 2v8a3 3 0 0 1-6 0V2M15 10v12M6 2v20M3 2h6"/></svg>`,
      cafe: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/></svg>`,
      hotel: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/></svg>`
    };

    const catLabelMap = {
      attraction: isEn ? 'Monuments' : 'Di tích',
      restaurant: isEn ? 'Cuisine' : 'Ẩm thực',
      cafe: isEn ? 'Cafe' : 'Cà phê',
      hotel: isEn ? 'Hotels' : 'Khách sạn'
    };

    mapSearchDropdown.innerHTML = results.slice(0, 8).map(item => {
      const cat = (item.cat || '').toLowerCase();
      const icon = iconMap[cat] || `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>`;
      const catLabel = catLabelMap[cat] || item.cat;
      return `
        <div class="search-result-item" data-name="${item.name}">
          <div class="result-main">
            <div class="result-icon-badge ${cat}">${icon}</div>
            <div class="result-texts">
              <span class="result-name">${item.name}</span>
              <span class="result-desc">${item.desc}</span>
            </div>
          </div>
          <span class="result-cat-tag ${cat}">${catLabel}</span>
        </div>
      `;
    }).join('');

    mapSearchDropdown.style.display = 'block';

    mapSearchDropdown.querySelectorAll('.search-result-item').forEach(el => {
      el.addEventListener('click', () => {
        const name = el.dataset.name;
        mapSearchInput.value = name;
        mapSearchDropdown.style.display = 'none';
        if (btnClearSearch) btnClearSearch.style.display = 'flex';
        mapStudio.flyToPoi(name);
        if (window.openPoiDetail) {
          window.openPoiDetail(name);
        }
      });
    });
  }

  mapSearchInput?.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    if (!val) {
      mapSearchDropdown.style.display = 'none';
      if (btnClearSearch) btnClearSearch.style.display = 'none';
      return;
    }
    if (btnClearSearch) btnClearSearch.style.display = 'flex';
    const matches = mapStudio.searchLandmarks(val);
    renderSearchResults(matches);
  });

  mapSearchInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const firstItem = mapSearchDropdown?.querySelector('.search-result-item');
      if (firstItem) {
        firstItem.click();
      }
    } else if (e.key === 'Escape') {
      if (mapSearchDropdown) mapSearchDropdown.style.display = 'none';
    }
  });

  btnClearSearch?.addEventListener('click', () => {
    mapSearchInput.value = '';
    btnClearSearch.style.display = 'none';
    if (mapSearchDropdown) mapSearchDropdown.style.display = 'none';
    mapSearchInput.focus();
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.map-search-wrapper')) {
      if (mapSearchDropdown) mapSearchDropdown.style.display = 'none';
    }
  });

  // 5. CHỌN MÓN ĂN ƯU TIÊN (DISH TAG CLOUD)
  const dishTags = document.querySelectorAll('.dish-tag');
  dishTags.forEach(tag => {
    tag.addEventListener('click', () => {
      tag.classList.toggle('active');
    });
  });

  function getSelectedDishes() {
    const activeTags = document.querySelectorAll('.dish-tag.active');
    return Array.from(activeTags).map(t => t.dataset.dish);
  }

  // 6. LẬP LỊCH TRÌNH TOUR VÀO LUỒNG CHAT (INTERACTIVE ITINERARY STREAM)
  const formItinerary = document.getElementById('form-itinerary');
  const btnGenItinerary = document.getElementById('btn-generate-itinerary');
  const selectDays = document.getElementById('select-days');
  const selectTripType = document.getElementById('select-trip-type');

  async function getUserCoordinates() {
    if (mapStudio.userLocation && mapStudio.userLocation.lat && mapStudio.userLocation.lng) {
      return {
        lat: mapStudio.userLocation.lat,
        lng: mapStudio.userLocation.lng,
        name: mapStudio.userLocation.name || i18n.t('userLocationHere', 'Vị trí hiện tại của bạn')
      };
    }

    if (navigator.geolocation) {
      try {
        const pos = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 2500,
            maximumAge: 60000
          });
        });
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const isNearHue = (lat >= 15.8 && lat <= 16.8 && lng >= 107.0 && lng <= 108.3);
        const locName = isNearHue
          ? i18n.t('userLocationHere', 'Vị trí hiện tại của bạn')
          : i18n.t('userLocationOutside', 'Vị trí của bạn (Ngoài Huế)');
        mapStudio.setUserLocation(lat, lng, locName);
        updatePlannerOriginDisplay();
        return { lat, lng, name: locName };
      } catch (e) {
        console.info('Không lấy được GPS tức thời, sử dụng vị trí mặc định Huế:', e);
      }
    }

    // Fallback trung tâm Huế (Cầu Tràng Tiền)
    const defLat = 16.4674;
    const defLng = 107.5905;
    const defName = i18n.t('defaultHueCenter', 'Cầu Tràng Tiền (Trung tâm Huế)');
    mapStudio.setUserLocation(defLat, defLng, defName);
    updatePlannerOriginDisplay();
    return { lat: defLat, lng: defLng, name: defName };
  }

  async function generateItineraryInChat(days, tripType, preferredDishes) {
    showMapPanel(true); // Tự động mở bản đồ khi tạo lịch trình
    const coords = await getUserCoordinates();
    const userLat = coords.lat;
    const userLng = coords.lng;
    const isEn = i18n.getLanguage() === 'en';

    let userLocName = coords.name;
    if (isEn && (userLocName.includes('Vị trí') || userLocName.toLowerCase().includes('your location'))) {
      userLocName = 'your current location';
    } else if (!isEn && (userLocName.toLowerCase().includes('your location') || userLocName.toLowerCase().includes('starting point'))) {
      userLocName = 'Vị trí hiện tại của bạn';
    }

    const activeTags = document.querySelectorAll('.dish-tag.active');
    const displayDishes = (isEn && activeTags.length > 0)
      ? Array.from(activeTags).map(t => t.textContent.trim())
      : preferredDishes;

    let dishLabel = '';
    if (displayDishes && displayDishes.length > 0) {
      dishLabel = isEn ? `prioritizing dishes: ${displayDishes.join(', ')}` : `ưu tiên các món: ${displayDishes.join(', ')}`;
    } else {
      dishLabel = isEn ? 'authentic Imperial specialties' : 'ẩm thực Cố đô đặc sắc';
    }

    const userQueryText = isEn
      ? `📅 Plan a ${days}-day Hue travel itinerary for ${tripType}, starting from ${userLocName}, ${dishLabel}.`
      : `📅 Lập lịch trình khám phá Huế ${days} ngày cho ${tripType}, xuất phát từ ${userLocName}, ${dishLabel}.`;
    lastUserPrompt = userQueryText;
    appendUserMessage(userQueryText);

    // Thu gọn quick planner card
    togglePlanner(false);

    const loadingText = isEn
      ? `Optimizing ${days}-day itinerary from ${userLocName}, connecting local dining and mapping routes...`
      : `Đang tối ưu hóa hành trình ${days} ngày xuất phát từ ${userLocName}, kết nối ẩm thực và vẽ lộ trình...`;
    const loadingId = appendAssistantLoading(loadingText);

    if (btnGenItinerary) {
      btnGenItinerary.classList.add('loading');
      btnGenItinerary.disabled = true;
    }

    try {
      const userPrefs = userStore.getPreferences ? userStore.getPreferences() : null;
      const res = await TourismApiClient.generateItinerary(days, preferredDishes, tripType, userLat, userLng, userPrefs);
      removeLoadingMessage(loadingId);
      appendItineraryDeckMessage(res, days, tripType, preferredDishes, userLocName);
    } catch (err) {
      removeLoadingMessage(loadingId);
      const errMsg = isEn ? `Could not create itinerary: ${err.message}. Please try again.` : `Không thể tạo lịch trình: ${err.message}. Vui lòng thử lại.`;
      appendAssistantError(errMsg);
    } finally {
      if (btnGenItinerary) {
        btnGenItinerary.classList.remove('loading');
        btnGenItinerary.disabled = false;
      }
      if (chatInput) chatInput.focus();
    }
  }

  formItinerary?.addEventListener('submit', (e) => {
    e.preventDefault();
    const days = parseInt(selectDays?.value, 10) || 2;
    const tripType = selectTripType?.value || 'Couples';
    const preferredDishes = getSelectedDishes();
    generateItineraryInChat(days, tripType, preferredDishes);
  });

  // Quản lý trạng thái phiên chat toàn cục
  let activeSessionId = 'session_' + Date.now();
  let activeSessionTitle = (typeof i18n !== 'undefined' && i18n.getLanguage() === 'en') ? 'New Chat' : 'Cuộc trò chuyện mới';
  let activeSessionMessages = [];
  let activeSessionContext = null;
  let isRestoringSession = false;
  let lastUserPrompt = '';

  // =============================================================================
  // THU THẬP PHẢN HỒI AI (AI FEEDBACK SYSTEM: LIKE / DISLIKE / COPY)
  // Ghi nhận phản hồi người dùng phục vụ đánh giá thực nghiệm & RLHF
  // =============================================================================
  function createFeedbackBarHtml(messageId, existingRating = null) {
    const hintText = typeof i18n !== 'undefined' ? i18n.t('feedbackHint', 'Đánh giá câu trả lời:') : 'Đánh giá câu trả lời:';
    const copyText = typeof i18n !== 'undefined' ? i18n.t('feedbackCopy', 'Sao chép') : 'Sao chép';
    const regenText = typeof i18n !== 'undefined' ? i18n.t('feedbackRegenerate', 'Tạo lại') : 'Tạo lại';
    const regenTitle = typeof i18n !== 'undefined' ? i18n.t('feedbackRegenerateTooltip', 'Tạo lại câu trả lời') : 'Tạo lại câu trả lời';
    const likeText = typeof i18n !== 'undefined' ? i18n.t('feedbackLike', 'Hữu ích') : 'Hữu ích';
    const dislikeText = typeof i18n !== 'undefined' ? i18n.t('feedbackDislike', 'Chưa tốt') : 'Chưa tốt';
    const dislikeTitle = typeof i18n !== 'undefined' ? i18n.t('feedbackDislikeTitle', 'Lý do bạn chưa hài lòng:') : 'Lý do bạn chưa hài lòng:';
    const reasonIncorrect = typeof i18n !== 'undefined' ? i18n.t('feedbackReasonIncorrect', 'Thông tin chưa chính xác') : 'Thông tin chưa chính xác';
    const reasonIrrelevant = typeof i18n !== 'undefined' ? i18n.t('feedbackReasonIrrelevant', 'Chưa đúng trọng tâm câu hỏi') : 'Chưa đúng trọng tâm câu hỏi';
    const reasonLocation = typeof i18n !== 'undefined' ? i18n.t('feedbackReasonLocation', 'Địa điểm/Lộ trình chưa hợp lý') : 'Địa điểm/Lộ trình chưa hợp lý';
    const reasonOther = typeof i18n !== 'undefined' ? i18n.t('feedbackReasonOther', 'Khác') : 'Khác';
    const commentPlaceholder = typeof i18n !== 'undefined' ? i18n.t('feedbackCommentPlaceholder', 'Góp ý chi tiết để AI cải thiện tốt hơn...') : 'Góp ý chi tiết để AI cải thiện tốt hơn...';
    const submitText = typeof i18n !== 'undefined' ? i18n.t('feedbackSubmitBtn', 'Gửi') : 'Gửi';
    const closeTitle = typeof i18n !== 'undefined' ? i18n.t('closeModal', 'Đóng') : 'Đóng';

    return `
      <div class="message-feedback-row" data-message-id="${messageId}">
        <div class="feedback-actions">
          <span class="feedback-hint">${hintText}</span>
          <button type="button" class="btn-msg-feedback btn-copy-msg" title="${copyText}" aria-label="${copyText}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span class="copy-label">${copyText}</span>
          </button>
          <button type="button" class="btn-msg-feedback btn-regenerate-msg" title="${regenTitle}" aria-label="${regenTitle}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12a9 9 0 1 1-2.64-6.36"></path>
              <polyline points="21 3 21 9 15 9"></polyline>
            </svg>
            <span>${regenText}</span>
          </button>
          <button type="button" class="btn-msg-feedback btn-feedback-like ${existingRating === 'like' ? 'active' : ''}" title="${likeText}" aria-label="${likeText}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
            </svg>
            <span>${likeText}</span>
          </button>
          <button type="button" class="btn-msg-feedback btn-feedback-dislike ${existingRating === 'dislike' ? 'active' : ''}" title="${dislikeText}" aria-label="${dislikeText}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path>
            </svg>
            <span>${dislikeText}</span>
          </button>
        </div>

        <div class="feedback-dislike-box hidden">
          <div class="feedback-dislike-title">${dislikeTitle}</div>
          <div class="feedback-chips">
            <button type="button" class="feedback-chip active" data-reason="incorrect">${reasonIncorrect}</button>
            <button type="button" class="feedback-chip" data-reason="irrelevant">${reasonIrrelevant}</button>
            <button type="button" class="feedback-chip" data-reason="location">${reasonLocation}</button>
            <button type="button" class="feedback-chip" data-reason="other">${reasonOther}</button>
          </div>
          <div class="feedback-input-row">
            <input type="text" class="feedback-comment-input" placeholder="${commentPlaceholder}" />
            <button type="button" class="btn-submit-feedback">${submitText}</button>
            <button type="button" class="btn-cancel-feedback" title="${closeTitle}">✕</button>
          </div>
        </div>
      </div>
    `;
  }

  function bindFeedbackEvents(container, meta) {
    const row = container.querySelector('.message-feedback-row');
    if (!row) return;

    const likeBtn = row.querySelector('.btn-feedback-like');
    const dislikeBtn = row.querySelector('.btn-feedback-dislike');
    const copyBtn = row.querySelector('.btn-copy-msg');
    const dislikeBox = row.querySelector('.feedback-dislike-box');
    const chips = row.querySelectorAll('.feedback-chip');
    const commentInput = row.querySelector('.feedback-comment-input');
    const submitBtn = row.querySelector('.btn-submit-feedback');
    const cancelBtn = row.querySelector('.btn-cancel-feedback');

    let selectedReason = 'incorrect';

    // "Tạo lại": gửi lại đúng câu hỏi gốc, KÈM ẢNH GỐC nếu câu hỏi đó có ảnh.
    // Truyền attachment tường minh để không vô tình dùng ảnh đang chờ gửi ở ô nhập.
    const regenerateBtn = row.querySelector('.btn-regenerate-msg');
    regenerateBtn?.addEventListener('click', () => {
      const chatSendButton = document.getElementById('chat-send-btn');
      if (!meta.prompt || chatSendButton?.disabled) return;
      sendChatQuery(meta.prompt, {
        image: meta.imageBase64 || null,
        storageThumb: meta.storageThumb || null
      });
    });

    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        selectedReason = chip.dataset.reason;
      });
    });

    copyBtn?.addEventListener('click', async () => {
      try {
        const textToCopy = meta.plainText || container.querySelector('.answer-content')?.innerText || container.innerText || '';
        await navigator.clipboard.writeText(textToCopy);
        const copyLabel = copyBtn.querySelector('.copy-label');
        if (copyLabel) copyLabel.textContent = typeof i18n !== 'undefined' ? i18n.t('feedbackCopied', 'Đã chép!') : 'Đã chép!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          if (copyLabel) copyLabel.textContent = typeof i18n !== 'undefined' ? i18n.t('feedbackCopy', 'Sao chép') : 'Sao chép';
          copyBtn.classList.remove('copied');
        }, 2000);
      } catch (e) {
        console.warn('Không thể sao chép văn bản:', e);
      }
    });

    likeBtn?.addEventListener('click', async () => {
      if (likeBtn.classList.contains('active')) return;
      likeBtn.classList.add('active');
      dislikeBtn.classList.remove('active');
      if (dislikeBox) dislikeBox.classList.add('hidden');

      updateMessageFeedbackInSession(meta.messageId, 'like');

      await submitAiFeedback({
        messageId: meta.messageId,
        sessionId: activeSessionId,
        rating: 'like',
        prompt: meta.prompt || '',
        responseExcerpt: (meta.plainText || '').substring(0, 300),
        isItinerary: Boolean(meta.isItinerary)
      });

      authController.showToast(typeof i18n !== 'undefined' ? i18n.t('feedbackLikeRecordedToast', 'Cảm ơn bạn! Đánh giá hữu ích đã được ghi nhận.') : 'Cảm ơn bạn! Đánh giá hữu ích đã được ghi nhận.');
    });

    dislikeBtn?.addEventListener('click', async () => {
      if (dislikeBtn.classList.contains('active')) {
        dislikeBox?.classList.toggle('hidden');
        return;
      }
      dislikeBtn.classList.add('active');
      likeBtn.classList.remove('active');
      if (dislikeBox) {
        dislikeBox.classList.remove('hidden');
        commentInput?.focus();
      }

      updateMessageFeedbackInSession(meta.messageId, 'dislike');

      await submitAiFeedback({
        messageId: meta.messageId,
        sessionId: activeSessionId,
        rating: 'dislike',
        reason: selectedReason,
        prompt: meta.prompt || '',
        responseExcerpt: (meta.plainText || '').substring(0, 300),
        isItinerary: Boolean(meta.isItinerary)
      });

      authController.showToast(typeof i18n !== 'undefined' ? i18n.t('feedbackRecordedToast', 'Đã ghi nhận! Bạn có thể chọn lý do góp ý bên dưới.') : 'Đã ghi nhận! Bạn có thể chọn lý do góp ý bên dưới.');
    });

    cancelBtn?.addEventListener('click', () => {
      if (dislikeBox) dislikeBox.classList.add('hidden');
    });

    submitBtn?.addEventListener('click', async () => {
      const comment = commentInput?.value?.trim() || '';
      submitBtn.disabled = true;
      submitBtn.textContent = '...';

      await submitAiFeedback({
        messageId: meta.messageId,
        sessionId: activeSessionId,
        rating: 'dislike',
        reason: selectedReason,
        comment: comment,
        prompt: meta.prompt || '',
        responseExcerpt: (meta.plainText || '').substring(0, 300),
        isItinerary: Boolean(meta.isItinerary)
      });

      updateMessageFeedbackInSession(meta.messageId, 'dislike', selectedReason, comment);

      if (dislikeBox) {
        const thanksNote = typeof i18n !== 'undefined' ? i18n.t('feedbackThanksDetailed', 'Cảm ơn đóng góp của bạn! Phản hồi này sẽ dùng để hoàn thiện mô hình AI.') : 'Cảm ơn đóng góp của bạn! Phản hồi này sẽ dùng để hoàn thiện mô hình AI.';
        dislikeBox.innerHTML = `
          <div class="feedback-thankyou-note">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span>${thanksNote}</span>
          </div>
        `;
      }
      authController.showToast(typeof i18n !== 'undefined' ? i18n.t('ratingThanksToast', 'Đã gửi phản hồi thành công!') : 'Đã gửi phản hồi thành công!');
    });
  }

  function updateMessageFeedbackInSession(messageId, rating, reason = '', comment = '') {
    if (!messageId || !activeSessionMessages) return;
    const targetMsg = activeSessionMessages.find(m => m.id === messageId || m.messageId === messageId);
    if (targetMsg) {
      targetMsg.feedbackRating = rating;
      if (reason) targetMsg.feedbackReason = reason;
      if (comment) targetMsg.feedbackComment = comment;
      persistActiveSession();
    }
  }

  function appendItineraryDeckMessage(res, days, tripType, preferredDishes, userLocName = null, persist = true, customDeckId = null, existingRating = null) {
    const isEn = i18n.getLanguage() === 'en';
    let cleanLocName = userLocName;
    if (isEn) {
      if (!cleanLocName || cleanLocName.includes('Vị trí') || cleanLocName.toLowerCase().includes('your location')) {
        cleanLocName = 'your current location';
      }
    } else {
      if (!cleanLocName || cleanLocName.toLowerCase().includes('your location')) {
        cleanLocName = 'Vị trí hiện tại của bạn';
      }
    }
    userLocName = cleanLocName;
    const plan = res.itinerary_data;
    if (!plan || !plan.days || plan.days.length === 0) {
      appendAssistantError(isEn ? 'No suitable itinerary data found for the selected criteria.' : 'Không tìm thấy dữ liệu lịch trình phù hợp với tiêu chí đã chọn.');
      return;
    }

    const deckId = customDeckId || `deck-${Date.now()}`;
    const allStopsForMap = [];
    let totalStopsCount = 0;
    let totalTripDistanceKm = 0;
    let hasUserOrigin = false;

    plan.days.forEach(day => {
      const slots = day.slots || day.stops || [];
      totalStopsCount += slots.length;
      if (day.total_distance_km) totalTripDistanceKm += day.total_distance_km;

      slots.forEach(slot => {
        const isFood = (slot.category || '').toLowerCase().includes('restaurant') ||
          (slot.category || '').toLowerCase().includes('quán') ||
          (slot.activity_type || '').toLowerCase().includes('ẩm thực');
        const isUserLoc = (slot.category || '').toLowerCase().includes('userlocation') ||
          (slot.activity_type || '').toLowerCase().includes('khởi hành');

        // Chỉ cho phép điểm xuất phát người dùng xuất hiện 1 lần duy nhất ở đầu hành trình
        if (isUserLoc) {
          if (hasUserOrigin) return;
          hasUserOrigin = true;
        }

        const lat = slot.latitude || slot.lat;
        const lng = slot.longitude || slot.lng;
        if (lat && lng) {
          allStopsForMap.push({
            lat, lng,
            name: slot.place_name || slot.name,
            category: isUserLoc ? 'UserLocation' : (slot.category || (isFood ? 'Restaurant' : 'Attraction')),
            address: slot.address || '',
            place_id: slot.place_id || slot.placeId
          });
        }
      });
    });

    // Tạo HTML cho Day Tabs
    let dayTabsHtml = '';
    let dayContentsHtml = '';

    const dayColors = {
      1: '#18181B',
      2: '#D97706',
      3: '#0D9488'
    };

    plan.days.forEach((day, index) => {
      const isFirstDay = index === 0;
      const slots = day.slots || day.stops || [];
      const totalKm = day.total_distance_km ? ` · ${day.total_distance_km.toFixed(1)} km` : '';
      const dotColor = dayColors[day.day_number] || '#18181B';

      dayTabsHtml += `
        <button type="button" class="deck-day-tab ${isFirstDay ? 'active' : ''}" data-deck="${deckId}" data-day="${day.day_number}" title="${i18n.t('viewScheduleDay', 'Xem lịch trình và lộ trình Ngày')} ${day.day_number}">
          <span class="day-tab-dot" style="background-color: ${dotColor};"></span>
          <span>${i18n.t('legDayPrefix', 'Ngày')} ${day.day_number}</span>
        </button>
      `;

      const dayStops = [];
      slots.forEach(slot => {
        const lat = slot.latitude || slot.lat;
        const lng = slot.longitude || slot.lng;
        if (lat && lng) dayStops.push({ lat, lng });
      });

      let gmapsRouteBtn = '';
      if (dayStops.length >= 2) {
        const origin = `${dayStops[0].lat},${dayStops[0].lng}`;
        const dest = `${dayStops[dayStops.length - 1].lat},${dayStops[dayStops.length - 1].lng}`;
        const waypoints = dayStops.slice(1, -1).map(s => `${s.lat},${s.lng}`).join('|');
        const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${dest}${waypoints ? `&waypoints=${encodeURIComponent(waypoints)}` : ''}`;
        gmapsRouteBtn = `
          <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn-gmaps-route" title="${i18n.t('openRouteGmaps', 'Mở chỉ đường toàn tuyến Ngày')} ${day.day_number} Google Maps">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
            <span>Google Maps</span>
          </a>
        `;
      }

      let timelineStepsHtml = '';
      slots.forEach((slot, slotIdx) => {
        const isFood = (slot.category || '').toLowerCase().includes('restaurant') ||
          (slot.category || '').toLowerCase().includes('quán') ||
          (slot.activity_type || '').toLowerCase().includes('ẩm thực');
        const isUserOrigin = (slot.category || '').toLowerCase().includes('userlocation') ||
          (slot.activity_type || '').toLowerCase().includes('khởi hành');
        const lat = slot.latitude || slot.lat;
        const lng = slot.longitude || slot.lng;

        const hasOriginInDay = slots.some(s => {
          return (s.category || '').toLowerCase().includes('userlocation') ||
            (s.activity_type || '').toLowerCase().includes('khởi hành') ||
            (s.slot_name || '').toLowerCase().includes('xuất phát') ||
            (s.place_name || s.name || '').toLowerCase().includes('vị trí của bạn');
        });
        const legNum = hasOriginInDay ? slotIdx : (slotIdx + 1);
        const legBadge = isUserOrigin
          ? ''
          : `<span class="meta-pill pill-leg-num">${i18n.t('tourLegItem', 'Chặng')} ${legNum}</span>`;

        let distanceBadge = '';
        if (slot.distance_from_prev_km && slot.distance_from_prev_km > 0) {
          const distLabel = (isFirstDay && slotIdx === 1)
            ? `${i18n.t('distFromYou', 'Cách vị trí bạn')}: ${slot.distance_from_prev_km.toFixed(1)} km`
            : `${slot.distance_from_prev_km.toFixed(1)} km`;
          distanceBadge = `<span class="meta-pill pill-distance">${distLabel}</span>`;
        } else if (slot.distance_to_anchor_km) {
          distanceBadge = `<span class="meta-pill pill-distance">${slot.distance_to_anchor_km.toFixed(1)} km</span>`;
        }

        const dishBadge = slot.dish_highlight || slot.specialty_dish
          ? `<span class="meta-pill pill-dish">${i18n.t('dishLabel', 'Món')}: ${slot.dish_highlight || slot.specialty_dish}</span>`
          : '';

        const ratingBadge = (!isUserOrigin && slot.rating)
          ? `<span class="meta-pill pill-rating">⭐ ${slot.rating.toFixed(1)}</span>`
          : '';

        let displayActivityType = slot.activity_type || slot.category;
        if (isEn && displayActivityType) {
          const actLower = displayActivityType.toLowerCase();
          if (actLower.includes('di tích') || actLower.includes('tham quan') || actLower.includes('thắng cảnh') || actLower.includes('di sản') || actLower.includes('attraction')) {
            displayActivityType = 'Historical Heritage';
          } else if (actLower.includes('ẩm thực') || actLower.includes('ăn uống') || actLower.includes('đặc sản') || actLower.includes('restaurant')) {
            displayActivityType = 'Traditional Cuisine';
          } else if (actLower.includes('cà phê') || actLower.includes('cafe') || actLower.includes('coffee')) {
            displayActivityType = 'Coffee & Sunset';
          } else if (actLower.includes('khách sạn') || actLower.includes('nghỉ dưỡng') || actLower.includes('hotel') || actLower.includes('lưu trú')) {
            displayActivityType = 'Hotel & Resort';
          } else if (actLower.includes('khởi hành') || actLower.includes('xuất phát') || actLower.includes('userlocation')) {
            displayActivityType = 'Departure';
          } else if (actLower.includes('ngắm cảnh') || actLower.includes('giải trí')) {
            displayActivityType = 'Scenic & Entertainment';
          }
        } else if (!displayActivityType) {
          displayActivityType = isFood ? i18n.t('cuisine', 'Ẩm thực') : i18n.t('monuments', 'Di tích');
        }

        const typeBadge = isUserOrigin
          ? `<span class="meta-pill pill-origin">${i18n.t('legOriginDefault', 'Điểm xuất phát')}</span>`
          : `<span class="meta-pill">${displayActivityType}</span>`;

        let timeBadgeHtml = '';
        if (isUserOrigin) {
          const rawMatch = (slot.slot_name || '').match(/\((.*?)\)/);
          const timeRange = (rawMatch ? rawMatch[1] : '07:30 – 08:00').replace(/-/g, '–').trim();
          timeBadgeHtml = `<span class="badge-period">${i18n.t('departureLabel', 'Khởi hành')}</span><span class="badge-time">${timeRange}</span>`;
        } else {
          const raw = slot.slot_name || slot.slot_time || i18n.t('tourLeg', 'Chặng tour');
          const match = raw.match(/^(.*?)\s*\((.*?)\)$/);
          if (match) {
            const timeRange = match[2].replace(/-/g, '–').trim();
            timeBadgeHtml = `<span class="badge-period">${match[1]}</span><span class="badge-time">${timeRange}</span>`;
          } else {
            timeBadgeHtml = `<span class="badge-period">${raw}</span>`;
          }
        }

        const locateBtn = (lat && lng)
          ? `<button type="button" class="btn-locate" data-lat="${lat}" data-lng="${lng}" data-name="${slot.place_name || slot.name}" title="${i18n.t('viewOnMap', 'Xem vị trí trên bản đồ')}">
               <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="3" fill="currentColor"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/><circle cx="12" cy="12" r="7" stroke-dasharray="2 2"/></svg>
               <span>${i18n.t('itineraryLocateBtn', 'Định vị')}</span>
             </button>`
          : '';

        const detailBtn = isUserOrigin
          ? ''
          : `<button type="button" class="btn-step-detail" data-name="${slot.place_name || slot.name}">
               <span>${i18n.t('itineraryDetailBtn', 'Xem chi tiết')}</span>
               <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
             </button>`;

        let displayPlaceName = slot.place_name || slot.name;
        let displayPlaceDesc = slot.description || slot.address || i18n.t('poiHeritageExp', 'Điểm trải nghiệm di sản Cố đô');
        if (isUserOrigin) {
          displayPlaceName = isEn ? 'Your location (Starting Point)' : (slot.place_name || slot.name || 'Vị trí của bạn (Điểm xuất phát)');
          displayPlaceDesc = isEn ? 'Imperial heritage tour departure point' : (slot.description || slot.address || 'Điểm xuất phát hành trình Cố đô');
        } else if (isEn) {
          if (displayPlaceDesc === 'Điểm trải nghiệm di sản Cố đô') {
            displayPlaceDesc = 'Imperial heritage experience spot';
          }
        }

        timelineStepsHtml += `
          <div class="timeline-step ${isUserOrigin ? 'timeline-step-origin' : ''}" data-name="${slot.place_name || slot.name}" data-step-index="${slotIdx}">
            <div class="step-time-badge">${timeBadgeHtml}</div>
            <div class="step-content">
              <h4 class="step-poi-name ${isUserOrigin ? 'origin-name' : ''}" data-name="${slot.place_name || slot.name}" title="${isUserOrigin ? i18n.t('userOriginTitle', 'Điểm xuất phát tour của bạn') : i18n.t('clickForDetails', 'Nhấp để xem hồ sơ & đánh giá chi tiết')}">${displayPlaceName}</h4>
              <p class="step-poi-desc">${displayPlaceDesc}</p>
              <div class="step-meta-row">
                <div class="step-meta-tags">
                  ${legBadge}
                  ${typeBadge}
                  ${ratingBadge}
                  ${distanceBadge}
                  ${dishBadge}
                </div>
                <div class="step-meta-actions">
                  ${locateBtn}
                  ${detailBtn}
                </div>
              </div>
            </div>
          </div>
        `;
      });

      let themeText = day.theme || day.cluster_name || i18n.t('exploreHeritage', 'Khám phá Cố đô');
      if (isEn && themeText) {
        themeText = themeText
          .replace(/Kinh Thành Huế & Hương vị Ẩm thực Cố đô/gi, 'Hue Citadel & Imperial Culinary Delights')
          .replace(/Di tích bờ Nam & Cảnh quan lăng tẩm/gi, 'Southern Monuments & Royal Tombs')
          .replace(/Sông Hương & Làng nghề truyền thống/gi, 'Perfume River & Traditional Craft Villages')
          .replace(/Hành trình Di sản Hoàng cung & Cổ tự ven Sông Hương/gi, 'Imperial Citadel Heritage & Perfume River Ancient Temples')
          .replace(/Khám phá Quần thể Lăng tẩm Vương triều & Làng hương Cổ/gi, 'Royal Tombs Complex & Ancient Incense Craft Village')
          .replace(/Trải nghiệm Cảnh quan Sinh thái & Làng quê Cố Đô/gi, 'Eco-scenic Landscape & Imperial Countryside Experience')
          .replace(/Khám phá Cố đô/gi, 'Hue Heritage Discovery');
      }

      dayContentsHtml += `
        <div class="deck-day-content ${isFirstDay ? 'active' : ''}" id="${deckId}-day-${day.day_number}">
          <div class="deck-day-summary">
            <div class="deck-day-theme">${i18n.t('legDayPrefix', 'Ngày')} ${day.day_number}: ${themeText}</div>
            <div class="deck-day-actions">
              ${gmapsRouteBtn}
              <span class="day-badge">${slots.length} ${i18n.t('legsUnit', 'chặng')}${totalKm}</span>
            </div>
          </div>
          <div class="day-body" style="padding: 0;">
            ${timelineStepsHtml}
          </div>
        </div>
      `;
    });

    if (plan.days.length > 1) {
      dayTabsHtml += `
        <button type="button" class="deck-day-tab" data-deck="${deckId}" data-day="all" title="${i18n.t('allDaysRouteTitle', 'Xem tuyến đường toàn bộ các ngày cùng lúc')}">
          <span class="day-tab-dot" style="background: #18181B;"></span>
          <span>${i18n.t('allDaysTab', 'Tất cả ngày')}</span>
        </button>
      `;
    }

    const totalKmText = totalTripDistanceKm > 0 ? ` · ~${totalTripDistanceKm.toFixed(1)} km` : '';

    const introHtml = isEn
      ? `<p>I have optimized the <strong>${days}-day itinerary</strong> for <strong>${tripType}</strong> departing from <strong>${userLocName || 'your current location'}</strong> based on realistic travel distances. The full route is synchronized on the map.</p>`
      : `<p>Mình đã tối ưu hóa lịch trình <strong>${days} ngày</strong> cho <strong>${tripType}</strong> xuất phát từ <strong>${userLocName || 'Vị trí của bạn'}</strong> theo khoảng cách di chuyển thực tế. Toàn bộ lộ trình đã được đồng bộ lên bản đồ bên cạnh.</p>`;

    const msg = document.createElement('div');
    msg.className = 'chat-message assistant has-deck';
    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
          <line x1="9" y1="3" x2="9" y2="18" />
          <line x1="15" y1="6" x2="15" y2="21" />
        </svg>
      </div>
      <div class="message-bubble">
        <div class="message-author">${i18n.t('itineraryTourAuthor', 'Lịch trình Tour Cố đô')}</div>
        ${introHtml}
        
        <div class="chat-itinerary-deck" id="${deckId}">
          <div class="deck-header">
            <div class="deck-header-info">
              <h3 class="deck-title">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
                ${i18n.t('itineraryTitlePrefix', 'Lộ trình Khám phá Huế')} (${days} ${i18n.t('daysUnit', 'ngày')})
              </h3>
              <span class="deck-subtitle">${i18n.t('targetAudience', 'Đối tượng')}: ${tripType} · ${totalStopsCount} ${i18n.t('stopsCount', 'điểm đến')}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <div class="deck-badge">${days} ${i18n.t('daysUnit', 'Ngày')}${totalKmText}</div>
              <button type="button" class="btn-deck-budget" id="btn-budget-${deckId}" title="${i18n.t('budgetBtnTooltip', 'Dự toán chi phí vé di tích, ẩm thực và phương tiện')}">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                  <line x1="2" y1="10" x2="22" y2="10"></line>
                </svg>
                <span>${i18n.t('itineraryBudgetBtn', 'Dự toán chi phí')}</span>
              </button>
              <button type="button" class="btn-deck-save-tour" id="btn-save-${deckId}" title="${i18n.t('saveTourTooltip', 'Lưu lịch trình này vào tài khoản cá nhân')}">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>${i18n.t('itinerarySaveBtn', 'Lưu Tour')}</span>
              </button>
            </div>
          </div>

          <div class="deck-day-tabs">
            ${dayTabsHtml}
          </div>

          <div class="deck-days-wrapper">
            ${dayContentsHtml}
          </div>

          <div class="deck-followup">
            <span class="deck-followup-label">${i18n.t('followupLabel', 'Hỏi tiếp:')}</span>
            <button type="button" class="btn-deck-followup">${i18n.t('followupCost', 'Chi phí dự kiến chuyến đi này khoảng bao nhiêu?')}</button>
            <button type="button" class="btn-deck-followup">${i18n.t('followupBestTime', 'Thời điểm tham quan Đại Nội đẹp nhất trong ngày?')}</button>
            <button type="button" class="btn-deck-followup">${i18n.t('followupTransport', 'Phương tiện di chuyển hợp lý nhất ở Huế?')}</button>
          </div>

          <div class="deck-feedback-wrapper">
            ${createFeedbackBarHtml(deckId, existingRating)}
          </div>
        </div>
      </div>
    `;

    chatThread.appendChild(msg);

    // Gán sự kiện Feedback cho thẻ lịch trình
    bindFeedbackEvents(msg, {
      messageId: deckId,
      prompt: isEn ? `Create Hue Imperial tour ${days} days for ${tripType}` : `Lập lịch trình tour Cố đô Huế ${days} ngày cho ${tripType}`,
      plainText: isEn ? `Hue Imperial Itinerary (${days} days) for ${tripType} with ${totalStopsCount} destinations.` : `Lộ trình Khám phá Huế (${days} ngày) cho ${tripType} với ${totalStopsCount} điểm đến.`,
      isItinerary: true
    });

    setTimeout(() => {
      msg.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 60);

    // Đồng bộ ngay lập tức thẻ active của Chặng 1 sau khi deck xuất hiện
    setTimeout(() => {
      if (mapStudio && mapStudio.routeDisplayMode === 'leg') {
        mapStudio.syncTimelineHighlight();
      }
    }, 250);

    // Gán sự kiện chuyển Day Tabs trong thẻ lịch trình
    const deckEl = document.getElementById(deckId);
    if (deckEl) {
      const tabs = deckEl.querySelectorAll('.deck-day-tab');
      tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          const dayNum = tab.dataset.day;
          tabs.forEach(t => t.classList.remove('active'));
          tab.classList.add('active');

          const contents = deckEl.querySelectorAll('.deck-day-content');
          if (dayNum === 'all') {
            // Khi xem tất cả: hiện đầy đủ nội dung các ngày & vẽ tuyến độc lập trên bản đồ
            contents.forEach(c => c.classList.add('active'));
            mapStudio.renderTourItineraryDay('all');
          } else {
            contents.forEach(c => c.classList.remove('active'));
            const targetContent = document.getElementById(`${deckId}-day-${dayNum}`);
            if (targetContent) targetContent.classList.add('active');
            mapStudio.renderTourItineraryDay(parseInt(dayNum, 10));
          }
        });
      });

      // Gán sự kiện click định vị từng điểm trên Leaflet
      deckEl.querySelectorAll('.btn-locate').forEach(btn => {
        btn.addEventListener('click', () => {
          const lat = parseFloat(btn.dataset.lat);
          const lng = parseFloat(btn.dataset.lng);
          const dayContent = btn.closest('.deck-day-content');
          const stepEl = btn.closest('.timeline-step');

          const dayIdMatch = dayContent?.id?.match(/-day-(\d+)/);
          if (dayIdMatch && mapStudio.currentItineraryDay !== 'all') {
            const targetDay = parseInt(dayIdMatch[1], 10);
            if (mapStudio.currentItineraryDay !== targetDay) {
              const targetTab = deckEl.querySelector(`.deck-day-tab[data-day="${targetDay}"]`);
              if (targetTab) {
                tabs.forEach(t => t.classList.remove('active'));
                targetTab.classList.add('active');
                const contents = deckEl.querySelectorAll('.deck-day-content');
                contents.forEach(c => c.classList.remove('active'));
                dayContent.classList.add('active');
                mapStudio.renderTourItineraryDay(targetDay);
              }
            }
          }

          if (stepEl?.classList.contains('timeline-step-origin')) {
            // Khi click định vị điểm xuất phát: highlight thẻ origin và pan map tới vị trí xuất phát
            mapStudio.clearTimelineHighlight();
            stepEl.classList.add('is-active-leg');
            mapStudio.panTo(lat, lng, 16);
            return;
          }

          const name = btn.dataset.name;
          if (name && mapStudio.routeDisplayMode === 'leg') {
            mapStudio.setActiveLegByDestination(name);
          } else {
            mapStudio.panTo(lat, lng, 16);
          }
        });
      });

      // Gán sự kiện click xem chi tiết từng điểm (mở Drawer POI và đồng bộ chặng trên bản đồ)
      deckEl.querySelectorAll('.btn-step-detail, .step-poi-name').forEach(el => {
        el.addEventListener('click', () => {
          const name = el.dataset.name;
          if (name && window.openPoiDetail) {
            window.openPoiDetail(name);
          }
          if (name && mapStudio.routeDisplayMode === 'leg') {
            mapStudio.setActiveLegByDestination(name);
          }
        });
      });

      // Gán sự kiện cho các nút hỏi tiếp theo
      deckEl.querySelectorAll('.btn-deck-followup').forEach(btn => {
        btn.addEventListener('click', () => {
          const query = btn.textContent.trim();
          if (query.includes('Chi phí dự kiến') || query.includes('estimated budget') || query.includes('cost')) {
            const tourTitle = `${i18n.t('itineraryTitlePrefix', 'Lịch trình Huế')} ${days} ${i18n.t('daysUnit', 'ngày')} (${tripType})`;
            budgetEstimator.openModal(plan, tourTitle);
          } else {
            sendChatQuery(query);
          }
        });
      });

      // Gán sự kiện cho nút Dự toán chi phí
      const btnBudget = document.getElementById(`btn-budget-${deckId}`);
      btnBudget?.addEventListener('click', () => {
        const tourTitle = `${i18n.t('itineraryTitlePrefix', 'Lịch trình Huế')} ${days} ${i18n.t('daysUnit', 'ngày')} (${tripType})`;
        budgetEstimator.openModal(plan, tourTitle);
      });

      // Gán sự kiện cho nút Lưu Tour vào tài khoản Google / Cloud
      const btnSaveTour = document.getElementById(`btn-save-${deckId}`);
      btnSaveTour?.addEventListener('click', async () => {
        if (!authController.currentUser) {
          authController.openAuthModal('login');
          authController.showToast(i18n.t('loginToSaveTour', 'Vui lòng đăng nhập để lưu lịch trình vào tài khoản.'));
          return;
        }

        try {
          btnSaveTour.disabled = true;
          btnSaveTour.innerHTML = `<span>${i18n.t('savingTour', 'Đang lưu...')}</span>`;
          const tourTitle = `${i18n.t('itineraryTitlePrefix', 'Lịch trình Huế')} ${days} ${i18n.t('daysUnit', 'ngày')} (${tripType})`;
          await saveItinerary(authController.currentUser.uid, {
            title: tourTitle,
            days,
            tripType,
            userLocationName: userLocName || (isEn ? 'Hue City' : 'Thành phố Huế'),
            stopsCount: totalStopsCount,
            totalKm: totalTripDistanceKm,
            rawResult: res,
            items: allStopsForMap
          });
          btnSaveTour.classList.add('saved');
          btnSaveTour.innerHTML = `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>${i18n.t('savedTourBtn', 'Đã lưu')}</span>
          `;
          authController.showToast(i18n.t('tourSavedSuccess', 'Đã lưu lịch trình thành công vào tài khoản!'));
        } catch (err) {
          btnSaveTour.disabled = false;
          btnSaveTour.innerHTML = `<span>${i18n.t('itinerarySaveBtn', 'Lưu Tour')}</span>`;
          authController.showToast(`${i18n.t('cannotSaveTour', 'Lỗi khi lưu lịch trình')}: ${err.message}`);
        }
      });
    }

    // Tự động vẽ lộ trình phân tách theo Ngày (Mặc định hiển thị Ngày 1 để thoáng mắt, không chằng chịt)
    if (plan.days && plan.days.length > 0) {
      mapStudio.setTourItinerary(plan, 1);
    } else if (allStopsForMap.length > 0) {
      mapStudio.drawTourRoute(allStopsForMap);
    }

    // Lưu thẻ lịch trình vào phiên chat hiện tại
    if (persist && !isRestoringSession) {
      activeSessionMessages.push({
        id: deckId,
        role: 'assistant',
        text: isEn ? `📅 ${days}-day Hue Imperial Tour for ${tripType}` : `📅 Lịch trình tour Cố đô Huế ${days} ngày cho ${tripType}`,
        isItinerary: true,
        itineraryRes: res,
        days,
        tripType,
        preferredDishes,
        userLocName,
        feedbackRating: existingRating,
        timestamp: Date.now()
      });
      persistActiveSession();
    }
  }

  // Lắng nghe sự kiện mở lại lịch trình đã lưu từ Auth Modal
  window.addEventListener('load-saved-tour', (e) => {
    const tour = e.detail;
    if (!tour) return;
    showMapPanel(true);
    if (tour.rawResult) {
      appendItineraryDeckMessage(tour.rawResult, tour.days, tour.tripType, [], tour.userLocationName);
    } else if (tour.items && tour.items.length > 0) {
      mapStudio.drawTourRoute(tour.items);
    }
  });

  // 7. TRỢ LÝ HỎI ĐÁP (CHAT ASSISTANT)
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatThread = document.getElementById('chat-thread');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const btnClearChat = document.getElementById('btn-clear-chat');

  // Đính kèm ảnh đa phương thức (Multimodal Image Analysis)
  const btnUploadImage = document.getElementById('btn-upload-image');
  const chatImageInput = document.getElementById('chat-image-input');
  const chatImagePreviewBar = document.getElementById('chat-image-preview-bar');
  const previewImageElem = document.getElementById('preview-image-elem');
  const previewImageName = document.getElementById('preview-image-name');
  const btnRemoveImage = document.getElementById('btn-remove-image');
  let currentAttachedImageBase64 = null;
  let currentAttachedImageStorageBase64 = null;
  let currentAttachedImageName = '';

  function clearAttachedImage() {
    currentAttachedImageBase64 = null;
    currentAttachedImageStorageBase64 = null;
    currentAttachedImageName = '';
    if (chatImagePreviewBar) chatImagePreviewBar.style.display = 'none';
    if (chatImageInput) chatImageInput.value = '';
    if (previewImageElem) previewImageElem.src = '';
    btnUploadImage?.classList.remove('has-image');
  }

  // Kích thước ảnh:
  // - Bản gửi AI Vision + hiển thị trong khung chat: cạnh dài tối đa 1600px (đủ nét để nhận diện
  //   địa danh/món ăn, nặng ~200–500KB thay vì 3–12MB của ảnh gốc chụp từ điện thoại).
  // - Bản lưu Firestore: 520px (~40–80KB) để cả phiên chat không vượt giới hạn 1MB/document.
  const AI_IMAGE_MAX_DIM = 1600;
  const AI_IMAGE_QUALITY = 0.85;
  const STORAGE_THUMB_MAX_DIM = 520;
  const STORAGE_THUMB_QUALITY = 0.68;

  // Giải mã file ảnh một lần duy nhất (dùng object URL, không cần đọc base64 của ảnh gốc)
  function loadImageFromFile(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error(i18n.t('cannotReadImageFormat', 'Trình duyệt không đọc được định dạng ảnh này')));
      };
      img.src = url;
    });
  }

  // Thu nhỏ ảnh (giữ tỉ lệ) và xuất ra JPEG base64. Ảnh nhỏ hơn maxDim thì giữ nguyên kích thước.
  function renderJpegDataUrl(img, maxDim, quality) {
    const scale = Math.min(1, maxDim / Math.max(img.naturalWidth, img.naturalHeight));
    const w = Math.max(1, Math.round(img.naturalWidth * scale));
    const h = Math.max(1, Math.round(img.naturalHeight * scale));
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    // Nền trắng để ảnh PNG trong suốt không bị đen khi chuyển sang JPEG
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);
    return canvas.toDataURL('image/jpeg', quality);
  }

  async function handleImageFileSelected(file) {
    if (!file || !file.type.startsWith('image/')) return;
    try {
      const img = await loadImageFromFile(file);
      currentAttachedImageBase64 = renderJpegDataUrl(img, AI_IMAGE_MAX_DIM, AI_IMAGE_QUALITY);
      currentAttachedImageStorageBase64 = renderJpegDataUrl(img, STORAGE_THUMB_MAX_DIM, STORAGE_THUMB_QUALITY);
      currentAttachedImageName = file.name;
      if (previewImageElem) previewImageElem.src = currentAttachedImageBase64;
      if (previewImageName) previewImageName.textContent = file.name;
      if (chatImagePreviewBar) chatImagePreviewBar.style.display = 'flex';
      btnUploadImage?.classList.add('has-image');
      chatInput?.focus();
    } catch (err) {
      console.error('Lỗi xử lý ảnh:', err);
      clearAttachedImage();
      authController.showToast(i18n.t('imgNotSupported', 'Không đọc được ảnh này. Vui lòng chọn ảnh JPG, PNG hoặc WEBP.'));
    }
  }

  btnUploadImage?.addEventListener('click', () => {
    chatImageInput?.click();
  });

  chatImageInput?.addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      await handleImageFileSelected(file);
    }
  });

  btnRemoveImage?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    clearAttachedImage();
  });

  // Hỗ trợ dán ảnh trực tiếp từ Clipboard (Ctrl + V)
  document.addEventListener('paste', async (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
      if (item.type && item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          await handleImageFileSelected(file);
          break;
        }
      }
    }
  });

  function initPromptCards() {
    // Đã xóa bỏ hoàn toàn 4 thẻ gợi ý màn hình chào
  }

  function renderWelcomeHero() {
    if (!chatThread) return;
    chatThread.innerHTML = `
      <div class="chat-welcome-hero" id="chat-welcome-hero">
        <h1 class="welcome-heading">${i18n.t('welcomeHeading', 'Hôm nay bạn muốn khám phá Huế như thế nào?')}</h1>
        <p class="welcome-subheading">${i18n.t('welcomeSubheading', 'Tra cứu di tích lịch sử, tìm quán ăn đặc sản chuẩn vị hoặc để AI tối ưu hóa lộ trình tham quan cho bạn.')}</p>
      </div>
    `;
  }

  // Khởi tạo ban đầu
  initPromptCards();

  // =============================================================================
  // QUẢN LÝ PHIÊN TRÒ CHUYỆN & THANH BÊN (GEMINI LEFT SIDEBAR & SESSIONS)
  // =============================================================================
  const sidebarGemini = document.getElementById('sidebar-gemini');
  const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
  const btnSidebarToggle = document.getElementById('btn-sidebar-toggle') || document.getElementById('btn-sidebar-collapse');
  const btnSidebarCollapse = document.getElementById('btn-sidebar-collapse');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');
  const btnSidebarNewChat = document.getElementById('btn-sidebar-new-chat');
  const btnSidebarSavedTours = document.getElementById('btn-sidebar-saved-tours');
  const btnSidebarToggleMap = document.getElementById('btn-sidebar-toggle-map');
  const sidebarFooterGroup = document.getElementById('sidebar-footer-group');
  const btnSidebarSettings = document.getElementById('btn-sidebar-settings');
  const sidebarUserChip = document.getElementById('sidebar-user-chip');
  const sidebarAvatarImg = document.getElementById('sidebar-avatar-img');
  const sidebarAvatarFallback = document.getElementById('sidebar-avatar-fallback');
  const sidebarUserName = document.getElementById('sidebar-user-name');
  const sidebarUserStatus = document.getElementById('sidebar-user-status');

  // Sidebar User Popover Elements
  const sidebarUserPopover = document.getElementById('sidebar-user-popover');
  const popoverAvatarImg = document.getElementById('popover-avatar-img');
  const popoverAvatarFallback = document.getElementById('popover-avatar-fallback');
  const popoverUserName = document.getElementById('popover-user-name');
  const popoverUserEmail = document.getElementById('popover-user-email');
  const popoverBadgeStatus = document.getElementById('popover-badge-status');
  const popoverLoggedInActions = document.getElementById('popover-logged-in-actions');
  const popoverGuestActions = document.getElementById('popover-guest-actions');

  const btnPopoverSavedTours = document.getElementById('btn-popover-saved-tours');
  const btnPopoverConfig = document.getElementById('btn-popover-config');
  const btnPopoverLogout = document.getElementById('btn-popover-logout');
  const btnPopoverLogin = document.getElementById('btn-popover-login');
  const btnPopoverSignup = document.getElementById('btn-popover-signup');
  const btnPopoverGuestConfig = document.getElementById('btn-popover-guest-config');
  const btnPopoverDemo = document.getElementById('btn-popover-demo');

  const btnNewChat = document.getElementById('btn-new-chat');
  const btnToggleChatHistory = document.getElementById('btn-toggle-chat-history');
  const btnWorkbenchSavedTours = document.getElementById('btn-workbench-saved-tours');
  const historyCountBadge = document.getElementById('history-count-badge');
  const sidebarHistoryCountBadge = document.getElementById('sidebar-history-count-badge');
  const workbenchHistoryCountBadge = document.getElementById('workbench-history-count-badge');
  const chatSessionsList = document.getElementById('chat-sessions-list');

  // Khởi tạo thời tiết Huế
  const sidebarWeatherContainer = document.getElementById('sidebar-weather-container');
  const headerWeatherPill = document.getElementById('header-weather-pill');
  const hueWeatherService = new HueWeatherService();
  window.hueWeatherService = hueWeatherService;

  async function initHueWeatherWidget() {
    try {
      const data = await hueWeatherService.getHueWeather();
      if (sidebarWeatherContainer) {
        sidebarWeatherContainer.innerHTML = hueWeatherService.renderWidgetHtml(data);
        const btnExpand = sidebarWeatherContainer.querySelector('#btn-weather-expand');
        const detailsCard = sidebarWeatherContainer.querySelector('#weather-details-card');
        btnExpand?.addEventListener('click', (e) => {
          e.stopPropagation();
          const isHidden = detailsCard?.classList.toggle('hidden');
          btnExpand.classList.toggle('expanded', !isHidden);
        });
      }
      if (headerWeatherPill) {
        headerWeatherPill.innerHTML = `
          ${hueWeatherService.getWeatherIconSvg(data.iconType, 15)}
          <span>${data.temp}°C ${i18n.getLanguage() === 'en' ? 'Hue' : 'Huế'}</span>
        `;
        headerWeatherPill.addEventListener('click', () => {
          if (sidebarGemini?.classList.contains('collapsed')) {
            toggleSidebar(true);
          } else if (window.innerWidth <= 1024) {
            toggleSidebar(true);
          }
        });
      }
    } catch (err) {
      console.warn('Không thể nạp thời tiết Huế:', err);
    }
  }
  initHueWeatherWidget();

  function getCurrentUserId() {
    return window.authController?.currentUser?.uid || null;
  }

  function parseTimestamp(rawDate) {
    if (!rawDate) return new Date();
    if (typeof rawDate.toDate === 'function') {
      try { return rawDate.toDate(); } catch { }
    }
    if (typeof rawDate === 'object' && rawDate.seconds !== undefined) {
      return new Date(rawDate.seconds * 1000);
    }
    if (typeof rawDate === 'number') {
      return new Date(rawDate);
    }
    const d = new Date(rawDate);
    if (!isNaN(d.getTime())) {
      return d;
    }
    return new Date();
  }

  function formatRelativeTime(dateVal) {
    if (!dateVal) return i18n.t('justNow', 'Vừa xong');
    const date = parseTimestamp(dateVal);
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);
    if (isNaN(diffSec) || diffSec < 60) return i18n.t('justNow', 'Vừa xong');
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} ${i18n.t('minsAgo', 'phút trước')}`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour} ${i18n.t('hoursAgo', 'giờ trước')}`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay === 1) return i18n.t('yesterday', 'Hôm qua');
    if (diffDay < 7) return `${diffDay} ${i18n.t('daysAgo', 'ngày trước')}`;
    const day = (date.getDate() || 1).toString().padStart(2, '0');
    const month = ((date.getMonth() || 0) + 1).toString().padStart(2, '0');
    return `${day}/${month}`;
  }

  async function persistActiveSession() {
    if (isRestoringSession || !activeSessionId || activeSessionMessages.length === 0) return;
    const uid = getCurrentUserId();

    // Tự động gán tiêu đề session theo câu hỏi đầu tiên của người dùng
    const firstUserMsg = activeSessionMessages.find(m => m.role === 'user');
    if (firstUserMsg && (!activeSessionTitle || activeSessionTitle === 'Cuộc trò chuyện mới' || activeSessionTitle === 'New Chat')) {
      activeSessionTitle = firstUserMsg.text.length > 36
        ? firstUserMsg.text.substring(0, 36).trim() + '...'
        : firstUserMsg.text.trim();
    }

    let latestContext = activeSessionContext || null;
    for (let i = activeSessionMessages.length - 1; i >= 0; i--) {
      const ctx = activeSessionMessages[i].role === 'assistant' ? activeSessionMessages[i].resData?.session_context : null;
      if (ctx) { latestContext = ctx; break; }
    }

    try {
      await saveChatSession(uid, {
        id: activeSessionId,
        title: activeSessionTitle || i18n.t('newChat', 'Cuộc trò chuyện mới'),
        messages: activeSessionMessages,
        session_context: latestContext
      });
      refreshChatHistoryList(false);
    } catch (e) {
      console.warn('Lỗi lưu session:', e);
    }
  }

  async function refreshChatHistoryList(openAfterRefresh = false) {
    const isEn = i18n.getLanguage() === 'en';
    const uid = getCurrentUserId();
    const sessions = await getUserChatSessions(uid);

    const sessionCount = sessions.length;
    // Đồng bộ số lượng phiên trên cả thanh bên (sidebar) và nút Lịch sử ở thanh tác vụ bên phải (workbench header)
    if (sidebarHistoryCountBadge) {
      sidebarHistoryCountBadge.textContent = sessionCount;
    }
    if (workbenchHistoryCountBadge) {
      workbenchHistoryCountBadge.textContent = sessionCount;
    }
    if (historyCountBadge) {
      historyCountBadge.textContent = sessionCount;
    }
    document.querySelectorAll('.history-count-badge').forEach(badge => {
      badge.textContent = sessionCount;
    });

    if (!chatSessionsList) return;

    if (sessions.length === 0) {
      chatSessionsList.innerHTML = `
        <div class="chat-history-empty">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <p>${i18n.t('noHistory', 'Chưa có cuộc trò chuyện nào.')}<br><span style="font-size:0.75rem; color:#A1A1AA;">${i18n.t('noHistorySub', 'Bắt đầu hỏi AI để tự động lưu lịch sử!')}</span></p>
        </div>
      `;
      return;
    }

    chatSessionsList.innerHTML = '';
    sessions.forEach(sess => {
      const item = document.createElement('div');
      item.className = `chat-session-item ${sess.id === activeSessionId ? 'active' : ''}`;
      item.dataset.sessionId = sess.id;
      const safeSessionTitle = escapeHtml(sess.title || i18n.t('sessionDefaultTitle', 'Cuộc trò chuyện'));
      const msgCountText = isEn ? `${(sess.messages || []).length} msgs` : `${(sess.messages || []).length} tin`;
      item.innerHTML = `
        <div class="session-main">
          <div class="session-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div class="session-meta">
            <span class="session-title" title="${safeSessionTitle}">${safeSessionTitle}</span>
            <span class="session-date">${formatRelativeTime(sess.updatedAt || sess.createdAt)} · ${msgCountText}</span>
          </div>
        </div>
        <button type="button" class="btn-delete-session" title="${i18n.t('deleteSessionTooltip', 'Xóa cuộc trò chuyện này')}" aria-label="${i18n.t('delete', 'Xóa')}">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      `;

      item.addEventListener('click', (e) => {
        if (e.target.closest('.btn-delete-session')) return;
        restoreChatSession(sess);
      });

      const btnDel = item.querySelector('.btn-delete-session');
      btnDel?.addEventListener('click', async (e) => {
        e.stopPropagation();
        const confirmMsg = isEn ? `Are you sure you want to delete "${sess.title}"?` : `Bạn có chắc muốn xóa cuộc trò chuyện "${sess.title}" không?`;
        if (confirm(confirmMsg)) {
          await deleteChatSession(uid, sess.id);
          if (activeSessionId === sess.id) {
            startNewChatSession();
          } else {
            refreshChatHistoryList();
          }
        }
      });

      chatSessionsList.appendChild(item);
    });

    if (openAfterRefresh) {
      toggleChatHistoryDrawer(true);
    }
  }

  function restoreChatSession(session) {
    if (!session) return;
    isRestoringSession = true;
    activeSessionId = session.id;
    activeSessionTitle = session.title;
    activeSessionMessages = session.messages || [];
    activeSessionContext = session.session_context || null;

    // Quét ngược tìm context hoặc fallback từ matched_places nếu session_context gốc bị thiếu
    if (!activeSessionContext && activeSessionMessages.length > 0) {
      for (let i = activeSessionMessages.length - 1; i >= 0; i--) {
        const m = activeSessionMessages[i];
        if (m.role === 'assistant') {
          if (m.resData?.session_context) {
            activeSessionContext = m.resData.session_context;
            break;
          }
          const p = m.resData?.matched_places?.[0];
          if (p && p.name) {
            activeSessionContext = inferContextFromPlace(p);
            break;
          }
        }
      }
    }

    // Dọn sạch hoàn toàn trạng thái bản đồ cũ trước khi nạp phiên chat mới
    if (mapStudio && typeof mapStudio.resetToDefaultState === 'function') {
      mapStudio.resetToDefaultState();
    }

    chatThread.innerHTML = '';

    if (activeSessionMessages.length === 0) {
      renderWelcomeHero();
    } else {
      // Ghi nhớ ảnh của câu hỏi ngay trước câu trả lời để nút "Tạo lại" gửi kèm được
      // (sau khi tải lại phiên, chỉ còn bản thumbnail 520px đã lưu trên Firestore)
      let lastUserImage = null;
      activeSessionMessages.forEach(msg => {
        const textVal = msg.text || msg.content || '';
        if (msg.role === 'user') {
          lastUserImage = msg.imageBase64 || null;
          if (textVal || msg.imageBase64) appendUserMessage(textVal, false, msg.imageBase64 || null);
        } else if (msg.role === 'assistant') {
          if (msg.isItinerary && msg.itineraryRes) {
            appendItineraryDeckMessage(msg.itineraryRes, msg.days, msg.tripType, msg.preferredDishes, msg.userLocName, false, msg.id, msg.feedbackRating);
          } else {
            const answerVal = textVal || msg.resData?.answer || '';
            appendAssistantResponse(
              { ...msg.resData, answer: answerVal, messageId: msg.id, feedbackRating: msg.feedbackRating, prompt: msg.prompt },
              false,
              '',
              { image: lastUserImage, storageThumb: lastUserImage }
            );
          }
          lastUserImage = null;
        }
      });
    }

    isRestoringSession = false;
    if (window.innerWidth <= 1024) {
      toggleSidebar(false);
    }
    refreshChatHistoryList(false);
  }

  function startNewChatSession() {
    activeSessionId = 'session_' + Date.now();
    activeSessionTitle = (typeof i18n !== 'undefined' && i18n.getLanguage() === 'en') ? 'New Chat' : 'Cuộc trò chuyện mới';
    activeSessionMessages = [];
    activeSessionContext = null;
    renderWelcomeHero();
    if (window.innerWidth <= 1024) {
      toggleSidebar(false);
    }
    refreshChatHistoryList(false);
    if (chatInput) chatInput.focus();

    // DỌN SẠCH TOÀN BỘ BẢN ĐỒ: Đóng popup chặng, xóa route lộ trình và ẩn stepper thanh chặng
    if (mapStudio && typeof mapStudio.resetToDefaultState === 'function') {
      mapStudio.resetToDefaultState();
    }
  }

  function closeUserPopover() {
    sidebarUserPopover?.classList.remove('active');
    sidebarUserChip?.setAttribute('aria-expanded', 'false');
  }

  function toggleUserPopover() {
    if (!sidebarUserPopover) return;
    const isNowActive = sidebarUserPopover.classList.toggle('active');
    sidebarUserChip?.setAttribute('aria-expanded', isNowActive ? 'true' : 'false');
  }

  function toggleSidebar(forceState) {
    if (!sidebarGemini) return;
    closeUserPopover();
    const isMobile = window.innerWidth <= 1024;
    if (isMobile) {
      // Trên mobile, sidebar luôn là bản đầy đủ dạng Drawer trượt ra, không dùng dạng thanh icon 56px
      sidebarGemini.classList.remove('collapsed');
      const willOpen = typeof forceState === 'boolean' ? forceState : !sidebarGemini.classList.contains('mobile-open');
      sidebarGemini.classList.toggle('mobile-open', willOpen);
      sidebarBackdrop?.classList.toggle('active', willOpen);
    } else {
      const willCollapse = typeof forceState === 'boolean' ? !forceState : !sidebarGemini.classList.contains('collapsed');
      sidebarGemini.classList.toggle('collapsed', willCollapse);

      const toggleBtn = btnSidebarToggle || btnSidebarCollapse;
      if (toggleBtn) {
        const tooltipText = willCollapse ? i18n.t('sidebarExpand', 'Mở thanh bên') : i18n.t('sidebarToggle', 'Thu gọn thanh bên');
        toggleBtn.setAttribute('title', tooltipText);
        toggleBtn.setAttribute('data-tooltip', tooltipText);
      }

      btnToggleSidebar?.classList.toggle('active', !willCollapse);
      try {
        localStorage.setItem('hue_sidebar_collapsed', willCollapse ? '1' : '0');
      } catch { }

      // Cập nhật kích thước bản đồ mượt mà sau khi hiệu ứng thanh bên hoàn tất
      setTimeout(() => {
        if (window.mapStudio?.map) {
          window.mapStudio.map.invalidateSize({ animate: false });
        }
      }, 340);
    }
  }

  // Khôi phục trạng thái thu gọn thanh bên trên Desktop
  try {
    if (window.innerWidth > 1024 && localStorage.getItem('hue_sidebar_collapsed') === '1') {
      sidebarGemini?.classList.add('collapsed');
      const toggleBtn = btnSidebarToggle || btnSidebarCollapse;
      if (toggleBtn) {
        toggleBtn.setAttribute('title', i18n.t('sidebarExpand', 'Mở thanh bên'));
        toggleBtn.setAttribute('data-tooltip', i18n.t('sidebarExpand', 'Mở thanh bên'));
      }
    }
  } catch { }

  function updateSidebarUserProfile(user) {
    if (!sidebarUserName) return;
    if (user) {
      const displayName = user.displayName || user.email?.split('@')[0] || i18n.t('guestTourist', 'Du khách Cố đô');
      const email = user.email || 'Cloud Firestore';
      const initial = (displayName || 'U')[0].toUpperCase();

      sidebarUserName.textContent = displayName;
      sidebarUserStatus.textContent = user.isDemo ? i18n.t('demoAccount', 'Tài khoản Demo') : i18n.t('syncFirestore', 'Đồng bộ Cloud Firestore');

      if (popoverUserName) popoverUserName.textContent = displayName;
      if (popoverUserEmail) popoverUserEmail.textContent = email;
      if (popoverBadgeStatus) {
        popoverBadgeStatus.textContent = user.isDemo ? i18n.t('badgeDemo', 'Bản Demo') : (user.providerData?.some(p => p.providerId === 'google.com') ? 'Google' : i18n.t('loggedInBadge', 'Đã đăng nhập'));
        popoverBadgeStatus.className = 'popover-badge-status badge-logged-in';
      }

      if (popoverLoggedInActions) popoverLoggedInActions.style.display = 'flex';
      if (popoverGuestActions) popoverGuestActions.style.display = 'none';

      if (user.photoURL) {
        if (sidebarAvatarImg) {
          sidebarAvatarImg.src = user.photoURL;
          sidebarAvatarImg.classList.remove('hidden');
        }
        sidebarAvatarFallback?.classList.add('hidden');

        if (popoverAvatarImg) {
          popoverAvatarImg.src = user.photoURL;
          popoverAvatarImg.classList.remove('hidden');
        }
        popoverAvatarFallback?.classList.add('hidden');
      } else {
        sidebarAvatarImg?.classList.add('hidden');
        if (sidebarAvatarFallback) {
          sidebarAvatarFallback.textContent = initial;
          sidebarAvatarFallback.classList.remove('hidden');
        }

        popoverAvatarImg?.classList.add('hidden');
        if (popoverAvatarFallback) {
          popoverAvatarFallback.textContent = initial;
          popoverAvatarFallback.classList.remove('hidden');
        }
      }
    } else {
      sidebarUserName.textContent = i18n.t('guestUser', 'Khách vãng lai');
      sidebarUserStatus.textContent = i18n.t('clickToLogin', 'Bấm để đăng nhập');
      sidebarAvatarImg?.classList.add('hidden');
      if (sidebarAvatarFallback) {
        sidebarAvatarFallback.textContent = 'U';
        sidebarAvatarFallback.classList.remove('hidden');
      }

      if (popoverUserName) popoverUserName.textContent = i18n.t('guestUser', 'Khách vãng lai');
      if (popoverUserEmail) popoverUserEmail.textContent = i18n.t('notLoggedIn', 'Chưa đăng nhập');
      if (popoverBadgeStatus) {
        popoverBadgeStatus.textContent = i18n.t('guestBadge', 'Khách');
        popoverBadgeStatus.className = 'popover-badge-status';
      }

      if (popoverLoggedInActions) popoverLoggedInActions.style.display = 'none';
      if (popoverGuestActions) popoverGuestActions.style.display = 'flex';

      popoverAvatarImg?.classList.add('hidden');
      if (popoverAvatarFallback) {
        popoverAvatarFallback.textContent = 'U';
        popoverAvatarFallback.classList.remove('hidden');
      }
    }
  }

  // Sự kiện bật / tắt User Account Popover
  sidebarUserChip?.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleUserPopover();
  });

  sidebarUserPopover?.addEventListener('click', (e) => {
    e.stopPropagation();
  });

  document.addEventListener('click', (e) => {
    if (!sidebarFooterGroup?.contains(e.target)) {
      closeUserPopover();
    }
  });

  // Nút Cài đặt hệ thống ở thanh bên
  btnSidebarSettings?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openConfigModal();
  });

  // Các nút bên trong Popover
  btnPopoverSavedTours?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openSavedToursModal();
    if (window.innerWidth <= 1024) toggleSidebar(false);
  });

  btnPopoverConfig?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openConfigModal();
  });

  btnPopoverGuestConfig?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openConfigModal();
  });

  btnPopoverLogout?.addEventListener('click', async () => {
    closeUserPopover();
    try {
      await logoutUser();
      window.authController?.showToast(i18n.t('logoutSuccess', 'Đã đăng xuất tài khoản thành công.'));
    } catch (err) {
      console.error('Lỗi khi đăng xuất:', err);
    }
  });

  btnPopoverLogin?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openAuthModal('login');
  });

  btnPopoverSignup?.addEventListener('click', () => {
    closeUserPopover();
    window.authController?.openAuthModal('signup');
  });

  btnPopoverDemo?.addEventListener('click', () => {
    closeUserPopover();
    loginWithDemoUser();
    window.authController?.showToast(i18n.t('demoModeActive', 'Đã kích hoạt chế độ Trải nghiệm Khách (Demo).'));
  });

  // Khởi tạo và quản lý Modal Cài đặt Ứng dụng (Application Settings)
  const initSettingsModal = () => {
    const tabBtns = document.querySelectorAll('.settings-tab-btn');
    const panels = document.querySelectorAll('.settings-panel');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');

        tabBtns.forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');

        panels.forEach(p => {
          if (p.id === targetId) {
            p.classList.add('active');
            p.removeAttribute('hidden');
          } else {
            p.classList.remove('active');
            p.setAttribute('hidden', '');
          }
        });
      });
    });

    // Preferences: Tải và lắng nghe trạng thái đã lưu
    const autoMapToggle = document.getElementById('pref-toggle-auto-map');
    const animToggle = document.getElementById('pref-toggle-animations');
    const weatherToggle = document.getElementById('pref-toggle-weather-tips');
    const aiDetailSelect = document.getElementById('pref-ai-detail-select');
    const aiStyleInputs = document.querySelectorAll('input[name="ai-style-option"]');
    const btnClearCache = document.getElementById('btn-settings-clear-cache');

    if (autoMapToggle) {
      autoMapToggle.checked = localStorage.getItem('hue_pref_auto_map') !== 'false';
      autoMapToggle.addEventListener('change', (e) => {
        localStorage.setItem('hue_pref_auto_map', e.target.checked);
      });
    }

    if (animToggle) {
      const animEnabled = localStorage.getItem('hue_pref_animations') !== 'false';
      animToggle.checked = animEnabled;
      document.body.classList.toggle('reduce-motion', !animEnabled);
      animToggle.addEventListener('change', (e) => {
        localStorage.setItem('hue_pref_animations', e.target.checked);
        document.body.classList.toggle('reduce-motion', !e.target.checked);
      });
    }

    if (weatherToggle) {
      const weatherEnabled = localStorage.getItem('hue_pref_weather_tips') !== 'false';
      weatherToggle.checked = weatherEnabled;
      document.getElementById('weather-smart-tip')?.classList.toggle('hidden', !weatherEnabled);
      weatherToggle.addEventListener('change', (e) => {
        localStorage.setItem('hue_pref_weather_tips', e.target.checked);
        document.getElementById('weather-smart-tip')?.classList.toggle('hidden', !e.target.checked);
      });
    }

    const savedStyle = localStorage.getItem('hue_pref_ai_style') || 'balanced';
    aiStyleInputs.forEach(input => {
      if (input.value === savedStyle) input.checked = true;
      input.addEventListener('change', (e) => {
        if (e.target.checked) {
          localStorage.setItem('hue_pref_ai_style', e.target.value);
        }
      });
    });

    if (aiDetailSelect) {
      aiDetailSelect.value = localStorage.getItem('hue_pref_ai_detail') || 'detailed';
      aiDetailSelect.addEventListener('change', (e) => {
        localStorage.setItem('hue_pref_ai_detail', e.target.value);
      });
    }

    if (btnClearCache) {
      btnClearCache.addEventListener('click', () => {
        sessionStorage.clear();
        localStorage.removeItem('hue_cached_places_v1');
        localStorage.removeItem('hue_last_query');
        window.authController?.showToast(i18n.t('cacheRefreshed', 'Đã làm mới bộ nhớ đệm và dữ liệu tạm thành công.'));
      });
    }
  };

  /**
   * Theme & Language Controller (evon:ui-ux Minimalist Design)
   * Tích hợp Dark/Light theme toggle & Chuyển đổi ngôn ngữ VI / EN
   */
  const initThemeAndLanguage = () => {
    // 1. Language Switcher (Segmented pill VI | EN)
    const langBtns = document.querySelectorAll('.lang-btn');
    langBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const selectedLang = btn.dataset.lang;
        if (!selectedLang) return;
        i18n.setLanguage(selectedLang);
        window.authController?.showToast?.(i18n.t('toastLangChanged'));
      });
    });

    // Cập nhật DOM theo ngôn ngữ lưu trong máy
    i18n.updateDomTranslations();

    // 2. Dark Mode Toggle
    const btnThemeToggle = document.getElementById('btn-header-theme-toggle');
    const prefThemeSelect = document.getElementById('pref-theme-select');
    const moonIcon = btnThemeToggle?.querySelector('.theme-icon-moon');
    const sunIcon = btnThemeToggle?.querySelector('.theme-icon-sun');

    const getSavedTheme = () => {
      try {
        return localStorage.getItem('hue_theme') || 'system';
      } catch {
        return 'system';
      }
    };

    const updateThemeUI = (effectiveTheme, themeChoice) => {
      document.documentElement.setAttribute('data-theme', effectiveTheme);

      if (effectiveTheme === 'dark') {
        moonIcon?.classList.add('hidden');
        sunIcon?.classList.remove('hidden');
        btnThemeToggle?.setAttribute('title', i18n.t('themeToggleLight'));
        btnThemeToggle?.setAttribute('aria-label', i18n.t('themeToggleLight'));
      } else {
        moonIcon?.classList.remove('hidden');
        sunIcon?.classList.add('hidden');
        btnThemeToggle?.setAttribute('title', i18n.t('themeToggleDark'));
        btnThemeToggle?.setAttribute('aria-label', i18n.t('themeToggleDark'));
      }

      if (prefThemeSelect && prefThemeSelect.value !== themeChoice) {
        prefThemeSelect.value = themeChoice;
      }
    };

    const applyTheme = (themeChoice) => {
      let effective = themeChoice;
      if (themeChoice === 'system') {
        const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        effective = systemPrefersDark ? 'dark' : 'light';
      }
      updateThemeUI(effective, themeChoice);
    };

    // Áp dụng theme ban đầu
    applyTheme(getSavedTheme());

    // Nút toggle trên Header
    btnThemeToggle?.addEventListener('click', () => {
      const currentEffective = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = currentEffective === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem('hue_theme', nextTheme);
      } catch { }
      applyTheme(nextTheme);
      window.authController?.showToast?.(
        nextTheme === 'dark' ? i18n.t('toastThemeDark') : i18n.t('toastThemeLight')
      );
    });

    // Tùy chọn trong Settings Modal
    prefThemeSelect?.addEventListener('change', (e) => {
      const selected = e.target.value;
      try {
        localStorage.setItem('hue_theme', selected);
      } catch { }
      applyTheme(selected);
      window.authController?.showToast?.(i18n.t('toastThemeDark'));
    });

    // Lắng nghe thay đổi theme từ hệ thống khi để "system"
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (getSavedTheme() === 'system') {
          applyTheme('system');
        }
      });
    }

    // Khi ngôn ngữ thay đổi, cập nhật tooltip của nút theme và các widget reactive
    window.addEventListener('hue:language-change', () => {
      const currentEffective = document.documentElement.getAttribute('data-theme') || 'light';
      btnThemeToggle?.setAttribute(
        'title',
        currentEffective === 'dark' ? i18n.t('themeToggleLight') : i18n.t('themeToggleDark')
      );
      initHueWeatherWidget();
      updateMapToggleUI(!studioLayout?.classList.contains('map-collapsed'));
      checkBackendStatus();
      updatePlannerOriginDisplay();
      refreshChatHistoryList(false);

      // Nếu đang ở màn hình chào mừng (chưa có tin nhắn), re-render hero bằng ngôn ngữ mới
      const welcomeHero = document.getElementById('chat-welcome-hero');
      if (welcomeHero && activeSessionMessages.length === 0) {
        renderWelcomeHero();
      }

      // Re-render Sổ tay du lịch nếu đang mở
      if (notebookModal?.classList.contains('active')) {
        if (tabWishlist?.classList.contains('active')) {
          renderWishlist(searchWishlistInput?.value || '');
        } else if (tabCheckin?.classList.contains('active')) {
          renderCheckinList(currentCheckinCategory);
        }
      }
    });
  };

  initSettingsModal();
  initThemeAndLanguage();

  btnToggleSidebar?.addEventListener('click', () => toggleSidebar());
  btnSidebarToggle?.addEventListener('click', () => toggleSidebar());
  btnSidebarCollapse?.addEventListener('click', () => toggleSidebar());
  sidebarBackdrop?.addEventListener('click', () => toggleSidebar(false));

  btnNewChat?.addEventListener('click', () => startNewChatSession());
  btnSidebarNewChat?.addEventListener('click', () => {
    startNewChatSession();
    if (window.innerWidth <= 1024) toggleSidebar(false);
  });

  btnToggleChatHistory?.addEventListener('click', () => toggleSidebar());

  btnWorkbenchSavedTours?.addEventListener('click', () => {
    if (window.authController) {
      if (!window.authController.currentUser) {
        window.authController.openAuthModal('login');
        window.authController.showToast(i18n.t('loginToViewSavedTours', 'Vui lòng đăng nhập để xem các lịch trình đã lưu.'));
      } else {
        window.authController.openSavedToursModal();
      }
    }
  });

  btnSidebarSavedTours?.addEventListener('click', () => {
    if (window.authController) {
      if (!window.authController.currentUser) {
        window.authController.openAuthModal('login');
        window.authController.showToast(i18n.t('loginToViewSavedTours', 'Vui lòng đăng nhập để xem các lịch trình đã lưu.'));
      } else {
        window.authController.openSavedToursModal();
      }
    }
    if (window.innerWidth <= 1024) toggleSidebar(false);
  });

  btnSidebarToggleMap?.addEventListener('click', () => {
    toggleMapPanel();
    if (window.innerWidth <= 1024) toggleSidebar(false);
  });

  // Tự động làm mới danh sách session và cập nhật user profile khi auth thay đổi
  onAuthChange((user) => {
    refreshChatHistoryList();
    updateSidebarUserProfile(user);
  });

  // Tải danh sách session ban đầu
  refreshChatHistoryList();

  // attachment = null  → dùng ảnh đang đính kèm ở ô nhập (gửi tin nhắn bình thường).
  // attachment = { image, storageThumb } → dùng đúng ảnh này (nút "Tạo lại"), không đụng tới
  //   ảnh/chữ người dùng đang soạn dở ở ô nhập.
  /**
   * Trí nhớ phiên chat đa lượt: lấy tối đa 4 tin nhắn văn bản gần nhất (2 lượt hỏi-đáp, không kèm ảnh)
   * và mốc ngữ cảnh (session_context) mà server trả về ở lượt trả lời gần nhất. session_context đã nằm
   * sẵn trong resData của tin nhắn trợ lý được lưu Firestore nên mở lại phiên cũ vẫn nhớ ngữ cảnh.
   * Khi "Tạo lại" một câu hỏi, bỏ cặp hỏi-đáp cũ của chính câu đó để không tự tham chiếu vào nó.
   */
  function buildConversationMemory(query, isRegenerate) {
    let messages = activeSessionMessages || [];
    if (isRegenerate) {
      for (let i = messages.length - 1; i >= 0; i--) {
        const m = messages[i];
        if (m.role === 'user' && (m.text || m.content || '').trim() === query) {
          messages = messages.slice(0, i);
          break;
        }
      }
    }

    const history = messages
      .filter(m => (m.role === 'user' || m.role === 'assistant') && !m.isItinerary)
      .map(m => ({ role: m.role, text: String(m.text || m.content || '').trim().slice(0, 400) }))
      .filter(m => m.text)
      .slice(-4);

    let sessionContext = null;
    for (let i = messages.length - 1; i >= 0; i--) {
      const ctx = messages[i].role === 'assistant' ? messages[i].resData?.session_context : null;
      if (ctx) { sessionContext = ctx; break; }
    }
    // Fallback cho tin nhắn cũ chỉ còn matched_places:
    if (!sessionContext) {
      for (let i = messages.length - 1; i >= 0; i--) {
        const m = messages[i];
        if (m.role === 'assistant') {
          const firstPlace = m.resData?.matched_places?.[0];
          if (firstPlace && firstPlace.name) {
            sessionContext = inferContextFromPlace(firstPlace);
            break;
          }
        }
      }
    }
    if (!sessionContext && activeSessionContext) {
      sessionContext = activeSessionContext;
    }

    return { sessionId: activeSessionId, history, sessionContext };
  }

  async function sendChatQuery(query, attachment = null) {
    const usePendingInput = attachment === null;
    const activeImage = usePendingInput ? currentAttachedImageBase64 : (attachment.image || null);
    const activeStorageImage = usePendingInput
      ? currentAttachedImageStorageBase64
      : (attachment.storageThumb || attachment.image || null);
    const trimmedQuery = (query !== undefined && query !== null) ? String(query).trim() : '';

    // Cho phép gửi nếu có query HOẶC có ảnh
    if (!trimmedQuery && !activeImage) return;

    // Xóa Welcome Hero khi bắt đầu chat
    const hero = document.getElementById('chat-welcome-hero');
    if (hero) hero.remove();

    // Kiểm tra câu hỏi có liên quan đến vị trí/không gian/chỉ đường/bản đồ
    const isSpatialQuery = /chỉ đường|đường đi|đi đến|từ .+ đi|khoảng cách|cách bao xa|gần đây|quanh đây|ở đâu|vị trí|tọa độ|bản đồ|lộ trình|tour|thuê xe/i.test(trimmedQuery);

    // Kiểm tra nếu người dùng yêu cầu lập lịch trình qua câu chat
    const lowerQuery = trimmedQuery.toLowerCase();
    const isPlanIntent = (
      lowerQuery.includes('lập lịch trình') ||
      lowerQuery.includes('tạo lịch trình') ||
      lowerQuery.includes('gợi ý lịch trình') ||
      lowerQuery.includes('lên lịch trình') ||
      lowerQuery.includes('lên tour') ||
      lowerQuery.includes('lập tour') ||
      lowerQuery.includes('tour du lịch')
    );

    if ((isPlanIntent || isSpatialQuery || activeImage) && localStorage.getItem('hue_pref_auto_map') !== 'false') {
      showMapPanel(true); // Tự động mở bản đồ theo ngữ cảnh không gian / ảnh
    }

    if (isPlanIntent && !activeImage) {
      let days = 2;
      if (lowerQuery.includes('1 ngày') || lowerQuery.includes('một ngày')) days = 1;
      else if (lowerQuery.includes('3 ngày') || lowerQuery.includes('ba ngày')) days = 3;
      else if (lowerQuery.includes('2 ngày') || lowerQuery.includes('hai ngày')) days = 2;

      const tripType = selectTripType ? selectTripType.value : 'Couples';
      const preferredDishes = getSelectedDishes();
      if (usePendingInput && chatInput) chatInput.value = '';
      generateItineraryInChat(days, tripType, preferredDishes);
      return;
    }

    // Hiển thị tin nhắn người dùng: khung chat dùng bản 1600px, lưu Firestore dùng thumbnail 520px
    const isEn = i18n.getLanguage() === 'en';
    const displayPrompt = trimmedQuery || (activeImage ? (isEn ? 'Analyze landmark or dish in this photo' : 'Phân tích địa danh hoặc món ăn trong ảnh này') : '');
    // Chụp trí nhớ hội thoại TRƯỚC khi đẩy câu hỏi hiện tại vào phiên
    const conversationMemory = buildConversationMemory(displayPrompt, !usePendingInput);
    lastUserPrompt = displayPrompt;
    appendUserMessage(displayPrompt, true, activeImage, activeStorageImage);

    // Dọn sạch ảnh đính kèm và input (chỉ khi gửi từ ô nhập)
    if (usePendingInput) {
      clearAttachedImage();
      if (chatInput) chatInput.value = '';
    }
    if (chatSendBtn) chatSendBtn.disabled = true;

    // Hiển thị loading placeholder
    const loadingText = activeImage
      ? (isEn ? 'Identifying & analyzing photo...' : 'Đang nhận diện & phân tích ...')
      : (isEn ? 'Analyzing query...' : 'Đang phân tích ...');
    const loadingId = appendAssistantLoading(loadingText);

    try {
      // Truyền tọa độ GPS người dùng nếu đã có định vị & hồ sơ gu du lịch cá nhân hóa
      const userLat = mapStudio.userLocation ? mapStudio.userLocation.lat : null;
      const userLng = mapStudio.userLocation ? mapStudio.userLocation.lng : null;
      const userPrefs = userStore.getPreferences();

      const res = await TourismApiClient.askAssistant(
        trimmedQuery, isEn ? 'Hue City' : 'Thành phố Huế', userLat, userLng, userPrefs, activeImage, conversationMemory
      );
      removeLoadingMessage(loadingId);
      appendAssistantResponse(res, true, displayPrompt, { image: activeImage, storageThumb: activeStorageImage });
    } catch (err) {
      removeLoadingMessage(loadingId);
      appendAssistantError(err.message);
    } finally {
      if (chatSendBtn) chatSendBtn.disabled = false;
      if (chatInput) chatInput.focus();
    }
  }

  chatForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = chatInput?.value?.trim() || '';
    sendChatQuery(query);
  });

  // Lightbox xem ảnh đính kèm ngay trong trang (đóng bằng nút ×, click nền hoặc phím Esc)
  let imageLightbox = null;

  function closeImageLightbox() {
    if (!imageLightbox?.classList.contains('open')) return;
    imageLightbox.classList.remove('open');
    imageLightbox.querySelector('img').removeAttribute('src');
    document.body.style.overflow = '';
  }

  function openImageLightbox(src) {
    if (!src) return;
    if (!imageLightbox) {
      imageLightbox = document.createElement('div');
      imageLightbox.className = 'image-lightbox';
      imageLightbox.setAttribute('role', 'dialog');
      imageLightbox.setAttribute('aria-modal', 'true');
      const isEn = i18n.getLanguage() === 'en';
      imageLightbox.setAttribute('aria-label', isEn ? 'View attached photo' : 'Xem ảnh đính kèm');
      imageLightbox.innerHTML = `
        <button type="button" class="image-lightbox-close" aria-label="${isEn ? 'Close' : 'Đóng'}">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <img class="image-lightbox-img" alt="${isEn ? 'Attached photo enlarged' : 'Ảnh đính kèm phóng to'}" />
      `;
      imageLightbox.addEventListener('click', (e) => {
        if (e.target === imageLightbox || e.target.closest('.image-lightbox-close')) closeImageLightbox();
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeImageLightbox();
      });
      document.body.appendChild(imageLightbox);
    }
    imageLightbox.querySelector('img').src = src;
    imageLightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
    imageLightbox.querySelector('.image-lightbox-close').focus();
  }

  function appendUserMessage(text, persist = true, imageBase64 = null, storageThumbBase64 = null) {
    const safeText = (text !== undefined && text !== null) ? String(text).trim() : '';
    if (!safeText && !imageBase64) return;

    const msg = document.createElement('div');
    msg.className = `chat-message user${imageBase64 ? ' has-image' : ''}`;

    let imageHtml = '';
    if (imageBase64) {
      const isEn = i18n.getLanguage() === 'en';
      imageHtml = `
        <div class="chat-attached-image-container">
          <img src="${imageBase64}" class="chat-attached-image" alt="${isEn ? 'Attached photo' : 'Ảnh đính kèm'}" title="${isEn ? 'Click to view full size' : 'Nhấp để xem kích thước lớn'}" />
        </div>
      `;
    }

    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
      <div class="message-bubble${imageBase64 ? ' has-image' : ''}">
        ${imageHtml}
        ${safeText ? `<p class="chat-user-caption">${escapeHtml(safeText)}</p>` : ''}
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;

    // Xem ảnh kích thước lớn khi nhấp chuột
    msg.querySelector('.chat-attached-image')?.addEventListener('click', (e) => {
      openImageLightbox(e.currentTarget.src);
    });

    if (persist && !isRestoringSession) {
      activeSessionMessages.push({
        role: 'user',
        text: safeText,
        content: safeText,
        imageBase64: storageThumbBase64 || imageBase64 || null,
        hasImage: !!imageBase64,
        timestamp: Date.now()
      });
      persistActiveSession();
    }
  }

  function appendAssistantLoading(customText = null) {
    const isEn = i18n.getLanguage() === 'en';
    const text = customText || (isEn ? 'Analyzing spatial context and synthesizing suggestions...' : 'Đang phân tích không gian và tổng hợp gợi ý...');
    const id = `loading-${Date.now()}`;
    const msg = document.createElement('div');
    msg.id = id;
    msg.className = 'chat-message assistant';
    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/></svg>
      </div>
      <div class="message-bubble">
        <div class="message-author">${i18n.t('assistantName', 'Trợ lý Cố đô')}</div>
        <p class="loading-text">${text}</p>
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;
    return id;
  }

  function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // =============================================================================
  // XAI: GIẢI THÍCH CHUỖI SUY LUẬN ĐỒ THỊ MINH BẠCH (EXPLAINABLE GRAPH TRACE)
  // =============================================================================
  function createGraphTraceHtml(trace, routeTaken = 'local_knowledge', confidenceScore = 0.88) {
    if (!trace || !Array.isArray(trace) || trace.length === 0) return '';

    const isEn = i18n.getLanguage() === 'en';
    const confPct = Math.round((confidenceScore || 0.85) * 100);
    const isWeb = routeTaken === 'web_fallback';
    const routeLabel = isWeb ? 'Web Search (DuckDuckGo)' : (isEn ? 'Hue Heritage Knowledge' : 'Tri thức Cố đô');

    const stepsHtml = trace.map((step, idx) => {
      const label = step.label || step.step;
      const detail = step.detail || '';

      let metricHtml = '';
      if (step.score !== undefined) {
        metricHtml = `<span class="xai-step-metric">${(step.score * 100).toFixed(0)}%</span>`;
      } else if (step.count !== undefined) {
        metricHtml = `<span class="xai-step-metric">${step.count} ${isEn ? 'results' : 'kết quả'}</span>`;
      } else if (step.decision) {
        const decText = step.decision === 'local_knowledge' ? (isEn ? 'Internal Knowledge' : 'Tri thức nội bộ') : 'Web Fallback';
        metricHtml = `<span class="xai-step-metric">${decText}</span>`;
      }

      let extraWidgetHtml = '';
      if (step.step === 'confidence_scoring' && step.score !== undefined) {
        const pct = Math.min(100, Math.max(0, Math.round(step.score * 100)));
        extraWidgetHtml = `
          <div class="xai-confidence-meter">
            <div class="xai-meter-track">
              <div class="xai-meter-fill" style="width: ${pct}%"></div>
            </div>
            <span class="xai-meter-val">${pct}%</span>
          </div>
        `;
      }

      return `
        <div class="xai-timeline-item" data-step-type="${step.step}">
          <span class="xai-step-num">${String(idx + 1).padStart(2, '0')}</span>
          <div class="xai-step-body">
            <div class="xai-step-header">
              <span class="xai-step-title">${label}</span>
              ${metricHtml}
            </div>
            ${detail ? `<div class="xai-step-desc">${detail}</div>` : ''}
            ${extraWidgetHtml}
          </div>
        </div>
      `;
    }).join('');

    return `
      <div class="xai-trace-wrapper">
        <button type="button" class="xai-trace-toggle" aria-expanded="false" title="${isEn ? 'View GraphRAG reasoning process' : 'Xem tiến trình suy luận GraphRAG'}">
          <svg class="xai-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"/></svg>
          <span class="xai-trace-label">${isEn ? `Used ${trace.length} retrieval steps` : `Đã dùng ${trace.length} bước truy xuất`}</span>
          <span class="xai-trace-meta">${routeLabel} · ${confPct}%</span>
        </button>

        <div class="xai-trace-drawer">
          <div class="xai-drawer-inner">
            <div class="xai-drawer-header">
              <span class="xai-drawer-title">${isEn ? 'Retrieval & Reasoning Process' : 'Tiến trình truy xuất &amp; lập luận'}</span>
              <span class="xai-drawer-tag">LangGraph · NetworkX KG · ChromaDB</span>
            </div>

            <div class="xai-timeline">
              ${stepsHtml}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // attachment: ảnh của câu hỏi tương ứng (nếu có) — giữ lại để nút "Tạo lại" gửi kèm
  function appendAssistantResponse(res, persist = true, promptText = '', attachment = null) {
    const isEn = i18n.getLanguage() === 'en';
    const msg = document.createElement('div');
    msg.className = 'chat-message assistant';

    const messageId = res.messageId || `msg_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const savedRating = res.feedbackRating || null;
    const finalPrompt = promptText || res.prompt || lastUserPrompt || '';

    const rawAnswer = res.answer || res.text || res.content || '';
    const formattedAnswer = rawAnswer
      ? escapeHtml(rawAnswer)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>')
      : '';

    // Khối thẻ chỉ đường nếu phản hồi có điều hướng (Navigation Intent)
    let navCardHtml = '';
    const nav = res.navigation;
    const isNav = Boolean(nav && nav.is_navigation && nav.origin && nav.destination);

    if (isNav) {
      showMapPanel(true); // Tự động mở bản đồ theo ngữ cảnh chỉ đường
      const origin = nav.origin;
      const destination = nav.destination;
      const profile = nav.profile || 'driving';
      const isWalking = profile === 'walking';

      // Chuẩn hóa tên trường tọa độ (lat/latitude, lng/longitude)
      origin.lat = origin.lat || origin.latitude;
      origin.lng = origin.lng || origin.longitude;
      destination.lat = destination.lat || destination.latitude;
      destination.lng = destination.lng || destination.longitude;

      // Nếu origin chưa có tọa độ nhưng người dùng đã định vị, điền tọa độ GPS người dùng
      if ((!origin.lat || !origin.lng) && mapStudio.userLocation) {
        origin.lat = mapStudio.userLocation.lat;
        origin.lng = mapStudio.userLocation.lng;
        origin.name = mapStudio.userLocation.name || i18n.t('userLocationHere', 'Vị trí của bạn');
      }

      // Fallback nếu vẫn thiếu tọa độ origin: Cầu Tràng Tiền (Trung tâm Huế)
      if (!origin.lat || !origin.lng) {
        origin.lat = 16.4674;
        origin.lng = 107.5905;
        origin.name = origin.name || i18n.t('defaultHueCenter', 'Cầu Tràng Tiền (Trung tâm Huế)');
      }

      // Tính khoảng cách ước lượng ban đầu
      const R = 6371;
      const dLat = (destination.lat - origin.lat) * Math.PI / 180;
      const dLon = (destination.lng - origin.lng) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(origin.lat * Math.PI / 180) * Math.cos(destination.lat * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
      // Ưu tiên cự ly đường bộ chuẩn xác từ Backend Spatial Ground Truth Engine
      const rawHaversine = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      const estDistKm = (nav.distance_km != null)
        ? parseFloat(nav.distance_km).toFixed(1)
        : Math.max(0.8, rawHaversine * 1.6).toFixed(1);
      const estDurationMin = (nav.duration_min != null)
        ? nav.duration_min
        : Math.max(2, Math.round(parseFloat(estDistKm) * 2.5));

      const gmapsDirUrl = `https://www.google.com/maps/dir/?api=1&origin=${origin.lat},${origin.lng}&destination=${destination.lat},${destination.lng}`;
      const navCardId = `nav-card-${Date.now()}`;

      navCardHtml = `
        <div class="chat-nav-card" id="${navCardId}">
          <div class="nav-card-header">
            <div class="nav-card-header-main">
              <div class="nav-card-icon-badge">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
              </div>
              <div>
                <div class="nav-card-title">${i18n.t('navRouteOptimal', 'Lộ trình Chỉ đường Tối ưu')}</div>
                <div class="nav-card-subtitle">${isWalking ? (isEn ? 'Scenic walking route' : 'Tuyến đi bộ ngắm cảnh') : (isEn ? 'Motorbike / Car via inner city routes' : 'Xe máy / Ô tô theo đường nội đô Huế')}</div>
              </div>
            </div>
            <div class="nav-card-badge-metrics">
              <span class="nav-metric-pill nav-metric-dist">~${estDistKm} km</span>
              <span class="nav-metric-pill highlight nav-metric-dur">~${estDurationMin} ${isEn ? 'mins' : 'phút'}</span>
            </div>
          </div>

          <div class="nav-card-body">
            <div class="nav-route-row origin">
              <div class="route-marker-badge origin">A</div>
              <div class="route-point-content">
                <div class="route-point-label">${i18n.t('navPointDepart', 'Điểm khởi hành')}</div>
                <div class="route-point-name">${origin.name}</div>
              </div>
            </div>

            <div class="nav-route-divider">
              <div class="divider-line"></div>
              <div class="divider-arrow">↓</div>
              <div class="divider-line"></div>
            </div>

            <div class="nav-route-row destination">
              <div class="route-marker-badge dest">B</div>
              <div class="route-point-content">
                <div class="route-point-label">${i18n.t('navPointDest', 'Điểm đến')}</div>
                <div class="route-point-name">${destination.name}</div>
                ${destination.address ? `<div class="route-point-address">📍 ${destination.address}</div>` : ''}
              </div>
            </div>
          </div>

          <div class="nav-card-actions">
            <button type="button" class="btn-nav-replot" data-origin-lat="${origin.lat}" data-origin-lng="${origin.lng}" data-origin-name="${origin.name}" data-dest-lat="${destination.lat}" data-dest-lng="${destination.lng}" data-dest-name="${destination.name}" data-profile="${profile}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
              <span>${i18n.t('navReplotBtn', 'Vẽ lại trên Bản đồ')}</span>
            </button>
            <a href="${gmapsDirUrl}" target="_blank" rel="noopener noreferrer" class="btn-nav-gmaps" title="${isEn ? 'Open directions on Google Maps app' : 'Mở chỉ đường trên ứng dụng Google Maps'}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
              <span>${i18n.t('navGmapsBtn', 'Mở Google Maps')}</span> &rarr;
            </a>
          </div>
        </div>
      `;

      // Tự động vẽ lộ trình thực tế lên bản đồ Leaflet và đồng bộ cự ly OSRM vào Thẻ Lộ trình
      setTimeout(async () => {
        try {
          const routeRes = await mapStudio.drawNavigationRoute(origin, destination, profile);
          if (routeRes && routeRes.distanceKm) {
            const cardEl = document.getElementById(navCardId);
            if (cardEl) {
              const distEl = cardEl.querySelector('.nav-metric-dist');
              const durEl = cardEl.querySelector('.nav-metric-dur');
              if (distEl) distEl.textContent = `~${routeRes.distanceKm} km`;
              if (durEl) durEl.textContent = `~${routeRes.durationMin} ${isEn ? 'mins' : 'phút'}`;
            }
          }
        } catch (e) {
          console.warn('Lỗi đồng bộ OSRM vào Thẻ Lộ trình:', e);
        }
      }, 200);
    }

    // Chỉ hiển thị các pill gợi ý địa điểm khi KHÔNG PHẢI câu hỏi chỉ đường (tránh làm loãng thông tin)
    let placesPillsHtml = '';
    const matched = res.matched_places || [];
    if (matched.length > 0 && !isNav) {
      placesPillsHtml = `
        <div class="chat-suggested-places">
          <div class="suggested-places-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
            <span>${i18n.t('suggestedDestOnMap', 'Điểm đến gợi ý trên bản đồ:')}</span>
          </div>
          <div class="suggested-places-list">
            ${matched.map(p => {
        const catLower = (p.category || '').toLowerCase();
        const isFood = catLower.includes('restaurant') || catLower.includes('ẩm thực') || catLower.includes('quán');
        const isCafe = catLower.includes('cafe') || catLower.includes('cà phê');
        const isHotel = catLower.includes('hotel') || catLower.includes('khách sạn');

        let catClass = 'attraction';
        let iconSvg = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/></svg>`;

        if (isFood) {
          catClass = 'restaurant';
          iconSvg = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 2v8a3 3 0 0 1-6 0V2M15 10v12M6 2v20M3 2h6"/></svg>`;
        } else if (isCafe) {
          catClass = 'cafe';
          iconSvg = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/></svg>`;
        } else if (isHotel) {
          catClass = 'hotel';
          iconSvg = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/></svg>`;
        }

        const safePoiName = escapeHtml(p.name || '');
        const safePlaceId = escapeHtml(p.place_id || p.node_id || '');

        return `
                <button type="button" class="chat-poi-btn ${catClass}" data-lat="${p.latitude}" data-lng="${p.longitude}" data-name="${safePoiName}" data-place-id="${safePlaceId}" title="${i18n.t('pinOnMap', 'Ghim điểm này lên bản đồ')}">
                  <span class="poi-btn-icon">${iconSvg}</span>
                  <span class="poi-btn-name">${safePoiName}</span>
                  <span class="poi-btn-action">&rarr;</span>
                </button>
              `;
      }).join('')}
          </div>
        </div>
      `;
    }

    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/></svg>
      </div>
      <div class="message-bubble">
        <div class="message-author">${i18n.t('assistantName', 'Trợ lý Cố đô')}</div>
        <div class="answer-content">${formattedAnswer}</div>
        ${createGraphTraceHtml(res.graph_trace, res.route_taken, res.confidence_score)}
        ${navCardHtml}
        ${placesPillsHtml}
        ${createFeedbackBarHtml(messageId, savedRating)}
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;

    // Gán sự kiện mở/đóng XAI Graph Trace Panel
    msg.querySelectorAll('.xai-trace-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        const wrapper = btn.closest('.xai-trace-wrapper');
        if (!wrapper) return;
        const isExpanded = wrapper.classList.toggle('is-expanded');
        btn.setAttribute('aria-expanded', isExpanded);
      });
    });

    // Gán sự kiện Feedback (Thích / Chưa tốt / Sao chép)
    bindFeedbackEvents(msg, {
      messageId: messageId,
      prompt: finalPrompt,
      plainText: res.answer || '',
      isItinerary: false,
      imageBase64: attachment?.image || null,
      storageThumb: attachment?.storageThumb || null
    });

    // Gán sự kiện click nút vẽ lại trên bản đồ trong thẻ lộ trình
    msg.querySelectorAll('.btn-nav-replot').forEach(btn => {
      btn.addEventListener('click', () => {
        showMapPanel(true);
        const oLat = parseFloat(btn.dataset.originLat);
        const oLng = parseFloat(btn.dataset.originLng);
        const oName = btn.dataset.originName;
        const dLat = parseFloat(btn.dataset.destLat);
        const dLng = parseFloat(btn.dataset.destLng);
        const dName = btn.dataset.destName;
        const prof = btn.dataset.profile || 'driving';

        mapStudio.drawNavigationRoute(
          { lat: oLat, lng: oLng, name: oName },
          { lat: dLat, lng: dLng, name: dName },
          prof
        );
      });
    });

    // Gán sự kiện click vào các nút địa điểm trong chat bubble: Ghim bản đồ + Mở Drawer
    msg.querySelectorAll('.chat-poi-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        showMapPanel(true);
        const lat = parseFloat(btn.dataset.lat);
        const lng = parseFloat(btn.dataset.lng);
        const name = btn.dataset.name;
        const placeId = btn.dataset.placeId || null;
        mapStudio.panTo(lat, lng, 17);
        if (name && window.openPoiDetail) {
          window.openPoiDetail(name, placeId);
        }
      });
    });

    // TỰ ĐỘNG VẼ CÁC ĐỊA ĐIỂM ĐƯỢC GỢI Ý LÊN BẢN ĐỒ BÊN CẠNH NGAY LẬP TỨC
    if (matched.length > 0 && !(nav && nav.is_navigation) && localStorage.getItem('hue_pref_auto_map') !== 'false') {
      mapStudio.highlightChatPlaces(matched);
    }

    // Cập nhật trạng thái ngữ cảnh phiên chat hiện tại
    if (res && res.session_context) {
      activeSessionContext = res.session_context;
    }

    // Lưu phản hồi trợ lý vào phiên chat hiện tại
    if (persist && !isRestoringSession) {
      activeSessionMessages.push({
        id: messageId,
        role: 'assistant',
        text: res.answer || '',
        prompt: finalPrompt,
        resData: res,
        feedbackRating: savedRating,
        timestamp: Date.now()
      });
      persistActiveSession();
    }
  }

  function appendAssistantError(errorMsg) {
    const isEn = i18n.getLanguage() === 'en';
    const errPrefix = isEn ? 'Query Error' : 'Lỗi truy vấn';
    const errSuffix = isEn ? 'Please check your Backend connection.' : 'Vui lòng kiểm tra lại kết nối Backend.';
    const msg = document.createElement('div');
    msg.className = 'chat-message assistant';
    msg.innerHTML = `
      <div class="message-avatar">⚠️</div>
      <div class="message-bubble" style="border-color: #EF4444;">
        <p style="color: #DC2626;">${errPrefix}: ${errorMsg}. ${errSuffix}</p>
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;
  }

  // =============================================================================
  // 8. MODAL / DRAWER XEM CHI TIẾT ĐỊA ĐIỂM (POI DEEP-DIVE PANEL)
  // Khai phá cạnh SERVES, cạnh NEAR_BY, điểm đánh giá & review thực tế TripAdvisor
  // =============================================================================
  const poiDrawer = document.getElementById('poi-drawer');
  const poiDrawerBackdrop = document.getElementById('poi-drawer-backdrop');
  const btnCloseDrawer = document.getElementById('btn-close-drawer');
  const poiCatBadge = document.getElementById('poi-cat-badge');
  const poiRatingVal = document.getElementById('poi-rating-val');
  const poiReviewCount = document.getElementById('poi-review-count');
  const poiTitle = document.getElementById('poi-title');
  const poiAddressText = document.getElementById('poi-address-text');
  const poiDescText = document.getElementById('poi-desc-text');
  const poiSectionReviews = document.getElementById('poi-section-reviews');
  const poiReviewsList = document.getElementById('poi-reviews-list');
  const poiSectionNearby = document.getElementById('poi-section-nearby');
  const poiNearbyList = document.getElementById('poi-nearby-list');
  const poiBtnGoogleMaps = document.getElementById('poi-btn-google-maps');
  const poiBtnDirectNav = document.getElementById('poi-btn-direct-nav');
  const poiBtnAddTour = document.getElementById('poi-btn-add-tour');
  const poiBtnAskAi = document.getElementById('poi-btn-ask-ai');
  const poiBtnFavorite = document.getElementById('poi-btn-favorite');
  const poiBtnCheckin = document.getElementById('poi-btn-checkin');
  const poiFavLabel = document.getElementById('poi-fav-label');
  const poiCheckinLabel = document.getElementById('poi-checkin-label');

  let currentPoiData = null;

  function updateDrawerUserStatus(targetName, targetId) {
    const isEn = i18n.getLanguage() === 'en';
    const isFav = userStore.isFavorite(targetId || targetName);
    const isCheck = userStore.isCheckedIn(targetId || targetName);

    if (poiBtnFavorite) {
      poiBtnFavorite.classList.toggle('active', isFav);
      if (poiFavLabel) poiFavLabel.textContent = isFav ? i18n.t('poiFavDone', 'Đã thích') : i18n.t('poiFavLabel', 'Yêu thích');
      poiBtnFavorite.title = isFav ? (isEn ? 'Remove from favorites' : 'Bỏ lưu yêu thích') : (isEn ? 'Save to notebook' : 'Lưu vào sổ tay yêu thích');
      const favSvg = poiBtnFavorite.querySelector('svg');
      if (favSvg) favSvg.setAttribute('fill', isFav ? 'currentColor' : 'none');
    }

    if (poiBtnCheckin) {
      poiBtnCheckin.classList.toggle('active', isCheck);
      if (poiCheckinLabel) poiCheckinLabel.textContent = isCheck ? i18n.t('poiCheckinDone', 'Đã check-in') : i18n.t('poiCheckinLabel', 'Check-in');
      poiBtnCheckin.title = isCheck ? (isEn ? 'Undo check-in' : 'Hủy check-in') : (isEn ? 'Mark as visited' : 'Đánh dấu đã ghé thăm');
    }
  }

  async function openPoiDetail(name, placeId = null) {
    if (!name && !placeId) return;
    const isEn = i18n.getLanguage() === 'en';
    showMapPanel(true); // Hiển thị bản đồ để người dùng quan sát vị trí địa điểm

    // 1. Mở Drawer ngay lập tức với trạng thái sẵn sàng
    poiDrawer?.classList.add('open');
    poiDrawer?.setAttribute('aria-hidden', 'false');

    // Tìm dữ liệu địa phương từ masterLandmarks để hiển thị tức thì (Zero-latency fallback)
    const localPlace = window.mapStudio?.masterLandmarks?.find(p =>
      (placeId && p.place_id === placeId) || (name && p.name === name)
    );

    const initialName = localPlace?.name || name || i18n.t('poiLoadingInfo', 'Đang tải thông tin...');
    if (poiTitle) poiTitle.textContent = initialName;
    if (poiAddressText) poiAddressText.textContent = localPlace?.address || localPlace?.desc || (isEn ? 'Hue City' : 'Thành phố Huế');
    if (poiDescText) poiDescText.textContent = localPlace?.desc || i18n.t('poiLoadingDesc', 'Đang đồng bộ hồ sơ văn hóa và điểm đánh giá...');

    // Cập nhật trạng thái Yêu thích & Check-in ngay lập tức
    updateDrawerUserStatus(initialName, placeId);

    // Cập nhật nhãn category & rating sơ bộ từ dữ liệu bản đồ
    const initialCat = (localPlace?.cat || 'Attraction').toLowerCase();
    let initialCatClass = 'attraction';
    let initialCatIcon = '🏯';
    let initialCatLabel = i18n.t('legendAttraction', 'Di tích & Thắng cảnh');

    if (initialCat.includes('restaurant') || initialCat.includes('ẩm thực') || initialCat.includes('quán')) {
      initialCatClass = 'restaurant';
      initialCatIcon = '🍲';
      initialCatLabel = i18n.t('legendRestaurant', 'Ẩm thực Cố đô');
    } else if (initialCat.includes('cafe') || initialCat.includes('cà phê') || initialCat.includes('sunset')) {
      initialCatClass = 'cafe';
      initialCatIcon = '☕';
      initialCatLabel = i18n.t('legendCafe', 'Cà phê & Sunset');
    } else if (initialCat.includes('hotel') || initialCat.includes('khách sạn') || initialCat.includes('resort')) {
      initialCatClass = 'hotel';
      initialCatIcon = '🏨';
      initialCatLabel = i18n.t('legendHotel', 'Khách sạn / Resort');
    }

    if (poiCatBadge) {
      poiCatBadge.className = `poi-cat-badge ${initialCatClass}`;
      poiCatBadge.textContent = `${initialCatIcon} ${initialCatLabel}`;
    }
    if (poiRatingVal) poiRatingVal.textContent = (localPlace?.rating_value || 4.6).toFixed(1);
    if (poiReviewCount) poiReviewCount.textContent = `(${localPlace?.review_count || 350} ${i18n.t('reviewsCount', 'đánh giá')})`;

    if (poiReviewsList) {
      if (localPlace?.reviews && localPlace.reviews.length > 0) {
        if (poiSectionReviews) poiSectionReviews.style.display = 'flex';
        poiReviewsList.innerHTML = localPlace.reviews.map(r => `
          <div class="poi-review-card">
            <div class="review-header">
              <span class="review-stars">${'⭐'.repeat(Math.round(r.rating || 5))}</span>
              <span class="review-tag">👤 ${r.trip_type || i18n.t('tourist', 'Du khách')} · ${r.visit_date || '2024'}</span>
            </div>
            <h5 class="review-title">${r.title}</h5>
            <p class="review-comment">“${r.comment}”</p>
          </div>
        `).join('');
      } else {
        poiReviewsList.innerHTML = `<div style="font-size: 0.78rem; color: var(--color-ink-muted); padding: 6px 0;">${i18n.t('poiReviewSyncing', 'Đang đồng bộ nhận xét từ du khách...')}</div>`;
      }
    }
    if (poiNearbyList) poiNearbyList.innerHTML = `<div style="font-size: 0.78rem; color: var(--color-ink-muted); padding: 6px 0;">${i18n.t('poiNearbySearching', 'Đang tìm các địa điểm lân cận...')}</div>`;

    try {
      const data = await TourismApiClient.getPlaceDetail(name, placeId);
      currentPoiData = data;
      updateDrawerUserStatus(data.name || initialName, data.place_id || placeId);

      // 2. Cập nhật Tiêu đề và Địa chỉ (bảo vệ tránh lệch tên)
      if (poiTitle) poiTitle.textContent = data.name || initialName;
      if (poiAddressText) poiAddressText.textContent = data.address || localPlace?.address || (isEn ? 'Hue City' : 'Thành phố Huế');
      if (poiDescText) poiDescText.textContent = data.description || localPlace?.desc || (isEn ? 'Famous tourism and culinary destination in Imperial Hue.' : 'Địa điểm du lịch và ẩm thực nổi tiếng tại Cố đô Huế.');

      // 3. Category badge
      const cat = (data.category || '').toLowerCase();
      let catClass = 'attraction';
      let catIcon = '🏯';
      let catLabel = i18n.t('legendAttraction', 'Di tích & Thắng cảnh');

      if (cat.includes('restaurant') || cat.includes('ẩm thực') || cat.includes('quán')) {
        catClass = 'restaurant';
        catIcon = '🍲';
        catLabel = i18n.t('legendRestaurant', 'Ẩm thực Cố đô');
      } else if (cat.includes('cafe') || cat.includes('cà phê') || cat.includes('sunset')) {
        catClass = 'cafe';
        catIcon = '☕';
        catLabel = i18n.t('legendCafe', 'Cà phê & Sunset');
      } else if (cat.includes('hotel') || cat.includes('khách sạn') || cat.includes('resort')) {
        catClass = 'hotel';
        catIcon = '🏨';
        catLabel = i18n.t('legendHotel', 'Khách sạn / Resort');
      }

      if (poiCatBadge) {
        poiCatBadge.className = `poi-cat-badge ${catClass}`;
        poiCatBadge.textContent = `${catIcon} ${catLabel}`;
      }

      // 4. Rating & Reviews
      if (poiRatingVal) poiRatingVal.textContent = (data.rating_value || localPlace?.rating_value || 4.7).toFixed(1);
      if (poiReviewCount) poiReviewCount.textContent = `(${data.review_count || localPlace?.review_count || 120} ${i18n.t('reviewsCount', 'đánh giá')})`;

      // 5. Nhận xét chân thực từ du khách (TripAdvisor / SQLite / Curated Local)
      const activeReviews = (data.reviews && data.reviews.length > 0) ? data.reviews : (localPlace?.reviews || []);
      if (poiReviewsList) {
        if (activeReviews.length > 0) {
          if (poiSectionReviews) poiSectionReviews.style.display = 'flex';
          poiReviewsList.innerHTML = activeReviews.map(r => `
            <div class="poi-review-card">
              <div class="review-header">
                <span class="review-stars">${'⭐'.repeat(Math.round(r.rating || 5))}</span>
                <span class="review-tag">👤 ${r.trip_type || i18n.t('tourist', 'Du khách')} · ${r.visit_date || '2024'}</span>
              </div>
              <h5 class="review-title">${r.title}</h5>
              <p class="review-comment">“${r.comment}”</p>
            </div>
          `).join('');
        } else {
          poiReviewsList.innerHTML = `<div style="font-size: 0.78rem; color: #64748B;">${i18n.t('poiNoReviews', 'Chưa có trích đoạn nhận xét chi tiết.')}</div>`;
        }
      }

      // 7. Điểm lân cận qua cạnh NEAR_BY
      if (poiNearbyList) {
        if (data.nearby_places && data.nearby_places.length > 0) {
          if (poiSectionNearby) poiSectionNearby.style.display = 'flex';
          poiNearbyList.innerHTML = data.nearby_places.map(nb => {
            const nbCat = (nb.category || '').toLowerCase();
            const nbIcon = nbCat.includes('restaurant') ? '🍲' : (nbCat.includes('cafe') ? '☕' : (nbCat.includes('hotel') ? '🏨' : '🏯'));
            return `
              <div class="poi-nearby-card" data-name="${nb.name}" data-lat="${nb.lat || ''}" data-lng="${nb.lng || ''}">
                <div class="nearby-main">
                  <span class="nearby-icon">${nbIcon}</span>
                  <span class="nearby-name">${nb.name}</span>
                </div>
                <span class="nearby-dist">${nb.distance_km} km</span>
              </div>
            `;
          }).join('');

          // Click vào địa điểm lân cận -> Chuyển sang địa điểm đó
          poiNearbyList.querySelectorAll('.poi-nearby-card').forEach(card => {
            card.addEventListener('click', () => {
              const nbName = card.dataset.name;
              const nbLat = parseFloat(card.dataset.lat);
              const nbLng = parseFloat(card.dataset.lng);
              if (nbLat && nbLng) {
                mapStudio.panTo(nbLat, nbLng, 16);
              }
              openPoiDetail(nbName);
            });
          });
        } else {
          poiNearbyList.innerHTML = `<div style="font-size: 0.78rem; color: var(--color-ink-muted);">${i18n.t('poiNoNearby', 'Không có địa điểm lân cận trong bán kính gần.')}</div>`;
        }
      }

      // 8. Cập nhật nút điều hướng Google Maps
      if (poiBtnGoogleMaps) {
        if (data.latitude && data.longitude) {
          poiBtnGoogleMaps.href = `https://www.google.com/maps/dir/?api=1&destination=${data.latitude},${data.longitude}`;
        } else {
          poiBtnGoogleMaps.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.name + ' Hue')}`;
        }
      }

    } catch (err) {
      console.warn('Lỗi tải chi tiết POI:', err);
      if (poiDescText && localPlace?.desc) {
        poiDescText.textContent = localPlace.desc;
      }
    }
  }

  function closePoiDetail() {
    poiDrawer?.classList.remove('open');
    poiDrawer?.setAttribute('aria-hidden', 'true');
  }

  btnCloseDrawer?.addEventListener('click', closePoiDetail);
  poiDrawerBackdrop?.addEventListener('click', closePoiDetail);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && poiDrawer?.classList.contains('open')) {
      closePoiDetail();
    }
  });

  // Action: Chỉ đường trực tiếp từ vị trí của bạn đến điểm này
  poiBtnDirectNav?.addEventListener('click', () => {
    if (!currentPoiData) return;
    const destLat = currentPoiData.latitude || currentPoiData.lat;
    const destLng = currentPoiData.longitude || currentPoiData.lng;
    const destName = currentPoiData.name;

    if (!destLat || !destLng) {
      alert(i18n.t('poiNoCoordsAlert', 'Địa điểm này chưa có thông tin tọa độ chính xác để chỉ đường.'));
      return;
    }

    // Đóng drawer
    closePoiDetail();

    // Điểm xuất phát: Vị trí người dùng đã định vị, hoặc fallback Cầu Tràng Tiền
    const origin = mapStudio.userLocation || {
      lat: 16.4674,
      lng: 107.5905,
      name: i18n.t('defaultHueCenter', 'Cầu Tràng Tiền (Trung tâm Huế)')
    };

    const destination = {
      lat: destLat,
      lng: destLng,
      name: destName,
      address: currentPoiData.address || ''
    };

    mapStudio.drawNavigationRoute(origin, destination, 'driving');
  });

  // Action: Thêm vào tour
  poiBtnAddTour?.addEventListener('click', () => {
    if (!currentPoiData) return;
    closePoiDetail();
    togglePlanner(true);
    // Bật tag món ăn tương ứng nếu có
    dishTags.forEach(tag => {
      if (currentPoiData.name.includes(tag.dataset.dish) || (currentPoiData.cuisines || '').includes(tag.dataset.dish)) {
        tag.classList.add('active');
      }
    });
  });

  // Action: Hỏi AI về điểm này
  poiBtnAskAi?.addEventListener('click', () => {
    if (!currentPoiData) return;
    closePoiDetail();
    const isEn = i18n.getLanguage() === 'en';
    const tabChat = document.getElementById('tab-btn-chat');
    if (tabChat) tabChat.click();
    if (chatInput) {
      chatInput.value = isEn
        ? `Please introduce ${currentPoiData.name} and specialty dishes around here in detail.`
        : `Hãy giới thiệu chi tiết về ${currentPoiData.name} và các món ăn đặc sản nổi tiếng ở đây.`;
    }
    chatForm?.dispatchEvent(new Event('submit'));
  });

  // Action: Lưu vào sổ tay yêu thích từ POI drawer
  poiBtnFavorite?.addEventListener('click', () => {
    const isEn = i18n.getLanguage() === 'en';
    const activeName = currentPoiData?.name || poiTitle?.textContent;
    if (!activeName) return;

    const target = {
      place_id: currentPoiData?.place_id || currentPoiData?.id,
      name: activeName,
      category: currentPoiData?.category || poiCatBadge?.textContent || 'Attraction',
      address: currentPoiData?.address || poiAddressText?.textContent || (isEn ? 'Hue City' : 'Thành phố Huế'),
      latitude: currentPoiData?.latitude || currentPoiData?.lat,
      longitude: currentPoiData?.longitude || currentPoiData?.lng,
      rating_value: currentPoiData?.rating_value || parseFloat(poiRatingVal?.textContent) || 4.6
    };

    const { isFav } = userStore.toggleFavorite(target);
    updateDrawerUserStatus(target.name, target.place_id);
    showHueToast(isFav ? `${i18n.t('savedPoiPrefix', 'Đã lưu')} "${target.name}" ${i18n.t('toWishlistSuffix', 'vào Sổ tay')}` : `${i18n.t('unsavedPoiPrefix', 'Đã bỏ lưu')} "${target.name}"`);
  });

  // Action: Check-in từ POI drawer
  poiBtnCheckin?.addEventListener('click', () => {
    const isEn = i18n.getLanguage() === 'en';
    const activeName = currentPoiData?.name || poiTitle?.textContent;
    if (!activeName) return;

    const target = {
      place_id: currentPoiData?.place_id || currentPoiData?.id,
      name: activeName,
      category: currentPoiData?.category || poiCatBadge?.textContent || 'Attraction',
      address: currentPoiData?.address || poiAddressText?.textContent || (isEn ? 'Hue City' : 'Thành phố Huế'),
      latitude: currentPoiData?.latitude || currentPoiData?.lat,
      longitude: currentPoiData?.longitude || currentPoiData?.lng
    };

    const { isChecked } = userStore.toggleCheckin(target);
    updateDrawerUserStatus(target.name, target.place_id);
    const stats = userStore.getExplorerStats();
    showHueToast(isChecked ? `${i18n.t('checkedInPrefix', 'Đã check-in:')} "${target.name}" (${stats.rankTitle})` : `${i18n.t('uncheckedInPrefix', 'Đã hủy check-in')} "${target.name}"`);
  });

  // Action: Click vào các thẻ địa điểm nổi bật ở màn hình chào mừng
  document.querySelectorAll('.featured-place-card').forEach(card => {
    card.addEventListener('click', () => {
      showMapPanel(true);
      const name = card.dataset.name;
      const lat = parseFloat(card.dataset.lat);
      const lng = parseFloat(card.dataset.lng);
      if (lat && lng) {
        mapStudio.panTo(lat, lng, 16);
      }
      if (name && window.openPoiDetail) {
        window.openPoiDetail(name);
      }
    });
  });

  window.openPoiDetail = openPoiDetail;

  window.locatePoi = (lat, lng) => {
    showMapPanel(true);
    mapStudio.panTo(lat, lng, 16);
  };

  /**
   * Điều hướng và vẽ lộ trình trực tiếp trên bản đồ từ vị trí người dùng đến POI đích
   */
  window.navigateToDestination = (destLat, destLng, destName = '', destAddress = '') => {
    if (!destLat || !destLng) {
      alert(i18n.t('poiNoCoordsAlert', 'Địa điểm này chưa có tọa độ chính xác để chỉ đường.'));
      return;
    }

    // 1. Tự động mở bảng bản đồ nếu đang bị ẩn
    showMapPanel(true);

    // 2. Đóng popup hiện tại để tránh che khuất tuyến đường
    if (mapStudio.map) {
      mapStudio.map.closePopup();
    }

    // 3. Đóng ngăn chi tiết (nếu đang mở)
    closePoiDetail();

    // 4. Xác định điểm xuất phát: Vị trí người dùng (GPS) hoặc mặc định Cầu Tràng Tiền (Trung tâm Huế)
    const origin = mapStudio.userLocation || {
      lat: 16.4674,
      lng: 107.5905,
      name: i18n.t('defaultHueCenter', 'Cầu Tràng Tiền (Trung tâm Huế)')
    };

    const destination = {
      lat: parseFloat(destLat),
      lng: parseFloat(destLng),
      name: destName || i18n.t('destinationLabel', 'Điểm đến'),
      address: destAddress || ''
    };

    // 5. Vẽ tuyến đường thực tế qua OSRM và hiển thị Banner điều hướng
    mapStudio.drawNavigationRoute(origin, destination, 'driving');
  };

  // =============================================================================
  // 9. TOAST NOTIFICATION HELPER (HỆ THỐNG THÔNG BÁO TINH GỌN CHUẨN CỐ ĐÔ)
  // =============================================================================
  function showHueToast(message, duration = 3000) {
    let container = document.querySelector('.hue-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'hue-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'hue-toast';
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    setTimeout(() => {
      toast.classList.remove('show');
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 320);
    }, duration);
  }
  window.showHueToast = showHueToast;

  // =============================================================================
  // 10. GLOBAL POPUP FAVORITE & CHECK-IN HANDLERS (LEAFLET POPUP TOOLS)
  // =============================================================================
  window.togglePlaceFavorite = (name, placeId, category, address, lat, lng, btnEl) => {
    const isEn = i18n.getLanguage() === 'en';
    const target = {
      name,
      place_id: placeId,
      category,
      address,
      latitude: lat,
      longitude: lng
    };
    const { isFav } = userStore.toggleFavorite(target);
    if (btnEl) {
      btnEl.classList.toggle('active', isFav);
      const span = btnEl.querySelector('span');
      if (span) span.textContent = isFav ? i18n.t('poiFavDone', 'Đã thích') : i18n.t('poiFavLabel', 'Yêu thích');
      btnEl.title = isFav ? (isEn ? 'Remove from favorites' : 'Bỏ lưu yêu thích') : (isEn ? 'Save to notebook' : 'Lưu vào sổ tay yêu thích');
      const svg = btnEl.querySelector('svg');
      if (svg) svg.setAttribute('fill', isFav ? 'currentColor' : 'none');
    }
    showHueToast(isFav ? `${i18n.t('savedPoiPrefix', 'Đã lưu')} "${name}" ${i18n.t('toWishlistSuffix', 'vào Sổ tay')}` : `${i18n.t('unsavedPoiPrefix', 'Đã bỏ lưu')} "${name}"`);
  };

  window.togglePlaceCheckin = (name, placeId, category, address, lat, lng, btnEl) => {
    const target = {
      name,
      place_id: placeId,
      category,
      address,
      latitude: lat,
      longitude: lng
    };
    const { isChecked } = userStore.toggleCheckin(target);
    if (btnEl) {
      btnEl.classList.toggle('active', isChecked);
      const span = btnEl.querySelector('span');
      if (span) span.textContent = isChecked ? i18n.t('poiCheckinDone', 'Đã check-in') : i18n.t('poiCheckinLabel', 'Check-in');
      btnEl.title = isChecked ? i18n.t('removeCheckinTooltip', 'Hủy check-in') : i18n.t('markVisitedTooltip', 'Đánh dấu đã ghé thăm');
    }
    const stats = userStore.getExplorerStats();
    showHueToast(isChecked ? `${i18n.t('checkedInPrefix', 'Đã check-in:')} "${name}" (${stats.rankTitle})` : `${i18n.t('uncheckedInPrefix', 'Đã hủy check-in')} "${name}"`);
  };

  // =============================================================================
  // 11. SỔ TAY DU LỊCH & HÀNH TRÌNH CHECK-IN (TRAVEL NOTEBOOK & PASSPORT CONTROLLER)
  // =============================================================================
  const notebookModal = document.getElementById('travel-notebook-modal');
  const btnCloseNotebook = document.getElementById('btn-close-notebook-modal');
  const tabWishlist = document.getElementById('tab-notebook-wishlist');
  const tabCheckin = document.getElementById('tab-notebook-checkin');
  const tabPreferences = document.getElementById('tab-notebook-preferences');
  const panelWishlist = document.getElementById('panel-notebook-wishlist');
  const panelCheckin = document.getElementById('panel-notebook-checkin');
  const panelPreferences = document.getElementById('panel-notebook-preferences');
  const badgeWishlistCount = document.getElementById('badge-wishlist-count');
  const badgeCheckinCount = document.getElementById('badge-checkin-count');
  const headerNotebookBadge = document.getElementById('header-notebook-badge');
  const sidebarNotebookBadge = document.getElementById('sidebar-notebook-badge');
  const wishlistItemsList = document.getElementById('wishlist-items-list');
  const checkinItemsList = document.getElementById('checkin-items-list');
  const searchWishlistInput = document.getElementById('input-search-wishlist');
  const wishlistTotalPill = document.getElementById('wishlist-total-pill');
  const explorerBadgeCircle = document.getElementById('explorer-badge-circle');
  const explorerRankTitle = document.getElementById('explorer-rank-title');
  const explorerRankCount = document.getElementById('explorer-rank-count');
  const explorerProgressFill = document.getElementById('explorer-progress-fill');
  const explorerRankDesc = document.getElementById('explorer-rank-desc');
  const checkinFilterPills = document.querySelectorAll('.checkin-filter-pill');

  let currentCheckinCategory = 'all';

  function updateNotebookBadges() {
    const favCount = userStore.getFavorites().length;
    const checkinCount = userStore.getCheckins().length;

    if (headerNotebookBadge) {
      headerNotebookBadge.textContent = favCount;
      headerNotebookBadge.classList.toggle('hidden', favCount === 0);
      headerNotebookBadge.style.display = favCount > 0 ? 'inline-flex' : 'none';
    }
    if (sidebarNotebookBadge) {
      sidebarNotebookBadge.textContent = favCount;
      sidebarNotebookBadge.classList.toggle('hidden', favCount === 0);
      sidebarNotebookBadge.style.display = favCount > 0 ? 'inline-flex' : 'none';
    }
    if (badgeWishlistCount) badgeWishlistCount.textContent = favCount;
    if (badgeCheckinCount) badgeCheckinCount.textContent = checkinCount;
  }

  function openNotebookModal(defaultTab = 'wishlist') {
    if (!notebookModal) return;
    notebookModal.classList.add('active');
    document.body.style.overflow = 'hidden';
    switchNotebookTab(defaultTab);
  }

  function closeNotebookModal() {
    if (!notebookModal) return;
    notebookModal.classList.remove('active');
    document.body.style.overflow = '';
  }

  function switchNotebookTab(tabName) {
    [tabWishlist, tabCheckin, tabPreferences].forEach(t => {
      t?.classList.remove('active');
      t?.setAttribute('aria-selected', 'false');
    });
    [panelWishlist, panelCheckin, panelPreferences].forEach(p => {
      p?.classList.remove('active');
      p?.setAttribute('hidden', '');
    });

    if (tabName === 'wishlist') {
      tabWishlist?.classList.add('active');
      tabWishlist?.setAttribute('aria-selected', 'true');
      panelWishlist?.classList.add('active');
      panelWishlist?.removeAttribute('hidden');
      renderWishlist(searchWishlistInput?.value || '');
    } else if (tabName === 'checkin') {
      tabCheckin?.classList.add('active');
      tabCheckin?.setAttribute('aria-selected', 'true');
      panelCheckin?.classList.add('active');
      panelCheckin?.removeAttribute('hidden');
      renderCheckinList(currentCheckinCategory);
    } else if (tabName === 'preferences') {
      tabPreferences?.classList.add('active');
      tabPreferences?.setAttribute('aria-selected', 'true');
      panelPreferences?.classList.add('active');
      panelPreferences?.removeAttribute('hidden');
      populatePreferencesForm();
    }
  }

  tabWishlist?.addEventListener('click', () => switchNotebookTab('wishlist'));
  tabCheckin?.addEventListener('click', () => switchNotebookTab('checkin'));
  tabPreferences?.addEventListener('click', () => switchNotebookTab('preferences'));
  btnCloseNotebook?.addEventListener('click', closeNotebookModal);
  notebookModal?.addEventListener('click', (e) => {
    if (e.target === notebookModal) closeNotebookModal();
  });

  // Triggers mở Sổ tay Du lịch & Gu cá nhân
  document.getElementById('btn-sidebar-travel-notebook')?.addEventListener('click', () => openNotebookModal('wishlist'));
  document.getElementById('btn-sidebar-budget')?.addEventListener('click', () => {
    const isEn = i18n.getLanguage() === 'en';
    budgetEstimator.openModal(null, isEn ? 'Hue Imperial Trip Budget Estimator' : 'Dự toán Ngân sách Du lịch Cố Đô Huế');
  });
  document.getElementById('btn-open-travel-notebook')?.addEventListener('click', () => {
    document.getElementById('user-dropdown-menu')?.classList.remove('active');
    openNotebookModal('wishlist');
  });
  document.getElementById('btn-popover-notebook')?.addEventListener('click', () => {
    document.getElementById('sidebar-user-popover')?.classList.remove('active');
    openNotebookModal('wishlist');
  });
  document.getElementById('btn-popover-guest-notebook')?.addEventListener('click', () => {
    document.getElementById('sidebar-user-popover')?.classList.remove('active');
    openNotebookModal('wishlist');
  });

  function renderWishlist(query = '') {
    if (!wishlistItemsList) return;
    let favorites = userStore.getFavorites();

    if (query.trim()) {
      const q = mapStudio.removeVietnameseTones(query.trim().toLowerCase());
      favorites = favorites.filter(item => {
        const nameNorm = mapStudio.removeVietnameseTones((item.name || '').toLowerCase());
        const addrNorm = mapStudio.removeVietnameseTones((item.address || '').toLowerCase());
        const noteNorm = mapStudio.removeVietnameseTones((item.note || '').toLowerCase());
        return nameNorm.includes(q) || addrNorm.includes(q) || noteNorm.includes(q);
      });
    }

    if (wishlistTotalPill) {
      wishlistTotalPill.textContent = `${favorites.length} ${i18n.t('placesUnit', 'địa điểm')}`;
    }

    const isEn = i18n.getLanguage() === 'en';

    if (favorites.length === 0) {
      wishlistItemsList.innerHTML = `
        <div class="notebook-empty-state">
          <p class="empty-state-title">${i18n.t('wishlistEmptyTitle', 'Chưa có địa điểm lưu trữ')}</p>
          <p class="empty-state-desc">${query.trim() ? i18n.t('mapNoSearchResult', 'Không tìm thấy địa điểm phù hợp với từ khóa.') : i18n.t('wishlistEmptyDesc', 'Khám phá các địa danh trên bản đồ và nhấn Lưu để quản lý danh sách của bạn.')}</p>
        </div>
      `;
      return;
    }

    wishlistItemsList.innerHTML = favorites.map(item => {
      const cat = (item.category || '').toLowerCase();
      let catLabel = i18n.t('monumentsUpper', 'DI TÍCH');
      if (cat.includes('restaurant') || cat.includes('ẩm thực') || cat.includes('quán')) {
        catLabel = i18n.t('cuisineUpper', 'ẨM THỰC');
      } else if (cat.includes('cafe') || cat.includes('cà phê')) {
        catLabel = i18n.t('cafeUpper', 'CÀ PHÊ');
      } else if (cat.includes('hotel') || cat.includes('khách sạn') || cat.includes('resort')) {
        catLabel = i18n.t('resortUpper', 'NGHỈ DƯỠNG');
      }

      const safeName = (item.name || '').replace(/"/g, '&quot;');
      const safeAddr = (item.address || (isEn ? 'Hue City' : 'Thành phố Huế')).replace(/"/g, '&quot;');
      const safeNote = (item.note || '').replace(/"/g, '&quot;');

      return `
        <div class="wishlist-card" data-name="${safeName}" data-lat="${item.latitude || ''}" data-lng="${item.longitude || ''}">
          <div class="wishlist-card-header">
            <span class="wishlist-cat-tag">${catLabel}</span>
            <div class="wishlist-actions">
              <button type="button" class="btn-wishlist-action btn-fly-map">${i18n.t('mapBtn', 'Bản đồ')}</button>
              <span class="wishlist-action-sep">/</span>
              <button type="button" class="btn-wishlist-action btn-remove-fav">${i18n.t('removeFavBtn', 'Bỏ lưu')}</button>
            </div>
          </div>
          <h4 class="wishlist-card-title">${item.name}</h4>
          <p class="wishlist-card-address">${safeAddr}</p>
          <div class="wishlist-note-wrap">
            <input type="text" class="wishlist-note-input" placeholder="${i18n.t('personalNotePlaceholder', 'Ghi chú cá nhân...')}" value="${safeNote}" />
          </div>
        </div>
      `;
    }).join('');
  }

  // Event Delegation cho Wishlist (Gắn 1 lần duy nhất, zero-lag)
  wishlistItemsList?.addEventListener('click', (e) => {
    const flyBtn = e.target.closest('.btn-fly-map');
    if (flyBtn) {
      const card = flyBtn.closest('.wishlist-card');
      if (!card) return;
      const name = card.dataset.name;
      const lat = parseFloat(card.dataset.lat);
      const lng = parseFloat(card.dataset.lng);
      closeNotebookModal();
      showMapPanel(true);
      if (lat && lng) {
        mapStudio.panTo(lat, lng, 16);
      }
      mapStudio.flyToPoi(name);
      return;
    }

    const removeBtn = e.target.closest('.btn-remove-fav');
    if (removeBtn) {
      const card = removeBtn.closest('.wishlist-card');
      if (!card) return;
      const name = card.dataset.name;
      userStore.removeFavorite(name);
      showHueToast(`${i18n.t('unsavedPoiPrefix', 'Đã bỏ lưu')} "${name}"`);
      renderWishlist(searchWishlistInput?.value || '');
      return;
    }
  });

  wishlistItemsList?.addEventListener('change', (e) => {
    const isEn = i18n.getLanguage() === 'en';
    const noteInput = e.target.closest('.wishlist-note-input');
    if (noteInput) {
      const card = noteInput.closest('.wishlist-card');
      if (!card) return;
      const name = card.dataset.name;
      userStore.updateFavoriteNote(name, noteInput.value.trim());
      showHueToast(isEn ? `Saved note for "${name}"` : `Đã lưu ghi chú cho "${name}"`);
    }
  });

  searchWishlistInput?.addEventListener('input', () => {
    renderWishlist(searchWishlistInput.value);
  });

  function updateExplorerRankUi(stats) {
    const isEn = i18n.getLanguage() === 'en';
    const levelTag = document.getElementById('explorer-level-tag');
    if (levelTag) levelTag.textContent = `${i18n.t('passportLevel', 'CẤP')} ${stats.level || '01'}`;
    if (explorerRankTitle) explorerRankTitle.textContent = stats.rankTitle;
    if (explorerRankCount) explorerRankCount.textContent = `${stats.count} / ${stats.total}`;
    if (explorerProgressFill) explorerProgressFill.style.width = `${stats.percentage}%`;
    if (explorerRankDesc) {
      explorerRankDesc.textContent = stats.remainingForNext > 0
        ? (isEn ? `Need ${stats.remainingForNext} more check-ins to reach "${stats.nextRankTitle}".` : `Cần thêm ${stats.remainingForNext} điểm check-in để đạt "${stats.nextRankTitle}".`)
        : (isEn ? 'Completed all Imperial heritage trails.' : 'Đã hoàn thành toàn bộ hành trình di sản Cố Đô.');
    }
  }

  function getCategoryLabel(catRaw) {
    const cat = (catRaw || '').toLowerCase();
    if (cat.includes('restaurant') || cat.includes('ẩm thực') || cat.includes('quán')) return i18n.t('cuisineUpper', 'ẨM THỰC');
    if (cat.includes('cafe') || cat.includes('cà phê')) return i18n.t('cafeUpper', 'CÀ PHÊ');
    if (cat.includes('hotel') || cat.includes('khách sạn') || cat.includes('resort')) return i18n.t('resortUpper', 'NGHỈ DƯỠNG');
    return i18n.t('monumentsUpper', 'DI TÍCH');
  }

  function renderCheckinList(category = 'all') {
    currentCheckinCategory = category;
    if (!checkinItemsList) return;

    const isEn = i18n.getLanguage() === 'en';
    const stats = userStore.getExplorerStats();
    updateExplorerRankUi(stats);

    const allLandmarks = mapStudio.masterLandmarks || [];
    const catNormalized = (category || 'all').toLowerCase();
    const filtered = catNormalized === 'all'
      ? allLandmarks
      : allLandmarks.filter(item => (item.cat || '').toLowerCase() === catNormalized);

    checkinItemsList.innerHTML = filtered.map(item => {
      const isChecked = userStore.isCheckedIn(item.place_id || item.name);
      const catLabel = getCategoryLabel(item.cat);
      const safeName = (item.name || '').replace(/"/g, '&quot;');

      return `
        <div class="checkin-card ${isChecked ? 'checked' : ''}" data-name="${safeName}" data-lat="${item.lat}" data-lng="${item.lng}">
          <div class="checkin-card-left">
            <span class="checkin-checkbox-box" aria-hidden="true">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </span>
            <div class="checkin-info">
              <div class="checkin-name">${item.name}</div>
              <div class="checkin-meta">
                <span class="checkin-cat-tag">${catLabel}</span>
                ${isChecked ? `<span class="checkin-done-tag">${i18n.t('visitedBadge', 'Đã ghé thăm')}</span>` : ''}
              </div>
            </div>
          </div>
          <button type="button" class="btn-checkin-fly" title="${isEn ? 'View on map' : 'Xem trên bản đồ'}">${i18n.t('mapBtn', 'Bản đồ')}</button>
        </div>
      `;
    }).join('');
  }

  // Event Delegation cho Check-in (Gắn 1 lần duy nhất cho toàn bộ danh sách địa danh)
  checkinItemsList?.addEventListener('click', (e) => {
    const flyBtn = e.target.closest('.btn-checkin-fly');
    if (flyBtn) {
      const card = flyBtn.closest('.checkin-card');
      if (!card) return;
      const name = card.dataset.name;
      const lat = parseFloat(card.dataset.lat);
      const lng = parseFloat(card.dataset.lng);
      closeNotebookModal();
      showMapPanel(true);
      if (lat && lng) {
        mapStudio.panTo(lat, lng, 16);
      }
      mapStudio.flyToPoi(name);
      return;
    }

    const checkinLeft = e.target.closest('.checkin-card-left');
    if (checkinLeft) {
      const card = checkinLeft.closest('.checkin-card');
      if (!card) return;
      const name = card.dataset.name;
      const allLandmarks = mapStudio.masterLandmarks || [];
      const landmark = allLandmarks.find(p => p.name === name);
      if (!landmark) return;

      const target = {
        place_id: landmark.place_id,
        name: landmark.name,
        category: landmark.cat,
        address: landmark.desc || landmark.address,
        latitude: landmark.lat,
        longitude: landmark.lng
      };

      const { isChecked } = userStore.toggleCheckin(target);
      const newStats = userStore.getExplorerStats();
      const catLabel = getCategoryLabel(landmark.cat);

      // Cập nhật DOM của card tức thì không tốn CPU dựng lại danh sách
      card.classList.toggle('checked', isChecked);
      const metaEl = card.querySelector('.checkin-meta');
      if (metaEl) {
        metaEl.innerHTML = `<span class="checkin-cat-tag">${catLabel}</span>${isChecked ? `<span class="checkin-done-tag">${i18n.t('visitedBadge', 'Đã ghé thăm')}</span>` : ''}`;
      }

      updateExplorerRankUi(newStats);
      showHueToast(isChecked ? `${i18n.t('checkedInPrefix', 'Đã check-in:')} "${name}"` : `${i18n.t('uncheckedInPrefix', 'Đã hủy check-in:')} "${name}"`);
    }
  });

  checkinFilterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      checkinFilterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      renderCheckinList(pill.dataset.filter);
    });
  });

  // =============================================================================
  // 12. HỒ SƠ GU DU LỊCH & KHẨU VỊ CÁ NHÂN HÓA (TRAVEL PREFERENCES CONTROLLER)
  // =============================================================================
  const preferencesForm = document.getElementById('preferences-form');
  const prefSelectParty = document.getElementById('pref-select-party');
  const prefSelectTransport = document.getElementById('pref-select-transport');
  const prefInputNotes = document.getElementById('pref-input-notes');

  function openPreferencesModal() {
    openNotebookModal('preferences');
  }

  function populatePreferencesForm() {
    const prefs = userStore.getPreferences();

    document.querySelectorAll('input[name="pref_style"]').forEach(cb => {
      cb.checked = (prefs.styles || []).includes(cb.value);
    });

    document.querySelectorAll('input[name="pref_dietary"]').forEach(cb => {
      cb.checked = (prefs.dietary || []).includes(cb.value);
    });

    if (prefSelectParty && prefs.party) {
      prefSelectParty.value = prefs.party;
    }
    if (prefSelectTransport && prefs.transport) {
      prefSelectTransport.value = prefs.transport;
    }
    if (prefInputNotes) {
      prefInputNotes.value = prefs.customNotes || '';
    }
  }

  preferencesForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const selectedStyles = Array.from(document.querySelectorAll('input[name="pref_style"]:checked')).map(el => el.value);
    const selectedDietary = Array.from(document.querySelectorAll('input[name="pref_dietary"]:checked')).map(el => el.value);
    const party = prefSelectParty?.value || 'Couples';
    const transport = prefSelectTransport?.value || 'Motorbike';
    const customNotes = prefInputNotes?.value?.trim() || '';

    userStore.savePreferences({
      styles: selectedStyles.length > 0 ? selectedStyles : ['heritage', 'foodie'],
      dietary: selectedDietary,
      party,
      transport,
      customNotes
    });

    showHueToast(i18n.t('prefSavedSuccess', 'Đã lưu Hồ sơ Gu Du Lịch thành công.'));
  });

  // Triggers mở Hồ sơ Gu du lịch
  document.getElementById('btn-sidebar-user-preferences')?.addEventListener('click', openPreferencesModal);
  document.getElementById('btn-open-user-preferences')?.addEventListener('click', openPreferencesModal);
  document.getElementById('btn-popover-preferences')?.addEventListener('click', openPreferencesModal);
  document.getElementById('btn-popover-guest-preferences')?.addEventListener('click', openPreferencesModal);

  // Phím tắt ESC đóng modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (notebookModal?.classList.contains('active')) closeNotebookModal();
    }
  });

  // Lắng nghe thay đổi UserStore để cập nhật reactive
  window.addEventListener('hue-user-store-changed', () => {
    updateNotebookBadges();
    if (notebookModal?.classList.contains('active')) {
      if (tabWishlist?.classList.contains('active')) {
        renderWishlist(searchWishlistInput?.value || '');
      } else if (tabCheckin?.classList.contains('active')) {
        renderCheckinList(currentCheckinCategory);
      } else if (tabPreferences?.classList.contains('active')) {
        populatePreferencesForm();
      }
    }
    if (currentPoiData && poiDrawer?.classList.contains('open')) {
      updateDrawerUserStatus(currentPoiData.name, currentPoiData.place_id);
    }
  });

  // Khởi tạo số liệu ban đầu
  updateNotebookBadges();
  populatePreferencesForm();

});
