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

  // 4. MAP TOOLBAR CONTROLS
  const btnResetMap = document.getElementById('btn-reset-map');
  const btnToggleRadius = document.getElementById('btn-toggle-radius');
  const selectMapStyle = document.getElementById('select-map-style');

  selectMapStyle?.addEventListener('change', (e) => {
    mapStudio.setMapStyle(e.target.value);
  });

  btnResetMap?.addEventListener('click', () => {
    mapStudio.resetView();
  });

  btnToggleRadius?.addEventListener('click', () => {
    const isShowing = mapStudio.toggleRadius();
    btnToggleRadius.classList.toggle('active', isShowing);
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
              <h4 class="step-poi-name">${slot.place_name || slot.name}</h4>
              <p class="step-poi-desc">${slot.description || slot.address || 'Điểm trải nghiệm di sản Cố Đô'}</p>
              <div class="step-meta-row">
                <span class="meta-pill">${slot.activity_type || slot.category || (isFood ? 'Ẩm thực' : 'Di tích')}</span>
                ${ratingBadge}
                ${distanceBadge}
                ${dishBadge}
                ${lat && lng ? `<button type="button" class="btn-locate" data-lat="${lat}" data-lng="${lng}" data-name="${slot.place_name || slot.name}">📍 Ghim bản đồ</button>` : ''}
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

      // Nếu có các điểm trả về -> Vẽ lên bản đồ
      if (res.matched_places && res.matched_places.length > 0) {
        const stops = res.matched_places.map(p => ({
          lat: p.latitude,
          lng: p.longitude,
          name: p.name,
          category: p.category || 'Attraction',
          address: p.address || ''
        }));
        mapStudio.drawTourRoute(stops);
      }
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
    
    let placesHtml = '';
    if (res.matched_places && res.matched_places.length > 0) {
      placesHtml = `
        <div style="margin-top: 0.65rem; padding-top: 0.5rem; border-top: 1px dashed var(--color-border);">
          <strong style="font-size: 0.8rem; color: var(--color-deep);">Thực thể không gian liên quan:</strong>
          <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.35rem;">
            ${res.matched_places.map(p => `
              <span class="meta-pill pill-poi" onclick="window.locatePoi(${p.latitude}, ${p.longitude})">
                📍 ${p.name} (${p.category || 'POI'})
              </span>
            `).join('')}
          </div>
        </div>
      `;
    }

    const formattedAnswer = res.answer
      ? res.answer
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br/>')
      : '';

    msg.innerHTML = `
      <div class="message-avatar">🏯</div>
      <div class="message-bubble">
        <div>${formattedAnswer}</div>
        ${placesHtml}
        <div class="message-meta">
          <span style="color: var(--color-ink-muted);">Độ tin cậy: ${(res.confidence_score * 100).toFixed(0)}%</span>
        </div>
      </div>
    `;
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;
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

  window.locatePoi = (lat, lng) => {
    mapStudio.panTo(lat, lng, 16);
  };

});
