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
    this.currentRadiusMeters = 1500;
    this.activeCategoryFilter = 'all';
    this.currentTileLayer = null;
    this.markerInstances = new Map();

    // Dữ liệu Địa danh & Cơ sở Dịch vụ Chuẩn Cố Đô Huế (32 địa điểm chia 4 nhóm danh mục)
    this.masterLandmarks = [
      // 1. Quần thể Di sản & Thắng cảnh (Attraction)
      { name: 'Đại Nội Huế (Hoàng Thành)', lat: 16.4690, lng: 107.5781, cat: 'Attraction', desc: 'Kinh thành Huế · Hoàng cung triều Nguyễn', tags: 'hoang thanh, dai noi, kinh thanh, ngo mon' },
      { name: 'Chùa Thiên Mụ', lat: 16.4537, lng: 107.5446, cat: 'Attraction', desc: 'Đồi Hà Khê · Cổ tự hơn 400 năm bên bờ sông Hương', tags: 'thien mu, chua, phat giao, song huong' },
      { name: 'Lăng Tự Đức (Khiêm Lăng)', lat: 16.4330, lng: 107.5664, cat: 'Attraction', desc: 'Thủy Xuân · Quần thể lăng tẩm thơ mộng bậc nhất triều Nguyễn', tags: 'tu duc, khiem lang, lang tam' },
      { name: 'Lăng Khải Định (Ứng Lăng)', lat: 16.3990, lng: 107.5903, cat: 'Attraction', desc: 'Châu Chữ, Thủy Bằng · Kiệt tác khảm sành sứ giao thoa Đông - Tây', tags: 'khai dinh, ung lang, kien truc' },
      { name: 'Lăng Minh Mạng (Hiếu Lăng)', lat: 16.3877, lng: 107.5692, cat: 'Attraction', desc: 'Hương Thọ · Quần thể lăng đăng đối uy nghiêm bên dòng Tả Trạch', tags: 'minh mang, hieu lang, phong thuy' },
      { name: 'Lăng Đồng Khánh', lat: 16.4300, lng: 107.5700, cat: 'Attraction', desc: 'Thượng Hai, Thủy Xuân · Công trình kiến trúc cung đình tinh xảo', tags: 'dong khanh, lang tam' },
      { name: 'Lăng Gia Long (Thiên Thọ Lăng)', lat: 16.3532, lng: 107.5855, cat: 'Attraction', desc: 'Hương Thọ · Nơi an nghỉ của vị vua sáng lập triều Nguyễn giữa rừng thông', tags: 'gia long, thien tho lang' },
      { name: 'Cầu Trường Tiền', lat: 16.4676, lng: 107.5900, cat: 'Attraction', desc: 'Sông Hương, TP Huế · Biểu tượng lịch sử 6 vài 12 nhịp', tags: 'truong tien, trang tien, cau, song huong' },
      { name: 'Chợ Đông Ba', lat: 16.4725, lng: 107.5886, cat: 'Attraction', desc: 'Trần Hưng Đạo · Chợ truyền thống lớn nhất Cố Đô với muôn vàn đặc sản', tags: 'dong ba, cho, dac san' },
      { name: 'Đồi Vọng Cảnh', lat: 16.4255, lng: 107.5505, cat: 'Attraction', desc: 'Thủy Xuân · Tầm nhìn bao quát khúc uốn sông Hương và đồi thông lãng mạn', tags: 'vong canh, sunset, doi, view' },
      { name: 'Làng hương Thủy Xuân', lat: 16.4385, lng: 107.5680, cat: 'Attraction', desc: 'Huyền Trân Công Chúa · Làng nghề tăm hương sắc màu rực rỡ', tags: 'thuy xuan, lang huong, checkin' },
      { name: 'Chùa Từ Hiếu', lat: 16.4390, lng: 107.5819, cat: 'Attraction', desc: 'Thủy Xuân · Cổ tự yên bình gắn liền Thiền sư Thích Nhất Hạnh và lăng Thái giám', tags: 'tu hieu, chua, thien' },
      { name: 'Cầu ngói Thanh Toàn', lat: 16.4668, lng: 107.6427, cat: 'Attraction', desc: 'Thủy Thanh, Hương Thủy · Cây cầu ngói cổ kính độc đáo bên dòng sông Như Ý', tags: 'thanh toan, cau ngoi' },
      { name: 'Điện Hòn Chén', lat: 16.4316, lng: 107.5312, cat: 'Attraction', desc: 'Núi Ngọc Trản, Hương Thọ · Thánh địa tín ngưỡng Mẫu Thiên Y A Na bên sông Hương', tags: 'hon chen, ngoctrann, dien' },
      { name: 'Đầm Chuồn (Phá Tam Giang)', lat: 16.5050, lng: 107.6480, cat: 'Attraction', desc: 'Phú An, Phú Vang · Đầm nước lợ trù phú ngắm bình minh và thưởng thức hải sản', tags: 'dam chuon, pha tam giang, song nuoc' },

      // 2. Ẩm thực & Quán ăn truyền thống (Restaurant)
      { name: 'Bún bò Cẩm', lat: 16.4668, lng: 107.5931, cat: 'Restaurant', desc: '38 Trần Cao Vân, Phú Hội · Bún bò Huế chuẩn vị đậm đà thơm mùi sả ruốc', tags: 'bun bo, cam, an sang' },
      { name: 'Bún bò Bà Tám', lat: 16.4735, lng: 107.5820, cat: 'Restaurant', desc: '23 Chu Văn An, Phú Hội · Nước dùng thanh ngọt, thịt bắp bò mềm ngậy', tags: 'bun bo, ba tam' },
      { name: 'Bánh bèo Bà Đỏ', lat: 16.4823, lng: 107.5893, cat: 'Restaurant', desc: '8 Nguyễn Bỉnh Khiêm, Gia Hội · Khay bánh bèo chén, bánh nậm tôm thịt, lọc giòn', tags: 'banh beo, ba do, banh nam, banh loc' },
      { name: 'Cơm hến Hoa Đông', lat: 16.4716, lng: 107.6042, cat: 'Restaurant', desc: '64 kiệt 7 Ưng Bình, Cồn Hến · Quán cơm hến, mì hến trứ danh cái nôi Cồn Hến', tags: 'com hen, hoa dong, con hen, mi hen' },
      { name: 'Bánh khoái Lạc Thiện', lat: 16.4720, lng: 107.5780, cat: 'Restaurant', desc: '6 Đinh Tiên Hoàng, Phú Hòa · Vỏ giòn rụm, nước lèo tương gan lạc gia truyền lâu đời', tags: 'banh khoai, lac thien, nem lui' },
      { name: 'Chè Hẻm Huế', lat: 16.4630, lng: 107.5940, cat: 'Restaurant', desc: 'Kiệt 29 Hùng Vương, Phú Hội · Chè bột lọc heo quay, chè hạt sen long nhãn Cố Đô', tags: 'che hem, che heo quay, che bot loc, trang mieng' },
      { name: 'Quán chay Sân Mây', lat: 16.4522, lng: 107.5645, cat: 'Restaurant', desc: '8 Thanh Tịnh, Vỹ Dạ · Không gian thiền vị nhà rường cổ kính và ẩm thực chay thanh tịnh', tags: 'an chay, san may, com chay' },
      { name: 'Cơm niêu Không Gian Xưa', lat: 16.4578, lng: 107.5992, cat: 'Restaurant', desc: '205 Điện Biên Phủ, Trường An · Bữa cơm gia đình thuần Việt trong quần thể nhà rường', tags: 'com nieu, khong gian xua' },
      { name: 'Bánh ướt thịt nướng Huyền Anh', lat: 16.4545, lng: 107.5532, cat: 'Restaurant', desc: '50 Kim Long, TP Huế · Bánh ướt trắng mềm cuốn thịt nướng chấm tương đậu mè béo ngậy', tags: 'banh uot, thit nuong, huyen anh, kim long' },

      // 3. Cà phê & Điểm ngắm Hoàng hôn (Cafe)
      { name: 'Cà phê Muối Đặng Thái Thân', lat: 16.4712, lng: 107.5762, cat: 'Cafe', desc: '10 Đặng Thái Thân, Thuận Thành · Khởi nguồn món Cà phê muối trứ danh của xứ Huế', tags: 'ca phe muoi, dang thai than, cafe' },
      { name: 'Tân Cafe Đinh Tiên Hoàng', lat: 16.4738, lng: 107.5775, cat: 'Cafe', desc: '14 Đinh Tiên Hoàng, Thuận Thành · Phong cách bao cấp hoài cổ, không gian cây xanh', tags: 'tan cafe, vintage, cafe' },
      { name: 'Vọng Cảnh Sunset Coffee', lat: 16.4251, lng: 107.5510, cat: 'Cafe', desc: 'Đồi Vọng Cảnh, Thủy Xuân · Quán cafe đồi thông ngắm hoàng hôn buông xuống dòng sông Hương', tags: 'sunset, vong canh, cafe' },
      { name: 'The Busa Park Huế', lat: 16.4670, lng: 107.5985, cat: 'Cafe', desc: 'Bờ sông Hương, Phú Hội · Không gian lounge ngoài trời ngắm cầu Trường Tiền về đêm', tags: 'busa park, lounge, riverside, song huong' },

      // 4. Khách sạn & Nghỉ dưỡng (Hotel)
      { name: 'Saigon Morin Hotel', lat: 16.4678, lng: 107.5912, cat: 'Hotel', desc: '30 Lê Lợi, Phú Hội · Khách sạn thuộc địa Pháp cổ kính nhất miền Trung từ năm 1901', tags: 'saigon morin, hotel, khach san, le loi' },
      { name: 'Silk Path Grand Hue Hotel', lat: 16.4570, lng: 107.5878, cat: 'Hotel', desc: '02 Lê Lợi, Vĩnh Ninh · Khách sạn 5 sao mang phong cách quý tộc cung đình trang nhã', tags: 'silk path, resort, khach san 5 sao' },
      { name: 'Pilgrimage Village Boutique Resort', lat: 16.4290, lng: 107.5850, cat: 'Hotel', desc: '130 Minh Mạng, Thủy Xuân · Khu nghỉ dưỡng Làng Hành Hương mộc mạc giữa làng quê', tags: 'lang hanh huong, pilgrimage, resort' },
      { name: 'Azerai La Residence Hue', lat: 16.4615, lng: 107.5822, cat: 'Hotel', desc: '05 Lê Lợi, Vĩnh Ninh · Biệt thự phong cách Art Deco danh tiếng ngắm sông Hương thơ mộng', tags: 'azerai, la residence, luxury, riverside' }
    ];
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
   * Tạo Custom SVG Marker biểu tượng Cố Đô hiện đại & sắc màu riêng theo 4 danh mục
   */
  createCustomIcon(category = 'Attraction', label = '', stepNumber = null) {
    const catLower = (category || '').toLowerCase();
    
    let bgGradient = 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)';
    let iconChar = '🏯';
    let shadowColor = 'rgba(217, 119, 6, 0.45)';

    if (catLower.includes('restaurant') || catLower.includes('ẩm thực') || catLower.includes('quán')) {
      // Ẩm thực: Hồng ngọc / Đỏ cam nổi bật
      bgGradient = 'linear-gradient(135deg, #FF4B6E 0%, #D81B60 100%)';
      iconChar = '🍲';
      shadowColor = 'rgba(216, 27, 96, 0.45)';
    } else if (catLower.includes('cafe') || catLower.includes('cà phê') || catLower.includes('sunset')) {
      // Cà phê & Sunset: Tím hoàng hôn thơ mộng
      bgGradient = 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)';
      iconChar = '☕';
      shadowColor = 'rgba(139, 92, 246, 0.45)';
    } else if (catLower.includes('hotel') || catLower.includes('khách sạn') || catLower.includes('resort')) {
      // Khách sạn & Nghỉ dưỡng: Xanh ngọc lục bảo sang trọng
      bgGradient = 'linear-gradient(135deg, #0E8B7D 0%, #0A6E63 100%)';
      iconChar = '🏨';
      shadowColor = 'rgba(14, 139, 125, 0.45)';
    }

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
      const marker = this.addPoi(p.lat, p.lng, p.name, p.cat, p.desc);
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
      marker = this.addPoi(poi.lat, poi.lng, poi.name, poi.cat, poi.desc);
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

  addPoi(lat, lng, name, category = 'Attraction', address = '', stepNumber = null) {
    if (!lat || !lng) return null;
    const icon = this.createCustomIcon(category, '', stepNumber);

    const stepLabel = stepNumber !== null 
      ? `<div style="font-size: 0.72rem; font-weight: 800; color: #D97706; text-transform: uppercase; margin-bottom: 3px; letter-spacing: 0.5px;">📍 Điểm dừng ${stepNumber}</div>` 
      : '';

    const safeName = (name || '').replace(/'/g, "\\'");
    const popupHtml = `
      <div class="custom-leaflet-popup">
        ${stepLabel}
        <div class="popup-title">${name}</div>
        <div class="popup-category">${category}</div>
        <div class="popup-address">${address || 'Thành phố Huế'}</div>
        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #E2E8F0; display: flex; flex-direction: column; gap: 4px;">
          <button type="button" class="btn-open-detail-popup" onclick="window.openPoiDetail && window.openPoiDetail('${safeName}')">
            <span>📋 Xem Chi Tiết & Đánh Giá</span> &rarr;
          </button>
          <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}" target="_blank" rel="noopener noreferrer" style="font-size: 0.74rem; color: #2563EB; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; justify-content: center; gap: 4px; padding: 4px 0;">
            <span>🧭 Chỉ đường Google Maps</span>
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
        p.address || 'Địa điểm gợi ý từ Trợ lý AI'
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
