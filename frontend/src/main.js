// =============================================================================
// HUẾ SMART TOURISM — MAIN APPLICATION CONTROLLER
// Trực quan hóa Kiến trúc Spatial GraphRAG theo chuẩn Hallmark Editorial
// =============================================================================

import './style.css';
import { TourismApiClient } from './api.js';
import { SpatialMapStudio } from './map.js';
import { AuthController } from './auth.js';
import { 
  saveItinerary, 
  saveChatSession, 
  getUserChatSessions, 
  deleteChatSession, 
  onAuthChange 
} from './firebase.js';

document.addEventListener('DOMContentLoaded', async () => {
  // 0. KHỞI TẠO HỆ THỐNG XÁC THỰC (AUTH CONTROLLER - GOOGLE GMAIL & EMAIL)
  const authController = new AuthController();
  authController.init();
  window.authController = authController;

  // 1. KHỞI TẠO BẢN ĐỒ KHÔNG GIAN
  const mapStudio = new SpatialMapStudio('map-container');
  mapStudio.init();
  window.mapStudio = mapStudio;

  // 2. KIỂM TRA TRẠNG THÁI FASTAPI BACKEND
  const statusPill = document.getElementById('system-status-pill');
  const statusLabel = document.getElementById('status-label');
  const statusDot = statusPill.querySelector('.status-dot');

  async function checkBackendStatus() {
    try {
      const health = await TourismApiClient.checkHealth();
      if (health.status === 'healthy') {
        statusDot.className = 'status-dot pulse';
        statusLabel.textContent = 'Trực tuyến';
        statusPill.title = 'Hệ thống đang hoạt động';
      } else {
        throw new Error('Offline');
      }
    } catch {
      statusDot.className = 'status-dot error';
      statusLabel.textContent = 'Ngoại tuyến';
      statusPill.title = 'Không thể kết nối máy chủ';
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
      btnHeaderToggleMap.title = isOpen ? 'Thu gọn bản đồ (Tập trung giao diện Chatbot)' : 'Mở bản đồ không gian Cố đô';
      if (headerMapToggleLabel) {
        headerMapToggleLabel.textContent = isOpen ? 'Thu gọn Bản đồ' : 'Mở Bản đồ';
      }
    }
    if (btnWorkbenchToggleMap) {
      btnWorkbenchToggleMap.classList.toggle('active', isOpen);
      btnWorkbenchToggleMap.title = isOpen ? 'Thu gọn bản đồ bên cạnh' : 'Mở bản đồ bên cạnh';
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
      originEl.textContent = mapStudio.userLocation.name;
    } else {
      originEl.textContent = 'Đang định vị GPS...';
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
        alert('Trình duyệt của bạn không hỗ trợ Geolocation API.');
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
        const locName = isNearHue ? 'Vị trí hiện tại của bạn' : 'Vị trí của bạn (Ngoài Huế)';

        mapStudio.setUserLocation(lat, lng, locName);
        updatePlannerOriginDisplay();
        if (!silent) {
          mapStudio.panTo(lat, lng, 16);
          btnLocateUser?.classList.add('active');
        }
        btnLocateUser.title = `Đã định vị: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
      },
      (err) => {
        btnLocateUser?.classList.remove('loading');
        console.warn('Geolocation error or denied:', err);
        const defaultHueLat = 16.4674;
        const defaultHueLng = 107.5905;
        mapStudio.setUserLocation(defaultHueLat, defaultHueLng, 'Cầu Tràng Tiền (Trung tâm Huế)');
        updatePlannerOriginDisplay();

        if (!silent) {
          mapStudio.panTo(defaultHueLat, defaultHueLng, 16);
          btnLocateUser?.classList.add('active');
          btnLocateUser.title = 'Vị trí mặc định: Cầu Tràng Tiền, Huế';
          alert('Không thể lấy vị trí thực tế của bạn (trình duyệt chặn hoặc chưa cấp quyền). Hệ thống đã đặt vị trí xuất phát mặc định tại Cầu Tràng Tiền, trung tâm Huế!');
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

  // Danh mục tiêu đề bản đồ tương ứng
  const categoryTitles = {
    all: 'Bản đồ Di sản',
    attraction: 'Di tích Cố đô',
    restaurant: 'Ẩm thực Cố đô',
    cafe: 'Cà phê & Sunset',
    hotel: 'Khách sạn & Resort'
  };

  // Xử lý click chọn bộ lọc danh mục
  filterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.category;
      filterChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      mapStudio.filterByCategory(cat);
      if (mapActiveMeta) {
        const title = categoryTitles[cat] || 'Địa điểm Cố đô';
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
      mapActiveMeta.textContent = 'Bản đồ Di sản';
      mapActiveMeta.title = 'Bản đồ Di sản';
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
    if (workbenchToggleText) {
      workbenchToggleText.textContent = isCollapsed ? 'Hiện trợ lý' : 'Toàn cảnh';
    }
    btnToggleWorkbench.title = isCollapsed 
      ? 'Mở lại bảng trợ lý & lịch trình bên phải' 
      : 'Thu gọn bảng trợ lý để xem bản đồ toàn cảnh';

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
    if (results.length === 0) {
      mapSearchDropdown.innerHTML = `
        <div class="search-empty-item">
          Không tìm thấy địa điểm phù hợp với từ khóa
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
      attraction: 'Di tích',
      restaurant: 'Ẩm thực',
      cafe: 'Cà phê',
      hotel: 'Khách sạn'
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
        name: mapStudio.userLocation.name || 'Vị trí hiện tại của bạn'
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
        const locName = isNearHue ? 'Vị trí hiện tại của bạn' : 'Vị trí của bạn (Ngoài Huế)';
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
    const defName = 'Cầu Tràng Tiền (Trung tâm Huế)';
    mapStudio.setUserLocation(defLat, defLng, defName);
    updatePlannerOriginDisplay();
    return { lat: defLat, lng: defLng, name: defName };
  }

  async function generateItineraryInChat(days, tripType, preferredDishes) {
    showMapPanel(true); // Tự động mở bản đồ khi tạo lịch trình
    const coords = await getUserCoordinates();
    const userLat = coords.lat;
    const userLng = coords.lng;
    const userLocName = coords.name;

    const dishLabel = preferredDishes && preferredDishes.length > 0
      ? `ưu tiên các món: ${preferredDishes.join(', ')}`
      : 'ẩm thực Cố đô đặc sắc';
    const userQueryText = `📅 Lập lịch trình khám phá Huế ${days} ngày cho ${tripType}, xuất phát từ ${userLocName}, ${dishLabel}.`;
    appendUserMessage(userQueryText);

    // Thu gọn quick planner card
    togglePlanner(false);

    const loadingId = appendAssistantLoading(
      `Đang tối ưu hóa hành trình ${days} ngày xuất phát từ ${userLocName}, kết nối ẩm thực và vẽ lộ trình...`
    );

    if (btnGenItinerary) {
      btnGenItinerary.classList.add('loading');
      btnGenItinerary.disabled = true;
    }

    try {
      const res = await TourismApiClient.generateItinerary(days, preferredDishes, tripType, userLat, userLng);
      removeLoadingMessage(loadingId);
      appendItineraryDeckMessage(res, days, tripType, preferredDishes, userLocName);
    } catch (err) {
      removeLoadingMessage(loadingId);
      appendAssistantError(`Không thể tạo lịch trình: ${err.message}. Vui lòng thử lại.`);
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

  function appendItineraryDeckMessage(res, days, tripType, preferredDishes, userLocName = 'Vị trí của bạn', persist = true) {
    const plan = res.itinerary_data;
    if (!plan || !plan.days || plan.days.length === 0) {
      appendAssistantError('Không tìm thấy dữ liệu lịch trình phù hợp với tiêu chí đã chọn.');
      return;
    }

    const deckId = `deck-${Date.now()}`;
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
        <button type="button" class="deck-day-tab ${isFirstDay ? 'active' : ''}" data-deck="${deckId}" data-day="${day.day_number}" title="Xem lịch trình và lộ trình Ngày ${day.day_number}">
          <span class="day-tab-dot" style="background-color: ${dotColor};"></span>
          <span>Ngày ${day.day_number}</span>
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
          <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn-gmaps-route" title="Mở chỉ đường toàn tuyến Ngày ${day.day_number} trên Google Maps">
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
          : `<span class="meta-pill pill-leg-num">Chặng ${legNum}</span>`;

        let distanceBadge = '';
        if (slot.distance_from_prev_km && slot.distance_from_prev_km > 0) {
          const distLabel = (isFirstDay && slotIdx === 1)
            ? `Cách vị trí bạn: ${slot.distance_from_prev_km.toFixed(1)} km`
            : `${slot.distance_from_prev_km.toFixed(1)} km`;
          distanceBadge = `<span class="meta-pill pill-distance">${distLabel}</span>`;
        } else if (slot.distance_to_anchor_km) {
          distanceBadge = `<span class="meta-pill pill-distance">${slot.distance_to_anchor_km.toFixed(1)} km</span>`;
        }

        const dishBadge = slot.dish_highlight || slot.specialty_dish
          ? `<span class="meta-pill pill-dish">Món: ${slot.dish_highlight || slot.specialty_dish}</span>`
          : '';

        const ratingBadge = (!isUserOrigin && slot.rating)
          ? `<span class="meta-pill pill-rating">⭐ ${slot.rating.toFixed(1)}</span>`
          : '';

        const typeBadge = isUserOrigin
          ? `<span class="meta-pill pill-origin">Điểm xuất phát</span>`
          : `<span class="meta-pill">${slot.activity_type || slot.category || (isFood ? 'Ẩm thực' : 'Di tích')}</span>`;

        let timeBadgeHtml = '';
        if (isUserOrigin) {
          const rawMatch = (slot.slot_name || '').match(/\((.*?)\)/);
          const timeRange = (rawMatch ? rawMatch[1] : '07:30 – 08:00').replace(/-/g, '–').trim();
          timeBadgeHtml = `<span class="badge-period">Khởi hành</span><span class="badge-time">${timeRange}</span>`;
        } else {
          const raw = slot.slot_name || slot.slot_time || 'Chặng tour';
          const match = raw.match(/^(.*?)\s*\((.*?)\)$/);
          if (match) {
            const timeRange = match[2].replace(/-/g, '–').trim();
            timeBadgeHtml = `<span class="badge-period">${match[1]}</span><span class="badge-time">${timeRange}</span>`;
          } else {
            timeBadgeHtml = `<span class="badge-period">${raw}</span>`;
          }
        }

        const locateBtn = (lat && lng)
          ? `<button type="button" class="btn-locate" data-lat="${lat}" data-lng="${lng}" data-name="${slot.place_name || slot.name}" title="Xem vị trí trên bản đồ">
               <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="3" fill="currentColor"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/><circle cx="12" cy="12" r="7" stroke-dasharray="2 2"/></svg>
               <span>Định vị</span>
             </button>`
          : '';

        const detailBtn = isUserOrigin
          ? ''
          : `<button type="button" class="btn-step-detail" data-name="${slot.place_name || slot.name}">
               <span>Xem chi tiết</span>
               <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
             </button>`;

        timelineStepsHtml += `
          <div class="timeline-step ${isUserOrigin ? 'timeline-step-origin' : ''}" data-name="${slot.place_name || slot.name}" data-step-index="${slotIdx}">
            <div class="step-time-badge">${timeBadgeHtml}</div>
            <div class="step-content">
              <h4 class="step-poi-name ${isUserOrigin ? 'origin-name' : ''}" data-name="${slot.place_name || slot.name}" title="${isUserOrigin ? 'Điểm xuất phát tour của bạn' : 'Nhấp để xem hồ sơ & đánh giá chi tiết'}">${slot.place_name || slot.name}</h4>
              <p class="step-poi-desc">${slot.description || slot.address || 'Điểm trải nghiệm di sản Cố đô'}</p>
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

      dayContentsHtml += `
        <div class="deck-day-content ${isFirstDay ? 'active' : ''}" id="${deckId}-day-${day.day_number}">
          <div class="deck-day-summary">
            <div class="deck-day-theme">Ngày ${day.day_number}: ${day.theme || day.cluster_name || 'Khám phá Cố đô'}</div>
            <div class="deck-day-actions">
              ${gmapsRouteBtn}
              <span class="day-badge">${slots.length} chặng${totalKm}</span>
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
        <button type="button" class="deck-day-tab" data-deck="${deckId}" data-day="all" title="Xem tuyến đường toàn bộ các ngày cùng lúc">
          <span class="day-tab-dot" style="background: #18181B;"></span>
          <span>Tất cả ngày</span>
        </button>
      `;
    }

    const totalKmText = totalTripDistanceKm > 0 ? ` · ~${totalTripDistanceKm.toFixed(1)} km` : '';

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
        <div class="message-author">Lịch trình Tour Cố đô</div>
        <p>Mình đã tối ưu hóa lịch trình <strong>${days} ngày</strong> cho <strong>${tripType}</strong> xuất phát từ <strong>${userLocName || 'Vị trí của bạn'}</strong> theo khoảng cách di chuyển thực tế. Toàn bộ lộ trình đã được đồng bộ lên bản đồ bên cạnh.</p>
        
        <div class="chat-itinerary-deck" id="${deckId}">
          <div class="deck-header">
            <div class="deck-header-info">
              <h3 class="deck-title">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
                Lộ trình Khám phá Huế (${days} ngày)
              </h3>
              <span class="deck-subtitle">Đối tượng: ${tripType} · ${totalStopsCount} điểm đến</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <div class="deck-badge">${days} Ngày${totalKmText}</div>
              <button type="button" class="btn-deck-save-tour" id="btn-save-${deckId}" title="Lưu lịch trình này vào tài khoản cá nhân">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Lưu Tour</span>
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
            <span class="deck-followup-label">Hỏi tiếp:</span>
            <button type="button" class="btn-deck-followup">Chi phí dự kiến chuyến đi này khoảng bao nhiêu?</button>
            <button type="button" class="btn-deck-followup">Thời điểm tham quan Đại Nội đẹp nhất trong ngày?</button>
            <button type="button" class="btn-deck-followup">Phương tiện di chuyển hợp lý nhất ở Huế?</button>
          </div>
        </div>
      </div>
    `;

    chatThread.appendChild(msg);
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
          sendChatQuery(btn.textContent.trim());
        });
      });

      // Gán sự kiện cho nút Lưu Tour vào tài khoản Google / Cloud
      const btnSaveTour = document.getElementById(`btn-save-${deckId}`);
      btnSaveTour?.addEventListener('click', async () => {
        if (!authController.currentUser) {
          authController.openAuthModal('login');
          authController.showToast('Vui lòng đăng nhập để lưu lịch trình vào tài khoản.');
          return;
        }

        try {
          btnSaveTour.disabled = true;
          btnSaveTour.innerHTML = '<span>Đang lưu...</span>';
          await saveItinerary(authController.currentUser.uid, {
            title: `Lịch trình Huế ${days} ngày (${tripType})`,
            days,
            tripType,
            userLocationName: userLocName || 'Thành phố Huế',
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
            <span>Đã lưu</span>
          `;
          authController.showToast('Đã lưu lịch trình thành công vào tài khoản!');
        } catch (err) {
          btnSaveTour.disabled = false;
          btnSaveTour.innerHTML = '<span>Lưu Tour</span>';
          authController.showToast(`Lỗi khi lưu lịch trình: ${err.message}`);
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
        role: 'assistant',
        text: `📅 Lịch trình tour Cố đô Huế ${days} ngày cho ${tripType}`,
        isItinerary: true,
        itineraryRes: res,
        days,
        tripType,
        preferredDishes,
        userLocName,
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

  function initPromptCards() {
    if (!chatThread) return;
    chatThread.querySelectorAll('.prompt-card').forEach(card => {
      card.addEventListener('click', () => {
        const prompt = card.dataset.prompt;
        if (prompt) sendChatQuery(prompt);
      });
    });
  }

  function renderWelcomeHero() {
    if (!chatThread) return;
    chatThread.innerHTML = `
      <div class="chat-welcome-hero" id="chat-welcome-hero">
        <div class="welcome-badge">
          <span class="welcome-badge-dot"></span>
          <span>Cố đô Huế AI Copilot</span>
        </div>
        <h1 class="welcome-heading">Hôm nay bạn muốn khám phá Huế như thế nào?</h1>
        <p class="welcome-subheading">Tra cứu di tích lịch sử, tìm quán ăn đặc sản chuẩn vị hoặc để AI tối ưu hóa lộ trình tham quan cho bạn.</p>

        <div class="welcome-prompt-grid">
          <button type="button" class="prompt-card" data-prompt="Lập lịch trình khám phá Huế 2 ngày 1 đêm tối ưu cho gia đình">
            <div class="prompt-card-icon">🏛️</div>
            <div class="prompt-card-content">
              <div class="prompt-card-title">Hành trình Di sản 2 Ngày</div>
              <div class="prompt-card-desc">Đại Nội, Lăng Khải Định, Tự Đức & Chùa Thiên Mụ</div>
            </div>
            <span class="prompt-card-arrow">↗</span>
          </button>

          <button type="button" class="prompt-card" data-prompt="Gợi ý các quán ăn đặc sản Huế chuẩn vị: bún bò mụ Rơi, bánh bèo nậm lọc, cơm hến và chè hẻm">
            <div class="prompt-card-icon">🍜</div>
            <div class="prompt-card-content">
              <div class="prompt-card-title">Bản đồ Ẩm thực Cố đô</div>
              <div class="prompt-card-desc">Bún bò mụ Rơi, bánh ép, cơm hến & chè hẻm nổi tiếng</div>
            </div>
            <span class="prompt-card-arrow">↗</span>
          </button>

          <button type="button" class="prompt-card" data-prompt="Những quán cà phê và điểm ngắm hoàng hôn đẹp nhất bên bờ sông Hương">
            <div class="prompt-card-icon">🌅</div>
            <div class="prompt-card-content">
              <div class="prompt-card-title">Sunset & Cà phê Sông Hương</div>
              <div class="prompt-card-desc">Điểm ngắm hoàng hôn đồi Vọng Cảnh & bến thuyền thơ mộng</div>
            </div>
            <span class="prompt-card-arrow">↗</span>
          </button>

          <button type="button" class="prompt-card" data-prompt="Từ Đại Nội đi Chợ Đông Ba như thế nào, khoảng cách bao xa và nên ghé những điểm nào dọc đường?">
            <div class="prompt-card-icon">🧭</div>
            <div class="prompt-card-content">
              <div class="prompt-card-title">Chỉ đường & Khoảng cách</div>
              <div class="prompt-card-desc">Lộ trình từ Đại Nội qua Chợ Đông Ba và cầu Tràng Tiền</div>
            </div>
            <span class="prompt-card-arrow">↗</span>
          </button>
        </div>
      </div>
    `;
    initPromptCards();
  }

  // Khởi tạo sự kiện cho các thẻ gợi ý ban đầu
  initPromptCards();

  // =============================================================================
  // QUẢN LÝ PHIÊN TRÒ CHUYỆN & LỊCH SỬ CHAT (CHAT SESSIONS ON FIRESTORE)
  // =============================================================================
  let activeSessionId = 'session_' + Date.now();
  let activeSessionTitle = 'Cuộc trò chuyện mới';
  let activeSessionMessages = [];
  let isRestoringSession = false;

  const btnNewChat = document.getElementById('btn-new-chat');
  const btnToggleChatHistory = document.getElementById('btn-toggle-chat-history');
  const btnWorkbenchSavedTours = document.getElementById('btn-workbench-saved-tours');
  const historyCountBadge = document.getElementById('history-count-badge');
  const chatHistoryDrawer = document.getElementById('chat-history-drawer');
  const chatHistoryBackdrop = document.getElementById('chat-history-backdrop');
  const btnCloseHistory = document.getElementById('btn-close-history');
  const btnHistoryNewChat = document.getElementById('btn-history-new-chat');
  const chatSessionsList = document.getElementById('chat-sessions-list');

  function getCurrentUserId() {
    return window.authController?.currentUser?.uid || null;
  }

  function parseTimestamp(rawDate) {
    if (!rawDate) return new Date();
    if (typeof rawDate.toDate === 'function') {
      try { return rawDate.toDate(); } catch {}
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
    if (!dateVal) return 'Vừa xong';
    const date = parseTimestamp(dateVal);
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);
    if (isNaN(diffSec) || diffSec < 60) return 'Vừa xong';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} phút trước`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour} giờ trước`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay === 1) return 'Hôm qua';
    if (diffDay < 7) return `${diffDay} ngày trước`;
    const day = (date.getDate() || 1).toString().padStart(2, '0');
    const month = ((date.getMonth() || 0) + 1).toString().padStart(2, '0');
    return `${day}/${month}`;
  }

  async function persistActiveSession() {
    if (isRestoringSession || !activeSessionId || activeSessionMessages.length === 0) return;
    const uid = getCurrentUserId();
    
    // Tự động gán tiêu đề session theo câu hỏi đầu tiên của người dùng
    const firstUserMsg = activeSessionMessages.find(m => m.role === 'user');
    if (firstUserMsg && (!activeSessionTitle || activeSessionTitle === 'Cuộc trò chuyện mới')) {
      activeSessionTitle = firstUserMsg.text.length > 36 
        ? firstUserMsg.text.substring(0, 36).trim() + '...' 
        : firstUserMsg.text.trim();
    }

    try {
      await saveChatSession(uid, {
        id: activeSessionId,
        title: activeSessionTitle || 'Cuộc trò chuyện mới',
        messages: activeSessionMessages
      });
      refreshChatHistoryList(false);
    } catch (e) {
      console.warn('Lỗi lưu session:', e);
    }
  }

  async function refreshChatHistoryList(openAfterRefresh = false) {
    const uid = getCurrentUserId();
    const sessions = await getUserChatSessions(uid);

    if (historyCountBadge) {
      historyCountBadge.textContent = sessions.length;
      historyCountBadge.style.display = sessions.length > 0 ? 'inline-flex' : 'none';
    }

    if (!chatSessionsList) return;

    if (sessions.length === 0) {
      chatSessionsList.innerHTML = `
        <div class="chat-history-empty">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <p>Chưa có cuộc trò chuyện nào.<br><span style="font-size:0.75rem; color:#A1A1AA;">Bắt đầu hỏi AI để tự động lưu lịch sử!</span></p>
        </div>
      `;
      return;
    }

    chatSessionsList.innerHTML = '';
    sessions.forEach(sess => {
      const item = document.createElement('div');
      item.className = `chat-session-item ${sess.id === activeSessionId ? 'active' : ''}`;
      item.dataset.sessionId = sess.id;
      item.innerHTML = `
        <div class="session-main">
          <div class="session-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div class="session-meta">
            <span class="session-title" title="${sess.title || 'Cuộc trò chuyện'}">${sess.title || 'Cuộc trò chuyện'}</span>
            <span class="session-date">${formatRelativeTime(sess.updatedAt || sess.createdAt)} · ${(sess.messages || []).length} tin</span>
          </div>
        </div>
        <button type="button" class="btn-delete-session" title="Xóa cuộc trò chuyện này" aria-label="Xóa">
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
        if (confirm(`Bạn có chắc muốn xóa cuộc trò chuyện "${sess.title}" không?`)) {
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

    // Dọn sạch hoàn toàn trạng thái bản đồ cũ trước khi nạp phiên chat mới
    if (mapStudio && typeof mapStudio.resetToDefaultState === 'function') {
      mapStudio.resetToDefaultState();
    }

    chatThread.innerHTML = '';

    if (activeSessionMessages.length === 0) {
      renderWelcomeHero();
    } else {
      activeSessionMessages.forEach(msg => {
        if (msg.role === 'user') {
          appendUserMessage(msg.text, false);
        } else if (msg.role === 'assistant') {
          if (msg.isItinerary && msg.itineraryRes) {
            appendItineraryDeckMessage(msg.itineraryRes, msg.days, msg.tripType, msg.preferredDishes, msg.userLocName, false);
          } else {
            appendAssistantResponse(msg.resData || { answer: msg.text }, false);
          }
        }
      });
    }

    isRestoringSession = false;
    toggleChatHistoryDrawer(false);
    refreshChatHistoryList(false);
  }

  function startNewChatSession() {
    activeSessionId = 'session_' + Date.now();
    activeSessionTitle = 'Cuộc trò chuyện mới';
    activeSessionMessages = [];
    renderWelcomeHero();
    toggleChatHistoryDrawer(false);
    refreshChatHistoryList(false);
    if (chatInput) chatInput.focus();

    // DỌN SẠCH TOÀN BỘ BẢN ĐỒ: Đóng popup chặng, xóa route lộ trình và ẩn stepper thanh chặng
    if (mapStudio && typeof mapStudio.resetToDefaultState === 'function') {
      mapStudio.resetToDefaultState();
    }
  }

  function toggleChatHistoryDrawer(forceState) {
    if (!chatHistoryDrawer) return;
    const isOpen = typeof forceState === 'boolean' ? forceState : !chatHistoryDrawer.classList.contains('open');
    if (isOpen) {
      chatHistoryDrawer.hidden = false;
      requestAnimationFrame(() => {
        chatHistoryDrawer.classList.add('open');
        btnToggleChatHistory?.classList.add('active');
      });
      refreshChatHistoryList();
    } else {
      chatHistoryDrawer.classList.remove('open');
      btnToggleChatHistory?.classList.remove('active');
      setTimeout(() => {
        if (!chatHistoryDrawer.classList.contains('open')) {
          chatHistoryDrawer.hidden = true;
        }
      }, 280);
    }
  }

  btnNewChat?.addEventListener('click', () => startNewChatSession());
  btnHistoryNewChat?.addEventListener('click', () => startNewChatSession());
  btnToggleChatHistory?.addEventListener('click', () => toggleChatHistoryDrawer());
  btnWorkbenchSavedTours?.addEventListener('click', () => {
    if (window.authController) {
      if (!window.authController.currentUser) {
        window.authController.openAuthModal('login');
        window.authController.showToast('Vui lòng đăng nhập để xem các lịch trình đã lưu.');
      } else {
        window.authController.openSavedToursModal();
      }
    }
  });
  btnCloseHistory?.addEventListener('click', () => toggleChatHistoryDrawer(false));
  chatHistoryBackdrop?.addEventListener('click', () => toggleChatHistoryDrawer(false));

  // Tự động làm mới danh sách session khi trạng thái đăng nhập thay đổi
  onAuthChange(() => {
    refreshChatHistoryList();
  });

  // Tải danh sách session ban đầu
  refreshChatHistoryList();

  async function sendChatQuery(query) {
    if (!query) return;

    // Xóa Welcome Hero khi bắt đầu chat
    const hero = document.getElementById('chat-welcome-hero');
    if (hero) hero.remove();

    // Kiểm tra câu hỏi có liên quan đến vị trí/không gian/chỉ đường/bản đồ
    const isSpatialQuery = /chỉ đường|đường đi|đi đến|từ .+ đi|khoảng cách|cách bao xa|gần đây|quanh đây|ở đâu|vị trí|tọa độ|bản đồ|lộ trình|tour|thuê xe/i.test(query);

    // Kiểm tra nếu người dùng yêu cầu lập lịch trình qua câu chat
    const lowerQuery = query.toLowerCase();
    const isPlanIntent = (
      lowerQuery.includes('lập lịch trình') ||
      lowerQuery.includes('tạo lịch trình') ||
      lowerQuery.includes('gợi ý lịch trình') ||
      lowerQuery.includes('lên lịch trình') ||
      lowerQuery.includes('lên tour') ||
      lowerQuery.includes('lập tour') ||
      lowerQuery.includes('tour du lịch')
    );

    if (isPlanIntent || isSpatialQuery) {
      showMapPanel(true); // Tự động mở bản đồ theo ngữ cảnh không gian
    }

    if (isPlanIntent) {
      let days = 2;
      if (lowerQuery.includes('1 ngày') || lowerQuery.includes('một ngày')) days = 1;
      else if (lowerQuery.includes('3 ngày') || lowerQuery.includes('ba ngày')) days = 3;
      else if (lowerQuery.includes('2 ngày') || lowerQuery.includes('hai ngày')) days = 2;
      
      const tripType = selectTripType ? selectTripType.value : 'Couples';
      const preferredDishes = getSelectedDishes();
      if (chatInput) chatInput.value = '';
      generateItineraryInChat(days, tripType, preferredDishes);
      return;
    }

    // Hiển thị tin nhắn người dùng
    appendUserMessage(query);
    if (chatInput) chatInput.value = '';
    if (chatSendBtn) chatSendBtn.disabled = true;

    // Hiển thị loading placeholder
    const loadingId = appendAssistantLoading();

    try {
      // Truyền tọa độ GPS người dùng nếu đã có định vị
      const userLat = mapStudio.userLocation ? mapStudio.userLocation.lat : null;
      const userLng = mapStudio.userLocation ? mapStudio.userLocation.lng : null;

      const res = await TourismApiClient.askAssistant(query, 'Thành phố Huế', userLat, userLng);
      removeLoadingMessage(loadingId);
      appendAssistantResponse(res);
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

  function appendUserMessage(text, persist = true) {
    const msg = document.createElement('div');
    msg.className = 'chat-message user';
    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
      <div class="message-bubble">
        <p>${text}</p>
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;

    if (persist && !isRestoringSession) {
      activeSessionMessages.push({
        role: 'user',
        text: text,
        timestamp: Date.now()
      });
      persistActiveSession();
    }
  }

  function appendAssistantLoading(customText = 'Đang phân tích không gian và tổng hợp gợi ý...') {
    const id = `loading-${Date.now()}`;
    const msg = document.createElement('div');
    msg.id = id;
    msg.className = 'chat-message assistant';
    msg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/></svg>
      </div>
      <div class="message-bubble">
        <div class="message-author">Trợ lý Cố đô</div>
        <p class="loading-text">${customText}</p>
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

  function appendAssistantResponse(res, persist = true) {
    const msg = document.createElement('div');
    msg.className = 'chat-message assistant';

    const formattedAnswer = res.answer
      ? res.answer
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
        origin.name = mapStudio.userLocation.name || 'Vị trí của bạn';
      }

      // Fallback nếu vẫn thiếu tọa độ origin: Cầu Tràng Tiền (Trung tâm Huế)
      if (!origin.lat || !origin.lng) {
        origin.lat = 16.4674;
        origin.lng = 107.5905;
        origin.name = origin.name || 'Cầu Tràng Tiền (Trung tâm Huế)';
      }

      // Tính khoảng cách ước lượng ban đầu
      const R = 6371;
      const dLat = (destination.lat - origin.lat) * Math.PI / 180;
      const dLon = (destination.lng - origin.lng) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(origin.lat * Math.PI / 180) * Math.cos(destination.lat * Math.PI / 180) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const estDistKm = (R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))).toFixed(1);
      const estDurationMin = Math.max(2, Math.round(parseFloat(estDistKm) * 2.5));

      const gmapsDirUrl = `https://www.google.com/maps/dir/?api=1&origin=${origin.lat},${origin.lng}&destination=${destination.lat},${destination.lng}`;

      navCardHtml = `
        <div class="chat-nav-card">
          <div class="nav-card-header">
            <div class="nav-card-header-main">
              <div class="nav-card-icon-badge">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
              </div>
              <div>
                <div class="nav-card-title">Lộ trình Chỉ đường Tối ưu</div>
                <div class="nav-card-subtitle">${isWalking ? 'Tuyến đi bộ ngắm cảnh' : 'Xe máy / Ô tô theo đường nội đô Huế'}</div>
              </div>
            </div>
            <div class="nav-card-badge-metrics">
              <span class="nav-metric-pill">~${estDistKm} km</span>
              <span class="nav-metric-pill highlight">~${estDurationMin} phút</span>
            </div>
          </div>

          <div class="nav-card-body">
            <div class="nav-route-row origin">
              <div class="route-marker-badge origin">A</div>
              <div class="route-point-content">
                <div class="route-point-label">Điểm khởi hành</div>
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
                <div class="route-point-label">Điểm đến</div>
                <div class="route-point-name">${destination.name}</div>
                ${destination.address ? `<div class="route-point-address">📍 ${destination.address}</div>` : ''}
              </div>
            </div>
          </div>

          <div class="nav-card-actions">
            <button type="button" class="btn-nav-replot" data-origin-lat="${origin.lat}" data-origin-lng="${origin.lng}" data-origin-name="${origin.name}" data-dest-lat="${destination.lat}" data-dest-lng="${destination.lng}" data-dest-name="${destination.name}" data-profile="${profile}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
              <span>Vẽ lại trên Bản đồ</span>
            </button>
            <a href="${gmapsDirUrl}" target="_blank" rel="noopener noreferrer" class="btn-nav-gmaps" title="Mở chỉ đường trên ứng dụng Google Maps">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
              <span>Mở Google Maps</span> &rarr;
            </a>
          </div>
        </div>
      `;

      // Tự động vẽ lộ trình thực tế lên bản đồ Leaflet ngay lập tức!
      setTimeout(() => {
        mapStudio.drawNavigationRoute(origin, destination, profile);
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
            <span>Điểm đến gợi ý trên bản đồ:</span>
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

              return `
                <button type="button" class="chat-poi-btn ${catClass}" data-lat="${p.latitude}" data-lng="${p.longitude}" data-name="${p.name}" title="Ghim điểm này lên bản đồ">
                  <span class="poi-btn-icon">${iconSvg}</span>
                  <span class="poi-btn-name">${p.name}</span>
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
        <div class="message-author">Trợ lý Cố đô</div>
        <div class="answer-content">${formattedAnswer}</div>
        ${navCardHtml}
        ${placesPillsHtml}
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;

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
        mapStudio.panTo(lat, lng, 17);
        if (name && window.openPoiDetail) {
          window.openPoiDetail(name);
        }
      });
    });

    // TỰ ĐỘNG VẼ CÁC ĐỊA ĐIỂM ĐƯỢC GỢI Ý LÊN BẢN ĐỒ BÊN CẠNH NGAY LẬP TỨC
    if (matched.length > 0 && !(nav && nav.is_navigation)) {
      mapStudio.highlightChatPlaces(matched);
    }

    // Lưu phản hồi trợ lý vào phiên chat hiện tại
    if (persist && !isRestoringSession) {
      activeSessionMessages.push({
        role: 'assistant',
        text: res.answer || '',
        resData: res,
        timestamp: Date.now()
      });
      persistActiveSession();
    }
  }

  function appendAssistantError(errorMsg) {
    const msg = document.createElement('div');
    msg.className = 'chat-message assistant';
    msg.innerHTML = `
      <div class="message-avatar">⚠️</div>
      <div class="message-bubble" style="border-color: #EF4444;">
        <p style="color: #DC2626;">Lỗi truy vấn: ${errorMsg}. Vui lòng kiểm tra lại kết nối Backend.</p>
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

  let currentPoiData = null;

  async function openPoiDetail(name, placeId = null) {
    if (!name && !placeId) return;
    showMapPanel(true); // Hiển thị bản đồ để người dùng quan sát vị trí địa điểm

    // 1. Mở Drawer ngay lập tức với trạng thái sẵn sàng
    poiDrawer?.classList.add('open');
    poiDrawer?.setAttribute('aria-hidden', 'false');

    // Tìm dữ liệu địa phương từ masterLandmarks để hiển thị tức thì (Zero-latency fallback)
    const localPlace = window.mapStudio?.masterLandmarks?.find(p => 
      (placeId && p.place_id === placeId) || (name && p.name === name)
    );

    const initialName = localPlace?.name || name || 'Đang tải thông tin...';
    if (poiTitle) poiTitle.textContent = initialName;
    if (poiAddressText) poiAddressText.textContent = localPlace?.address || localPlace?.desc || 'Thành phố Huế';
    if (poiDescText) poiDescText.textContent = localPlace?.desc || 'Đang đồng bộ hồ sơ văn hóa và điểm đánh giá...';

    // Cập nhật nhãn category & rating sơ bộ từ dữ liệu bản đồ
    const initialCat = (localPlace?.cat || 'Attraction').toLowerCase();
    let initialCatClass = 'attraction';
    let initialCatIcon = '🏯';
    let initialCatLabel = 'Di tích & Thắng cảnh';

    if (initialCat.includes('restaurant') || initialCat.includes('ẩm thực') || initialCat.includes('quán')) {
      initialCatClass = 'restaurant';
      initialCatIcon = '🍲';
      initialCatLabel = 'Ẩm thực Cố đô';
    } else if (initialCat.includes('cafe') || initialCat.includes('cà phê') || initialCat.includes('sunset')) {
      initialCatClass = 'cafe';
      initialCatIcon = '☕';
      initialCatLabel = 'Cà phê & Sunset';
    } else if (initialCat.includes('hotel') || initialCat.includes('khách sạn') || initialCat.includes('resort')) {
      initialCatClass = 'hotel';
      initialCatIcon = '🏨';
      initialCatLabel = 'Khách sạn / Resort';
    }

    if (poiCatBadge) {
      poiCatBadge.className = `poi-cat-badge ${initialCatClass}`;
      poiCatBadge.textContent = `${initialCatIcon} ${initialCatLabel}`;
    }
    if (poiRatingVal) poiRatingVal.textContent = (localPlace?.rating_value || 4.6).toFixed(1);
    if (poiReviewCount) poiReviewCount.textContent = `(${localPlace?.review_count || 350} đánh giá)`;

    if (poiReviewsList) poiReviewsList.innerHTML = '<div style="font-size: 0.78rem; color: var(--color-ink-muted); padding: 6px 0;">Đang đồng bộ nhận xét từ du khách...</div>';
    if (poiNearbyList) poiNearbyList.innerHTML = '<div style="font-size: 0.78rem; color: var(--color-ink-muted); padding: 6px 0;">Đang tìm các địa điểm lân cận...</div>';

    try {
      const data = await TourismApiClient.getPlaceDetail(name, placeId);
      currentPoiData = data;

      // 2. Cập nhật Tiêu đề và Địa chỉ (bảo vệ tránh lệch tên)
      if (poiTitle) poiTitle.textContent = data.name || initialName;
      if (poiAddressText) poiAddressText.textContent = data.address || localPlace?.address || 'Thành phố Huế';
      if (poiDescText) poiDescText.textContent = data.description || localPlace?.desc || 'Địa điểm du lịch và ẩm thực nổi tiếng tại Cố đô Huế.';

      // 3. Category badge
      const cat = (data.category || '').toLowerCase();
      let catClass = 'attraction';
      let catIcon = '🏯';
      let catLabel = 'Di tích & Thắng cảnh';

      if (cat.includes('restaurant') || cat.includes('ẩm thực') || cat.includes('quán')) {
        catClass = 'restaurant';
        catIcon = '🍲';
        catLabel = 'Ẩm thực Cố đô';
      } else if (cat.includes('cafe') || cat.includes('cà phê') || cat.includes('sunset')) {
        catClass = 'cafe';
        catIcon = '☕';
        catLabel = 'Cà phê & Sunset';
      } else if (cat.includes('hotel') || cat.includes('khách sạn') || cat.includes('resort')) {
        catClass = 'hotel';
        catIcon = '🏨';
        catLabel = 'Khách sạn / Resort';
      }

      if (poiCatBadge) {
        poiCatBadge.className = `poi-cat-badge ${catClass}`;
        poiCatBadge.textContent = `${catIcon} ${catLabel}`;
      }

      // 4. Rating & Reviews
      if (poiRatingVal) poiRatingVal.textContent = (data.rating_value || 4.7).toFixed(1);
      if (poiReviewCount) poiReviewCount.textContent = `(${data.review_count || 120} đánh giá)`;

      // 5. Nhận xét chân thực từ du khách (TripAdvisor / SQLite)
      if (poiReviewsList) {
        if (data.reviews && data.reviews.length > 0) {
          if (poiSectionReviews) poiSectionReviews.style.display = 'flex';
          poiReviewsList.innerHTML = data.reviews.map(r => `
            <div class="poi-review-card">
              <div class="review-header">
                <span class="review-stars">${'⭐'.repeat(Math.round(r.rating || 5))}</span>
                <span class="review-tag">👤 ${r.trip_type || 'Du khách'} · ${r.visit_date || '2024'}</span>
              </div>
              <h5 class="review-title">${r.title}</h5>
              <p class="review-comment">“${r.comment}”</p>
            </div>
          `).join('');
        } else {
          poiReviewsList.innerHTML = '<div style="font-size: 0.78rem; color: #64748B;">Chưa có trích đoạn nhận xét chi tiết.</div>';
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
          poiNearbyList.innerHTML = '<div style="font-size: 0.78rem; color: var(--color-ink-muted);">Không có địa điểm lân cận trong bán kính gần.</div>';
        }
      }

      // 8. Cập nhật nút điều hướng Google Maps
      if (poiBtnGoogleMaps) {
        if (data.latitude && data.longitude) {
          poiBtnGoogleMaps.href = `https://www.google.com/maps/dir/?api=1&destination=${data.latitude},${data.longitude}`;
        } else {
          poiBtnGoogleMaps.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.name + ' Huế')}`;
        }
      }

    } catch (err) {
      console.warn('Lỗi tải chi tiết POI:', err);
      if (poiDescText) poiDescText.textContent = `Không thể tải hồ sơ chi tiết: ${err.message}.`;
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
      alert('Địa điểm này chưa có thông tin tọa độ chính xác để chỉ đường.');
      return;
    }

    // Đóng drawer
    closePoiDetail();

    // Điểm xuất phát: Vị trí người dùng đã định vị, hoặc fallback Cầu Tràng Tiền
    const origin = mapStudio.userLocation || {
      lat: 16.4674,
      lng: 107.5905,
      name: 'Cầu Tràng Tiền (Trung tâm Huế)'
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
    const tabItinerary = document.getElementById('tab-btn-itinerary');
    if (tabItinerary) tabItinerary.click();
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
    const tabChat = document.getElementById('tab-btn-chat');
    if (tabChat) tabChat.click();
    if (chatInput) chatInput.value = `Hãy giới thiệu chi tiết về ${currentPoiData.name} và các món ăn đặc sản nổi tiếng ở đây.`;
    chatForm?.dispatchEvent(new Event('submit'));
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
      alert('Địa điểm này chưa có tọa độ chính xác để chỉ đường.');
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
      name: 'Cầu Tràng Tiền (Trung tâm Huế)'
    };

    const destination = {
      lat: parseFloat(destLat),
      lng: parseFloat(destLng),
      name: destName || 'Điểm đến',
      address: destAddress || ''
    };

    // 5. Vẽ tuyến đường thực tế qua OSRM và hiển thị Banner điều hướng
    mapStudio.drawNavigationRoute(origin, destination, 'driving');
  };

});
