const fs = require('fs');

let html = fs.readFileSync('frontend/index.html', 'utf8');

// List of exact string replacements
const replacements = [
  // 1. Sidebar Brand & Toggle
  [
    '<span class="sidebar-brand-title">Cố đô Huế</span>',
    '<span class="sidebar-brand-title" data-i18n="brandTitle">Cố đô Huế</span>'
  ],
  [
    '<button type="button" class="btn-sidebar-toggle" id="btn-sidebar-toggle" title="Thu gọn thanh bên"\n          aria-label="Thu gọn hoặc mở thanh bên" data-tooltip="Thu gọn thanh bên">',
    '<button type="button" class="btn-sidebar-toggle" id="btn-sidebar-toggle" title="Thu gọn thanh bên"\n          aria-label="Thu gọn hoặc mở thanh bên" data-i18n-title="sidebarToggle" data-i18n-tooltip="sidebarToggle">'
  ],
  [
    '<button type="button" class="btn-sidebar-new-chat" id="btn-sidebar-new-chat" title="Bắt đầu cuộc trò chuyện mới"\n          data-tooltip="Cuộc trò chuyện mới">',
    '<button type="button" class="btn-sidebar-new-chat" id="btn-sidebar-new-chat" title="Bắt đầu cuộc trò chuyện mới"\n          data-i18n-title="newChat" data-i18n-tooltip="newChat">'
  ],
  [
    '<div class="sidebar-weather-container" id="sidebar-weather-container" data-tooltip="Thời tiết Cố đô Huế">',
    '<div class="sidebar-weather-container" id="sidebar-weather-container" data-i18n-tooltip="weatherTitle">'
  ],
  [
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-travel-notebook"\n          title="Mở Sổ tay Du lịch & Gu cá nhân" data-tooltip="Sổ tay Cố Đô">',
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-travel-notebook"\n          title="Mở Sổ tay Du lịch & Gu cá nhân" data-i18n-title="travelNotebook" data-i18n-tooltip="travelNotebook">'
  ],
  [
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-saved-tours" title="Xem các lịch trình đã lưu"\n          data-tooltip="Lịch trình đã lưu">',
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-saved-tours" title="Xem các lịch trình đã lưu"\n          data-i18n-title="savedTours" data-i18n-tooltip="savedTours">'
  ],
  [
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-budget" title="Dự toán chi phí du lịch Huế"\n          data-tooltip="Dự toán chi phí">',
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-budget" title="Dự toán chi phí du lịch Huế"\n          data-i18n-title="budgetEstimator" data-i18n-tooltip="budgetEstimator">'
  ],
  [
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-toggle-map"\n          title="Mở / Thu gọn bản đồ không gian" data-tooltip="Bản đồ không gian">',
    '<button type="button" class="sidebar-nav-item" id="btn-sidebar-toggle-map"\n          title="Mở / Thu gọn bản đồ không gian" data-i18n-title="spatialMap" data-i18n-tooltip="spatialMap">'
  ],
  [
    '<button type="button" class="sidebar-nav-item btn-sidebar-settings" id="btn-sidebar-settings"\n          title="Cài đặt ứng dụng" data-tooltip="Cài đặt">',
    '<button type="button" class="sidebar-nav-item btn-sidebar-settings" id="btn-sidebar-settings"\n          title="Cài đặt ứng dụng" data-i18n-title="settings" data-i18n-tooltip="settings">'
  ],
  [
    '<div class="sidebar-user-footer" id="sidebar-user-footer">\n          <div class="sidebar-user-chip" id="btn-sidebar-user" role="button" aria-haspopup="true" aria-expanded="false"\n            title="Tài khoản người dùng" data-tooltip="Tài khoản cá nhân">',
    '<div class="sidebar-user-footer" id="sidebar-user-footer">\n          <div class="sidebar-user-chip" id="btn-sidebar-user" role="button" aria-haspopup="true" aria-expanded="false"\n            title="Tài khoản người dùng" data-i18n-title="accountTooltip" data-i18n-tooltip="accountTooltip">'
  ],
  [
    '<span class="sidebar-user-name" id="sidebar-user-name">Khách vãng lai</span>',
    '<span class="sidebar-user-name" id="sidebar-user-name" data-i18n="userGuest">Khách vãng lai</span>'
  ],
  [
    '<div class="popover-user-name" id="popover-user-name">Khách vãng lai</div>',
    '<div class="popover-user-name" id="popover-user-name" data-i18n="userGuest">Khách vãng lai</div>'
  ],
  [
    '<div class="popover-user-email" id="popover-user-email">Chưa đăng nhập</div>',
    '<div class="popover-user-email" id="popover-user-email" data-i18n="notLoggedIn">Chưa đăng nhập</div>'
  ],
  [
    '<span class="popover-badge-status" id="popover-badge-status">Khách</span>',
    '<span class="popover-badge-status" id="popover-badge-status" data-i18n="badgeGuest">Khách</span>'
  ],
  [
    '<button type="button" class="popover-item" id="btn-popover-notebook">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>\n                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>\n              </svg>\n              <span>Sổ tay du lịch</span>',
    '<button type="button" class="popover-item" id="btn-popover-notebook">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>\n                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>\n              </svg>\n              <span data-i18n="popoverNotebook">Sổ tay du lịch</span>'
  ],
  [
    '<button type="button" class="popover-item" id="btn-popover-saved-tours">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n              </svg>\n              <span>Xem các lịch trình đã lưu</span>',
    '<button type="button" class="popover-item" id="btn-popover-saved-tours">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n              </svg>\n              <span data-i18n="popoverSavedTours">Xem các lịch trình đã lưu</span>'
  ],
  [
    '<button type="button" class="popover-item" id="btn-popover-config">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <circle cx="12" cy="12" r="3"></circle>\n                <path\n                  d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">\n                </path>\n              </svg>\n              <span>Cài đặt ứng dụng</span>',
    '<button type="button" class="popover-item" id="btn-popover-config">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <circle cx="12" cy="12" r="3"></circle>\n                <path\n                  d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">\n                </path>\n              </svg>\n              <span data-i18n="popoverSettings">Cài đặt ứng dụng</span>'
  ],
  [
    '<span>Đăng xuất tài khoản</span>',
    '<span data-i18n="popoverLogout">Đăng xuất tài khoản</span>'
  ],
  [
    '<button type="button" class="popover-item popover-item-primary" id="btn-popover-login">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>\n                <polyline points="10 17 15 12 10 7"></polyline>\n                <line x1="15" y1="12" x2="3" y2="12"></line>\n              </svg>\n              <span>Đăng nhập</span>',
    '<button type="button" class="popover-item popover-item-primary" id="btn-popover-login">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>\n                <polyline points="10 17 15 12 10 7"></polyline>\n                <line x1="15" y1="12" x2="3" y2="12"></line>\n              </svg>\n              <span data-i18n="popoverLogin">Đăng nhập</span>'
  ],
  [
    '<span>Đăng ký thành viên mới</span>',
    '<span data-i18n="popoverSignup">Đăng ký thành viên mới</span>'
  ],
  [
    '<span>Trải nghiệm Khách (Demo Mode)</span>',
    '<span data-i18n="popoverDemo">Trải nghiệm Khách (Demo Mode)</span>'
  ],

  // 2. Header
  [
    '<button type="button" class="btn-toggle-sidebar mobile-only" id="btn-toggle-sidebar"\n              title="Đóng / Mở thanh lịch sử (Menu bên trái)" aria-label="Menu thanh bên">',
    '<button type="button" class="btn-toggle-sidebar mobile-only" id="btn-toggle-sidebar"\n              title="Đóng / Mở thanh lịch sử (Menu bên trái)" aria-label="Menu thanh bên" data-i18n-title="sidebarToggle">'
  ],
  [
    '<div class="header-weather-pill" id="header-weather-pill" title="Thời tiết Cố đô Huế hôm nay">',
    '<div class="header-weather-pill" id="header-weather-pill" title="Thời tiết Cố đô Huế hôm nay" data-i18n-title="weatherPillTooltip">'
  ],
  [
    '<button type="button" class="header-map-toggle-btn" id="btn-header-toggle-map"\n              title="Mở / Thu gọn bản đồ không gian" aria-label="Mở bản đồ">',
    '<button type="button" class="header-map-toggle-btn" id="btn-header-toggle-map"\n              title="Mở / Thu gọn bản đồ không gian" aria-label="Mở bản đồ" data-i18n-title="mapToggleOpen">'
  ],
  [
    '<button type="button" class="btn-auth-header btn-header-login" id="btn-header-login"\n                title="Đăng nhập tài khoản">',
    '<button type="button" class="btn-auth-header btn-header-login" id="btn-header-login"\n                title="Đăng nhập tài khoản" data-i18n-title="login">'
  ],
  [
    '<button type="button" class="btn-auth-header btn-header-signup" id="btn-header-signup"\n                title="Đăng ký tài khoản mới">',
    '<button type="button" class="btn-auth-header btn-header-signup" id="btn-header-signup"\n                title="Đăng ký tài khoản mới" data-i18n-title="signup">'
  ],
  [
    '<span class="user-name-label" id="user-name-label">Người dùng</span>',
    '<span class="user-name-label" id="user-name-label" data-i18n="userDefault">Người dùng</span>'
  ],
  [
    '<div class="dropdown-user-name" id="dropdown-user-name">Người dùng</div>',
    '<div class="dropdown-user-name" id="dropdown-user-name" data-i18n="userDefault">Người dùng</div>'
  ],
  [
    '<button type="button" class="dropdown-item" id="btn-open-travel-notebook">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>\n                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>\n                  </svg>\n                  <span>Sổ tay du lịch</span>',
    '<button type="button" class="dropdown-item" id="btn-open-travel-notebook">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>\n                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>\n                  </svg>\n                  <span data-i18n="popoverNotebook">Sổ tay du lịch</span>'
  ],
  [
    '<button type="button" class="dropdown-item" id="btn-open-saved-tours">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n                  </svg>\n                  <span>Lịch trình đã lưu</span>',
    '<button type="button" class="dropdown-item" id="btn-open-saved-tours">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n                  </svg>\n                  <span data-i18n="savedTours">Lịch trình đã lưu</span>'
  ],
  [
    '<button type="button" class="dropdown-item" id="btn-open-firebase-config">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <circle cx="12" cy="12" r="3"></circle>\n                    <path\n                      d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">\n                    </path>\n                  </svg>\n                  <span>Cài đặt ứng dụng</span>',
    '<button type="button" class="dropdown-item" id="btn-open-firebase-config">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <circle cx="12" cy="12" r="3"></circle>\n                    <path\n                      d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z">\n                    </path>\n                  </svg>\n                  <span data-i18n="popoverSettings">Cài đặt ứng dụng</span>'
  ],
  [
    '<button type="button" class="dropdown-item dropdown-item-danger" id="btn-header-logout">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>\n                    <polyline points="16 17 21 12 16 7"></polyline>\n                    <line x1="21" y1="12" x2="9" y2="12"></line>\n                  </svg>\n                  <span>Đăng xuất</span>',
    '<button type="button" class="dropdown-item dropdown-item-danger" id="btn-header-logout">\n                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>\n                    <polyline points="16 17 21 12 16 7"></polyline>\n                    <line x1="21" y1="12" x2="9" y2="12"></line>\n                  </svg>\n                  <span data-i18n="logout">Đăng xuất</span>'
  ],

  // 3. Spatial Map Toolbar
  [
    '<span class="toolbar-meta" id="map-active-meta" title="Bản đồ Di sản">Bản đồ Di sản</span>',
    '<span class="toolbar-meta" id="map-active-meta" title="Bản đồ Di sản" data-i18n="mapActiveMeta">Bản đồ Di sản</span>'
  ],
  [
    '<option value="google_streets" selected>Đường phố</option>',
    '<option value="google_streets" selected data-i18n="mapStyleStreets">Đường phố</option>'
  ],
  [
    '<option value="google_satellite">Vệ tinh</option>',
    '<option value="google_satellite" data-i18n="mapStyleSatellite">Vệ tinh</option>'
  ],
  [
    '<button class="map-btn" id="btn-reset-map" title="Về trung tâm Cố đô Huế">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />\n                  <path d="M3 3v5h5" />\n                </svg>\n                <span>Trung tâm</span>',
    '<button class="map-btn" id="btn-reset-map" title="Về trung tâm Cố đô Huế" data-i18n-title="mapCenterBtn">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />\n                  <path d="M3 3v5h5" />\n                </svg>\n                <span data-i18n="mapCenterBtn">Trung tâm</span>'
  ],
  [
    '<button class="map-btn btn-locate-user" id="btn-locate-user" title="Định vị vị trí hiện tại (GPS)">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">\n                  <circle cx="12" cy="12" r="3" fill="currentColor" />\n                  <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />\n                  <circle cx="12" cy="12" r="7" stroke-dasharray="2 2" />\n                </svg>\n                <span id="locate-btn-label">Vị trí của tôi</span>',
    '<button class="map-btn btn-locate-user" id="btn-locate-user" title="Định vị vị trí hiện tại (GPS)" data-i18n-title="mapLocateBtn">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">\n                  <circle cx="12" cy="12" r="3" fill="currentColor" />\n                  <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />\n                  <circle cx="12" cy="12" r="7" stroke-dasharray="2 2" />\n                </svg>\n                <span id="locate-btn-label" data-i18n="mapLocateBtn">Vị trí của tôi</span>'
  ],
  [
    '<button class="map-btn btn-toggle-workbench" id="btn-toggle-workbench"\n                title="Thu gọn / Mở rộng bảng điều khiển bên phải" aria-label="Toàn cảnh bản đồ">\n                <svg class="icon-toggle-expand" width="13" height="13" viewBox="0 0 24 24" fill="none"\n                  stroke="currentColor" stroke-width="2">\n                  <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />\n                </svg>\n                <span id="workbench-toggle-text">Toàn cảnh</span>',
    '<button class="map-btn btn-toggle-workbench" id="btn-toggle-workbench"\n                title="Thu gọn / Mở rộng bảng điều khiển bên phải" aria-label="Toàn cảnh bản đồ" data-i18n-title="mapExpandBtn">\n                <svg class="icon-toggle-expand" width="13" height="13" viewBox="0 0 24 24" fill="none"\n                  stroke="currentColor" stroke-width="2">\n                  <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />\n                </svg>\n                <span id="workbench-toggle-text" data-i18n="mapExpandBtn">Toàn cảnh</span>'
  ],
  [
    '<button class="map-btn btn-close-map-panel" id="btn-close-map-panel"\n                title="Thu gọn bản đồ (Tập trung giao diện Chatbot)" aria-label="Thu gọn bản đồ">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">\n                  <path d="M18 6L6 18M6 6l12 12" />\n                </svg>\n                <span>Thu gọn</span>',
    '<button class="map-btn btn-close-map-panel" id="btn-close-map-panel"\n                title="Thu gọn bản đồ (Tập trung giao diện Chatbot)" aria-label="Thu gọn bản đồ" data-i18n-title="mapCollapseBtn">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">\n                  <path d="M18 6L6 18M6 6l12 12" />\n                </svg>\n                <span data-i18n="mapCollapseBtn">Thu gọn</span>'
  ],
  [
    'placeholder="Tìm di tích, chùa, quán bún bò, cà phê, khách sạn..." autocomplete="off">',
    'placeholder="Tìm di tích, chùa, quán bún bò, cà phê, khách sạn..." data-i18n-placeholder="mapSearchPlaceholder" autocomplete="off">'
  ],
  [
    '<button type="button" id="btn-clear-search" class="btn-clear-search" style="display: none;"\n                  title="Xóa tìm kiếm">✕</button>',
    '<button type="button" id="btn-clear-search" class="btn-clear-search" style="display: none;"\n                  title="Xóa tìm kiếm" data-i18n-title="mapClearSearch">✕</button>'
  ],
  [
    '<span class="chip-label">Tất cả</span>',
    '<span class="chip-label" data-i18n="mapViewAll">Tất cả</span>'
  ],
  [
    '<span class="chip-label">Di tích</span>',
    '<span class="chip-label" data-i18n="mapViewAttractions">Di tích</span>'
  ],
  [
    '<span class="chip-label">Quán ăn</span>',
    '<span class="chip-label" data-i18n="mapViewFood">Quán ăn</span>'
  ],
  [
    '<span class="chip-label">Cà phê</span>',
    '<span class="chip-label" data-i18n="mapViewCafe">Cà phê</span>'
  ],
  [
    '<span class="chip-label">Khách sạn</span>',
    '<span class="chip-label" data-i18n="mapViewStay">Khách sạn</span>'
  ],

  // 4. Map Legend
  [
    '<div class="legend-item"><span class="legend-dot dot-attraction"></span> Di tích / Thắng cảnh</div>',
    '<div class="legend-item"><span class="legend-dot dot-attraction"></span> <span data-i18n="legendAttraction">Di tích / Thắng cảnh</span></div>'
  ],
  [
    '<div class="legend-item"><span class="legend-dot dot-restaurant"></span> Ẩm thực Cố đô</div>',
    '<div class="legend-item"><span class="legend-dot dot-restaurant"></span> <span data-i18n="legendRestaurant">Ẩm thực Cố đô</span></div>'
  ],
  [
    '<div class="legend-item"><span class="legend-dot dot-cafe"></span> Cà phê & Sunset</div>',
    '<div class="legend-item"><span class="legend-dot dot-cafe"></span> <span data-i18n="legendCafe">Cà phê & Sunset</span></div>'
  ],
  [
    '<div class="legend-item"><span class="legend-dot dot-hotel"></span> Khách sạn / Nghỉ dưỡng</div>',
    '<div class="legend-item"><span class="legend-dot dot-hotel"></span> <span data-i18n="legendHotel">Khách sạn / Nghỉ dưỡng</span></div>'
  ],
  [
    '<div class="legend-item"><span class="legend-line line-route"></span> Tuyến Tour Tối Ưu</div>',
    '<div class="legend-item"><span class="legend-line line-route"></span> <span data-i18n="legendRoute">Tuyến Tour Tối Ưu</span></div>'
  ],

  // 5. Workbench Actions
  [
    '<h2 class="workbench-title">Hỏi đáp & Lịch trình Thông minh</h2>',
    '<h2 class="workbench-title" data-i18n="workbenchMainTitle">Hỏi đáp & Lịch trình Thông minh</h2>'
  ],
  [
    '<button type="button" class="btn-workbench-action btn-new-chat-action" id="btn-new-chat"\n                title="Bắt đầu cuộc trò chuyện mới" aria-label="Đoạn chat mới">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">\n                  <line x1="12" y1="5" x2="12" y2="19" />\n                  <line x1="5" y1="12" x2="19" y2="12" />\n                </svg>\n                <span>Đoạn chat mới</span>',
    '<button type="button" class="btn-workbench-action btn-new-chat-action" id="btn-new-chat"\n                title="Bắt đầu cuộc trò chuyện mới" aria-label="Đoạn chat mới" data-i18n-title="tabNewChat">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">\n                  <line x1="12" y1="5" x2="12" y2="19" />\n                  <line x1="5" y1="12" x2="19" y2="12" />\n                </svg>\n                <span data-i18n="tabNewChat">Đoạn chat mới</span>'
  ],
  [
    '<button type="button" class="btn-workbench-action" id="btn-toggle-chat-history"\n                title="Mở lịch sử các phiên chat" aria-label="Lịch sử chat">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <circle cx="12" cy="12" r="10" />\n                  <polyline points="12 6 12 12 16 14" />\n                </svg>\n                <span>Lịch sử</span>',
    '<button type="button" class="btn-workbench-action" id="btn-toggle-chat-history"\n                title="Mở lịch sử các phiên chat" aria-label="Lịch sử chat" data-i18n-title="tabHistory">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <circle cx="12" cy="12" r="10" />\n                  <polyline points="12 6 12 12 16 14" />\n                </svg>\n                <span data-i18n="tabHistory">Lịch sử</span>'
  ],
  [
    '<button type="button" class="btn-workbench-action" id="btn-workbench-saved-tours"\n                title="Xem danh sách các tour và lịch trình bạn đã lưu" aria-label="Tour đã lưu">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n                </svg>\n                <span>Tour đã lưu</span>',
    '<button type="button" class="btn-workbench-action" id="btn-workbench-saved-tours"\n                title="Xem danh sách các tour và lịch trình bạn đã lưu" aria-label="Tour đã lưu" data-i18n-title="tabSavedTours">\n                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>\n                </svg>\n                <span data-i18n="tabSavedTours">Tour đã lưu</span>'
  ],
  [
    '<button type="button" class="btn-workbench-action" id="btn-workbench-toggle-map"\n                title="Mở / Thu gọn bản đồ bên cạnh" aria-label="Bản đồ">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />\n                  <line x1="9" y1="3" x2="9" y2="18" />\n                  <line x1="15" y1="6" x2="15" y2="21" />\n                </svg>\n                <span id="workbench-map-toggle-label">Bản đồ</span>',
    '<button type="button" class="btn-workbench-action" id="btn-workbench-toggle-map"\n                title="Mở / Thu gọn bản đồ bên cạnh" aria-label="Bản đồ" data-i18n-title="tabMap">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />\n                  <line x1="9" y1="3" x2="9" y2="18" />\n                  <line x1="15" y1="6" x2="15" y2="21" />\n                </svg>\n                <span id="workbench-map-toggle-label" data-i18n="tabMap">Bản đồ</span>'
  ],
  [
    '<button type="button" class="btn-workbench-action" id="btn-toggle-planner"\n                title="Mở bộ công cụ tạo lịch trình" aria-expanded="false">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />\n                  <line x1="9" y1="3" x2="9" y2="18" />\n                  <line x1="15" y1="6" x2="15" y2="21" />\n                </svg>\n                <span>Tạo lịch trình</span>',
    '<button type="button" class="btn-workbench-action" id="btn-toggle-planner"\n                title="Mở bộ công cụ tạo lịch trình" aria-expanded="false" data-i18n-title="tabPlan">\n                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                  <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />\n                  <line x1="9" y1="3" x2="9" y2="18" />\n                  <line x1="15" y1="6" x2="15" y2="21" />\n                </svg>\n                <span data-i18n="tabPlan">Tạo lịch trình</span>'
  ],

  // 6. Quick Planner Card
  [
    '<span>Lập lịch trình tour tối ưu</span>',
    '<span data-i18n="plannerTitle">Lập lịch trình tour tối ưu</span>'
  ],
  [
    '<button type="button" class="btn-close-planner" id="btn-close-planner"\n                title="Đóng bảng lập lịch">✕</button>',
    '<button type="button" class="btn-close-planner" id="btn-close-planner"\n                title="Đóng bảng lập lịch" data-i18n-title="plannerCloseTooltip">✕</button>'
  ],
  [
    '<span class="origin-label">Điểm xuất phát Tour</span>',
    '<span class="origin-label" data-i18n="plannerOriginLabel">Điểm xuất phát Tour</span>'
  ],
  [
    '<strong class="origin-name" id="planner-origin-name">Vị trí hiện tại của bạn</strong>',
    '<strong class="origin-name" id="planner-origin-name" data-i18n="userLocationHere">Vị trí hiện tại của bạn</strong>'
  ],
  [
    '<button type="button" class="btn-refresh-origin" id="btn-refresh-origin" title="Cập nhật tọa độ GPS">',
    '<button type="button" class="btn-refresh-origin" id="btn-refresh-origin" title="Cập nhật tọa độ GPS" data-i18n-title="plannerGpsRefreshTooltip">'
  ],
  [
    '<label for="select-days" class="form-label">Số ngày du lịch</label>',
    '<label for="select-days" class="form-label" data-i18n="plannerDaysLabel">Số ngày du lịch</label>'
  ],
  [
    '<option value="1">1 ngày</option>',
    '<option value="1" data-i18n="plannerDays1">1 ngày</option>'
  ],
  [
    '<option value="2" selected>2 ngày</option>',
    '<option value="2" selected data-i18n="plannerDays2">2 ngày</option>'
  ],
  [
    '<option value="3">3 ngày</option>',
    '<option value="3" data-i18n="plannerDays3">3 ngày</option>'
  ],
  [
    '<label for="select-trip-type" class="form-label">Bạn đi cùng ai?</label>',
    '<label for="select-trip-type" class="form-label" data-i18n="plannerPartyLabel">Bạn đi cùng ai?</label>'
  ],
  [
    '<option value="Couples" selected>Cặp đôi</option>',
    '<option value="Couples" selected data-i18n="plannerPartyCouples">Cặp đôi</option>'
  ],
  [
    '<option value="Family">Gia đình</option>',
    '<option value="Family" data-i18n="plannerPartyFamily">Gia đình</option>'
  ],
  [
    '<option value="Friends">Nhóm bạn</option>',
    '<option value="Friends" data-i18n="plannerPartyFriends">Nhóm bạn</option>'
  ],
  [
    '<option value="Solo">Một mình</option>',
    '<option value="Solo" data-i18n="plannerPartySolo">Một mình</option>'
  ],
  [
    '<label class="form-label">Món ưu tiên thưởng thức</label>',
    '<label class="form-label" data-i18n="plannerDishLabel">Món ưu tiên thưởng thức</label>'
  ],
  [
    '<button type="button" class="dish-tag active" data-dish="Bún bò Huế">Bún bò Huế</button>',
    '<button type="button" class="dish-tag active" data-dish="Bún bò Huế" data-i18n="dishBunBo">Bún bò Huế</button>'
  ],
  [
    '<button type="button" class="dish-tag active" data-dish="Bánh bèo, nậm, lọc">Bánh bèo, nậm,\n                    lọc</button>',
    '<button type="button" class="dish-tag active" data-dish="Bánh bèo, nậm, lọc" data-i18n="dishBanhBeo">Bánh bèo, nậm, lọc</button>'
  ],
  [
    '<button type="button" class="dish-tag active" data-dish="Cơm hến">Cơm hến</button>',
    '<button type="button" class="dish-tag active" data-dish="Cơm hến" data-i18n="dishComHen">Cơm hến</button>'
  ],
  [
    '<button type="button" class="dish-tag" data-dish="Chè hẻm Huế">Chè Huế</button>',
    '<button type="button" class="dish-tag" data-dish="Chè hẻm Huế" data-i18n="dishCheHue">Chè Huế</button>'
  ],
  [
    '<button type="button" class="dish-tag" data-dish="Bánh khoái">Bánh khoái</button>',
    '<button type="button" class="dish-tag" data-dish="Bánh khoái" data-i18n="dishBanhKhoai">Bánh khoái</button>'
  ],
  [
    '<button type="button" class="dish-tag" data-dish="Cơm chay Huế">Cơm chay</button>',
    '<button type="button" class="dish-tag" data-dish="Cơm chay Huế" data-i18n="dishComChay">Cơm chay</button>'
  ],
  [
    'Tạo lịch trình vào Luồng Chat\n                </button>',
    '<span data-i18n="plannerSubmitBtn">Tạo lịch trình vào Luồng Chat</span>\n                </button>'
  ],

  // 7. POI Detail Drawer
  [
    '<h3 class="poi-section-title">Giới thiệu</h3>',
    '<h3 class="poi-section-title" data-i18n="poiIntroHeading">Giới thiệu</h3>'
  ],
  [
    '<span>Nhận xét từ du khách</span>',
    '<span data-i18n="poiReviewsHeading">Nhận xét từ du khách</span>'
  ],
  [
    '<span>Gần đây</span>',
    '<span data-i18n="poiRecentHeading">Gần đây</span>'
  ],
  [
    '<span id="poi-fav-label">Yêu thích</span>',
    '<span id="poi-fav-label" data-i18n="poiFavLabel">Yêu thích</span>'
  ],
  [
    '<button type="button" class="btn-drawer btn-poi-checkin" id="poi-btn-checkin" title="Đánh dấu đã ghé thăm">',
    '<button type="button" class="btn-drawer btn-poi-checkin" id="poi-btn-checkin" title="Đánh dấu đã ghé thăm" data-i18n-title="poiCheckinLabel">'
  ],
  [
    '<button type="button" class="btn-drawer btn-poi-route" id="poi-btn-route"\n            title="Vẽ tuyến đường từ vị trí của bạn trên bản đồ">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <polygon points="3 11 22 2 13 21 11 13 3 11" />\n            </svg>\n            <span>Chỉ đường</span>',
    '<button type="button" class="btn-drawer btn-poi-route" id="poi-btn-route"\n            title="Vẽ tuyến đường từ vị trí của bạn trên bản đồ" data-i18n-title="poiDirectionsBtn">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <polygon points="3 11 22 2 13 21 11 13 3 11" />\n            </svg>\n            <span data-i18n="poiDirectionsBtn">Chỉ đường</span>'
  ],
  [
    '<button type="button" class="btn-drawer btn-poi-add-tour" id="poi-btn-add-tour"\n            title="Thêm địa điểm này vào lịch trình tour">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <line x1="12" y1="5" x2="12" y2="19" />\n              <line x1="5" y1="12" x2="19" y2="12" />\n            </svg>\n            <span>Thêm Tour</span>',
    '<button type="button" class="btn-drawer btn-poi-add-tour" id="poi-btn-add-tour"\n            title="Thêm địa điểm này vào lịch trình tour" data-i18n-title="poiAddTourBtn">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <line x1="12" y1="5" x2="12" y2="19" />\n              <line x1="5" y1="12" x2="19" y2="12" />\n            </svg>\n            <span data-i18n="poiAddTourBtn">Thêm Tour</span>'
  ],
  [
    '<button type="button" class="btn-drawer btn-ask-ai" id="poi-btn-ask-ai" title="Hỏi trợ lý AI về điểm này">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />\n            </svg>\n            <span>Hỏi thêm</span>',
    '<button type="button" class="btn-drawer btn-ask-ai" id="poi-btn-ask-ai" title="Hỏi trợ lý AI về điểm này" data-i18n-title="poiAskAiBtn">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />\n            </svg>\n            <span data-i18n="poiAskAiBtn">Hỏi thêm</span>'
  ],

  // 8. Auth Modal
  [
    '<h2 class="auth-modal-title" id="auth-modal-title">Đăng nhập</h2>',
    '<h2 class="auth-modal-title" id="auth-modal-title" data-i18n="authModalTitleLogin">Đăng nhập</h2>'
  ],
  [
    '<p class="auth-modal-subtitle" id="auth-modal-subtitle">Chào mừng bạn đến với Cố đô Huế Travel</p>',
    '<p class="auth-modal-subtitle" id="auth-modal-subtitle" data-i18n="authModalSubtitle">Chào mừng bạn đến với Cố đô Huế Travel</p>'
  ],
  [
    '<button type="button" class="auth-tab-btn active" id="tab-auth-login">Đăng nhập</button>',
    '<button type="button" class="auth-tab-btn active" id="tab-auth-login" data-i18n="tabAuthLogin">Đăng nhập</button>'
  ],
  [
    '<button type="button" class="auth-tab-btn" id="tab-auth-signup">Đăng ký</button>',
    '<button type="button" class="auth-tab-btn" id="tab-auth-signup" data-i18n="tabAuthSignup">Đăng ký</button>'
  ],
  [
    '<span>Tiếp tục với Google</span>',
    '<span data-i18n="authGoogleBtn">Tiếp tục với Google</span>'
  ],
  [
    '<span>hoặc tiếp tục với email</span>',
    '<span data-i18n="authOrEmail">hoặc tiếp tục với email</span>'
  ],
  [
    '<label for="auth-input-name" class="auth-label">Họ và tên</label>',
    '<label for="auth-input-name" class="auth-label" data-i18n="authNameLabel">Họ và tên</label>'
  ],
  [
    '<input type="text" id="auth-input-name" class="auth-input" placeholder="Ví dụ: Nguyễn Văn A" />',
    '<input type="text" id="auth-input-name" class="auth-input" placeholder="Ví dụ: Nguyễn Văn A" data-i18n-placeholder="authNamePlaceholder" />'
  ],
  [
    '<label for="auth-input-email" class="auth-label">Địa chỉ Email</label>',
    '<label for="auth-input-email" class="auth-label" data-i18n="authEmailLabel">Địa chỉ Email</label>'
  ],
  [
    '<input type="email" id="auth-input-email" class="auth-input" placeholder="name@example.com" autocomplete="email" required />',
    '<input type="email" id="auth-input-email" class="auth-input" placeholder="name@example.com" data-i18n-placeholder="authEmailPlaceholder" autocomplete="email" required />'
  ],
  [
    '<label for="auth-input-password" class="auth-label">Mật khẩu</label>',
    '<label for="auth-input-password" class="auth-label" data-i18n="authPasswordLabel">Mật khẩu</label>'
  ],
  [
    '<input type="password" id="auth-input-password" class="auth-input" placeholder="Tối thiểu 6 ký tự" autocomplete="current-password" required />',
    '<input type="password" id="auth-input-password" class="auth-input" placeholder="Tối thiểu 6 ký tự" data-i18n-placeholder="authPasswordPlaceholder" autocomplete="current-password" required />'
  ],
  [
    '<span class="auth-remember-text">Ghi nhớ mật khẩu</span>',
    '<span class="auth-remember-text" data-i18n="authRememberPassword">Ghi nhớ mật khẩu</span>'
  ],
  [
    '<button type="submit" class="btn-auth-submit" id="btn-auth-submit">Đăng nhập</button>',
    '<button type="submit" class="btn-auth-submit" id="btn-auth-submit" data-i18n="authSubmitLogin">Đăng nhập</button>'
  ],
  [
    '<span id="auth-switch-text">Chưa có tài khoản?</span>',
    '<span id="auth-switch-text" data-i18n="authNoAccount">Chưa có tài khoản?</span>'
  ],
  [
    '<button type="button" class="btn-switch-auth-link" id="btn-switch-auth-mode">Đăng ký ngay</button>',
    '<button type="button" class="btn-switch-auth-link" id="btn-switch-auth-mode" data-i18n="authSwitchSignup">Đăng ký ngay</button>'
  ],
  [
    '<button type="button" class="btn-auth-guest-demo" id="btn-auth-guest-demo">\n          Dùng thử nhanh không cần đăng nhập\n        </button>',
    '<button type="button" class="btn-auth-guest-demo" id="btn-auth-guest-demo" data-i18n="authDemoGuest">\n          Dùng thử nhanh không cần đăng nhập\n        </button>'
  ],

  // 9. Settings Modal
  [
    '<h3 id="settings-modal-title">Cài đặt ứng dụng</h3>',
    '<h3 id="settings-modal-title" data-i18n="settingsTitle">Cài đặt ứng dụng</h3>'
  ],
  [
    '<p class="settings-modal-subtitle">Tùy biến trải nghiệm du lịch, trợ lý AI và kết nối hệ thống</p>',
    '<p class="settings-modal-subtitle" data-i18n="settingsSubtitle">Tùy biến trải nghiệm du lịch, trợ lý AI và kết nối hệ thống</p>'
  ],
  [
    '<button type="button" class="settings-tab-btn active" id="tab-settings-general" role="tab"\n            aria-selected="true" data-target="panel-settings-general">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <rect x="3" y="3" width="7" height="7"></rect>\n              <rect x="14" y="3" width="7" height="7"></rect>\n              <rect x="14" y="14" width="7" height="7"></rect>\n              <rect x="3" y="14" width="7" height="7"></rect>\n            </svg>\n            <span>Trải nghiệm</span>',
    '<button type="button" class="settings-tab-btn active" id="tab-settings-general" role="tab"\n            aria-selected="true" data-target="panel-settings-general">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <rect x="3" y="3" width="7" height="7"></rect>\n              <rect x="14" y="3" width="7" height="7"></rect>\n              <rect x="14" y="14" width="7" height="7"></rect>\n              <rect x="3" y="14" width="7" height="7"></rect>\n            </svg>\n            <span data-i18n="settingsTabGeneral">Trải nghiệm</span>'
  ],
  [
    '<button type="button" class="settings-tab-btn" id="tab-settings-ai" role="tab" aria-selected="false"\n            data-target="panel-settings-ai">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>\n              <path d="M12 2a10 10 0 0 1 10 10h-10V2z" opacity="0.3"></path>\n              <polygon points="12 8 13.5 11 16.5 11 14 13 15 16 12 14 9 16 10 13 7.5 11 10.5 11 12 8"\n                fill="currentColor"></polygon>\n            </svg>\n            <span>Trợ lý AI Cố Đô</span>',
    '<button type="button" class="settings-tab-btn" id="tab-settings-ai" role="tab" aria-selected="false"\n            data-target="panel-settings-ai">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>\n              <path d="M12 2a10 10 0 0 1 10 10h-10V2z" opacity="0.3"></path>\n              <polygon points="12 8 13.5 11 16.5 11 14 13 15 16 12 14 9 16 10 13 7.5 11 10.5 11 12 8"\n                fill="currentColor"></polygon>\n            </svg>\n            <span data-i18n="settingsTabAI">Trợ lý AI Cố Đô</span>'
  ],
  [
    '<span class="settings-item-title">Chế độ giao diện (Dark Mode)</span>',
    '<span class="settings-item-title" data-i18n="themeLabel">Chế độ giao diện (Dark Mode)</span>'
  ],
  [
    '<span class="settings-item-desc">Chọn tông màu sáng tinh tế hoặc chế độ tối dịu mắt (giảm chói khi du lịch ban đêm).</span>',
    '<span class="settings-item-desc" data-i18n="themeDesc">Chọn tông màu sáng tinh tế hoặc chế độ tối dịu mắt (giảm chói khi du lịch ban đêm).</span>'
  ],
  [
    '<option value="system">Tự động (Hệ thống)</option>',
    '<option value="system" data-i18n="themeSystem">Tự động (Hệ thống)</option>'
  ],
  [
    '<option value="light">Giao diện Sáng</option>',
    '<option value="light" data-i18n="themeLight">Giao diện Sáng</option>'
  ],
  [
    '<option value="dark">Giao diện Tối (Dark mode)</option>',
    '<option value="dark" data-i18n="themeDark">Giao diện Tối (Dark mode)</option>'
  ],
  [
    '<span class="settings-item-title">Tự động kích hoạt Bản đồ & Lộ trình</span>',
    '<span class="settings-item-title" data-i18n="autoMapLabel">Tự động kích hoạt Bản đồ & Lộ trình</span>'
  ],
  [
    '<span class="settings-item-desc">Tự động mở không gian bản đồ khi Trợ lý AI gợi ý địa danh hoặc tuyến\n                  tham quan.</span>',
    '<span class="settings-item-desc" data-i18n="autoMapDesc">Tự động mở không gian bản đồ khi Trợ lý AI gợi ý địa danh hoặc tuyến tham quan.</span>'
  ],
  [
    '<span class="settings-item-title">Hiệu ứng hoạt họa chuyển cảnh</span>',
    '<span class="settings-item-title" data-i18n="animLabel">Hiệu ứng hoạt họa chuyển cảnh</span>'
  ],
  [
    '<span class="settings-item-desc">Chuyển đổi giao diện mượt mà giữa Chế độ Khám phá, Bản đồ và Trò\n                  chuyện.</span>',
    '<span class="settings-item-desc" data-i18n="animDesc">Chuyển đổi giao diện mượt mà giữa Chế độ Khám phá, Bản đồ và Trò chuyện.</span>'
  ],
  [
    '<span class="settings-item-title">Mẹo du lịch thích ứng theo thời tiết Huế</span>',
    '<span class="settings-item-title" data-i18n="weatherTipsLabel">Mẹo du lịch thích ứng theo thời tiết Huế</span>'
  ],
  [
    '<span class="settings-item-desc">Đưa ra khuyến nghị linh hoạt theo thời tiết Cố đô (nắng râm, mưa Huế,\n                  nhiệt độ).</span>',
    '<span class="settings-item-desc" data-i18n="weatherTipsDesc">Đưa ra khuyến nghị linh hoạt theo thời tiết Cố đô (nắng râm, mưa Huế, nhiệt độ).</span>'
  ],
  [
    '<span class="settings-item-title">Xóa bộ nhớ đệm ứng dụng</span>',
    '<span class="settings-item-title" data-i18n="clearCacheTitle">Xóa bộ nhớ đệm ứng dụng</span>'
  ],
  [
    '<span class="settings-item-desc">Làm mới bộ nhớ đệm cục bộ của trình duyệt nếu bạn gặp tình trạng hiển thị\n                chậm hoặc sai lệch.</span>',
    '<span class="settings-item-desc" data-i18n="clearCacheDesc">Làm mới bộ nhớ đệm cục bộ của trình duyệt nếu bạn gặp tình trạng hiển thị chậm hoặc sai lệch.</span>'
  ],
  [
    '<button type="button" class="btn-settings-action" id="btn-settings-clear-cache">\n              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <polyline points="1 4 1 10 7 10"></polyline>\n                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>\n              </svg>\n              <span>Làm mới bộ nhớ</span>',
    '<button type="button" class="btn-settings-action" id="btn-settings-clear-cache">\n              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <polyline points="1 4 1 10 7 10"></polyline>\n                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>\n              </svg>\n              <span data-i18n="clearCacheBtn">Làm mới bộ nhớ</span>'
  ],
  [
    '<div class="settings-subheading">Phong cách tư vấn của Trợ lý AI</div>',
    '<div class="settings-subheading" data-i18n="aiStyleSubheading">Phong cách tư vấn của Trợ lý AI</div>'
  ],
  [
    '<div class="ai-style-name">Du lịch Cân bằng</div>',
    '<div class="ai-style-name" data-i18n="aiStyleBalancedName">Du lịch Cân bằng</div>'
  ],
  [
    '<div class="ai-style-desc">Hòa quyện di tích lịch sử, danh lam thắng cảnh và ẩm thực tinh hoa Cố đô.\n                </div>',
    '<div class="ai-style-desc" data-i18n="aiStyleBalancedDesc">Hòa quyện di tích lịch sử, danh lam thắng cảnh và ẩm thực tinh hoa Cố đô.</div>'
  ],
  [
    '<div class="ai-style-name">Chuyên sâu Di sản</div>',
    '<div class="ai-style-name" data-i18n="aiStyleHeritageName">Chuyên sâu Di sản</div>'
  ],
  [
    '<div class="ai-style-desc">Tập trung niên đại các vua triều Nguyễn, điển tích và kiến trúc cung đình.\n                </div>',
    '<div class="ai-style-desc" data-i18n="aiStyleHeritageDesc">Tập trung niên đại các vua triều Nguyễn, điển tích và kiến trúc cung đình.</div>'
  ],
  [
    '<div class="ai-style-name">Ẩm thực & Đời sống</div>',
    '<div class="ai-style-name" data-i18n="aiStyleFoodieName">Ẩm thực & Đời sống</div>'
  ],
  [
    '<div class="ai-style-desc">Ưu tiên các quán ngon truyền thống, ẩm thực vỉa hè, cà phê ngắm sông Hương.\n                </div>',
    '<div class="ai-style-desc" data-i18n="aiStyleFoodieDesc">Ưu tiên các quán ngon truyền thống, ẩm thực vỉa hè, cà phê ngắm sông Hương.</div>'
  ],
  [
    '<div class="settings-subheading">Mức độ chi tiết của phản hồi</div>',
    '<div class="settings-subheading" data-i18n="aiDetailSubheading">Mức độ chi tiết của phản hồi</div>'
  ],
  [
    '<option value="detailed" selected>Chi tiết đầy đủ (Lộ trình chi tiết từng mốc thời gian, lời khuyên di\n                chuyển)</option>',
    '<option value="detailed" selected data-i18n="aiDetailDetailed">Chi tiết đầy đủ (Lộ trình chi tiết từng mốc thời gian, lời khuyên di chuyển)</option>'
  ],
  [
    '<option value="concise">Súc tích & Trực diện (Tóm tắt nhanh gọn các điểm chính yếu)</option>',
    '<option value="concise" data-i18n="aiDetailConcise">Súc tích & Trực diện (Tóm tắt nhanh gọn các điểm chính yếu)</option>'
  ],

  // 10. Saved Tours Modal
  [
    '<h3>Lịch trình Du lịch Huế đã lưu</h3>',
    '<h3 data-i18n="savedToursTitle">Lịch trình Du lịch Huế đã lưu</h3>'
  ],
  [
    '<p class="saved-tours-subtitle">Các lộ trình đã được lưu trữ an toàn trên Google Firebase Cloud Database</p>',
    '<p class="saved-tours-subtitle" data-i18n="savedToursSubtitle">Các lộ trình đã được lưu trữ an toàn trên Google Firebase Cloud Database</p>'
  ],

  // 11. Budget Modal
  [
    '<span class="budget-kicker">CỐ ĐÔ HUẾ · DỰ TOÁN CHI PHÍ CHUYẾN ĐI</span>',
    '<span class="budget-kicker" data-i18n="budgetKicker">CỐ ĐÔ HUẾ · DỰ TOÁN CHI PHÍ CHUYẾN ĐI</span>'
  ],
  [
    '<h3 id="budget-modal-title" class="budget-modal-title">Bảng Dự toán Ngân sách Lịch trình</h3>',
    '<h3 id="budget-modal-title" class="budget-modal-title" data-i18n="budgetTitle">Bảng Dự toán Ngân sách Lịch trình</h3>'
  ],
  [
    '<p class="budget-modal-subtitle">Bóc tách chi tiết vé di tích chính thức, định mức ẩm thực và cước phương tiện theo lộ trình</p>',
    '<p class="budget-modal-subtitle" data-i18n="budgetSubtitle">Bóc tách chi tiết vé di tích chính thức, định mức ẩm thực và cước phương tiện theo lộ trình</p>'
  ],
  [
    '<button type="button" class="btn-budget-action" id="btn-print-budget" title="In hoặc lưu file PDF dự toán">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <polyline points="6 9 6 2 18 2 18 9"></polyline>\n                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>\n                <rect x="6" y="14" width="12" height="8"></rect>\n              </svg>\n              <span>In / Lưu PDF</span>',
    '<button type="button" class="btn-budget-action" id="btn-print-budget" title="In hoặc lưu file PDF dự toán" data-i18n-title="budgetPrintBtn">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n                <polyline points="6 9 6 2 18 2 18 9"></polyline>\n                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>\n                <rect x="6" y="14" width="12" height="8"></rect>\n              </svg>\n              <span data-i18n="budgetPrintBtn">In / Lưu PDF</span>'
  ],

  // 12. Notebook Modal
  [
    '<span class="notebook-kicker">CỐ ĐÔ HUẾ · SỔ TAY DU KHÁCH</span>',
    '<span class="notebook-kicker" data-i18n="notebookKicker">CỐ ĐÔ HUẾ · SỔ TAY DU KHÁCH</span>'
  ],
  [
    '<h3 id="notebook-modal-title" class="notebook-modal-title">Sổ tay Du lịch Cố Đô</h3>',
    '<h3 id="notebook-modal-title" class="notebook-modal-title" data-i18n="notebookTitle">Sổ tay Du lịch Cố Đô</h3>'
  ],
  [
    '<p class="notebook-modal-subtitle">Lưu trữ điểm đến yêu thích, hộ chiếu khám phá và thiết lập gu trải nghiệm\n            riêng</p>',
    '<p class="notebook-modal-subtitle" data-i18n="notebookSubtitle">Lưu trữ điểm đến yêu thích, hộ chiếu khám phá và thiết lập gu trải nghiệm riêng</p>'
  ],
  [
    '<button type="button" class="notebook-tab-btn active" data-tab="wishlist">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path\n                d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z">\n              </path>\n            </svg>\n            <span>Địa điểm Yêu thích</span>',
    '<button type="button" class="notebook-tab-btn active" data-tab="wishlist">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path\n                d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z">\n              </path>\n            </svg>\n            <span data-i18n="notebookTabWishlist">Địa điểm Yêu thích</span>'
  ],
  [
    '<button type="button" class="notebook-tab-btn" data-tab="passport">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2">\n              </polygon>\n            </svg>\n            <span>Hộ chiếu Khám phá</span>',
    '<button type="button" class="notebook-tab-btn" data-tab="passport">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2">\n              </polygon>\n            </svg>\n            <span data-i18n="notebookTabPassport">Hộ chiếu Khám phá</span>'
  ],
  [
    '<button type="button" class="notebook-tab-btn" data-tab="preferences">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <circle cx="12" cy="12" r="3"></circle>\n              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>\n            </svg>\n            <span>Gu du lịch & Khẩu vị</span>',
    '<button type="button" class="notebook-tab-btn" data-tab="preferences">\n            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <circle cx="12" cy="12" r="3"></circle>\n              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>\n            </svg>\n            <span data-i18n="notebookTabPreferences">Gu du lịch & Khẩu vị</span>'
  ],
  [
    'placeholder="Tìm kiếm theo tên địa danh hoặc ghi chú..." />',
    'placeholder="Tìm kiếm theo tên địa danh hoặc ghi chú..." data-i18n-placeholder="notebookSearchPlaceholder" />'
  ],
  [
    '<p class="explorer-rank-desc" id="explorer-rank-desc">Đánh dấu các địa danh bạn đã ghé thăm để nâng cấp\n                hành trình.</p>',
    '<p class="explorer-rank-desc" id="explorer-rank-desc" data-i18n="passportDescDefault">Đánh dấu các địa danh bạn đã ghé thăm để nâng cấp hành trình.</p>'
  ],
  [
    '<button type="button" class="checkin-filter-pill active" data-filter="all">Tất cả</button>',
    '<button type="button" class="checkin-filter-pill active" data-filter="all" data-i18n="passportFilterAll">Tất cả</button>'
  ],
  [
    '<button type="button" class="checkin-filter-pill" data-filter="attraction">Di tích</button>',
    '<button type="button" class="checkin-filter-pill" data-filter="attraction" data-i18n="passportFilterHeritage">Di tích</button>'
  ],
  [
    '<button type="button" class="checkin-filter-pill" data-filter="restaurant">Ẩm thực</button>',
    '<button type="button" class="checkin-filter-pill" data-filter="restaurant" data-i18n="passportFilterFood">Ẩm thực</button>'
  ],
  [
    '<button type="button" class="checkin-filter-pill" data-filter="cafe">Cà phê</button>',
    '<button type="button" class="checkin-filter-pill" data-filter="cafe" data-i18n="passportFilterCafe">Cà phê</button>'
  ],
  [
    '<button type="button" class="checkin-filter-pill" data-filter="hotel">Khách sạn</button>',
    '<button type="button" class="checkin-filter-pill" data-filter="hotel" data-i18n="passportFilterHotel">Khách sạn</button>'
  ],
  [
    '<h4 class="pref-section-heading">Phong cách Trải nghiệm</h4>',
    '<h4 class="pref-section-heading" data-i18n="prefStyleHeading">Phong cách Trải nghiệm</h4>'
  ],
  [
    '<p class="pref-section-caption">Chọn một hoặc nhiều trải nghiệm bạn ưu tiên khi khám phá Huế</p>',
    '<p class="pref-section-caption" data-i18n="prefStyleCaption">Chọn một hoặc nhiều trải nghiệm bạn ưu tiên khi khám phá Huế</p>'
  ],
  [
    '<span class="pref-label">Di tích & Lịch sử</span>',
    '<span class="pref-label" data-i18n="prefHeritageLabel">Di tích & Lịch sử</span>'
  ],
  [
    '<span class="pref-desc">Đại Nội, lăng tẩm hoàng gia, bảo tàng cổ vật</span>',
    '<span class="pref-desc" data-i18n="prefHeritageDesc">Đại Nội, lăng tẩm hoàng gia, bảo tàng cổ vật</span>'
  ],
  [
    '<span class="pref-label">Ẩm thực & Quán ngon</span>',
    '<span class="pref-label" data-i18n="prefFoodieLabel">Ẩm thực & Quán ngon</span>'
  ],
  [
    '<span class="pref-desc">Bún bò, bánh bèo nậm lọc, cơm hến, chè hẻm</span>',
    '<span class="pref-desc" data-i18n="prefFoodieDesc">Bún bò, bánh bèo nậm lọc, cơm hến, chè hẻm</span>'
  ],
  [
    '<span class="pref-label">Nhiếp ảnh & Cà phê</span>',
    '<span class="pref-label" data-i18n="prefPhotoLabel">Nhiếp ảnh & Cà phê</span>'
  ],
  [
    '<span class="pref-desc">Hoàng hôn đồi Vọng Cảnh, cà phê bờ sông Hương</span>',
    '<span class="pref-desc" data-i18n="prefPhotoDesc">Hoàng hôn đồi Vọng Cảnh, cà phê bờ sông Hương</span>'
  ],
  [
    '<span class="pref-label">Thiên nhiên & Sinh thái</span>',
    '<span class="pref-label" data-i18n="prefNatureLabel">Thiên nhiên & Sinh thái</span>'
  ],
  [
    '<span class="pref-desc">Rừng ngập mặn Rú Chá, phá Tam Giang, đồi thông</span>',
    '<span class="pref-desc" data-i18n="prefNatureDesc">Rừng ngập mặn Rú Chá, phá Tam Giang, đồi thông</span>'
  ],
  [
    '<span class="pref-label">Tâm linh & Thiền tịnh</span>',
    '<span class="pref-label" data-i18n="prefZenLabel">Tâm linh & Thiền tịnh</span>'
  ],
  [
    '<span class="pref-desc">Chùa Thiên Mụ, Từ Hiếu, Huyền Không Sơn Thượng</span>',
    '<span class="pref-desc" data-i18n="prefZenDesc">Chùa Thiên Mụ, Từ Hiếu, Huyền Không Sơn Thượng</span>'
  ],
  [
    '<h4 class="pref-section-heading">Khẩu vị & Dị ứng Ẩm thực</h4>',
    '<h4 class="pref-section-heading" data-i18n="prefDietaryHeading">Khẩu vị & Dị ứng Ẩm thực</h4>'
  ],
  [
    '<p class="pref-section-caption">AI sẽ chọn lọc quán ăn và nhắc lưu ý gia vị trước mỗi bữa ăn</p>',
    '<p class="pref-section-caption" data-i18n="prefDietaryCaption">AI sẽ chọn lọc quán ăn và nhắc lưu ý gia vị trước mỗi bữa ăn</p>'
  ],
  [
    '<span class="pref-label">Ăn chay</span>',
    '<span class="pref-label" data-i18n="prefVegLabel">Ăn chay</span>'
  ],
  [
    '<span class="pref-desc">Ưu tiên quán chay thanh tịnh, món chay Cố Đô</span>',
    '<span class="pref-desc" data-i18n="prefVegDesc">Ưu tiên quán chay thanh tịnh, món chay Cố Đô</span>'
  ],
  [
    '<span class="pref-label">Không ăn cay / Giảm ớt</span>',
    '<span class="pref-label" data-i18n="prefMildLabel">Không ăn cay / Giảm ớt</span>'
  ],
  [
    '<span class="pref-desc">Dặn quán không sa tế, không ớt tươi cay nồng</span>',
    '<span class="pref-desc" data-i18n="prefMildDesc">Dặn quán không sa tế, không ớt tươi cay nồng</span>'
  ],
  [
    '<span class="pref-label">Ăn cay chuẩn Huế</span>',
    '<span class="pref-label" data-i18n="prefSpicyLabel">Ăn cay chuẩn Huế</span>'
  ],
  [
    '<span class="pref-desc">Giữ nguyên vị cay nồng đặc sắc của xứ Huế</span>',
    '<span class="pref-desc" data-i18n="prefSpicyDesc">Giữ nguyên vị cay nồng đặc sắc của xứ Huế</span>'
  ],
  [
    '<span class="pref-label">Dị ứng hải sản</span>',
    '<span class="pref-label" data-i18n="prefSeafoodAllergyLabel">Dị ứng hải sản</span>'
  ],
  [
    '<span class="pref-desc">Tránh tôm cá, ruốc mắm và các phụ gia biển</span>',
    '<span class="pref-desc" data-i18n="prefSeafoodAllergyDesc">Tránh tôm cá, ruốc mắm và các phụ gia biển</span>'
  ],
  [
    '<h4 class="pref-section-heading">Đồng hành & Phương tiện Di chuyển</h4>',
    '<h4 class="pref-section-heading" data-i18n="prefPartyHeading">Đồng hành & Phương tiện Di chuyển</h4>'
  ],
  [
    '<p class="pref-section-caption">Phục vụ tính toán thời gian và nhịp độ chuyến đi phù hợp</p>',
    '<p class="pref-section-caption" data-i18n="prefPartyCaption">Phục vụ tính toán thời gian và nhịp độ chuyến đi phù hợp</p>'
  ],
  [
    '<label class="pref-field-label" for="pref-select-party">Nhóm du khách</label>',
    '<label class="pref-field-label" for="pref-select-party" data-i18n="prefPartyLabel">Nhóm du khách</label>'
  ],
  [
    '<option value="Cặp đôi" selected>Cặp đôi (Riêng tư & Lãng mạn)</option>',
    '<option value="Cặp đôi" selected data-i18n="prefPartyCouplesOpt">Cặp đôi (Riêng tư & Lãng mạn)</option>'
  ],
  [
    '<option value="Gia đình">Gia đình (Có người lớn / trẻ nhỏ)</option>',
    '<option value="Gia đình" data-i18n="prefPartyFamilyOpt">Gia đình (Có người lớn / trẻ nhỏ)</option>'
  ],
  [
    '<option value="Nhóm bạn bè">Nhóm bạn bè (Năng động & Khám phá)</option>',
    '<option value="Nhóm bạn bè" data-i18n="prefPartyFriendsOpt">Nhóm bạn bè (Năng động & Khám phá)</option>'
  ],
  [
    '<option value="Một mình">Du lịch một mình (Tự do & Linh hoạt)</option>',
    '<option value="Một mình" data-i18n="prefPartySoloOpt">Du lịch một mình (Tự do & Linh hoạt)</option>'
  ],
  [
    '<label class="pref-field-label" for="pref-select-transport">Phương tiện chính</label>',
    '<label class="pref-field-label" for="pref-select-transport" data-i18n="prefTransportLabel">Phương tiện chính</label>'
  ],
  [
    '<option value="Xe máy" selected>Xe máy (Linh hoạt trong ngõ hẻm)</option>',
    '<option value="Xe máy" selected data-i18n="prefTransMotorbikeOpt">Xe máy (Linh hoạt trong ngõ hẻm)</option>'
  ],
  [
    '<option value="Ô tô / Taxi">Ô tô / Taxi / Grab</option>',
    '<option value="Ô tô / Taxi" data-i18n="prefTransCarOpt">Ô tô / Taxi / Grab</option>'
  ],
  [
    '<option value="Đi bộ / Xe đạp">Đi bộ & Xe đạp dạo mát</option>',
    '<option value="Đi bộ / Xe đạp" data-i18n="prefTransWalkOpt">Đi bộ & Xe đạp dạo mát</option>'
  ],
  [
    '<h4 class="pref-section-heading">Ghi chú Thêm cho Trợ lý AI</h4>',
    '<h4 class="pref-section-heading" data-i18n="prefNotesHeading">Ghi chú Thêm cho Trợ lý AI</h4>'
  ],
  [
    '<p class="pref-section-caption">Bất kỳ yêu cầu hoặc thói quen du lịch cá nhân nào khác</p>',
    '<p class="pref-section-caption" data-i18n="prefNotesCaption">Bất kỳ yêu cầu hoặc thói quen du lịch cá nhân nào khác</p>'
  ],
  [
    'placeholder="Ví dụ: Thích chụp ảnh sáng sớm, muốn không gian yên tĩnh..."></textarea>',
    'placeholder="Ví dụ: Thích chụp ảnh sáng sớm, muốn không gian yên tĩnh..." data-i18n-placeholder="prefNotesPlaceholder"></textarea>'
  ],
  [
    'Lưu Hồ Sơ Thiết Lập\n              </button>',
    '<span data-i18n="prefSaveBtn">Lưu Hồ Sơ Thiết Lập</span>\n              </button>'
  ]
];

let applied = 0;
for (const [target, replacement] of replacements) {
  if (html.includes(target)) {
    html = html.replace(target, replacement);
    applied++;
  } else {
    console.warn('NOT FOUND:', target.substring(0, 60));
  }
}

fs.writeFileSync('frontend/index.html', html, 'utf8');
console.log(`Successfully applied ${applied}/${replacements.length} replacements to index.html`);
