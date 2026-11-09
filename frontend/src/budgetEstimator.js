// =============================================================================
// HUẾ SMART TOURISM — TRIP BUDGET & COST ESTIMATOR
// Dự toán chi phí du lịch Cố Đô Huế: Vé di tích, Ẩm thực, Di chuyển, Lưu trú
// =============================================================================

import { i18n } from './i18n.js';

// Bảng giá vé di tích chính thức từ Trung tâm Bảo tồn Di tích Cố đô Huế
export const HUE_MONUMENT_TICKETS = [
  {
    id: 'dai_noi',
    aliases: ['đại nội', 'hoàng thành', 'kinh thành', 'tử cấm thành', 'citadel', 'imperial city'],
    name: 'Đại Nội Huế (Hoàng Thành & Tử Cấm Thành)',
    nameEn: 'Hue Imperial Citadel (Imperial & Forbidden Purple City)',
    priceAdult: 200000,
    priceChild: 40000,
    comboEligible3: true,
    comboEligible4: true
  },
  {
    id: 'lang_khai_dinh',
    aliases: ['khải định', 'ứng lăng', 'khai dinh'],
    name: 'Lăng Vua Khải Định (Ứng Lăng)',
    nameEn: 'Khai Dinh Tomb (Ung Lang)',
    priceAdult: 150000,
    priceChild: 30000,
    comboEligible3: true,
    comboEligible4: true
  },
  {
    id: 'lang_minh_mang',
    aliases: ['minh mạng', 'hiếu lăng', 'minh mang'],
    name: 'Lăng Vua Minh Mạng (Hiếu Lăng)',
    nameEn: 'Minh Mang Tomb (Hieu Lang)',
    priceAdult: 150000,
    priceChild: 30000,
    comboEligible3: true,
    comboEligible4: true
  },
  {
    id: 'lang_tu_duc',
    aliases: ['tự đức', 'khiêm lăng', 'tu duc'],
    name: 'Lăng Vua Tự Đức (Khiêm Lăng)',
    nameEn: 'Tu Duc Tomb (Khiem Lang)',
    priceAdult: 150000,
    priceChild: 30000,
    comboEligible3: true,
    comboEligible4: true
  },
  {
    id: 'lang_gia_long',
    aliases: ['gia long', 'thiên thọ lăng'],
    name: 'Lăng Vua Gia Long (Thiên Thọ Lăng)',
    nameEn: 'Gia Long Tomb (Thien Tho Lang)',
    priceAdult: 150000,
    priceChild: 30000,
    comboEligible3: false,
    comboEligible4: false
  },
  {
    id: 'lang_dong_khanh',
    aliases: ['đồng khánh', 'tư lăng', 'dong khanh'],
    name: 'Lăng Vua Đồng Khánh (Tư Lăng)',
    nameEn: 'Dong Khanh Tomb (Tu Lang)',
    priceAdult: 50000,
    priceChild: 0,
    comboEligible3: false,
    comboEligible4: false
  },
  {
    id: 'lang_thieu_tri',
    aliases: ['thiệu trị', 'xương lăng', 'thieu tri'],
    name: 'Lăng Vua Thiệu Trị (Xương Lăng)',
    nameEn: 'Thieu Tri Tomb (Xuong Lang)',
    priceAdult: 50000,
    priceChild: 0,
    comboEligible3: false,
    comboEligible4: false
  },
  {
    id: 'dien_hon_chen',
    aliases: ['hòn chén', 'điện huệ nam', 'hon chen'],
    name: 'Điện Hòn Chén (Điện Huệ Nam)',
    nameEn: 'Hon Chen Temple (Hue Nam Temple)',
    priceAdult: 50000,
    priceChild: 0,
    comboEligible3: false,
    comboEligible4: false
  },
  {
    id: 'cung_an_dinh',
    aliases: ['an định', 'cung an dinh', 'an dinh'],
    name: 'Cung An Định (Viên ngọc tân cổ điển)',
    nameEn: 'An Dinh Palace (Neoclassical Gem)',
    priceAdult: 50000,
    priceChild: 0,
    comboEligible3: false,
    comboEligible4: false
  },
  {
    id: 'bao_tang_co_vat',
    aliases: ['cổ vật', 'điện long an', 'bảo tàng cổ vật'],
    name: 'Bảo tàng Cổ vật Cung đình Huế (Điện Long An)',
    nameEn: 'Museum of Royal Antiquities (Long An Palace)',
    priceAdult: 50000,
    priceChild: 0,
    comboEligible3: false,
    comboEligible4: false
  }
];

// Danh sách các thắng cảnh nổi tiếng miễn phí vé tại Huế
export const HUE_FREE_LANDMARKS = [
  'chùa thiên mụ', 'chùa từ hiếu', 'chùa huyền không sơn thượng',
  'cầu trường tiền', 'chợ đông ba', 'đồi vọng cảnh', 'đồi thiên an',
  'làng hương thủy xuân', 'sông hương', 'đầm chuồn', 'phố cổ bao vinh',
  'trường quốc học huế', 'bến thuyền tòa khâm', 'công viên 3/2'
];

// Định mức chi tiêu ẩm thực theo ngày (VNĐ / người / ngày)
export const DINING_TIERS = {
  economy: {
    id: 'economy',
    name: 'Tiết kiệm / Đặc sản vỉa hè',
    nameEn: 'Budget / Street Food Specialties',
    ratePerDay: 150000,
    desc: 'Bún bò Huế bình dân, cơm hến, bánh bèo nậm lọc, chè hẻm, cà phê muối',
    descEn: 'Authentic street bun bo, clam rice, savoury cakes, alley sweet soups, salt coffee'
  },
  standard: {
    id: 'standard',
    name: 'Tiêu chuẩn / Quán danh tiếng',
    nameEn: 'Standard / Renowned Local Eateries',
    ratePerDay: 300000,
    desc: 'Bún bò O Cương/Mụ Rơi, cơm niêu Huế, nem lụi, bánh khoái, cà phê sân vườn',
    descEn: 'Top-rated bun bo, claypot rice, lemongrass pork skewers, banh khoai, garden cafes'
  },
  premium: {
    id: 'premium',
    name: 'Trải nghiệm cao cấp / Cung đình',
    nameEn: 'Fine Dining / Imperial Feast',
    ratePerDay: 600000,
    desc: 'Yến tiệc Cung đình Huế, tiệc chay Cung đình, ẩm thực tinh hoa ven sông Hương',
    descEn: 'Royal banquet dining, Imperial vegetarian cuisine, fine riverside restaurants'
  }
};

// Định mức phương tiện di chuyển
export const TRANSPORT_TIERS = {
  motorbike: {
    id: 'motorbike',
    name: 'Thuê xe máy',
    nameEn: 'Motorbike Rental',
    basePerDay: 130000,
    fuelPerDay: 40000,
    desc: 'Linh hoạt, tối ưu khám phá hệ thống lăng tẩm và các điểm ngoại thành',
    descEn: 'High flexibility, ideal for royal tombs and suburban hidden spots'
  },
  taxi: {
    id: 'taxi',
    name: 'Taxi / Đặt xe công nghệ',
    nameEn: 'Taxi / Ride-hailing',
    baseOpening: 12000,
    ratePerKm: 13500,
    desc: 'Thoải mái, có máy lạnh, tính cước theo tổng quãng đường thực tế',
    descEn: 'Air-conditioned comfort, fare calculated by real GPS transit distance'
  },
  private_car: {
    id: 'private_car',
    name: 'Ô tô kèm tài xế riêng',
    nameEn: 'Private Car with Driver',
    basePerDay: 850000,
    desc: 'Phù hợp gia đình, nhóm bạn, tài xế bản địa hỗ trợ nhiệt tình',
    descEn: 'Best for families & groups, accompanied by friendly local drivers'
  },
  bicycle: {
    id: 'bicycle',
    name: 'Xe đạp / Xe đạp công cộng',
    nameEn: 'Bicycle / Public Bike',
    basePerDay: 50000,
    desc: 'Phù hợp ngắm cảnh bờ sông Hương, kinh thành và dạo phố cổ nội đô',
    descEn: 'Scenic leisure rides along Perfume River, Citadel walls and Old Quarter'
  }
};

// Định mức lưu trú (VNĐ / phòng / đêm)
export const HOTEL_TIERS = {
  none: {
    id: 'none',
    name: 'Không tính lưu trú',
    nameEn: 'No Lodging Included',
    ratePerNight: 0,
    desc: 'Đi về trong ngày hoặc đã tự túc chỗ ở',
    descEn: 'Day trip or self-arranged accommodation'
  },
  homestay: {
    id: 'homestay',
    name: 'Homestay / Khách sạn 2 sao',
    nameEn: 'Homestay / 2-Star Hotel',
    ratePerNight: 350000,
    desc: 'Gần gũi, ấm cúng, đậm chất phong cách nhà vườn hoặc phố Tây',
    descEn: 'Cozy garden-house style or vibrant Western quarter boutique stays'
  },
  hotel34: {
    id: 'hotel34',
    name: 'Khách sạn 3 - 4 sao',
    nameEn: '3 - 4 Star Hotel',
    ratePerNight: 800000,
    desc: 'Tiện nghi đầy đủ, trung tâm thành phố, bao gồm bữa sáng',
    descEn: 'Full amenities, city center location, inclusive of daily breakfast'
  },
  luxury: {
    id: 'luxury',
    name: 'Khách sạn 5 sao / Resort',
    nameEn: '5-Star Hotel / Luxury Resort',
    ratePerNight: 2200000,
    desc: 'Khu nghỉ dưỡng cao cấp ven sông Hương hoặc suối khoáng nóng',
    descEn: 'High-end riverside resorts or geothermal hot-spring retreats'
  }
};

// Bảng vé Combo di tích Huế
export const COMBO_RULES = {
  combo3: {
    id: 'combo3',
    name: 'Vé Tuyến 3 Điểm (Hoàng Cung + 2 Lăng Vua: Minh Mạng / Tự Đức / Khải Định)',
    nameEn: '3-Site Heritage Pass (Imperial Citadel + 2 Royal Tombs: Minh Mang / Tu Duc / Khai Dinh)',
    requiredIds: ['dai_noi', 'lang_minh_mang', 'lang_khai_dinh'],
    eligibleTombIds: ['lang_minh_mang', 'lang_tu_duc', 'lang_khai_dinh'],
    priceAdult: 420000,
    priceChild: 80000,
    singlePriceAdult: 500000,
    savingAdult: 80000,
    savingChild: 20000
  },
  combo4: {
    id: 'combo4',
    name: 'Vé Tuyến 4 Điểm (Hoàng Cung + Minh Mạng + Tự Đức + Khải Định)',
    nameEn: '4-Site Heritage Pass (Imperial Citadel + Minh Mang + Tu Duc + Khai Dinh Tombs)',
    requiredIds: ['dai_noi', 'lang_minh_mang', 'lang_tu_duc', 'lang_khai_dinh'],
    priceAdult: 530000,
    priceChild: 100000,
    singlePriceAdult: 650000,
    savingAdult: 120000,
    savingChild: 30000
  }
};

function getTierName(tierObj) {
  if (!tierObj) return '';
  return (i18n.currentLang === 'en' && tierObj.nameEn) ? tierObj.nameEn : tierObj.name;
}

function getTierDesc(tierObj) {
  if (!tierObj) return '';
  return (i18n.currentLang === 'en' && tierObj.descEn) ? tierObj.descEn : tierObj.desc;
}

export class HueBudgetEstimator {
  constructor() {
    this.modal = null;
    this.currentPlan = null;
    this.currentOptions = {
      days: 2,
      nights: 1,
      adults: 2,
      children: 0,
      diningTier: 'standard',
      transportType: 'taxi',
      hotelTier: 'hotel34',
      applyCombo: true
    };
    this._initialized = false;
  }

  init() {
    if (this._initialized) return;
    this.modal = document.getElementById('trip-budget-modal');
    if (!this.modal) return;

    this._bindModalEvents();
    this._initialized = true;
  }

  _bindModalEvents() {
    const btnClose = document.getElementById('btn-close-budget-modal');
    btnClose?.addEventListener('click', () => this.closeModal());

    this.modal?.addEventListener('click', (e) => {
      if (e.target === this.modal) this.closeModal();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modal?.classList.contains('active')) {
        this.closeModal();
      }
    });

    const btnPrint = document.getElementById('btn-print-budget');
    btnPrint?.addEventListener('click', () => {
      window.print();
    });

    window.addEventListener('hue:language-change', () => {
      if (this.modal?.classList.contains('active')) {
        this.render();
      }
    });
  }

  /**
   * Phân tích các điểm dừng trong lịch trình để trích xuất danh sách vé di tích
   */
  extractTicketItems(plan) {
    if (!plan) return [];

    const stops = [];
    const seenNames = new Set();

    if (plan.days && Array.isArray(plan.days)) {
      plan.days.forEach(d => {
        const slots = d.slots || d.stops || [];
        slots.forEach(s => {
          const name = s.place_name || s.name || '';
          if (name && !seenNames.has(name.toLowerCase())) {
            seenNames.add(name.toLowerCase());
            stops.push({ name, slot: s });
          }
        });
      });
    } else if (Array.isArray(plan.items)) {
      plan.items.forEach(s => {
        const name = s.name || s.place_name || '';
        if (name && !seenNames.has(name.toLowerCase())) {
          seenNames.add(name.toLowerCase());
          stops.push({ name, slot: s });
        }
      });
    }

    const matchedTickets = [];
    const matchedTicketIds = new Set();
    const isEn = i18n.currentLang === 'en';

    stops.forEach(({ name, slot }) => {
      const lower = name.toLowerCase();

      // Kiểm tra có phải di tích thu vé không
      for (const t of HUE_MONUMENT_TICKETS) {
        if (matchedTicketIds.has(t.id)) continue;
        const isMatch = t.aliases.some(alias => lower.includes(alias));
        if (isMatch) {
          matchedTicketIds.add(t.id);
          matchedTickets.push({
            id: t.id,
            name: (isEn && t.nameEn) ? t.nameEn : t.name,
            originalPlaceName: name,
            priceAdult: t.priceAdult,
            priceChild: t.priceChild,
            comboEligible3: t.comboEligible3,
            comboEligible4: t.comboEligible4,
            isFree: false
          });
          return;
        }
      }

      // Kiểm tra xem có phải điểm nổi tiếng miễn phí không
      const isFreeMatch = HUE_FREE_LANDMARKS.some(freeName => lower.includes(freeName));
      if (isFreeMatch) {
        matchedTickets.push({
          id: `free_${lower.replace(/\s+/g, '_')}`,
          name,
          originalPlaceName: name,
          priceAdult: 0,
          priceChild: 0,
          isFree: true
        });
      }
    });

    return matchedTickets;
  }

  /**
   * Tính toán toàn diện ngân sách du lịch Huế
   */
  calculateBudget(plan, options = {}) {
    const opts = { ...this.currentOptions, ...options };
    const adults = Math.max(1, parseInt(opts.adults, 10) || 1);
    const children = Math.max(0, parseInt(opts.children, 10) || 0);
    const days = Math.max(1, parseInt(opts.days, 10) || 1);
    const nights = Math.max(0, parseInt(opts.nights, 10) >= 0 ? parseInt(opts.nights, 10) : (days - 1));

    // Tính quãng đường ước tính
    let totalKm = 0;
    if (plan?.days && Array.isArray(plan.days)) {
      plan.days.forEach(d => {
        if (d.total_distance_km) totalKm += d.total_distance_km;
      });
    } else if (plan?.totalKm) {
      totalKm = plan.totalKm;
    }
    if (totalKm <= 0) {
      totalKm = days * 18; // Định mức di chuyển trung bình tại Huế: ~18km/ngày
    }

    // 1. TÍNH VÉ THAM QUAN TỰ ĐỘNG TỪ LỊCH TRÌNH
    const tickets = this.extractTicketItems(plan);
    const ticketIds = new Set(tickets.filter(t => !t.isFree).map(t => t.id));

    let comboApplied = null;
    let comboSavingsAdult = 0;
    let comboSavingsChild = 0;

    // Tự động kiểm tra điều kiện vé Combo 4 điểm hoặc 3 điểm
    const hasCombo4 = COMBO_RULES.combo4.requiredIds.every(id => ticketIds.has(id));
    const eligibleTombCount = (COMBO_RULES.combo3.eligibleTombIds || ['lang_minh_mang', 'lang_tu_duc', 'lang_khai_dinh'])
      .filter(id => ticketIds.has(id)).length;
    const hasCombo3 = ticketIds.has('dai_noi') && eligibleTombCount >= 2;

    if (opts.applyCombo && hasCombo4) {
      comboApplied = COMBO_RULES.combo4;
      comboSavingsAdult = comboApplied.savingAdult;
      comboSavingsChild = comboApplied.savingChild;
    } else if (opts.applyCombo && hasCombo3) {
      comboApplied = COMBO_RULES.combo3;
      comboSavingsAdult = comboApplied.savingAdult;
      comboSavingsChild = comboApplied.savingChild;
    }

    let rawTicketTotalAdult = 0;
    let rawTicketTotalChild = 0;

    tickets.forEach(t => {
      rawTicketTotalAdult += t.priceAdult;
      rawTicketTotalChild += t.priceChild;
    });

    let effectiveTicketAdult = rawTicketTotalAdult;
    let effectiveTicketChild = rawTicketTotalChild;

    if (comboApplied) {
      effectiveTicketAdult = rawTicketTotalAdult - comboSavingsAdult;
      effectiveTicketChild = rawTicketTotalChild - comboSavingsChild;
    }

    const totalTicketsCost = (effectiveTicketAdult * adults) + (effectiveTicketChild * children);
    const totalTicketSavings = (comboSavingsAdult * adults) + (comboSavingsChild * children);

    // 2. TÍNH ẨM THỰC
    const diningConfig = DINING_TIERS[opts.diningTier] || DINING_TIERS.standard;
    const effectiveEaters = adults + (children * 0.5);
    const totalDiningCost = effectiveEaters * diningConfig.ratePerDay * days;

    // 3. TÍNH DI CHUYỂN
    const transportConfig = TRANSPORT_TIERS[opts.transportType] || TRANSPORT_TIERS.motorbike;
    let totalTransportCost = 0;

    if (opts.transportType === 'motorbike') {
      const bikesNeeded = Math.ceil(adults / 2);
      totalTransportCost = bikesNeeded * (transportConfig.basePerDay + transportConfig.fuelPerDay) * days;
    } else if (opts.transportType === 'taxi') {
      const isLargeGroup = (adults + children) > 4;
      const taxiMultiplier = isLargeGroup ? 1.4 : 1.0;
      totalTransportCost = Math.round((days * 45000 + totalKm * transportConfig.ratePerKm) * taxiMultiplier);
    } else if (opts.transportType === 'private_car') {
      totalTransportCost = transportConfig.basePerDay * days;
    } else if (opts.transportType === 'bicycle') {
      totalTransportCost = adults * transportConfig.basePerDay * days;
    }

    // 4. TÍNH LƯU TRÚ
    const hotelConfig = HOTEL_TIERS[opts.hotelTier] || HOTEL_TIERS.none;
    const roomsNeeded = Math.max(1, Math.ceil(adults / 2));
    const totalHotelCost = nights > 0 ? (roomsNeeded * hotelConfig.ratePerNight * nights) : 0;

    // TỔNG KẾT
    const grandTotal = totalTicketsCost + totalDiningCost + totalTransportCost + totalHotelCost;
    const totalPeople = adults + children;
    const costPerPerson = totalPeople > 0 ? Math.round(grandTotal / totalPeople) : grandTotal;

    // Mẹo chi tiêu thông minh
    const isEn = i18n.currentLang === 'en';
    const tips = [];
    if (comboApplied) {
      const comboName = getTierName(comboApplied);
      tips.push(isEn
        ? `Automatically applied ${comboName}, saving your group ${this.formatVnd(totalTicketSavings)} compared to individual tickets.`
        : `Đã tự động áp dụng ${comboName}, giúp toàn đoàn tiết kiệm ${this.formatVnd(totalTicketSavings)} so với mua vé lẻ.`);
    } else if (ticketIds.has('dai_noi') && (ticketIds.has('lang_khai_dinh') || ticketIds.has('lang_minh_mang'))) {
      tips.push(isEn
        ? 'Tip: By adding Khai Dinh or Minh Mang tomb, you can purchase the 3-Site Heritage Pass (420,000 VND) to save 80,000 VND/person.'
        : 'Gợi ý: Nếu bổ sung thêm Lăng Khải Định hoặc Minh Mạng, bạn có thể mua Vé Tuyến 3 Điểm (420.000đ) để tiết kiệm 80.000đ/người.');
    }

    if (opts.transportType === 'taxi' && totalKm > 35) {
      tips.push(isEn
        ? 'Your route includes royal tombs far from the city center; consider booking a private car with driver to save on taxi fares.'
        : 'Lộ trình có các lăng ở xa trung tâm; bạn có thể cân nhắc thuê Ô tô có tài xế riêng để tiết kiệm hơn cước taxi.');
    } else if (opts.transportType === 'motorbike') {
      tips.push(isEn
        ? 'Exploring Hue by motorbike is scenic and relaxing; riverside roads and pine hills are shady and easy to navigate.'
        : 'Di chuyển bằng xe máy tại Huế rất thư thái; đường ven sông Hương và đồi thông râm mát và thuận tiện.');
    }

    if (nights === 0 && days > 1) {
      tips.push(isEn
        ? 'Note: You have selected 0 overnight stays for a multi-day trip. Increase overnight count in step 01 if you need hotel bookings.'
        : 'Lưu ý: Bạn đang chọn 0 đêm nghỉ cho chuyến đi nhiều ngày. Hãy tăng số đêm ở mục 01 nếu có nhu cầu đặt phòng khách sạn.');
    }

    return {
      adults,
      children,
      totalPeople,
      days,
      nights,
      roomsNeeded,
      totalKm,
      tickets: {
        list: tickets,
        rawSubtotal: (rawTicketTotalAdult * adults) + (rawTicketTotalChild * children),
        subtotal: totalTicketsCost,
        savings: totalTicketSavings,
        comboApplied
      },
      dining: {
        config: diningConfig,
        subtotal: totalDiningCost,
        days
      },
      transport: {
        config: transportConfig,
        subtotal: totalTransportCost,
        type: opts.transportType
      },
      accommodation: {
        config: hotelConfig,
        subtotal: totalHotelCost,
        nights,
        roomsNeeded
      },
      grandTotal,
      costPerPerson,
      tips
    };
  }

  formatVnd(amount) {
    if (typeof amount !== 'number') return i18n.currentLang === 'en' ? '0 VND' : '0 đ';
    if (i18n.currentLang === 'en') {
      return `${amount.toLocaleString('en-US')} VND`;
    }
    return `${amount.toLocaleString('vi-VN')} đ`;
  }

  openModal(plan, tourTitle = null) {
    this.init();
    if (!this.modal) return;

    if (!tourTitle) {
      tourTitle = i18n.currentLang === 'en' ? 'Explore Hue Itinerary' : 'Lịch trình Khám phá Cố Đô';
    }

    // Nếu không truyền plan nhưng trên bản đồ đang có một lịch trình hoạt động, ưu tiên kế thừa
    if (!plan && typeof window !== 'undefined' && window.mapStudio?.currentItinerary) {
      plan = window.mapStudio.currentItinerary;
    }

    this.currentPlan = plan;
    this.tourTitle = tourTitle;

    // Đồng bộ số ngày và số đêm theo lịch trình được truyền vào
    if (plan && (plan.days || plan.items)) {
      const daysCount = plan.days ? plan.days.length : (plan.totalDays || 2);
      this.currentOptions.days = daysCount;
      this.currentOptions.nights = Math.max(0, daysCount - 1);
    } else {
      // Mở tự do từ Sidebar: mặc định tour 2 ngày 1 đêm
      if (!this.currentOptions.days || this.currentOptions.days < 1) {
        this.currentOptions.days = 2;
        this.currentOptions.nights = 1;
      }
    }

    // Nếu có số đêm nghỉ và chưa chọn khách sạn thì gợi ý khách sạn 3-4 sao
    if (this.currentOptions.hotelTier === 'none' && this.currentOptions.nights > 0) {
      this.currentOptions.hotelTier = 'hotel34';
    }

    this.render();
    this.modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  closeModal() {
    if (!this.modal) return;
    this.modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  render() {
    const calculation = this.calculateBudget(this.currentPlan, this.currentOptions);
    const container = document.getElementById('budget-modal-content');
    if (!container) return;
    const isEn = i18n.currentLang === 'en';

    // Render danh sách vé di tích trong cột Bóc tách
    let ticketsBreakdownHtml = '';
    if (calculation.tickets.list.length > 0) {
      ticketsBreakdownHtml = calculation.tickets.list.map(t => {
        const isFree = t.isFree || (t.priceAdult === 0);
        const freeLabel = isEn ? 'Free' : 'Miễn phí';
        const perPersonSuffix = isEn ? '/ person' : '/ người';
        const matchPrefix = isEn ? 'Matched from itinerary:' : 'Khớp từ lịch trình:';
        return `
          <div class="budget-item-row">
            <div class="budget-item-info">
              <span class="budget-item-name">${t.name}</span>
              ${t.originalPlaceName && t.originalPlaceName !== t.name ? `<span class="budget-item-note">${matchPrefix} ${t.originalPlaceName}</span>` : ''}
            </div>
            <div class="budget-item-val ${isFree ? 'is-free' : ''}">
              ${isFree ? freeLabel : `${this.formatVnd(t.priceAdult)} ${perPersonSuffix}`}
            </div>
          </div>
        `;
      }).join('');
    } else {
      const emptyMain = isEn 
        ? 'Current itinerary has no ticketed monuments. Estimated admission: 0 VND.' 
        : 'Lịch trình hiện chưa có điểm di tích có thu vé. Vé tham quan ước tính: 0 đ.';
      const emptySub = isEn 
        ? '(This section automatically itemizes heritage passes when you build an itinerary with AI)' 
        : '(Mục này sẽ tự động bóc tách chi tiết các điểm di sản khi bạn lập lịch trình cùng Trợ lý AI)';
      ticketsBreakdownHtml = `
        <div class="budget-empty-note">
          ${emptyMain}
          <div style="margin-top: 0.35rem; font-size: 0.72rem; color: #71717A;">
            ${emptySub}
          </div>
        </div>
      `;
    }

    // Render tips
    let tipsHtml = '';
    if (calculation.tips.length > 0) {
      const tipsHeading = i18n.t('budgetSmartTipsHeading', 'Mẹo tiết kiệm chi phí thông minh:');
      tipsHtml = `
        <div class="budget-smart-tips">
          <div class="tips-title">${tipsHeading}</div>
          <ul class="tips-list">
            ${calculation.tips.map(tip => `<li>${tip}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    const step1Title = i18n.t('budgetStep1', '01. Thời gian & Thành viên');
    const daysTitle = i18n.t('budgetDaysTitle', 'Số ngày đi');
    const daysSub = i18n.t('budgetDaysSub', 'Thời lượng tour');
    const nightsTitle = i18n.t('budgetNightsTitle', 'Số đêm nghỉ');
    const nightsSub = this.currentOptions.nights > 0 
      ? (isEn ? `Book ${this.currentOptions.nights} night(s)` : `Đặt phòng ${this.currentOptions.nights} đêm`)
      : (isEn ? 'Day trip' : 'Đi trong ngày');
    const adultsTitle = i18n.t('budgetAdultsTitle', 'Người lớn');
    const adultsSub = i18n.t('budgetAdultsSub', 'Từ 12 tuổi');
    const childrenTitle = i18n.t('budgetChildrenTitle', 'Trẻ em');
    const childrenSub = i18n.t('budgetChildrenSub', 'Dưới 12 tuổi');

    const step2Title = i18n.t('budgetStep2', '02. Phương tiện di chuyển');
    const step3Title = i18n.t('budgetStep3', '03. Tiêu chuẩn ẩm thực');
    const step4Title = i18n.t('budgetStep4', '04. Khách sạn / Lưu trú');

    const perDaySuffix = isEn ? '/day' : '/ngày';
    const perNightSuffix = isEn ? '/night' : '/đêm';
    const perPersonSuffix = isEn ? '/ person' : '/ người';

    const kpiKicker = isEn ? 'TOTAL ESTIMATED TRIP BUDGET' : 'TỔNG CHI PHÍ DỰ TOÁN (ƯỚC TÍNH)';
    const avgLabel = isEn ? 'Average:' : 'Trung bình:';
    const scaleLabel = isEn 
      ? `${calculation.days} Days · ${calculation.nights} Nights · ~${calculation.totalKm.toFixed(1)} km`
      : `${calculation.days} Ngày · ${calculation.nights} Đêm · ~${calculation.totalKm.toFixed(1)} km`;

    const breakdownHeading = i18n.t('budgetBreakdownHeading', 'Bóc tách Chi tiết Hạng mục');
    const group1Title = isEn 
      ? `1. Monument Admission Tickets (${calculation.tickets.list.length} sites)`
      : `1. Vé Di tích & Thắng cảnh (${calculation.tickets.list.length} điểm)`;
    const group2Title = isEn 
      ? `2. Dining & Culinary (${calculation.days} days · ${calculation.totalPeople} people)`
      : `2. Ẩm thực & Thức uống (${calculation.days} ngày · ${calculation.totalPeople} người)`;
    const group3Title = isEn 
      ? `3. Transportation (${getTierName(calculation.transport.config)})`
      : `3. Phương tiện di chuyển (${getTierName(calculation.transport.config)})`;
    const group4Title = isEn 
      ? `4. Lodging (${calculation.accommodation.nights} nights)`
      : `4. Lưu trú (${calculation.accommodation.nights} đêm)`;

    const lodgingSubTip = calculation.accommodation.nights > 0 
      ? (isEn ? `${calculation.accommodation.nights} nights · ${calculation.accommodation.roomsNeeded} rooms` : `${calculation.accommodation.nights} đêm · ${calculation.accommodation.roomsNeeded} phòng`)
      : (isEn ? '0 nights' : '0 đêm');

    container.innerHTML = `
      <div class="budget-layout">
        <!-- CỘT TRÁI: ĐIỀU CHỈNH TIÊU CHÍ (CONTROLS) -->
        <div class="budget-controls-col">
          <!-- MỤC 01: THỜI GIAN & THÀNH VIÊN -->
          <div class="budget-control-section">
            <h4 class="budget-section-title">${step1Title}</h4>
            <div class="budget-stepper-grid">
              <!-- Số ngày -->
              <div class="budget-stepper-item">
                <div class="stepper-label-wrap">
                  <span class="stepper-title">${daysTitle}</span>
                  <span class="stepper-sub">${daysSub}</span>
                </div>
                <div class="budget-stepper">
                  <button type="button" class="btn-step" data-action="dec-days" ${this.currentOptions.days <= 1 ? 'disabled' : ''}>−</button>
                  <span class="step-value" id="val-days">${this.currentOptions.days}</span>
                  <button type="button" class="btn-step" data-action="inc-days">+</button>
                </div>
              </div>

              <!-- Số đêm lưu trú -->
              <div class="budget-stepper-item">
                <div class="stepper-label-wrap">
                  <span class="stepper-title">${nightsTitle}</span>
                  <span class="stepper-sub">${nightsSub}</span>
                </div>
                <div class="budget-stepper">
                  <button type="button" class="btn-step" data-action="dec-nights" ${this.currentOptions.nights <= 0 ? 'disabled' : ''}>−</button>
                  <span class="step-value" id="val-nights">${this.currentOptions.nights}</span>
                  <button type="button" class="btn-step" data-action="inc-nights">+</button>
                </div>
              </div>

              <!-- Người lớn -->
              <div class="budget-stepper-item">
                <div class="stepper-label-wrap">
                  <span class="stepper-title">${adultsTitle}</span>
                  <span class="stepper-sub">${adultsSub}</span>
                </div>
                <div class="budget-stepper">
                  <button type="button" class="btn-step" data-action="dec-adults" ${this.currentOptions.adults <= 1 ? 'disabled' : ''}>−</button>
                  <span class="step-value" id="val-adults">${this.currentOptions.adults}</span>
                  <button type="button" class="btn-step" data-action="inc-adults">+</button>
                </div>
              </div>

              <!-- Trẻ em -->
              <div class="budget-stepper-item">
                <div class="stepper-label-wrap">
                  <span class="stepper-title">${childrenTitle}</span>
                  <span class="stepper-sub">${childrenSub}</span>
                </div>
                <div class="budget-stepper">
                  <button type="button" class="btn-step" data-action="dec-children" ${this.currentOptions.children <= 0 ? 'disabled' : ''}>−</button>
                  <span class="step-value" id="val-children">${this.currentOptions.children}</span>
                  <button type="button" class="btn-step" data-action="inc-children">+</button>
                </div>
              </div>
            </div>
          </div>

          <!-- MỤC 02: PHƯƠNG TIỆN DI CHUYỂN -->
          <div class="budget-control-section">
            <h4 class="budget-section-title">${step2Title}</h4>
            <div class="budget-pill-group">
              ${Object.values(TRANSPORT_TIERS).map(t => `
                <button type="button" class="budget-pill-btn ${this.currentOptions.transportType === t.id ? 'active' : ''}" data-type="transport" data-value="${t.id}">
                  <span class="pill-name">${getTierName(t)}</span>
                  <span class="pill-desc">${getDesc(t)}</span>
                </button>
              `).join('')}
            </div>
          </div>

          <!-- MỤC 03: TIÊU CHUẨN ẨM THỰC -->
          <div class="budget-control-section">
            <h4 class="budget-section-title">${step3Title}</h4>
            <div class="budget-pill-group">
              ${Object.values(DINING_TIERS).map(d => `
                <button type="button" class="budget-pill-btn ${this.currentOptions.diningTier === d.id ? 'active' : ''}" data-type="dining" data-value="${d.id}">
                  <div class="pill-header-row">
                    <span class="pill-name">${getTierName(d)}</span>
                    <span class="pill-rate">${this.formatVnd(d.ratePerDay)}${perDaySuffix}</span>
                  </div>
                  <span class="pill-desc">${getDesc(d)}</span>
                </button>
              `).join('')}
            </div>
          </div>

          <!-- MỤC 04: KHÁCH SẠN / LƯU TRÚ -->
          <div class="budget-control-section">
            <div class="section-title-row">
              <h4 class="budget-section-title">${step4Title}</h4>
              <span class="section-sub-tip">${lodgingSubTip}</span>
            </div>
            <div class="budget-pill-group">
              ${Object.values(HOTEL_TIERS).map(h => `
                <button type="button" class="budget-pill-btn ${this.currentOptions.hotelTier === h.id ? 'active' : ''}" data-type="hotel" data-value="${h.id}">
                  <div class="pill-header-row">
                    <span class="pill-name">${getTierName(h)}</span>
                    ${h.ratePerNight > 0 ? `<span class="pill-rate">${this.formatVnd(h.ratePerNight)}${perNightSuffix}</span>` : ''}
                  </div>
                  <span class="pill-desc">${getDesc(h)}</span>
                </button>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- CỘT PHẢI: BẢNG BÓC TÁCH & TỔNG KẾT (SUMMARY & BREAKDOWN) -->
        <div class="budget-summary-col">
          <!-- FINANCIAL KPI CARDS -->
          <div class="budget-kpi-card">
            <span class="kpi-kicker">${kpiKicker}</span>
            <div class="kpi-main-number">${this.formatVnd(calculation.grandTotal)}</div>
            <div class="kpi-sub-row">
              <span class="kpi-per-person">${avgLabel} <strong>${this.formatVnd(calculation.costPerPerson)}</strong> ${perPersonSuffix}</span>
              <span class="kpi-scale">${scaleLabel}</span>
            </div>
          </div>

          ${calculation.tickets.savings > 0 ? `
            <div class="budget-saving-banner">
              <span class="saving-badge">${i18n.t('budgetComboBadge', 'Tiết kiệm vé')}</span>
              <span>${isEn ? 'Automatically applied' : 'Đã tự động áp dụng'} <strong>${getTierName(calculation.tickets.comboApplied)}</strong>, ${isEn ? 'saving' : 'tiết kiệm'} <strong>${this.formatVnd(calculation.tickets.savings)}</strong> ${isEn ? 'for your group!' : 'cho toàn đoàn!'}</span>
            </div>
          ` : ''}

          <!-- BẢNG BÓC TÁCH CHI PHÍ -->
          <div class="budget-breakdown-card">
            <h4 class="breakdown-title">${breakdownHeading}</h4>

            <!-- 1. VÉ THAM QUAN -->
            <div class="breakdown-group">
              <div class="breakdown-group-header">
                <span class="group-title">${group1Title}</span>
                <span class="group-subtotal">${this.formatVnd(calculation.tickets.subtotal)}</span>
              </div>
              <div class="breakdown-item-list">
                ${ticketsBreakdownHtml}
              </div>
            </div>

            <!-- 2. ẨM THỰC -->
            <div class="breakdown-group">
              <div class="breakdown-group-header">
                <span class="group-title">${group2Title}</span>
                <span class="group-subtotal">${this.formatVnd(calculation.dining.subtotal)}</span>
              </div>
              <div class="breakdown-item-row">
                <span class="item-sub-desc">${getTierName(calculation.dining.config)} (${this.formatVnd(calculation.dining.config.ratePerDay)}${isEn ? '/person/day' : '/người/ngày'} × ${calculation.days} ${isEn ? 'days' : 'ngày'})</span>
              </div>
            </div>

            <!-- 3. DI CHUYỂN -->
            <div class="breakdown-group">
              <div class="breakdown-group-header">
                <span class="group-title">${group3Title}</span>
                <span class="group-subtotal">${this.formatVnd(calculation.transport.subtotal)}</span>
              </div>
              <div class="breakdown-item-row">
                <span class="item-sub-desc">${calculation.transport.type === 'taxi' ? (isEn ? `Calculated based on ~${calculation.totalKm.toFixed(1)} km actual transit` : `Tính theo cước ~${calculation.totalKm.toFixed(1)} km lộ trình thực tế`) : (isEn ? `${calculation.days} travel days` : `${calculation.days} ngày di chuyển`)}</span>
              </div>
            </div>

            <!-- 4. LƯU TRÚ -->
            <div class="breakdown-group">
              <div class="breakdown-group-header">
                <span class="group-title">${group4Title}</span>
                <span class="group-subtotal">${this.formatVnd(calculation.accommodation.subtotal)}</span>
              </div>
              <div class="breakdown-item-row">
                <span class="item-sub-desc">
                  ${calculation.accommodation.nights > 0 
                    ? `${getTierName(calculation.accommodation.config)} (${calculation.accommodation.nights} ${isEn ? 'nights' : 'đêm'} × ${calculation.accommodation.roomsNeeded} ${isEn ? 'rooms' : 'phòng'} × ${this.formatVnd(calculation.accommodation.config.ratePerNight)})` 
                    : `${getTierName(calculation.accommodation.config)} (${isEn ? '0 nights - Day trip or arranged own lodging' : '0 đêm - Đi trong ngày hoặc tự túc chỗ ở'})`}
                </span>
              </div>
            </div>
          </div>

          ${tipsHtml}
        </div>
      </div>
    `;

    this._bindInteractiveControls(container);
  }

  _bindInteractiveControls(container) {
    // Steppers: Ngày, Đêm, Người lớn, Trẻ em
    container.querySelectorAll('.btn-step').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        if (action === 'inc-days') {
          this.currentOptions.days += 1;
          this.currentOptions.nights = this.currentOptions.days - 1;
        } else if (action === 'dec-days') {
          if (this.currentOptions.days > 1) {
            this.currentOptions.days -= 1;
            if (this.currentOptions.nights >= this.currentOptions.days) {
              this.currentOptions.nights = Math.max(0, this.currentOptions.days - 1);
            }
          }
        } else if (action === 'inc-nights') {
          this.currentOptions.nights += 1;
        } else if (action === 'dec-nights') {
          if (this.currentOptions.nights > 0) this.currentOptions.nights -= 1;
        } else if (action === 'inc-adults') {
          this.currentOptions.adults += 1;
        } else if (action === 'dec-adults') {
          if (this.currentOptions.adults > 1) this.currentOptions.adults -= 1;
        } else if (action === 'inc-children') {
          this.currentOptions.children += 1;
        } else if (action === 'dec-children') {
          if (this.currentOptions.children > 0) this.currentOptions.children -= 1;
        }
        this.render();
      });
    });

    // Pill selectors (Phương tiện, Ẩm thực, Khách sạn)
    container.querySelectorAll('.budget-pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        const val = btn.dataset.value;
        if (type === 'transport') {
          this.currentOptions.transportType = val;
        } else if (type === 'dining') {
          this.currentOptions.diningTier = val;
        } else if (type === 'hotel') {
          this.currentOptions.hotelTier = val;
        }
        this.render();
      });
    });
  }
}

export const budgetEstimator = new HueBudgetEstimator();
