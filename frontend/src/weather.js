// =============================================================================
// HUẾ SMART TOURISM — HUE REAL-TIME WEATHER SERVICE & WIDGET
// Tích hợp dữ liệu thời tiết thời gian thực Cố đô Huế (Open-Meteo API)
// Cung cấp lời khuyên du lịch, thời tiết hiện tại & dự báo các ngày tới
// =============================================================================

const HUE_LAT = 16.4674;
const HUE_LNG = 107.5905;
const CACHE_KEY = 'hue_smart_tourism_weather_cache';
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 phút cache

/**
 * Bảng mã WMO Weather Code sang tiếng Việt, icon SVG và gợi ý du lịch Huế
 */
const WMO_MAP = {
  0: { label: 'Trời quang đãng, nắng đẹp', icon: 'sun', advice: 'Thời tiết tuyệt đẹp, lý tưởng tham quan Đại Nội, Lăng Khải Định & đi thuyền sông Hương.' },
  1: { label: 'Ít mây, trời nắng nhẹ', icon: 'sun-cloud', advice: 'Nắng nhẹ dịu mát, rất thích hợp chụp ảnh check-in Cung An Định & Chùa Thiên Mụ.' },
  2: { label: 'Trời có mây, râm mát', icon: 'cloud-sun', advice: 'Tiết trời râm mát, thích hợp dạo bộ Cầu Gỗ Lim, chợ Đông Ba & ngắm hoàng hôn sông Hương.' },
  3: { label: 'Nhiều mây, dịu trời', icon: 'cloud', advice: 'Trời dịu mát, rất thuận lợi cho các tour khám phá ẩm thực phố cổ Bao Vinh.' },
  45: { label: 'Có sương mù nhẹ', icon: 'fog', advice: 'Sương sớm Cố đô rất thơ mộng, nên bắt đầu tour sau 8h sáng để ngắm cảnh rõ hơn.' },
  48: { label: 'Sương mù đọng', icon: 'fog', advice: 'Buổi sáng mờ ảo bên sông Hương, chú ý di chuyển cẩn thận trên các cung đường lăng tẩm.' },
  51: { label: 'Mưa phùn nhẹ', icon: 'drizzle', advice: 'Mưa phùn đặc trưng Huế, hãy mang theo chiếc ô xinh để dạo Đại Nội trong làn mưa thơ mộng.' },
  53: { label: 'Mưa phùn vừa', icon: 'drizzle', advice: 'Nên mang theo ô/áo mưa, ghé thưởng thức một tách trà cung đình ấm nóng ngắm mưa rơi.' },
  55: { label: 'Mưa phùn hạt dày', icon: 'drizzle', advice: 'Chuẩn bị ô khi ra ngoài; một tô Bún bò nóng hổi lúc này là lựa chọn tuyệt vời nhất.' },
  61: { label: 'Mưa rào nhẹ', icon: 'rain-light', advice: 'Có mưa rào ngắt quãng, hãy chuẩn bị ô hoặc ghé quán cà phê ngắm mưa sông Hương.' },
  63: { label: 'Mưa rào vừa', icon: 'rain', advice: 'Nên ưu tiên tham quan các điểm trong nhà: Bảo tàng Cổ vật Cung đình, Không gian lưu niệm Lê Bá Đảng.' },
  65: { label: 'Mưa to', icon: 'rain-heavy', advice: 'Mưa lớn ngoài trời, thích hợp trải nghiệm ẩm thực cung đình hoặc nghỉ ngơi tại khách sạn.' },
  80: { label: 'Mưa rào rải rác', icon: 'rain', advice: 'Mưa từng cơn rồi tạnh, chú ý theo dõi lộ trình và chuẩn bị áo mưa khi di chuyển bằng xe máy.' },
  81: { label: 'Mưa rào nặng hạt', icon: 'rain-heavy', advice: 'Nên di chuyển bằng taxi/ô tô khi đi giữa các lăng tẩm xa trung tâm.' },
  82: { label: 'Mưa rào rất to', icon: 'rain-heavy', advice: 'Nên tránh các hoạt động ven sông hồ hoặc leo đồi Vọng Cảnh lúc này.' },
  95: { label: 'Dông sét', icon: 'thunder', advice: 'Có dông sét, khuyến cáo ở trong nhà hoặc các điểm tham quan có mái che an toàn.' },
  96: { label: 'Dông kèm mưa', icon: 'thunder', advice: 'Thời tiết dông mưa, tạm dừng các hoạt động chèo SUP sông Hương và leo núi Bạch Mã.' }
};

export class HueWeatherService {
  constructor() {
    this.weatherData = null;
  }

  /**
   * Lấy dữ liệu thời tiết Huế (từ Cache hoặc Open-Meteo API)
   */
  async getHueWeather(forceRefresh = false) {
    if (!forceRefresh) {
      try {
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (Date.now() - parsed.timestamp < CACHE_TTL_MS) {
            this.weatherData = parsed.data;
            return this.weatherData;
          }
        }
      } catch (e) {
        console.warn('Lỗi đọc cache thời tiết:', e);
      }
    }

    try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${HUE_LAT}&longitude=${HUE_LNG}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Asia%2FBangkok`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
      const raw = await res.json();

      const current = raw.current || {};
      const daily = raw.daily || {};
      const code = current.weather_code || 0;
      const meta = WMO_MAP[code] || WMO_MAP[0];

      // Tinh chỉnh lời khuyên theo nhiệt độ
      let advice = meta.advice;
      const temp = Math.round(current.temperature_2m || 28);
      if (temp >= 33) {
        advice = 'Trời khá oi bức (>33°C), nên tham quan di tích vào sáng sớm (trước 9h) hoặc chiều sau 15h30, nhớ mang nón và nước lọc.';
      } else if (temp <= 21) {
        advice = 'Tiết trời se lạnh se sắt rất tình, đừng quên khoác thêm áo ấm nhẹ khi dạo Cố đô về đêm.';
      }

      const processedData = {
        city: 'TP. Huế',
        temp: temp,
        feelsLike: Math.round(current.apparent_temperature || temp),
        humidity: current.relative_humidity_2m || 75,
        windSpeed: Math.round(current.wind_speed_10m || 8),
        weatherCode: code,
        condition: meta.label,
        iconType: meta.icon,
        advice: advice,
        isDay: current.is_day !== 0,
        forecast: (daily.time || []).slice(0, 3).map((dateStr, idx) => ({
          date: dateStr,
          dayName: idx === 0 ? 'Hôm nay' : (idx === 1 ? 'Ngày mai' : 'Ngày kia'),
          maxTemp: Math.round(daily.temperature_2m_max[idx] || 30),
          minTemp: Math.round(daily.temperature_2m_min[idx] || 24),
          code: daily.weather_code[idx] || 0,
          label: (WMO_MAP[daily.weather_code[idx]] || WMO_MAP[0]).label,
          iconType: (WMO_MAP[daily.weather_code[idx]] || WMO_MAP[0]).icon
        })),
        updatedAt: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
      };

      this.weatherData = processedData;
      try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({
          timestamp: Date.now(),
          data: processedData
        }));
      } catch {}

      return processedData;
    } catch (err) {
      console.warn('Không thể nạp thời tiết thời gian thực Open-Meteo, dùng fallback Cố đô:', err);
      // Fallback an toàn cho Huế
      return {
        city: 'TP. Huế',
        temp: 27,
        feelsLike: 28,
        humidity: 78,
        windSpeed: 10,
        weatherCode: 1,
        condition: 'Trời nắng nhẹ, mát dịu',
        iconType: 'sun-cloud',
        advice: 'Nắng nhẹ dịu mát, rất lý tưởng để khám phá Đại Nội & thưởng thức ẩm thực Cố đô.',
        isDay: true,
        forecast: [
          { dayName: 'Hôm nay', maxTemp: 30, minTemp: 24, label: 'Nắng nhẹ', iconType: 'sun-cloud' },
          { dayName: 'Ngày mai', maxTemp: 31, minTemp: 24, label: 'Nắng đẹp', iconType: 'sun' },
          { dayName: 'Ngày kia', maxTemp: 29, minTemp: 23, label: 'Mây rải rác', iconType: 'cloud-sun' }
        ],
        updatedAt: 'Vừa xong'
      };
    }
  }

  /**
   * Tạo icon SVG thời tiết vector sắc nét
   */
  getWeatherIconSvg(iconType, size = 20) {
    switch (iconType) {
      case 'sun':
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#EAB308" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4" fill="#FEF08A"/>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
          </svg>
        `;
      case 'sun-cloud':
      case 'cloud-sun':
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v2M4.93 4.93l1.41 1.41M20 12h2" stroke="#EAB308"/>
            <circle cx="12" cy="8" r="3" fill="#FEF08A" stroke="#EAB308"/>
            <path d="M17.5 19H9a5 5 0 0 1-.5-9.97A7 7 0 0 1 19 14a4 4 0 0 1-1.5 5z" fill="#F0F9FF"/>
          </svg>
        `;
      case 'rain':
      case 'rain-light':
      case 'rain-heavy':
      case 'drizzle':
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" fill="#F1F5F9" stroke="#64748B"/>
            <line x1="8" y1="19" x2="8" y2="21" stroke="#3B82F6"/>
            <line x1="12" y1="17" x2="12" y2="21" stroke="#3B82F6"/>
            <line x1="16" y1="19" x2="16" y2="21" stroke="#3B82F6"/>
          </svg>
        `;
      case 'thunder':
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 16.9A5 5 0 0 0 18 7h-1.26a8 8 0 1 0-11.62 9" fill="#F1F5F9" stroke="#475569"/>
            <polyline points="13 11 9 17 15 17 11 23" fill="#FDE047" stroke="#D97706"/>
          </svg>
        `;
      case 'fog':
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="8" x2="20" y2="8"/>
            <line x1="4" y1="12" x2="20" y2="12"/>
            <line x1="6" y1="16" x2="18" y2="16"/>
            <line x1="8" y1="20" x2="16" y2="20"/>
          </svg>
        `;
      default: // cloud
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" fill="#F1F5F9"/>
          </svg>
        `;
    }
  }

  /**
   * Render widget thời tiết HTML dạng thẻ Editorial tinh tế
   */
  renderWidgetHtml(data) {
    if (!data) return '';

    return `
      <div class="hue-weather-widget" id="hue-weather-widget" title="Thời tiết Cố đô Huế thời gian thực">
        <div class="weather-widget-main">
          <div class="weather-icon-wrap">
            ${this.getWeatherIconSvg(data.iconType, 22)}
          </div>
          <div class="weather-core-info">
            <div class="weather-temp-row">
              <span class="weather-temp">${data.temp}°C</span>
              <span class="weather-city">${data.city}</span>
            </div>
            <div class="weather-condition">${data.condition}</div>
          </div>
          <button type="button" class="btn-weather-expand" id="btn-weather-expand" title="Xem chi tiết thời tiết">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        </div>

        <div class="weather-advice-pill">
          <span class="advice-sparkle">💡</span>
          <span class="advice-text">${data.advice}</span>
        </div>

        <!-- Dropdown / Expanded Details -->
        <div class="weather-details-card hidden" id="weather-details-card">
          <div class="weather-metrics-grid">
            <div class="weather-metric-item">
              <span class="metric-label">Cảm nhận</span>
              <strong class="metric-val">${data.feelsLike}°C</strong>
            </div>
            <div class="weather-metric-item">
              <span class="metric-label">Độ ẩm</span>
              <strong class="metric-val">${data.humidity}%</strong>
            </div>
            <div class="weather-metric-item">
              <span class="metric-label">Sức gió</span>
              <strong class="metric-val">${data.windSpeed} km/h</strong>
            </div>
          </div>

          <div class="weather-forecast-list">
            <div class="forecast-title">Dự báo 3 ngày tới tại Huế</div>
            ${(data.forecast || []).map(f => `
              <div class="forecast-item">
                <span class="forecast-day">${f.dayName}</span>
                <span class="forecast-icon">${this.getWeatherIconSvg(f.iconType, 16)}</span>
                <span class="forecast-label">${f.label}</span>
                <span class="forecast-temps">${f.minTemp}° - ${f.maxTemp}°</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }
}
