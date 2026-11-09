// =============================================================================
// HUẾ SMART TOURISM — HUE REAL-TIME WEATHER SERVICE & WIDGET
// Tích hợp dữ liệu thời tiết thời gian thực Cố đô Huế (Open-Meteo API)
// Cung cấp lời khuyên du lịch, thời tiết hiện tại & dự báo các ngày tới (VI & EN)
// =============================================================================

import { i18n } from './i18n.js';

const HUE_LAT = 16.4674;
const HUE_LNG = 107.5905;
const CACHE_KEY = 'hue_smart_tourism_weather_cache';
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 phút cache

/**
 * Bảng mã WMO Weather Code song ngữ (VI & EN), icon SVG và gợi ý du lịch Huế
 */
const WMO_MAP = {
  0: {
    label: { vi: 'Trời quang đãng, nắng đẹp', en: 'Clear sky, sunny' },
    icon: 'sun',
    advice: {
      vi: 'Thời tiết tuyệt đẹp, lý tưởng tham quan Đại Nội, Lăng Khải Định & đi thuyền sông Hương.',
      en: 'Splendid weather, ideal for exploring the Citadel, Khai Dinh Tomb & boat cruising on Perfume River.'
    }
  },
  1: {
    label: { vi: 'Ít mây, trời nắng nhẹ', en: 'Mainly clear, mild sun' },
    icon: 'sun-cloud',
    advice: {
      vi: 'Nắng nhẹ dịu mát, rất thích hợp chụp ảnh check-in Cung An Định & Chùa Thiên Mụ.',
      en: 'Gentle sunshine, great for photography at An Dinh Palace & Thien Mu Pagoda.'
    }
  },
  2: {
    label: { vi: 'Trời có mây, râm mát', en: 'Partly cloudy, mild' },
    icon: 'cloud-sun',
    advice: {
      vi: 'Tiết trời râm mát, thích hợp dạo bộ Cầu Gỗ Lim, chợ Đông Ba & ngắm hoàng hôn sông Hương.',
      en: 'Pleasant overcast, perfect for walking on Lim Wooden Bridge, Dong Ba Market & river sunset.'
    }
  },
  3: {
    label: { vi: 'Nhiều mây, dịu trời', en: 'Overcast, cool' },
    icon: 'cloud',
    advice: {
      vi: 'Trời dịu mát, rất thuận lợi cho các tour khám phá ẩm thực phố cổ Bao Vinh.',
      en: 'Cool and mild, great for culinary exploration in Bao Vinh ancient town.'
    }
  },
  45: {
    label: { vi: 'Có sương mù nhẹ', en: 'Light fog' },
    icon: 'fog',
    advice: {
      vi: 'Sương sớm Cố đô rất thơ mộng, nên bắt đầu tour sau 8h sáng để ngắm cảnh rõ hơn.',
      en: 'Early morning mist along the river; start your tour after 8:00 AM for clearer views.'
    }
  },
  48: {
    label: { vi: 'Sương mù đọng', en: 'Depositing rime fog' },
    icon: 'fog',
    advice: {
      vi: 'Buổi sáng mờ ảo bên sông Hương, chú ý di chuyển cẩn thận trên các cung đường lăng tẩm.',
      en: 'Misty morning along the Perfume River, take care when driving on royal tomb roads.'
    }
  },
  51: {
    label: { vi: 'Mưa phùn nhẹ', en: 'Light drizzle' },
    icon: 'drizzle',
    advice: {
      vi: 'Mưa phùn đặc trưng Huế, hãy mang theo chiếc ô xinh để dạo Đại Nội trong làn mưa thơ mộng.',
      en: 'Hue signature drizzle, bring a small umbrella to stroll the Citadel in romantic rain.'
    }
  },
  53: {
    label: { vi: 'Mưa phùn vừa', en: 'Moderate drizzle' },
    icon: 'drizzle',
    advice: {
      vi: 'Nên mang theo ô/áo mưa, ghé thưởng thức một tách trà cung đình ấm nóng ngắm mưa rơi.',
      en: 'Carry an umbrella or raincoat; stop by for a cup of warm imperial tea while watching the rain.'
    }
  },
  55: {
    label: { vi: 'Mưa phùn hạt dày', en: 'Dense drizzle' },
    icon: 'drizzle',
    advice: {
      vi: 'Chuẩn bị ô khi ra ngoài; một tô Bún bò nóng hổi lúc này là lựa chọn tuyệt vời nhất.',
      en: 'Bring rain gear; a hot bowl of authentic Hue beef noodle soup is the perfect choice right now.'
    }
  },
  61: {
    label: { vi: 'Mưa rào nhẹ', en: 'Slight rain shower' },
    icon: 'rain-light',
    advice: {
      vi: 'Có mưa rào ngắt quãng, hãy chuẩn bị ô hoặc ghé quán cà phê ngắm mưa sông Hương.',
      en: 'Intermittent showers, carry an umbrella or enjoy rain views from a riverside coffee shop.'
    }
  },
  63: {
    label: { vi: 'Mưa rào vừa', en: 'Moderate rain' },
    icon: 'rain',
    advice: {
      vi: 'Nên ưu tiên tham quan các điểm trong nhà: Bảo tàng Cổ vật Cung đình, Không gian lưu niệm Lê Bá Đảng.',
      en: 'Prioritize indoor attractions: Museum of Royal Antiquities or Lebadang Memory Space.'
    }
  },
  65: {
    label: { vi: 'Mưa to', en: 'Heavy rain' },
    icon: 'rain-heavy',
    advice: {
      vi: 'Mưa lớn ngoài trời, thích hợp trải nghiệm ẩm thực cung đình hoặc nghỉ ngơi tại khách sạn.',
      en: 'Heavy rain outdoors, ideal for imperial dining experiences or relaxing at your hotel.'
    }
  },
  80: {
    label: { vi: 'Mưa rào rải rác', en: 'Scattered rain showers' },
    icon: 'rain',
    advice: {
      vi: 'Mưa từng cơn rồi tạnh, chú ý theo dõi lộ trình và chuẩn bị áo mưa khi di chuyển bằng xe máy.',
      en: 'Passing rain showers, check your itinerary and keep a raincoat handy if on a motorbike.'
    }
  },
  81: {
    label: { vi: 'Mưa rào nặng hạt', en: 'Heavy rain showers' },
    icon: 'rain-heavy',
    advice: {
      vi: 'Nên di chuyển bằng taxi/ô tô khi đi giữa các lăng tẩm xa trung tâm.',
      en: 'Prefer taxi or private car transit when visiting royal tombs outside the city center.'
    }
  },
  82: {
    label: { vi: 'Mưa rào rất to', en: 'Violent rain showers' },
    icon: 'rain-heavy',
    advice: {
      vi: 'Nên tránh các hoạt động ven sông hồ hoặc leo đồi Vọng Cảnh lúc này.',
      en: 'Avoid waterside activities or climbing Vong Canh hill during heavy torrential downpours.'
    }
  },
  95: {
    label: { vi: 'Dông sét', en: 'Thunderstorm' },
    icon: 'thunder',
    advice: {
      vi: 'Có dông sét, khuyến cáo ở trong nhà hoặc các điểm tham quan có mái che an toàn.',
      en: 'Thunderstorm warning, recommended to stay indoors or visit sheltered heritage galleries.'
    }
  },
  96: {
    label: { vi: 'Dông kèm mưa', en: 'Thunderstorm with rain' },
    icon: 'thunder',
    advice: {
      vi: 'Thời tiết dông mưa, tạm dừng các hoạt động chèo SUP sông Hương và leo núi Bạch Mã.',
      en: 'Stormy weather, suspend river SUP paddle activities and Bach Ma mountain trekking.'
    }
  }
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

      const temp = Math.round(current.temperature_2m || 28);
      let adviceVi = meta.advice.vi;
      let adviceEn = meta.advice.en;

      if (temp >= 33) {
        adviceVi = 'Trời khá oi bức (>33°C), nên tham quan di tích vào sáng sớm (trước 9h) hoặc chiều sau 15h30, nhớ mang nón và nước lọc.';
        adviceEn = 'Hot weather (>33°C), visit monuments early in the morning (before 9 AM) or after 3:30 PM, carry water and hats.';
      } else if (temp <= 21) {
        adviceVi = 'Tiết trời se lạnh se sắt rất tình, đừng quên khoác thêm áo ấm nhẹ khi dạo Cố đô về đêm.';
        adviceEn = 'Pleasantly chilly weather, remember to bring a light jacket when touring Hue at night.';
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
        advice: { vi: adviceVi, en: adviceEn },
        isDay: current.is_day !== 0,
        forecast: (daily.time || []).slice(0, 3).map((dateStr, idx) => ({
          date: dateStr,
          dayIndex: idx,
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
        condition: { vi: 'Trời nắng nhẹ, mát dịu', en: 'Mainly clear, mild' },
        iconType: 'sun-cloud',
        advice: {
          vi: 'Nắng nhẹ dịu mát, rất lý tưởng để khám phá Đại Nội & thưởng thức ẩm thực Cố đô.',
          en: 'Mild sunny weather, ideal for discovering the Citadel and savoring Hue delicacies.'
        },
        isDay: true,
        forecast: [
          { dayIndex: 0, maxTemp: 30, minTemp: 24, label: { vi: 'Nắng nhẹ', en: 'Mild sun' }, iconType: 'sun-cloud' },
          { dayIndex: 1, maxTemp: 31, minTemp: 24, label: { vi: 'Nắng đẹp', en: 'Sunny' }, iconType: 'sun' },
          { dayIndex: 2, maxTemp: 29, minTemp: 23, label: { vi: 'Mây rải rác', en: 'Partly cloudy' }, iconType: 'cloud-sun' }
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
   * Render widget thời tiết HTML dạng thẻ Editorial tinh tế song ngữ
   */
  renderWidgetHtml(data) {
    if (!data) return '';

    const isEn = i18n.currentLang === 'en';
    const langKey = isEn ? 'en' : 'vi';

    const cityName = isEn ? 'Hue City' : 'TP. Huế';
    const conditionText = typeof data.condition === 'object' 
      ? (data.condition[langKey] || data.condition.vi) 
      : data.condition;
    const adviceText = typeof data.advice === 'object' 
      ? (data.advice[langKey] || data.advice.vi) 
      : data.advice;

    const widgetTitle = i18n.t('weatherWidgetTooltip', 'Thời tiết Cố đô Huế thời gian thực');
    const expandTitle = i18n.t('weatherExpandTooltip', 'Xem chi tiết thời tiết');
    const feelsLikeLabel = i18n.t('weatherFeelsLike', 'Cảm nhận');
    const humidityLabel = i18n.t('weatherHumidity', 'Độ ẩm');
    const windLabel = i18n.t('weatherWind', 'Sức gió');
    const forecastTitle = i18n.t('weatherForecast3Days', 'Dự báo 3 ngày tới tại Huế');

    const getDayName = (idx) => {
      if (idx === 0) return i18n.t('weatherToday', 'Hôm nay');
      if (idx === 1) return i18n.t('weatherTomorrow', 'Ngày mai');
      return i18n.t('weatherDayAfter', 'Ngày kia');
    };

    return `
      <div class="hue-weather-widget" id="hue-weather-widget" title="${widgetTitle}">
        <div class="weather-widget-main">
          <div class="weather-icon-wrap">
            ${this.getWeatherIconSvg(data.iconType, 22)}
          </div>
          <div class="weather-core-info">
            <div class="weather-temp-row">
              <span class="weather-temp">${data.temp}°C</span>
              <span class="weather-city">${cityName}</span>
            </div>
            <div class="weather-condition">${conditionText}</div>
          </div>
          <button type="button" class="btn-weather-expand" id="btn-weather-expand" title="${expandTitle}" aria-label="${expandTitle}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        </div>

        <div class="weather-advice-pill">
          <span class="advice-sparkle">💡</span>
          <span class="advice-text">${adviceText}</span>
        </div>

        <!-- Dropdown / Expanded Details -->
        <div class="weather-details-card hidden" id="weather-details-card">
          <div class="weather-metrics-grid">
            <div class="weather-metric-item">
              <span class="metric-label">${feelsLikeLabel}</span>
              <strong class="metric-val">${data.feelsLike}°C</strong>
            </div>
            <div class="weather-metric-item">
              <span class="metric-label">${humidityLabel}</span>
              <strong class="metric-val">${data.humidity}%</strong>
            </div>
            <div class="weather-metric-item">
              <span class="metric-label">${windLabel}</span>
              <strong class="metric-val">${data.windSpeed} km/h</strong>
            </div>
          </div>

          <div class="weather-forecast-list">
            <div class="forecast-title">${forecastTitle}</div>
            ${(data.forecast || []).map(f => {
              const dayName = getDayName(f.dayIndex !== undefined ? f.dayIndex : 0);
              const labelText = typeof f.label === 'object' ? (f.label[langKey] || f.label.vi) : f.label;
              return `
                <div class="forecast-item">
                  <span class="forecast-day">${dayName}</span>
                  <span class="forecast-icon">${this.getWeatherIconSvg(f.iconType, 16)}</span>
                  <span class="forecast-label">${labelText}</span>
                  <span class="forecast-temps">${f.minTemp}° - ${f.maxTemp}°</span>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `;
  }
}