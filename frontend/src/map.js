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
    this.radiusLayer = null;
    this.centerHue = [16.4637, 107.5909];
    this.defaultZoom = 13;
    this.showRadius = false;
    this.currentRadiusMeters = 1500;
    this.activeCategoryFilter = 'all';
    this.currentTileLayer = null;
    this.markerInstances = new Map();

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
    this.radiusLayer = L.layerGroup().addTo(this.map);

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
   * Cập nhật cự ly bán kính phân tích không gian (500m, 1000m, 1500m, 2500m, 5000m)
   */
  setRadiusDistance(radiusInMeters = 1500) {
    this.currentRadiusMeters = radiusInMeters;
    if (this.showRadius) {
      this.renderRadiusCircles();
    }
  }

  /**
   * Bật / tắt hiển thị bán kính không gian
   */
  toggleRadius() {
    this.showRadius = !this.showRadius;
    if (!this.showRadius) {
      this.radiusLayer.clearLayers();
    } else {
      this.renderRadiusCircles();
    }
    return this.showRadius;
  }

  renderRadiusCircles() {
    this.radiusLayer.clearLayers();
    const r = this.currentRadiusMeters || 1500;
    const rKm = (r / 1000).toFixed(1);

    // Vòng tròn bán kính quanh Đại Nội Huế (Bờ Bắc)
    L.circle([16.4690, 107.5781], {
      radius: r,
      color: '#D97706',
      weight: 2,
      dashArray: '6, 6',
      fillColor: '#F59E0B',
      fillOpacity: 0.12
    }).bindTooltip(`📍 Bờ Bắc: Vùng quanh Đại Nội (R = ${rKm} km)`, { permanent: false }).addTo(this.radiusLayer);

    // Vòng tròn bán kính quanh Trung tâm Bờ Nam (Lê Lợi / Hùng Vương)
    L.circle([16.4637, 107.5909], {
      radius: r,
      color: '#0E8B7D',
      weight: 2,
      dashArray: '6, 6',
      fillColor: '#0E8B7D',
      fillOpacity: 0.10
    }).bindTooltip(`📍 Bờ Nam: Trung tâm Du lịch (R = ${rKm} km)`, { permanent: false }).addTo(this.radiusLayer);
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

  clearAll() {
    if (this.markersLayer) this.markersLayer.clearLayers();
    if (this.routesLayer) this.routesLayer.clearLayers();
  }
}
