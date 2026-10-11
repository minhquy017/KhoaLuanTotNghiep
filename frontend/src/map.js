// =============================================================================
// HUẾ SMART TOURISM — SPATIAL MAP STUDIO (Leaflet Controller)
// Trực quan hóa không gian: Điểm di sản, Quán ăn, Cụm bán kính & Tuyến Tour
// =============================================================================

import L from 'leaflet';

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
    this.currentTileLayer = null;
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

    // Layer Groups
    this.markersLayer = L.layerGroup().addTo(this.map);
    this.routesLayer = L.layerGroup().addTo(this.map);
    this.radiusLayer = L.layerGroup().addTo(this.map);

    // Nạp sẵn một số địa danh biểu tượng của Cố đô Huế
    this.renderDefaultHeritageSites();

    // Đảm bảo kích thước bản đồ hiển thị mượt mà
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 150);
  }

  /**
   * Chuyển đổi giao diện nền bản đồ linh hoạt (Topo / Street / Satellite / OSM)
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
   * Tạo Custom SVG Marker biểu tượng Cố Đô hiện đại & nổi bật
   */
  createCustomIcon(category = 'Attraction', label = '', stepNumber = null) {
    const isRestaurant = category.toLowerCase().includes('restaurant') || 
                         category.toLowerCase().includes('ẩm thực') || 
                         category.toLowerCase().includes('quán');
    
    // Gradient màu nổi bật: Rose/Coral cho ẩm thực, Amber/Gold cho Di tích
    const bgGradient = isRestaurant 
      ? 'linear-gradient(135deg, #FF4B6E 0%, #D81B60 100%)' 
      : 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)';
    const iconChar = isRestaurant ? '🍲' : '🏯';
    const shadowColor = isRestaurant ? 'rgba(216, 27, 96, 0.4)' : 'rgba(217, 119, 6, 0.4)';

    const stepBadgeHtml = stepNumber !== null ? `
      <div style="
        position: absolute;
        top: -7px;
        right: -7px;
        background: #1E1B4B;
        color: #FBBF24;
        font-weight: 800;
        font-size: 11px;
        font-family: system-ui, -apple-system, sans-serif;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 6px rgba(0,0,0,0.45);
        z-index: 10;
      ">${stepNumber}</div>
    ` : '';

    return L.divIcon({
      className: 'heritage-custom-marker',
      html: `
        <div style="
          position: relative;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          ${stepBadgeHtml}
          <div style="
            background: ${bgGradient};
            width: 34px;
            height: 34px;
            border-radius: 50% 50% 50% 4px;
            transform: rotate(-45deg);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 14px ${shadowColor};
            border: 2.5px solid #FFFFFF;
            transition: transform 0.2s ease;
          ">
            <span style="
              transform: rotate(45deg);
              font-size: 15px;
              line-height: 1;
            ">${iconChar}</span>
          </div>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 34],
      popupAnchor: [0, -32]
    });
  }

  /**
   * Đặt lại góc nhìn trung tâm TP Huế
   */
  resetView() {
    if (this.map) {
      this.map.setView(this.centerHue, this.defaultZoom, { animate: true });
    }
  }

  /**
   * Bật / tắt hiển thị bán kính không gian 1.5km
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
    // Vòng tròn bán kính 1.5km quanh Đại Nội Huế (Bờ Bắc)
    L.circle([16.4699, 107.5786], {
      radius: 1500,
      color: '#D97706',
      weight: 2,
      dashArray: '6, 6',
      fillColor: '#F59E0B',
      fillOpacity: 0.12
    }).bindTooltip('📍 Bờ Bắc: Vùng lân cận Đại Nội (R = 1.5km)', { permanent: false }).addTo(this.radiusLayer);

    // Vòng tròn bán kính 1.5km quanh Trung tâm Bờ Nam
    L.circle([16.4637, 107.5909], {
      radius: 1500,
      color: '#0E8B7D',
      weight: 2,
      dashArray: '6, 6',
      fillColor: '#0E8B7D',
      fillOpacity: 0.10
    }).bindTooltip('📍 Bờ Nam: Vùng du lịch trung tâm (R = 1.5km)', { permanent: false }).addTo(this.radiusLayer);
  }

  /**
   * Hiển thị các địa danh biểu tượng ban đầu
   */
  renderDefaultHeritageSites() {
    this.clearAll();

    const landmarks = [
      { name: 'Đại Nội Huế (Hoàng Thành)', lat: 16.4690, lng: 107.5781, cat: 'Attraction', desc: 'Kinh thành Huế · Hoàng cung triều Nguyễn' },
      { name: 'Chùa Thiên Mụ', lat: 16.4537, lng: 107.5446, cat: 'Attraction', desc: 'Đồi Hà Khê · Ngôi cổ tự hơn 400 năm bên bờ sông Hương' },
      { name: 'Lăng Khải Định', lat: 16.3990, lng: 107.5903, cat: 'Attraction', desc: 'Châu Chữ, Thủy Bằng · Kiệt tác kiến trúc Đông - Tây' },
      { name: 'Chợ Đông Ba', lat: 16.4725, lng: 107.5886, cat: 'Attraction', desc: 'Trần Hưng Đạo, Phú Xuân · Thiên đường ẩm thực Cố Đô' },
      { name: 'Bánh bèo Bà Đỏ', lat: 16.4823, lng: 107.5893, cat: 'Restaurant', desc: '8 Nguyễn Bỉnh Khiêm, Gia Hội · Bánh bèo, nậm, lọc' },
      { name: 'Bún bò Cẩm', lat: 16.4668, lng: 107.5931, cat: 'Restaurant', desc: '38 Trần Cao Vân, Phú Hội · Đặc sản Bún bò Huế' }
    ];

    landmarks.forEach(p => {
      this.addPoi(p.lat, p.lng, p.name, p.cat, p.desc);
    });
  }

  addPoi(lat, lng, name, category = 'Attraction', address = '', stepNumber = null) {
    if (!lat || !lng) return null;
    const icon = this.createCustomIcon(category, '', stepNumber);

    const stepLabel = stepNumber !== null 
      ? `<div style="font-size: 0.72rem; font-weight: 800; color: #D97706; text-transform: uppercase; margin-bottom: 3px; letter-spacing: 0.5px;">📍 Điểm dừng ${stepNumber}</div>` 
      : '';

    const popupHtml = `
      <div class="custom-leaflet-popup">
        ${stepLabel}
        <div class="popup-title">${name}</div>
        <div class="popup-category">${category}</div>
        <div class="popup-address">${address || 'Thành phố Huế'}</div>
        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #E2E8F0;">
          <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}" target="_blank" rel="noopener noreferrer" style="font-size: 0.75rem; color: #2563EB; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
            <span>🧭 Dẫn đường Google Maps</span> &rarr;
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

  clearAll() {
    if (this.markersLayer) this.markersLayer.clearLayers();
    if (this.routesLayer) this.routesLayer.clearLayers();
  }
}
