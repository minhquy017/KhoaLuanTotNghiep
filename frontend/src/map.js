// =============================================================================
// HUẾ SMART TOURISM — SPATIAL MAP STUDIO (Leaflet Controller)
// Trực quan hóa không gian: Điểm di sản, Quán ăn, Cụm bán kính & Tuyến Tour
// =============================================================================

import L from 'leaflet';
window.L = L;
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import hueTopPlaces from './hue_top_places.json';

export class SpatialMapStudio {
  constructor(containerId = 'map-container') {
    this.containerId = containerId;
    this.map = null;
    this.markersLayer = null;
    this.routesLayer = null;
    this.centerHue = [16.4637, 107.5909];
    this.defaultZoom = 13;
    this.activeCategoryFilter = 'all';
    this.currentTileLayer = null;
    this.markerInstances = new Map();
    this.userLocation = null;
    this.userLocationMarker = null;
    this.navigationLayer = null;

    // Dữ liệu Top 158 Địa danh & Cơ sở Dịch vụ Chuẩn Cố Đô Huế (Khai phá từ Đồ thị Tri thức & CSDL)
    this.masterLandmarks = hueTopPlaces;
  }

  getTileUrlConfig(styleName) {
    const configs = {
      google_streets: {
        url: 'https://mt{s}.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}',
        options: {
          subdomains: ['0', '1', '2', '3'],
          attribution: '&copy; Google Maps',
          maxZoom: 20
        }
      },
      google_satellite: {
        url: 'https://mt{s}.google.com/vt/lyrs=y&hl=vi&x={x}&y={y}&z={z}',
        options: {
          subdomains: ['0', '1', '2', '3'],
          attribution: '&copy; Google Maps Vệ Tinh',
          maxZoom: 20
        }
      }
    };
    return configs[styleName] || configs.google_streets;
  }

  init() {
    if (this.map) return;

    // Khởi tạo bản đồ Leaflet
    this.map = L.map(this.containerId, {
      zoomControl: false,
      minZoom: 3,
      maxZoom: 20
    }).setView(this.centerHue, this.defaultZoom);

    // Zoom control ở góc dưới bên phải
    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    // Mặc định nạp bản đồ Google Maps sắc nét, hiện đại, tiếng Việt chuẩn
    this.setMapStyle('google_streets');

    // Layer Groups - Tích hợp MarkerClusterGroup với chùm ghim xếp lớp nghệ thuật (không hiển thị số khô khan)
    if (typeof L.markerClusterGroup === 'function') {
      this.markersLayer = L.markerClusterGroup({
        maxClusterRadius: 42,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        disableClusteringAtZoom: 17,
        iconCreateFunction: (cluster) => {
          const count = cluster.getChildCount();
          const isLarge = count > 12;
          const isMedium = count > 4;

          return L.divIcon({
            html: `
              <div class="stacked-cluster-pin ${isLarge ? 'cluster-large' : isMedium ? 'cluster-medium' : 'cluster-small'}" title="Quần thể điểm đến (Nhấp để mở rộng)">
                <div class="pin-layer pin-back-left"></div>
                ${isMedium ? '<div class="pin-layer pin-back-right"></div>' : ''}
                <div class="pin-layer pin-front-center">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="#FFFFFF">
                    <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z"/>
                  </svg>
                </div>
              </div>
            `,
            className: 'marker-cluster-wrapper',
            iconSize: L.point(38, 42),
            iconAnchor: L.point(19, 36)
          });
        }
      }).addTo(this.map);
    } else {
      this.markersLayer = L.layerGroup().addTo(this.map);
    }
    this.routesLayer = L.layerGroup().addTo(this.map);
    this.navigationLayer = L.layerGroup().addTo(this.map);

    // Nạp sẵn toàn bộ địa danh biểu tượng của Cố đô Huế
    this.renderDefaultHeritageSites();

    // Đảm bảo kích thước bản đồ hiển thị mượt mà
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 150);
  }

  /**
   * Chuyển đổi giao diện nền bản đồ linh hoạt (Street / Satellite)
   */
  setMapStyle(styleName = 'google_streets') {
    if (!this.map) return;
    const config = this.getTileUrlConfig(styleName);

    if (this.currentTileLayer) {
      this.map.removeLayer(this.currentTileLayer);
    }

    this.currentTileLayer = L.tileLayer(config.url, config.options);
    this.currentTileLayer.addTo(this.map);
  }

  /**
   * Tạo Custom Architectural SVG Marker chuẩn di sản Cố Đô (sắc sảo, tối giản, thanh lịch)
   */
  createCustomIcon(category = 'Attraction', label = '', stepNumber = null) {
    const catLower = (category || '').toLowerCase();
    
    // Bảng màu di sản Cố Đô có kỷ luật (chất gốm sứ, ngói lưu ly và thổ nhưỡng)
    let pinColor = '#B45309'; // Di tích: Vàng thổ hoàng / Hoàng cung
    let svgIcon = `
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/>
      </svg>
    `;

    if (catLower.includes('restaurant') || catLower.includes('ẩm thực') || catLower.includes('quán')) {
      pinColor = '#C2410C'; // Ẩm thực: Đỏ gạch / Đất nung
      svgIcon = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 2v8a3 3 0 0 1-6 0V2M15 10v12M6 2v20M3 2h6"/>
        </svg>
      `;
    } else if (catLower.includes('cafe') || catLower.includes('cà phê') || catLower.includes('sunset')) {
      pinColor = '#78350F'; // Cà phê & Sunset: Nâu hổ phách ấm
      svgIcon = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>
        </svg>
      `;
    } else if (catLower.includes('hotel') || catLower.includes('khách sạn') || catLower.includes('resort')) {
      pinColor = '#0F766E'; // Khách sạn & Nghỉ dưỡng: Xanh chàm trầm
      svgIcon = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/>
        </svg>
      `;
    }

    const stepBadgeHtml = stepNumber !== null ? `
      <div style="
        position: absolute;
        top: -6px;
        right: -6px;
        background: #1C1917;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 10px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #FFFFFF;
        box-shadow: 0 1px 4px rgba(0,0,0,0.25);
        z-index: 10;
      ">${stepNumber}</div>
    ` : '';

    return L.divIcon({
      className: 'heritage-custom-marker',
      html: `
        <div style="
          position: relative;
          width: 28px;
          height: 34px;
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          ${stepBadgeHtml}
          <div style="
            width: 26px;
            height: 26px;
            background-color: ${pinColor};
            border-radius: 50% 50% 50% 3px;
            transform: rotate(-45deg);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 3px 8px rgba(28, 25, 23, 0.22);
            border: 2px solid #FFFFFF;
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
          ">
            <div style="
              transform: rotate(45deg);
              display: flex;
              align-items: center;
              justify-content: center;
            ">${svgIcon}</div>
          </div>
        </div>
      `,
      iconSize: [28, 34],
      iconAnchor: [14, 32],
      popupAnchor: [0, -30]
    });
  }

  /**
   * Đặt lại góc nhìn trung tâm TP Huế
   */
  resetView() {
    if (this.map) {
      this.filterByCategory('all');
      this.map.setView(this.centerHue, this.defaultZoom, { animate: true });
    }
  }

  /**
   * Lấy số lượng địa điểm theo từng danh mục
   */
  getCategoryCounts() {
    const counts = { all: this.masterLandmarks.length, attraction: 0, restaurant: 0, cafe: 0, hotel: 0 };
    this.masterLandmarks.forEach(item => {
      const c = item.cat.toLowerCase();
      if (counts[c] !== undefined) {
        counts[c]++;
      }
    });
    return counts;
  }

  /**
   * Lọc địa điểm theo danh mục và tự động căn chỉnh khung hình
   */
  filterByCategory(category = 'all') {
    this.activeCategoryFilter = category;
    this.markersLayer.clearLayers();
    this.markerInstances.clear();

    const catNormalized = (category || 'all').toLowerCase();
    const filtered = catNormalized === 'all'
      ? this.masterLandmarks
      : this.masterLandmarks.filter(item => item.cat.toLowerCase() === catNormalized);

    const latlngs = [];
    filtered.forEach(p => {
      const marker = this.addPoi(p.lat, p.lng, p.name, p.cat, p.desc, null, p.place_id);
      if (marker) {
        this.markerInstances.set(p.name, marker);
        latlngs.push([p.lat, p.lng]);
      }
    });

    if (latlngs.length > 0 && this.map) {
      if (catNormalized === 'all') {
        this.map.setView(this.centerHue, this.defaultZoom, { animate: true });
      } else {
        const bounds = L.latLngBounds(latlngs);
        this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15, animate: true });
      }
    }

    return {
      category,
      count: filtered.length,
      landmarks: filtered
    };
  }

  /**
   * Tìm kiếm địa danh không dấu, hỗ trợ gõ nhanh tiếng Việt
   */
  searchLandmarks(query = '') {
    const q = this.removeVietnameseTones(query.trim().toLowerCase());
    if (!q) return [];

    return this.masterLandmarks.filter(item => {
      const nameNorm = this.removeVietnameseTones(item.name.toLowerCase());
      const descNorm = this.removeVietnameseTones(item.desc.toLowerCase());
      const tagsNorm = this.removeVietnameseTones((item.tags || '').toLowerCase());
      const catNorm = this.removeVietnameseTones(item.cat.toLowerCase());
      return nameNorm.includes(q) || descNorm.includes(q) || tagsNorm.includes(q) || catNorm.includes(q);
    });
  }

  removeVietnameseTones(str) {
    if (!str) return '';
    return str
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/đ/g, 'd')
      .replace(/Đ/g, 'd');
  }

  /**
   * Bay mượt mà đến địa điểm và mở popup
   */
  flyToPoi(name) {
    const poi = this.masterLandmarks.find(p => p.name === name);
    if (!poi || !this.map) return;

    let marker = this.markerInstances.get(poi.name);
    if (!marker) {
      // Nếu địa điểm chưa nằm trong layer do đang lọc danh mục khác, tạm thời thêm vào
      marker = this.addPoi(poi.lat, poi.lng, poi.name, poi.cat, poi.desc, null, poi.place_id);
      this.markerInstances.set(poi.name, marker);
    }

    this.map.flyTo([poi.lat, poi.lng], 16, { duration: 1.2 });
    setTimeout(() => {
      if (marker) marker.openPopup();
    }, 600);
  }

  /**
   * Hiển thị các địa danh biểu tượng ban đầu (Tất cả)
   */
  renderDefaultHeritageSites() {
    this.filterByCategory('all');
  }

  addPoi(lat, lng, name, category = 'Attraction', address = '', stepNumber = null, placeId = null) {
    if (!lat || !lng) return null;
    const icon = this.createCustomIcon(category, '', stepNumber);

    const stepLabel = stepNumber !== null 
      ? `<div class="popup-step-tag">Điểm dừng ${stepNumber}</div>` 
      : '';

    const safeName = (name || '').replace(/'/g, "\\'");
    const safePlaceId = (placeId || '').replace(/'/g, "\\'");
    const popupHtml = `
      <div class="custom-leaflet-popup">
        ${stepLabel}
        <div class="popup-title">${name}</div>
        <div class="popup-category">${category}</div>
        <div class="popup-address">${address || 'Thành phố Huế'}</div>
        <div class="popup-actions">
          <button type="button" class="btn-open-detail-popup" onclick="window.openPoiDetail && window.openPoiDetail('${safeName}', '${safePlaceId}')">
            <span>Xem chi tiết</span> &rarr;
          </button>
          <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}" target="_blank" rel="noopener noreferrer" class="popup-gmaps-link">
            <span>Chỉ đường Google Maps</span>
          </a>
        </div>
      </div>
    `;

    const marker = L.marker([lat, lng], { icon })
      .bindPopup(popupHtml)
      .addTo(this.markersLayer);

    return marker;
  }

  /**
   * Vẽ tuyến tour giao thông thực tế theo đường phố & cầu Huế (OSRM Driving Engine)
   */
  async drawTourRoute(stops = []) {
    this.clearAll();
    const validStops = stops.filter(s => s && s.lat && s.lng);
    if (validStops.length === 0) return;

    // 1. Đánh dấu từng POI với số thứ tự chặng (1, 2, 3...)
    validStops.forEach((stop, idx) => {
      const marker = this.addPoi(
        stop.lat, 
        stop.lng, 
        stop.name, 
        stop.category || 'Attraction', 
        stop.address,
        idx + 1
      );
      if (idx === 0 && marker) marker.openPopup();
    });

    if (validStops.length === 1) {
      this.map.setView([validStops[0].lat, validStops[0].lng], 14);
      return;
    }

    // 2. Gọi OSRM Routing API để lấy lộ trình di chuyển thực tế theo mạng lưới giao thông Huế
    let routeLatLngs = null;
    let routeInfo = null;

    try {
      // OSRM nhận toạ độ dạng: lng,lat;lng,lat...
      const coordString = validStops.map(s => `${s.lng},${s.lat}`).join(';');
      const url = `https://router.project-osrm.org/route/v1/driving/${coordString}?overview=full&geometries=geojson`;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
          const r = data.routes[0];
          // OSRM toạ độ dạng [lng, lat], chuyển sang Leaflet [lat, lng]
          routeLatLngs = r.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
          routeInfo = {
            distanceKm: (r.distance / 1000).toFixed(1),
            durationMin: Math.round(r.duration / 60)
          };
        }
      }
    } catch (err) {
      console.warn('Không thể nạp tuyến đường OSRM (sử dụng đường nối trực tiếp fallback):', err);
    }

    // 3. Fallback sang đường nối trực tiếp nếu OSRM timeout / offline
    const isRealRoad = !!routeLatLngs && routeLatLngs.length > 0;
    const finalLatLngs = isRealRoad ? routeLatLngs : validStops.map(s => [s.lat, s.lng]);

    // 4. Vẽ Polyline sắc nét theo các cung đường thực tế
    // Lớp viền trắng tương phản (Casing) giúp nhìn rõ trên cả nền Google Maps lẫn Vệ Tinh
    L.polyline(finalLatLngs, {
      color: '#FFFFFF',
      weight: 6.5,
      opacity: 0.95,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.routesLayer);

    // Lớp tuyến đường chính: Màu xanh Indigo đậm nét liền uốn lượn qua các con đường và cây cầu
    const mainPolyline = L.polyline(finalLatLngs, {
      color: isRealRoad ? '#1D4ED8' : '#0E8B7D',
      weight: 4.5,
      opacity: 1,
      dashArray: isRealRoad ? null : '6, 8',
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.routesLayer);

    // Gắn Tooltip hiển thị thông số lộ trình di chuyển thực tế
    if (routeInfo) {
      mainPolyline.bindTooltip(
        `🚗 <b>Lộ trình thực tế:</b> ${routeInfo.distanceKm} km · ~${routeInfo.durationMin} phút di chuyển`,
        { sticky: true }
      );
    }

    // 5. Căn chỉnh góc nhìn bản đồ bao trọn lộ trình
    this.map.fitBounds(mainPolyline.getBounds(), { padding: [50, 50] });
  }

  panTo(lat, lng, zoom = 16) {
    if (this.map && lat && lng) {
      this.map.setView([lat, lng], zoom, { animate: true });
      if (this.markersLayer) {
        this.markersLayer.eachLayer(layer => {
          if (layer.getLatLng) {
            const pos = layer.getLatLng();
            if (Math.abs(pos.lat - lat) < 0.0001 && Math.abs(pos.lng - lng) < 0.0001) {
              layer.openPopup();
            }
          }
        });
      }
    }
  }

  /**
   * Hiển thị các địa điểm được gợi ý từ Trợ lý Hỏi đáp (Chatbot)
   */
  highlightChatPlaces(places = []) {
    const validPlaces = places.filter(p => p && (p.latitude || p.lat) && (p.longitude || p.lng));
    if (validPlaces.length === 0) return;

    const addedMarkers = [];

    validPlaces.forEach((p) => {
      const lat = p.latitude || p.lat;
      const lng = p.longitude || p.lng;
      const isRestaurant = (p.category || '').toLowerCase().includes('restaurant') ||
                           (p.category || '').toLowerCase().includes('ẩm thực') ||
                           (p.category || '').toLowerCase().includes('quán');
      const cat = isRestaurant ? 'Restaurant' : (p.category || 'Attraction');

      const marker = this.addPoi(
        lat,
        lng,
        p.name,
        cat,
        p.address || 'Địa điểm gợi ý'
      );
      if (marker) addedMarkers.push(marker);
    });

    // Mở popup cho địa điểm đầu tiên
    if (addedMarkers.length > 0) {
      setTimeout(() => {
        addedMarkers[0].openPopup();
      }, 300);
    }

    // Căn góc nhìn bản đồ bao trọn các địa điểm được gợi ý
    if (validPlaces.length === 1) {
      const p = validPlaces[0];
      this.panTo(p.latitude || p.lat, p.longitude || p.lng, 16);
    } else {
      const latlngs = validPlaces.map(p => [p.latitude || p.lat, p.longitude || p.lng]);
      const bounds = L.latLngBounds(latlngs);
      this.map.fitBounds(bounds, { padding: [70, 70], maxZoom: 16 });
    }
  }

  /**
   * Thiết lập và hiển thị vị trí người dùng trên bản đồ (với radar pulse beacon & callout nổi bật)
   */
  setUserLocation(lat, lng, name = 'Vị trí của bạn') {
    if (!lat || !lng) return null;
    this.userLocation = { lat, lng, name };

    if (this.userLocationMarker) {
      this.userLocationMarker.remove();
    }

    const icon = L.divIcon({
      className: 'user-gps-marker-container',
      html: `
        <div class="user-gps-pulse-outer"></div>
        <div class="user-gps-pulse-inner"></div>
        <div class="user-gps-core">
          <div class="user-gps-core-dot">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="#FFFFFF">
              <polygon points="12 2 19 21 12 17 5 21 12 2" />
            </svg>
          </div>
        </div>
        <div class="user-gps-callout-pill">
          <span class="user-gps-callout-radar"></span>
          <span class="user-gps-callout-text">${name}</span>
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    });

    const popupHtml = `
      <div class="custom-leaflet-popup user-location-popup">
        <div class="popup-gps-header">
          <span class="popup-gps-badge">Định vị GPS</span>
          <h4 class="popup-gps-title">📍 ${name}</h4>
        </div>
        <p class="popup-gps-coords">Tọa độ: ${lat.toFixed(4)}°B, ${lng.toFixed(4)}°Đ</p>
        <div class="popup-gps-hint">✓ Hệ thống tính khoảng cách và dẫn đường từ điểm này</div>
      </div>
    `;

    this.userLocationMarker = L.marker([lat, lng], { icon, zIndexOffset: 1000 })
      .bindPopup(popupHtml)
      .addTo(this.map);

    return this.userLocation;
  }

  /**
   * Vẽ tuyến đường chỉ dẫn chi tiết (Navigation Route) từ Origin đến Destination qua OSRM
   */
  async drawNavigationRoute(origin, destination, profile = 'driving') {
    if (!origin || !destination) return null;
    const originLat = origin.latitude || origin.lat;
    const originLng = origin.longitude || origin.lng;
    const destLat = destination.latitude || destination.lat;
    const destLng = destination.longitude || destination.lng;

    if (!originLat || !originLng || !destLat || !destLng) return null;

    if (this.navigationLayer) {
      this.navigationLayer.clearLayers();
    } else {
      this.navigationLayer = L.layerGroup().addTo(this.map);
    }

    // 1. Tạo Start Marker (Cờ xuất phát / Origin)
    const originName = origin.name || 'Điểm xuất phát';
    const originIcon = L.divIcon({
      className: 'nav-flag-marker',
      html: `
        <div class="nav-flag-pin start" title="Điểm xuất phát: ${originName}">
          <span class="flag-icon">🚩</span>
          <span class="flag-label">${originName.substring(0, 16)}</span>
        </div>
      `,
      iconSize: [110, 34],
      iconAnchor: [16, 32]
    });

    L.marker([originLat, originLng], { icon: originIcon })
      .bindPopup(`<div class="custom-leaflet-popup"><b>🚩 Điểm xuất phát:</b><br/>${originName}</div>`)
      .addTo(this.navigationLayer);

    // 2. Tạo End Marker (Cờ đích đến / Destination)
    const destName = destination.name || 'Điểm đến';
    const destIcon = L.divIcon({
      className: 'nav-flag-marker',
      html: `
        <div class="nav-flag-pin destination" title="Điểm đến: ${destName}">
          <span class="flag-icon">🏁</span>
          <span class="flag-label">${destName.substring(0, 16)}</span>
        </div>
      `,
      iconSize: [110, 34],
      iconAnchor: [16, 32]
    });

    L.marker([destLat, destLng], { icon: destIcon })
      .bindPopup(`<div class="custom-leaflet-popup"><b>🏁 Điểm đến:</b><br/>${destName}<p style="margin:2px 0 0 0;font-size:0.75rem;color:#71717A;">${destination.address || ''}</p></div>`)
      .addTo(this.navigationLayer);

    // 3. Gọi OSRM Routing Engine
    let routeCoords = null;
    let distanceKm = (this.calcDistance(originLat, originLng, destLat, destLng)).toFixed(1);
    let durationMin = Math.max(2, Math.round(distanceKm * 2.5)); // Tốc độ nội đô Huế ~25km/h

    try {
      const url = `https://router.project-osrm.org/route/v1/${profile}/${originLng},${originLat};${destLng},${destLat}?overview=full&geometries=geojson&steps=true`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
          const r = data.routes[0];
          routeCoords = r.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
          distanceKm = (r.distance / 1000).toFixed(1);
          durationMin = Math.round(r.duration / 60);
        }
      }
    } catch (err) {
      console.warn('Lỗi kết nối OSRM, sử dụng tuyến nối trực tiếp fallback:', err);
    }

    const finalPath = (routeCoords && routeCoords.length > 0) 
      ? routeCoords 
      : [[originLat, originLng], [destLat, destLng]];

    // 4. Vẽ Polyline chỉ đường sắc nét
    // Casing viền trắng nổi bật
    L.polyline(finalPath, {
      color: '#FFFFFF',
      weight: 7,
      opacity: 0.95,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.navigationLayer);

    // Tuyến chính màu xanh Sapphire rực rỡ
    const mainNavLine = L.polyline(finalPath, {
      color: '#2563EB',
      weight: 4.8,
      opacity: 1,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.navigationLayer);

    // 5. Căn bản đồ bao trọn lộ trình
    this.map.fitBounds(mainNavLine.getBounds(), { padding: [60, 60] });

    // 6. Hiển thị Navigation Banner nổi trên đầu bản đồ
    this.showNavigationBanner({
      originName,
      destName,
      distanceKm,
      durationMin,
      originLat, originLng,
      destLat, destLng
    });

    return {
      distanceKm,
      durationMin,
      gmapsUrl: `https://www.google.com/maps/dir/?api=1&origin=${originLat},${originLng}&destination=${destLat},${destLng}`
    };
  }

  showNavigationBanner(info) {
    let banner = document.getElementById('map-nav-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'map-nav-banner';
      banner.className = 'map-nav-banner';
      const container = document.getElementById(this.containerId);
      if (container) container.appendChild(banner);
    }

    const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${info.originLat},${info.originLng}&destination=${info.destLat},${info.destLng}`;

    banner.innerHTML = `
      <div class="nav-banner-left">
        <div class="nav-banner-badge" title="Đang chỉ đường di chuyển">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
            <polygon points="3 11 22 2 13 21 11 13 3 11"/>
          </svg>
        </div>
        <div class="nav-banner-details">
          <div class="nav-banner-route">
            <span class="route-origin">${info.originName}</span>
            <span class="route-arrow-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </span>
            <span class="route-destination">${info.destName}</span>
          </div>
          <div class="nav-banner-metrics">
            <span class="metric-chip dist">${info.distanceKm} km</span>
            <span class="metric-chip time">~${info.durationMin} phút</span>
          </div>
        </div>
      </div>
      <div class="nav-banner-right">
        <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn-banner-gmaps" title="Mở chỉ đường Turn-by-Turn trên Google Maps">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
          </svg>
          <span>Google Maps</span>
        </a>
        <button type="button" class="btn-banner-close" id="btn-close-nav-banner" title="Tắt lộ trình chỉ đường" aria-label="Đóng">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    `;
    banner.style.display = 'flex';

    document.getElementById('btn-close-nav-banner')?.addEventListener('click', () => {
      this.clearNavigationRoute();
    });
  }

  clearNavigationRoute() {
    if (this.navigationLayer) {
      this.navigationLayer.clearLayers();
    }
    const banner = document.getElementById('map-nav-banner');
    if (banner) banner.style.display = 'none';
  }

  calcDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  clearAll() {
    if (this.markersLayer) this.markersLayer.clearLayers();
    if (this.routesLayer) this.routesLayer.clearLayers();
    if (this.navigationLayer) this.navigationLayer.clearLayers();
    const banner = document.getElementById('map-nav-banner');
    if (banner) banner.style.display = 'none';
  }
}
