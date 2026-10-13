// =============================================================================
// HUẾ SMART TOURISM — MAIN APPLICATION CONTROLLER
// Trực quan hóa Kiến trúc Spatial GraphRAG theo chuẩn Hallmark Editorial
// =============================================================================

import './style.css';
import { TourismApiClient } from './api.js';
import { SpatialMapStudio } from './map.js';

document.addEventListener('DOMContentLoaded', async () => {
  // 1. KHỞI TẠO BẢN ĐỒ KHÔNG GIAN
  const mapStudio = new SpatialMapStudio('map-container');
  mapStudio.init();

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

  // 3. ĐIỀU HƯỚNG TABS
  const navTabs = document.querySelectorAll('.nav-tab');
  const tabPanels = document.querySelectorAll('.tab-panel');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.target;

      navTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      tabPanels.forEach(panel => {
        if (panel.id === `panel-${target}`) {
          panel.classList.add('active');
          panel.removeAttribute('hidden');
        } else {
          panel.classList.remove('active');
          panel.setAttribute('hidden', '');
        }
      });

      // Kích hoạt lại map size khi đổi tab
      setTimeout(() => {
        if (mapStudio.map) mapStudio.map.invalidateSize();
      }, 100);
    });
  });

  // 4. MAP STUDIO TOOLBAR, SEARCH & FILTER CONTROLS
  const btnResetMap = document.getElementById('btn-reset-map');
  const btnToggleRadius = document.getElementById('btn-toggle-radius');
  const selectRadiusRange = document.getElementById('select-radius-range');
  const legendRadiusVal = document.getElementById('legend-radius-val');
  const selectMapStyle = document.getElementById('select-map-style');
  const mapActiveMeta = document.getElementById('map-active-meta');
  const filterChips = document.querySelectorAll('.filter-chip');
  const mapSearchInput = document.getElementById('map-search-input');
  const mapSearchDropdown = document.getElementById('map-search-dropdown');
  const btnClearSearch = document.getElementById('btn-clear-search');

  // Đổi phong cách bản đồ (Google Maps / Vệ Tinh)
  selectMapStyle?.addEventListener('change', (e) => {
    mapStudio.setMapStyle(e.target.value);
  });

  // Cập nhật số lượng hiển thị trên từng chip danh mục
  function updateFilterCounts() {
    const counts = mapStudio.getCategoryCounts();
    const countAll = document.getElementById('count-all');
    const countAttraction = document.getElementById('count-attraction');
    const countRestaurant = document.getElementById('count-restaurant');
    const countCafe = document.getElementById('count-cafe');
    const countHotel = document.getElementById('count-hotel');

    if (countAll) countAll.textContent = counts.all;
    if (countAttraction) countAttraction.textContent = counts.attraction;
    if (countRestaurant) countRestaurant.textContent = counts.restaurant;
    if (countCafe) countCafe.textContent = counts.cafe;
    if (countHotel) countHotel.textContent = counts.hotel;
  }
  updateFilterCounts();

  // Danh mục tiêu đề bản đồ tương ứng
  const categoryTitles = {
    all: 'Toàn cảnh 32 Điểm Di sản Cố Đô Huế',
    attraction: 'Di tích Lịch sử, Thắng cảnh & Lăng tẩm',
    restaurant: 'Ẩm thực Truyền thống & Quán ăn Cố Đô',
    cafe: 'Cà phê View đẹp & Điểm ngắm Hoàng hôn',
    hotel: 'Khách sạn Boutique & Resort Nghỉ dưỡng'
  };

  // Xử lý click chọn bộ lọc danh mục
  filterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.category;
      filterChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const result = mapStudio.filterByCategory(cat);
      if (mapActiveMeta) {
        const title = categoryTitles[cat] || 'Địa điểm Cố Đô';
        mapActiveMeta.textContent = `${title} (${result.count} địa điểm)`;
      }
    });
  });

  // Tùy chỉnh cự ly bán kính phân tích không gian
  selectRadiusRange?.addEventListener('change', (e) => {
    const meters = parseInt(e.target.value, 10);
    mapStudio.setRadiusDistance(meters);
    if (legendRadiusVal) {
      legendRadiusVal.textContent = (meters / 1000).toFixed(1);
    }
    // Tự động kích hoạt hiển thị vòng bán kính nếu đang tắt
    if (!mapStudio.showRadius) {
      const isShowing = mapStudio.toggleRadius();
      btnToggleRadius?.classList.toggle('active', isShowing);
    }
  });

  btnToggleRadius?.addEventListener('click', () => {
    const isShowing = mapStudio.toggleRadius();
    btnToggleRadius.classList.toggle('active', isShowing);
  });

  // Đặt lại góc nhìn bản đồ trung tâm và khôi phục bộ lọc
  btnResetMap?.addEventListener('click', () => {
    mapStudio.resetView();
    filterChips.forEach(c => {
      if (c.dataset.category === 'all') c.classList.add('active');
      else c.classList.remove('active');
    });
    if (mapActiveMeta) {
      mapActiveMeta.textContent = 'Toàn cảnh 32 Điểm Di sản Cố Đô Huế';
    }
    if (mapSearchInput) {
      mapSearchInput.value = '';
      if (btnClearSearch) btnClearSearch.style.display = 'none';
    }
    if (mapSearchDropdown) mapSearchDropdown.style.display = 'none';
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
      attraction: '🏯',
      restaurant: '🍲',
      cafe: '☕',
      hotel: '🏨'
    };

    const catLabelMap = {
      attraction: 'Di tích',
      restaurant: 'Ẩm thực',
      cafe: 'Cà phê',
      hotel: 'Khách sạn'
    };

    mapSearchDropdown.innerHTML = results.slice(0, 8).map(item => {
      const cat = (item.cat || '').toLowerCase();
      const icon = iconMap[cat] || '📍';
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

  // 6. LẬP LỊCH TRÌNH TOUR (SPATIAL ITINERARY PLANNER)
  const formItinerary = document.getElementById('form-itinerary');
  const btnGenItinerary = document.getElementById('btn-generate-itinerary');
  const itineraryResults = document.getElementById('itinerary-results');
  const selectDays = document.getElementById('select-days');
  const selectTripType = document.getElementById('select-trip-type');

  formItinerary?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const days = parseInt(selectDays.value, 10);
    const tripType = selectTripType.value;
    const preferredDishes = getSelectedDishes();

    // 8-State: Loading
    btnGenItinerary.classList.add('loading');
    btnGenItinerary.disabled = true;

    itineraryResults.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⏳</div>
        <h3 class="empty-title">Đang tính toán tuyến đường tối ưu...</h3>
        <p class="empty-text">Hệ thống đang truy vấn Đồ thị Tri thức Không gian, co cụm theo bán kính trục sông Hương và ghép nối quán ăn gần nhất.</p>
      </div>
    `;

    try {
      const data = await TourismApiClient.generateItinerary(days, preferredDishes, tripType);
      renderItineraryCards(data);
    } catch (err) {
      itineraryResults.innerHTML = `
        <div class="empty-state" style="border-color: #EF4444;">
          <div class="empty-icon">⚠️</div>
          <h3 class="empty-title" style="color: #DC2626;">Không thể lập lịch trình</h3>
          <p class="empty-text">${err.message}. Đảm bảo Backend FastAPI đang chạy tại <code>localhost:8000</code>.</p>
        </div>
      `;
    } finally {
      btnGenItinerary.classList.remove('loading');
      btnGenItinerary.disabled = false;
    }
  });

  function renderItineraryCards(res) {
    const plan = res.itinerary_data;
    if (!plan || !plan.days || plan.days.length === 0) {
      itineraryResults.innerHTML = `<div class="empty-state"><p>Không tìm thấy dữ liệu lịch trình phù hợp.</p></div>`;
      return;
    }

    let html = '';
    const allStopsForMap = [];

    plan.days.forEach(day => {
      const slots = day.slots || day.stops || [];
      const totalKm = day.total_distance_km ? ` · Tổng cự ly: ${day.total_distance_km.toFixed(1)} km` : '';
      
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
        gmapsRouteBtn = `<a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn-gmaps-route" title="Mở chỉ đường toàn tuyến Ngày ${day.day_number} trên Google Maps">🧭 Google Maps</a>`;
      }

      html += `
        <div class="day-card">
          <div class="day-header">
            <h3 class="day-title">Ngày ${day.day_number}: ${day.theme || day.cluster_name || 'Khám phá Cố Đô'}</h3>
            <div class="day-header-actions">
              ${gmapsRouteBtn}
              <span class="day-badge">${slots.length} chặng${totalKm}</span>
            </div>
          </div>
          <div class="day-body">
      `;

      slots.forEach(slot => {
        const isFood = (slot.category || '').toLowerCase().includes('restaurant') || 
                       (slot.category || '').toLowerCase().includes('quán') || 
                       (slot.activity_type || '').toLowerCase().includes('ẩm thực');
        const lat = slot.latitude || slot.lat;
        const lng = slot.longitude || slot.lng;

        if (lat && lng) {
          allStopsForMap.push({
            lat, lng,
            name: slot.place_name || slot.name,
            category: slot.category || (isFood ? 'Restaurant' : 'Attraction'),
            address: slot.address || ''
          });
        }

        const distanceBadge = (slot.distance_from_prev_km && slot.distance_from_prev_km > 0)
          ? `<span class="meta-pill pill-distance">Cự ly chặng: ${slot.distance_from_prev_km.toFixed(1)} km</span>`
          : (slot.distance_to_anchor_km ? `<span class="meta-pill pill-distance">Cự ly: ${slot.distance_to_anchor_km.toFixed(1)} km</span>` : '');

        const dishBadge = slot.dish_highlight || slot.specialty_dish
          ? `<span class="meta-pill pill-dish">🍲 Món: ${slot.dish_highlight || slot.specialty_dish}</span>`
          : '';

        const ratingBadge = slot.rating
          ? `<span class="meta-pill pill-rating">⭐ ${slot.rating.toFixed(1)}</span>`
          : '';

        html += `
          <div class="timeline-step">
            <div class="step-time-badge">${slot.slot_name || slot.slot_time || 'Chặng tour'}</div>
            <div class="step-content">
              <h4 class="step-poi-name" style="cursor: pointer;" data-name="${slot.place_name || slot.name}" title="Nhấp để xem hồ sơ & đánh giá chi tiết">${slot.place_name || slot.name} <span style="font-size: 0.72rem; color: #D97706;">📋</span></h4>
              <p class="step-poi-desc">${slot.description || slot.address || 'Điểm trải nghiệm di sản Cố Đô'}</p>
              <div class="step-meta-row">
                <span class="meta-pill">${slot.activity_type || slot.category || (isFood ? 'Ẩm thực' : 'Di tích')}</span>
                ${ratingBadge}
                ${distanceBadge}
                ${dishBadge}
                ${lat && lng ? `<button type="button" class="btn-locate" data-lat="${lat}" data-lng="${lng}" data-name="${slot.place_name || slot.name}">📍 Ghim</button>` : ''}
                <button type="button" class="btn-step-detail" data-name="${slot.place_name || slot.name}" style="background: none; border: none; font-size: 0.75rem; color: #D97706; font-weight: 700; cursor: pointer; padding: 0 4px;">📋 Xem Chi Tiết</button>
              </div>
            </div>
          </div>
        `;
      });

      html += `
          </div>
        </div>
      `;
    });

    itineraryResults.innerHTML = html;

    // Gán sự kiện click định vị từng điểm
    itineraryResults.querySelectorAll('.btn-locate').forEach(btn => {
      btn.addEventListener('click', () => {
        const lat = parseFloat(btn.dataset.lat);
        const lng = parseFloat(btn.dataset.lng);
        mapStudio.panTo(lat, lng, 16);
      });
    });

    // Gán sự kiện click xem chi tiết từng điểm trong lịch trình
    itineraryResults.querySelectorAll('.btn-step-detail, .step-poi-name').forEach(el => {
      el.addEventListener('click', () => {
        const name = el.dataset.name;
        if (name && window.openPoiDetail) {
          window.openPoiDetail(name);
        }
      });
    });

    // Vẽ toàn bộ tuyến tour lên bản đồ Leaflet
    if (allStopsForMap.length > 0) {
      mapStudio.drawTourRoute(allStopsForMap);
    }
  }

  // 7. TRỢ LÝ HỎI ĐÁP (CHAT ASSISTANT)
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatThread = document.getElementById('chat-thread');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const promptChips = document.querySelectorAll('.chip-item');

  promptChips.forEach(chip => {
    chip.addEventListener('click', () => {
      chatInput.value = chip.textContent.trim();
      chatForm.dispatchEvent(new Event('submit'));
    });
  });

  chatForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Hiển thị tin nhắn người dùng
    appendUserMessage(query);
    chatInput.value = '';
    chatSendBtn.disabled = true;

    // Hiển thị loading placeholder
    const loadingId = appendAssistantLoading();

    try {
      const res = await TourismApiClient.askAssistant(query);
      removeLoadingMessage(loadingId);
      appendAssistantResponse(res);
    } catch (err) {
      removeLoadingMessage(loadingId);
      appendAssistantError(err.message);
    } finally {
      chatSendBtn.disabled = false;
    }
  });

  function appendUserMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'chat-message user';
    msg.innerHTML = `
      <div class="message-avatar">👤</div>
      <div class="message-bubble">
        <p>${text}</p>
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;
  }

  function appendAssistantLoading() {
    const id = `loading-${Date.now()}`;
    const msg = document.createElement('div');
    msg.id = id;
    msg.className = 'chat-message assistant';
    msg.innerHTML = `
      <div class="message-avatar">🏯</div>
      <div class="message-bubble">
        <p style="color: var(--color-ink-muted);"><em>Đang tìm kiếm thông tin và tạo câu trả lời...</em></p>
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

  function appendAssistantResponse(res) {
    const msg = document.createElement('div');
    msg.className = 'chat-message assistant';

    const formattedAnswer = res.answer
      ? res.answer
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br/>')
      : '';

    // Tạo các pill bấm nhanh định vị các địa điểm trên bản đồ
    let placesPillsHtml = '';
    const matched = res.matched_places || [];
    if (matched.length > 0) {
      placesPillsHtml = `
        <div class="chat-suggested-places" style="margin-top: 12px; padding-top: 10px; border-top: 1px dashed #CBD5E1;">
          <div style="font-size: 0.76rem; font-weight: 700; color: #475569; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">📍 Địa điểm đã ghim lên bản đồ (Bấm để xem chi tiết):</div>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${matched.map(p => `
              <button type="button" class="chat-poi-btn" data-lat="${p.latitude}" data-lng="${p.longitude}" data-name="${p.name}" style="
                background: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 0.78rem;
                font-weight: 600;
                color: #0F172A;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                transition: all 0.2s ease;
              ">
                <span>${(p.category || '').toLowerCase().includes('restaurant') ? '🍲' : '🏯'}</span>
                <span>${p.name}</span>
                <span style="font-size: 0.7rem; color: #D97706; margin-left: 2px;">📋</span>
              </button>
            `).join('')}
          </div>
        </div>
      `;
    }

    msg.innerHTML = `
      <div class="message-avatar">🏯</div>
      <div class="message-bubble">
        <div>${formattedAnswer}</div>
        ${placesPillsHtml}
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;

    // Gán sự kiện click vào các nút địa điểm trong chat bubble: Ghim bản đồ + Mở Drawer
    msg.querySelectorAll('.chat-poi-btn').forEach(btn => {
      btn.addEventListener('click', () => {
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
    if (matched.length > 0) {
      mapStudio.highlightChatPlaces(matched);
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
  const poiSectionDishes = document.getElementById('poi-section-dishes');
  const poiDishesGrid = document.getElementById('poi-dishes-grid');
  const poiSectionReviews = document.getElementById('poi-section-reviews');
  const poiReviewsList = document.getElementById('poi-reviews-list');
  const poiSectionNearby = document.getElementById('poi-section-nearby');
  const poiNearbyList = document.getElementById('poi-nearby-list');
  const poiBtnGoogleMaps = document.getElementById('poi-btn-google-maps');
  const poiBtnAddTour = document.getElementById('poi-btn-add-tour');
  const poiBtnAskAi = document.getElementById('poi-btn-ask-ai');

  let currentPoiData = null;

  async function openPoiDetail(name, placeId = null) {
    if (!name && !placeId) return;

    // 1. Mở Drawer ngay lập tức với trạng thái loading
    poiDrawer?.classList.add('open');
    poiDrawer?.setAttribute('aria-hidden', 'false');

    if (poiTitle) poiTitle.textContent = name || 'Đang tải thông tin...';
    if (poiAddressText) poiAddressText.textContent = 'Đang truy vấn cơ sở dữ liệu TripAdvisor & Đồ thị Tri thức...';
    if (poiDescText) poiDescText.textContent = 'Đang đồng bộ hồ sơ văn hóa, điểm đánh giá và các cạnh liên kết...';
    if (poiDishesGrid) poiDishesGrid.innerHTML = '<div style="font-size: 0.78rem; color: #64748B; padding: 6px 0;">⏳ Đang khai phá thực đơn từ cạnh SERVES...</div>';
    if (poiReviewsList) poiReviewsList.innerHTML = '<div style="font-size: 0.78rem; color: #64748B; padding: 6px 0;">⏳ Đang trích xuất nhận xét chân thực từ du khách...</div>';
    if (poiNearbyList) poiNearbyList.innerHTML = '<div style="font-size: 0.78rem; color: #64748B; padding: 6px 0;">⏳ Đang tính toán các điểm đến lân cận...</div>';

    try {
      const data = await TourismApiClient.getPlaceDetail(name, placeId);
      currentPoiData = data;

      // 2. Cập nhật Tiêu đề và Địa chỉ
      if (poiTitle) poiTitle.textContent = data.name;
      if (poiAddressText) poiAddressText.textContent = data.address || 'Thành phố Huế';
      if (poiDescText) poiDescText.textContent = data.description || 'Địa điểm du lịch và ẩm thực nổi tiếng tại Cố đô Huế.';

      // 3. Category badge
      const cat = (data.category || '').toLowerCase();
      let catClass = 'attraction';
      let catIcon = '🏯';
      let catLabel = 'Di tích & Thắng cảnh';

      if (cat.includes('restaurant') || cat.includes('ẩm thực') || cat.includes('quán')) {
        catClass = 'restaurant';
        catIcon = '🍲';
        catLabel = 'Ẩm thực Cố Đô';
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

      // 5. Cạnh SERVES (Món đặc sản)
      if (poiDishesGrid) {
        if (data.dishes && data.dishes.length > 0) {
          if (poiSectionDishes) poiSectionDishes.style.display = 'flex';
          poiDishesGrid.innerHTML = data.dishes.map(d => `
            <div class="poi-dish-chip">
              <span>🍲</span>
              <span>${d.name}</span>
              <span class="dish-mention">${d.mention_count || 1} lượt nhắc · ⭐ ${d.avg_rating || 4.5}</span>
            </div>
          `).join('');
        } else {
          poiDishesGrid.innerHTML = `
            <div style="font-size: 0.78rem; color: #64748B; font-style: italic;">
              ${catClass === 'attraction' ? '🏛️ Quần thể kiến trúc lịch sử, không kinh doanh dịch vụ ăn uống trực tiếp.' : 'Chưa có dữ liệu thực đơn được liên kết trong Đồ thị.'}
            </div>
          `;
        }
      }

      // 6. Nhận xét chân thực từ du khách (TripAdvisor / SQLite)
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
          poiNearbyList.innerHTML = '<div style="font-size: 0.78rem; color: #64748B;">Không tìm thấy địa điểm lân cận trong bán kính 1.5km.</div>';
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

  window.openPoiDetail = openPoiDetail;

  window.locatePoi = (lat, lng) => {
    mapStudio.panTo(lat, lng, 16);
  };

});
