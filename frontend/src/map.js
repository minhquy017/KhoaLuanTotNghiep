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
    this.currentItinerary = null;
    this.currentItineraryDay = 1;
    this.currentDayLegs = [];
    this.activeLegIndex = 0;
    this.routeDisplayMode = 'leg'; // 'leg' (mặc định từng chặng) hoặc 'all' (toàn cảnh)
    this.cachedLegRoutes = new Map();
    this.dayRouteColors = {
      1: { stroke: '#2563EB', bg: '#2563EB', casing: '#FFFFFF', name: 'Ngày 1' },
      2: { stroke: '#D97706', bg: '#D97706', casing: '#FFFFFF', name: 'Ngày 2' },
      3: { stroke: '#0D9488', bg: '#0D9488', casing: '#FFFFFF', name: 'Ngày 3' },
      default: { stroke: '#4F46E5', bg: '#4F46E5', casing: '#FFFFFF', name: 'Lộ trình' }
    };

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

    // Lắng nghe sự kiện thanh điều hướng chặng nổi trên bản đồ
    const prevBtn = document.getElementById('btn-prev-leg');
    const nextBtn = document.getElementById('btn-next-leg');
    const modeBtn = document.getElementById('btn-toggle-route-mode');

    prevBtn?.addEventListener('click', () => this.prevLeg());
    nextBtn?.addEventListener('click', () => this.nextLeg());
    modeBtn?.addEventListener('click', () => this.toggleRouteDisplayMode());

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
  createCustomIcon(category = 'Attraction', label = '', stepNumber = null, badgeBg = null) {
    const catLower = (category || '').toLowerCase();
    
    // Bảng màu di sản Cố Đô có kỷ luật (chất gốm sứ, ngói lưu ly và thổ nhưỡng)
    let pinColor = '#B45309'; // Di tích: Vàng thổ hoàng / Hoàng cung
    let svgIcon = `
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 21h18M5 21V9l7-5 7 5v12M9 13h6v8H9z"/>
      </svg>
    `;

    if (catLower.includes('userlocation') || catLower.includes('khởi hành') || catLower.includes('xuất phát')) {
      pinColor = '#2563EB'; // Điểm xuất phát: Xanh Sapphire GPS
      svgIcon = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="#FFFFFF">
          <polygon points="12 2 19 21 12 17 5 21 12 2" />
        </svg>
      `;
    } else if (catLower.includes('restaurant') || catLower.includes('ẩm thực') || catLower.includes('quán')) {
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
        top: -7px;
        right: -8px;
        background: ${badgeBg || '#1C1917'};
        color: #FFFFFF;
        font-weight: 700;
        font-size: 10px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        border-radius: 9px;
        min-width: 18px;
        height: 18px;
        padding: 0 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #FFFFFF;
        box-shadow: 0 1px 4px rgba(0,0,0,0.25);
        z-index: 10;
        box-sizing: border-box;
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

  addPoi(lat, lng, name, category = 'Attraction', address = '', stepNumber = null, placeId = null, badgeBg = null) {
    if (!lat || !lng) return null;

    const isUserLoc = (category || '').toLowerCase().includes('userlocation') ||
                      (category || '').toLowerCase().includes('khởi hành') ||
                      (name || '').toLowerCase().includes('vị trí của bạn') ||
                      (name || '').toLowerCase().includes('vị trí hiện tại');

    // Nếu là vị trí người dùng, chỉ cập nhật duy nhất userLocationMarker, không tạo POI đè lên
    if (isUserLoc) {
      this.setUserLocation(lat, lng, name);
      return this.userLocationMarker;
    }

    const icon = this.createCustomIcon(category, '', stepNumber, badgeBg);

    const catLower = (category || '').toLowerCase();
    let catBadgeName = 'Di tích';
    let catClass = 'attraction';
    if (catLower.includes('restaurant') || catLower.includes('ẩm thực') || catLower.includes('quán')) {
      catBadgeName = 'Ẩm thực';
      catClass = 'restaurant';
    } else if (catLower.includes('cafe') || catLower.includes('cà phê') || catLower.includes('bar')) {
      catBadgeName = 'Cà phê';
      catClass = 'cafe';
    } else if (catLower.includes('hotel') || catLower.includes('khách sạn') || catLower.includes('resort')) {
      catBadgeName = 'Nghỉ dưỡng';
      catClass = 'hotel';
    }

    const stepLabel = stepNumber !== null 
      ? `<span class="popup-step-pill" ${badgeBg ? `style="background: ${badgeBg}; color: #FFFFFF;"` : ''}>Chặng ${stepNumber}</span>` 
      : '';

    const safeName = (name || '').replace(/'/g, "\\'");
    const safePlaceId = (placeId || '').replace(/'/g, "\\'");
    const safeAddress = (address || '').replace(/'/g, "\\'");
    const detailBtnHtml = `
      <button type="button" class="btn-popup-detail" onclick="window.openPoiDetail && window.openPoiDetail('${safeName}', '${safePlaceId}')">
        <span>Chi tiết</span>
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </button>
    `;

    const navBtnHtml = `
      <button type="button" class="btn-popup-gmaps" onclick="window.navigateToDestination && window.navigateToDestination(${lat}, ${lng}, '${safeName}', '${safeAddress}')" title="Chỉ đường từ vị trí của bạn trực tiếp trên bản đồ">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
        <span>Chỉ đường</span>
      </button>
    `;

    const popupHtml = `
      <div class="custom-leaflet-popup">
        <div class="popup-header-tags">
          ${stepLabel}
          <span class="popup-cat-pill cat-${catClass}">${catBadgeName}</span>
        </div>
        <h4 class="popup-title">${name}</h4>
        <div class="popup-address">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          <span>${address || 'Thành phố Huế'}</span>
        </div>
        <div class="popup-actions">
          ${detailBtnHtml}
          ${navBtnHtml}
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

    // 1. Phân loại điểm xuất phát người dùng và các điểm dừng tham quan thực tế
    let userOriginStop = null;
    const tourPois = [];

    validStops.forEach((stop) => {
      const isUserLoc = (stop.category || '').toLowerCase().includes('userlocation') ||
                        (stop.category || '').toLowerCase().includes('khởi hành') ||
                        (stop.name || '').toLowerCase().includes('vị trí của bạn') ||
                        (stop.name || '').toLowerCase().includes('vị trí hiện tại');
      if (isUserLoc) {
        if (!userOriginStop) {
          userOriginStop = stop;
        }
      } else {
        tourPois.push(stop);
      }
    });

    // Nếu có điểm xuất phát người dùng: Cập nhật beacon GPS duy nhất (không tạo marker POI đè lên)
    if (userOriginStop) {
      this.setUserLocation(userOriginStop.lat, userOriginStop.lng, userOriginStop.name || 'Vị trí của bạn (Điểm xuất phát)');
    }

    // 2. Đánh số thứ tự chặng cho các điểm tham quan / ẩm thực thực tế (Điểm dừng 1, Điểm dừng 2...)
    const poiMarkers = [];
    tourPois.forEach((stop, idx) => {
      const marker = this.addPoi(
        stop.lat, 
        stop.lng, 
        stop.name, 
        stop.category || 'Attraction', 
        stop.address,
        idx + 1,
        stop.placeId || stop.place_id
      );
      if (marker) poiMarkers.push(marker);
    });

    // Mở popup cho điểm dừng tham quan đầu tiên (hoặc điểm GPS nếu tour chỉ có 1 điểm)
    if (poiMarkers.length > 0) {
      setTimeout(() => {
        if (poiMarkers[0]) poiMarkers[0].openPopup();
      }, 300);
    } else if (this.userLocationMarker) {
      setTimeout(() => {
        if (this.userLocationMarker) this.userLocationMarker.openPopup();
      }, 300);
    }

    // Danh sách tọa độ đầy đủ cho lộ trình di chuyển (bao gồm cả điểm xuất phát nếu có)
    const allRoutePoints = userOriginStop ? [userOriginStop, ...tourPois] : tourPois;
    if (allRoutePoints.length <= 1) {
      const centerPt = allRoutePoints[0] || validStops[0];
      this.map.setView([centerPt.lat, centerPt.lng], 14);
      return;
    }

    // 3. Gọi OSRM Routing API để lấy lộ trình di chuyển thực tế theo mạng lưới giao thông Huế
    let routeLatLngs = null;
    let routeInfo = null;

    try {
      // OSRM nhận toạ độ dạng: lng,lat;lng,lat...
      const coordString = allRoutePoints.map(s => `${s.lng},${s.lat}`).join(';');
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

    // 4. Fallback sang đường nối trực tiếp nếu OSRM timeout / offline
    const isRealRoad = !!routeLatLngs && routeLatLngs.length > 0;
    const finalLatLngs = isRealRoad ? routeLatLngs : allRoutePoints.map(s => [s.lat, s.lng]);

    // 5. Vẽ Polyline sắc nét theo các cung đường thực tế
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

    // 6. Căn chỉnh góc nhìn bản đồ bao trọn lộ trình
    this.map.fitBounds(mainPolyline.getBounds(), { padding: [50, 50] });
  }

  /**
   * Thiết lập và nạp toàn bộ dữ liệu lịch trình đa ngày
   */
  setTourItinerary(plan, activeDay = 1) {
    this.currentItinerary = plan;
    this.routeDisplayMode = 'leg';
    this.renderTourItineraryDay(activeDay, 0);
  }

  /**
   * Hiển thị lộ trình phân tách theo Ngày & Từng chặng (Tuyệt đối không chằng chịt)
   * dayParam: 1, 2, 3... hoặc 'all'
   */
  async renderTourItineraryDay(dayParam = 1, initialLegIndex = 0) {
    if (!this.currentItinerary || !this.currentItinerary.days) return;
    this.currentItineraryDay = dayParam;

    this.clearAll();

    const days = this.currentItinerary.days;
    const isAllDays = dayParam === 'all' || dayParam === 0;

    const daysToRender = isAllDays
      ? days
      : days.filter(d => d.day_number === Number(dayParam));

    if (daysToRender.length === 0) {
      this.hideLegStepper();
      return;
    }

    const getDayStyle = (dayNum) => {
      return this.dayRouteColors[dayNum] || this.dayRouteColors.default;
    };

    const allAddedMarkers = [];
    this.currentDayLegs = [];

    // 1. Phân loại và tạo markers cho từng ngày
    for (const day of daysToRender) {
      const dayNum = day.day_number;
      const dayStyle = getDayStyle(dayNum);
      const rawSlots = day.slots || day.stops || [];

      const validSlots = rawSlots.filter(s => (s.latitude || s.lat) && (s.longitude || s.lng));
      if (validSlots.length === 0) continue;

      let userOrigin = null;
      const dayPois = [];

      validSlots.forEach(s => {
        const isUserLoc = (s.category || '').toLowerCase().includes('userlocation') ||
                          (s.category || '').toLowerCase().includes('khởi hành') ||
                          (s.slot_name || '').toLowerCase().includes('xuất phát') ||
                          (s.place_name || s.name || '').toLowerCase().includes('vị trí của bạn') ||
                          (s.place_name || s.name || '').toLowerCase().includes('vị trí hiện tại');
        const lat = s.latitude || s.lat;
        const lng = s.longitude || s.lng;
        const name = s.place_name || s.name;
        const cat = s.category || 'Attraction';
        const address = s.address || '';
        const placeId = s.place_id || s.placeId;

        if (isUserLoc) {
          if (!userOrigin) {
            userOrigin = { lat, lng, name, category: 'UserLocation' };
          }
        } else {
          dayPois.push({ lat, lng, name, category: cat, address, placeId });
        }
      });

      // Nếu có điểm xuất phát người dùng
      if (userOrigin) {
        this.setUserLocation(userOrigin.lat, userOrigin.lng, userOrigin.name || 'Vị trí của bạn (Điểm xuất phát)');
      }

      // Tạo marker cho các điểm tham quan / ăn uống trong ngày
      dayPois.forEach((poi, idx) => {
        const stepNumber = isAllDays ? `${dayNum}.${idx + 1}` : (idx + 1);
        const marker = this.addPoi(
          poi.lat,
          poi.lng,
          poi.name,
          poi.category,
          poi.address,
          stepNumber,
          poi.placeId,
          dayStyle.bg
        );
        if (marker) allAddedMarkers.push(marker);
      });

      // Tạo danh sách các chặng độc lập (Không bao giờ nối dính ngày nọ sang ngày kia)
      const routePointsForDay = userOrigin ? [userOrigin, ...dayPois] : dayPois;
      for (let i = 0; i < routePointsForDay.length - 1; i++) {
        const fromPt = routePointsForDay[i];
        const toPt = routePointsForDay[i + 1];
        this.currentDayLegs.push({
          legIndex: this.currentDayLegs.length,
          dayNum,
          from: fromPt,
          to: toPt,
          fromName: fromPt.name,
          toName: toPt.name,
          stepNumber: isAllDays ? `${dayNum}.${i + 1}` : (i + 1),
          dayStyle
        });
      }
    }

    if (this.currentDayLegs.length === 0) {
      this.hideLegStepper();
      return;
    }

    // 2. Chế độ hiển thị:
    if (this.routeDisplayMode === 'leg' && !isAllDays) {
      // Chế độ Từng chặng: Chỉ vẽ 1 đoạn đường A -> B duy nhất, sạch tinh và không chồng chéo!
      this.activeLegIndex = Math.max(0, Math.min(initialLegIndex, this.currentDayLegs.length - 1));
      await this.drawSingleActiveLeg(this.activeLegIndex);
    } else {
      // Chế độ Toàn cảnh: Vẽ toàn bộ các chặng
      await this.drawAllCurrentLegs();
      this.updateLegStepperForFullView(isAllDays);
    }
  }

  /**
   * Vẽ 1 chặng đơn lẻ (A -> B) - Tối ưu 100% không bị chằng chịt
   */
  async drawSingleActiveLeg(legIndex) {
    if (!this.currentDayLegs || this.currentDayLegs.length === 0) return;
    this.activeLegIndex = Math.max(0, Math.min(legIndex, this.currentDayLegs.length - 1));
    const leg = this.currentDayLegs[this.activeLegIndex];
    if (!leg) return;

    if (this.routesLayer) this.routesLayer.clearLayers();

    // Lấy route geometry từ OSRM cho cặp điểm này
    const legData = await this.fetchLegRoute(leg.from, leg.to);

    const finalLatLngs = legData && legData.coordinates && legData.coordinates.length > 0
      ? legData.coordinates
      : [[leg.from.lat, leg.from.lng], [leg.to.lat, leg.to.lng]];

    // 1. Lớp viền trắng tương phản (Casing)
    L.polyline(finalLatLngs, {
      color: '#FFFFFF',
      weight: 7,
      opacity: 0.95,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.routesLayer);

    // 2. Tuyến đường chính của chặng với màu sắc riêng của ngày
    const polyline = L.polyline(finalLatLngs, {
      color: leg.dayStyle.stroke,
      weight: 5,
      opacity: 1,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.routesLayer);

    const distText = legData && legData.distanceKm ? `${legData.distanceKm} km` : '';
    const durText = legData && legData.durationMin ? `~${legData.durationMin} phút` : '';

    polyline.bindTooltip(
      `🚗 <b>Chặng ${leg.legIndex + 1}:</b> ${leg.fromName} ➔ ${leg.toName}${distText ? ` (${distText} · ${durText})` : ''}`,
      { sticky: true }
    );

    // Zoom mượt mà vào đúng chặng này
    this.map.fitBounds(polyline.getBounds(), { padding: [70, 70], maxZoom: 16 });

    // Mở popup của điểm đến chặng này
    this.highlightPoiPopup(leg.to.name);

    // Cập nhật UI Stepper nổi trên bản đồ
    this.showLegStepper({
      legIndex: leg.legIndex,
      totalLegs: this.currentDayLegs.length,
      dayNum: leg.dayNum,
      fromName: leg.fromName,
      toName: leg.toName,
      distanceKm: legData?.distanceKm,
      durationMin: legData?.durationMin,
      color: leg.dayStyle.stroke
    });

    // Đồng bộ highlight thẻ tương ứng trên Timeline Deck
    this.syncTimelineHighlight();
  }

  /**
   * Vẽ toàn cảnh các chặng
   */
  async drawAllCurrentLegs() {
    if (!this.currentDayLegs || this.currentDayLegs.length === 0) return;
    if (this.routesLayer) this.routesLayer.clearLayers();

    const allBounds = [];

    // Nhóm theo ngày để không bao giờ nối dính ngày 1 sang ngày 2
    const legsByDay = new Map();
    this.currentDayLegs.forEach(leg => {
      if (!legsByDay.has(leg.dayNum)) legsByDay.set(leg.dayNum, []);
      legsByDay.get(leg.dayNum).push(leg);
    });

    for (const [dayNum, legs] of legsByDay.entries()) {
      const dayStyle = this.dayRouteColors[dayNum] || this.dayRouteColors.default;
      for (const leg of legs) {
        const legData = await this.fetchLegRoute(leg.from, leg.to);
        const finalLatLngs = legData && legData.coordinates && legData.coordinates.length > 0
          ? legData.coordinates
          : [[leg.from.lat, leg.from.lng], [leg.to.lat, leg.to.lng]];

        // Viền trắng
        L.polyline(finalLatLngs, {
          color: '#FFFFFF',
          weight: 6,
          opacity: 0.95,
          lineCap: 'round',
          lineJoin: 'round'
        }).addTo(this.routesLayer);

        // Nét vẽ chính
        const poly = L.polyline(finalLatLngs, {
          color: dayStyle.stroke,
          weight: 4.5,
          opacity: 0.9,
          lineCap: 'round',
          lineJoin: 'round'
        }).addTo(this.routesLayer);

        allBounds.push(poly.getBounds());
      }
    }

    if (allBounds.length > 0) {
      let combined = allBounds[0];
      for (let i = 1; i < allBounds.length; i++) {
        combined = combined.extend(allBounds[i]);
      }
      this.map.fitBounds(combined, { padding: [50, 50], maxZoom: 16 });
    }
  }

  async fetchLegRoute(from, to) {
    const key = `${Number(from.lat).toFixed(4)},${Number(from.lng).toFixed(4)}->${Number(to.lat).toFixed(4)},${Number(to.lng).toFixed(4)}`;
    if (this.cachedLegRoutes.has(key)) {
      return this.cachedLegRoutes.get(key);
    }

    try {
      const url = `https://router.project-osrm.org/route/v1/driving/${from.lng},${from.lat};${to.lng},${to.lat}?overview=full&geometries=geojson`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
          const r = data.routes[0];
          const result = {
            coordinates: r.geometry.coordinates.map(([lng, lat]) => [lat, lng]),
            distanceKm: (r.distance / 1000).toFixed(1),
            durationMin: Math.max(1, Math.round(r.duration / 60))
          };
          this.cachedLegRoutes.set(key, result);
          return result;
        }
      }
    } catch (e) {
      console.warn('Lỗi OSRM leg routing:', e);
    }

    const dist = this.haversineDistance(from.lat, from.lng, to.lat, to.lng);
    const fallback = {
      coordinates: [[from.lat, from.lng], [to.lat, to.lng]],
      distanceKm: dist.toFixed(1),
      durationMin: Math.max(2, Math.round(dist * 2.5))
    };
    this.cachedLegRoutes.set(key, fallback);
    return fallback;
  }

  showLegStepper(info) {
    const stepper = document.getElementById('map-leg-stepper');
    if (!stepper) return;
    stepper.style.display = 'flex';

    const panel = document.querySelector('.spatial-canvas-panel');
    if (panel) panel.classList.add('has-stepper');

    const stepBadge = document.getElementById('leg-step-badge');
    const dayBadge = document.getElementById('leg-day-badge');
    const routeTitle = document.getElementById('leg-route-title');
    const distanceText = document.getElementById('leg-distance-text');
    const durationText = document.getElementById('leg-duration-text');
    const prevBtn = document.getElementById('btn-prev-leg');
    const nextBtn = document.getElementById('btn-next-leg');
    const modeLabel = document.getElementById('route-mode-label');

    if (stepBadge) {
      stepBadge.innerHTML = `<span class="step-badge-dot"></span><span>Chặng ${info.legIndex + 1}/${info.totalLegs}</span>`;
      stepBadge.style.color = '#FFFFFF';
    }
    if (dayBadge) {
      dayBadge.textContent = `Ngày ${info.dayNum}`;
    }
    if (routeTitle) {
      routeTitle.innerHTML = `<span class="leg-point-from">${info.fromName}</span><span class="leg-arrow-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span><span class="leg-point-to">${info.toName}</span>`;
      routeTitle.title = `${info.fromName} đến ${info.toName}`;
    }
    if (distanceText) {
      const distVal = info.distanceKm ? `${info.distanceKm} km` : 'Lộ trình';
      distanceText.innerHTML = `
        <svg class="leg-meta-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>
        <span>${distVal}</span>
      `;
    }
    if (durationText) {
      if (info.durationMin) {
        durationText.innerHTML = `
          <svg class="leg-meta-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span>~${info.durationMin} phút</span>
        `;
        durationText.style.display = 'inline-flex';
      } else {
        durationText.style.display = 'none';
      }
    }
    if (prevBtn) {
      prevBtn.disabled = info.legIndex <= 0;
    }
    if (nextBtn) {
      nextBtn.disabled = info.legIndex >= info.totalLegs - 1;
    }
    if (modeLabel) {
      modeLabel.textContent = 'Toàn cảnh';
    }
  }

  updateLegStepperForFullView(isAllDays = false) {
    const stepper = document.getElementById('map-leg-stepper');
    if (!stepper) return;
    stepper.style.display = 'flex';

    const panel = document.querySelector('.spatial-canvas-panel');
    if (panel) panel.classList.add('has-stepper');

    const stepBadge = document.getElementById('leg-step-badge');
    const dayBadge = document.getElementById('leg-day-badge');
    const routeTitle = document.getElementById('leg-route-title');
    const distanceText = document.getElementById('leg-distance-text');
    const durationText = document.getElementById('leg-duration-text');
    const prevBtn = document.getElementById('btn-prev-leg');
    const nextBtn = document.getElementById('btn-next-leg');
    const modeLabel = document.getElementById('route-mode-label');

    if (stepBadge) {
      stepBadge.innerHTML = `<span class="step-badge-dot"></span><span>${isAllDays ? 'Tất cả ngày' : `Ngày ${this.currentItineraryDay}`}</span>`;
      stepBadge.style.color = '#FFFFFF';
    }
    if (dayBadge) {
      dayBadge.textContent = `${this.currentDayLegs.length} chặng`;
    }
    if (routeTitle) {
      routeTitle.innerHTML = `<span class="leg-point-to">${isAllDays ? 'Toàn bộ tour Cố Đô Huế' : `Toàn cảnh Ngày ${this.currentItineraryDay}`}</span>`;
    }
    if (distanceText) {
      distanceText.innerHTML = `
        <svg class="leg-meta-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        <span>Toàn cảnh lộ trình</span>
      `;
    }
    if (durationText) durationText.style.display = 'none';
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    if (modeLabel) modeLabel.textContent = 'Từng chặng';
    this.clearTimelineHighlight();
  }

  hideLegStepper() {
    const stepper = document.getElementById('map-leg-stepper');
    if (stepper) stepper.style.display = 'none';

    const panel = document.querySelector('.spatial-canvas-panel');
    if (panel) panel.classList.remove('has-stepper');
    this.clearTimelineHighlight();
  }

  nextLeg() {
    if (this.activeLegIndex < this.currentDayLegs.length - 1) {
      this.routeDisplayMode = 'leg';
      this.drawSingleActiveLeg(this.activeLegIndex + 1);
    }
  }

  prevLeg() {
    if (this.activeLegIndex > 0) {
      this.routeDisplayMode = 'leg';
      this.drawSingleActiveLeg(this.activeLegIndex - 1);
    }
  }

  toggleRouteDisplayMode() {
    this.routeDisplayMode = this.routeDisplayMode === 'leg' ? 'all' : 'leg';
    if (this.routeDisplayMode === 'leg') {
      this.drawSingleActiveLeg(this.activeLegIndex);
    } else {
      this.drawAllCurrentLegs();
      this.updateLegStepperForFullView(this.currentItineraryDay === 'all');
    }
  }

  setActiveLegByDestination(destName) {
    if (!this.currentDayLegs || this.currentDayLegs.length === 0) return;
    const cleanTarget = (destName || '').toLowerCase().trim();
    const idx = this.currentDayLegs.findIndex(leg => {
      const to = (leg.toName || '').toLowerCase().trim();
      return to.includes(cleanTarget) || cleanTarget.includes(to);
    });
    if (idx !== -1) {
      this.routeDisplayMode = 'leg';
      this.drawSingleActiveLeg(idx);
    }
  }

  highlightPoiPopup(name) {
    if (!name || !this.markersLayer) return;
    const cleanTarget = name.toLowerCase().trim();
    this.markersLayer.eachLayer(layer => {
      if (layer.getPopup && layer.getPopup()) {
        const content = layer.getPopup().getContent() || '';
        if (content.toLowerCase().includes(cleanTarget)) {
          layer.openPopup();
        }
      }
    });
  }

  clearTimelineHighlight() {
    document.querySelectorAll('.timeline-step').forEach(step => {
      step.classList.remove('is-active-leg');
    });
  }

  syncTimelineHighlight() {
    // 1. Luôn gỡ bỏ class active cũ trên tất cả các thẻ (kể cả điểm xuất phát)
    this.clearTimelineHighlight();

    if (!this.currentDayLegs || this.currentDayLegs.length === 0) return;
    const leg = this.currentDayLegs[this.activeLegIndex];
    if (!leg) return;

    const destName = (leg.toName || '').toLowerCase().trim();
    if (!destName) return;

    // 2. Kích hoạt thẻ điểm đến của chặng hiện tại
    let activated = false;
    document.querySelectorAll('.timeline-step').forEach(step => {
      const nameEl = step.querySelector('.step-poi-name');
      const poiName = (nameEl?.dataset?.name || nameEl?.textContent || '').toLowerCase().trim();
      if (!activated && (poiName.includes(destName) || destName.includes(poiName))) {
        step.classList.add('is-active-leg');
        step.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        activated = true;
      }
    });
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
    this.hideLegStepper();
  }
}
