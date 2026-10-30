// =============================================================================
// HUẾ SMART TOURISM — AUTHENTICATION & USER PROFILE CONTROLLER
// Quản lý giao diện Đăng nhập / Đăng ký (Google Gmail, Email/Password), Profile & Lịch trình
// =============================================================================

import {
  loginWithGoogle,
  loginWithEmail,
  registerWithEmail,
  logoutUser,
  onAuthChange,
  isFirebaseConfigured,
  saveFirebaseConfig,
  getFirebaseConfig,
  clearFirebaseConfig,
  loginWithDemoUser,
  getUserItineraries,
  deleteItinerary
} from './firebase.js';

export class AuthController {
  constructor() {
    this.currentUser = null;
    this.authModalMode = 'login'; // 'login' | 'signup'
  }

  init() {
    this.cacheDomElements();
    this.bindEvents();
    this.loadSavedCredentials();
    this.initAuthObserver();
  }

  cacheDomElements() {
    // Header Auth Elements
    this.authContainer = document.getElementById('header-auth-container');
    this.btnHeaderLogin = document.getElementById('btn-header-login');
    this.btnHeaderSignup = document.getElementById('btn-header-signup');
    this.userProfileChip = document.getElementById('header-user-chip');
    this.userAvatarImg = document.getElementById('user-avatar-img');
    this.userAvatarFallback = document.getElementById('user-avatar-fallback');
    this.userNameLabel = document.getElementById('user-name-label');
    this.userDropdownMenu = document.getElementById('user-dropdown-menu');
    this.dropdownUserEmail = document.getElementById('dropdown-user-email');
    this.dropdownUserName = document.getElementById('dropdown-user-name');
    this.dropdownBadgeGoogle = document.getElementById('dropdown-badge-google');
    this.btnOpenSavedTours = document.getElementById('btn-open-saved-tours');
    this.btnOpenFirebaseConfig = document.getElementById('btn-open-firebase-config');
    this.btnHeaderLogout = document.getElementById('btn-header-logout');

    // Auth Modal Elements
    this.authModal = document.getElementById('auth-modal');
    this.btnCloseAuthModal = document.getElementById('btn-close-auth-modal');
    this.tabLogin = document.getElementById('tab-auth-login');
    this.tabSignup = document.getElementById('tab-auth-signup');
    this.authModalTitle = document.getElementById('auth-modal-title');
    this.authModalSubtitle = document.getElementById('auth-modal-subtitle');
    this.btnGoogleAuth = document.getElementById('btn-google-auth');
    this.authForm = document.getElementById('auth-form');
    this.authNameGroup = document.getElementById('auth-name-group');
    this.authInputName = document.getElementById('auth-input-name');
    this.authInputEmail = document.getElementById('auth-input-email');
    this.authInputPassword = document.getElementById('auth-input-password');
    this.btnTogglePassword = document.getElementById('btn-toggle-password');
    this.eyeOpenIcon = this.btnTogglePassword?.querySelector('.eye-open');
    this.eyeClosedIcon = this.btnTogglePassword?.querySelector('.eye-closed');
    this.authOptionsGroup = document.getElementById('auth-options-group');
    this.authRememberMe = document.getElementById('auth-remember-me');
    this.btnAuthSubmit = document.getElementById('btn-auth-submit');
    this.authErrorBanner = document.getElementById('auth-error-banner');
    this.authSwitchText = document.getElementById('auth-switch-text');
    this.btnSwitchAuthMode = document.getElementById('btn-switch-auth-mode');
    this.btnQuickDemoLogin = document.getElementById('btn-quick-demo-login');

    // Application Settings Modal Elements
    this.configModal = document.getElementById('firebase-config-modal');
    this.btnCloseConfigModal = document.getElementById('btn-close-config-modal');

    // Saved Itineraries Modal Elements
    this.savedToursModal = document.getElementById('saved-itineraries-modal');
    this.btnCloseSavedToursModal = document.getElementById('btn-close-saved-tours-modal');
    this.savedToursList = document.getElementById('saved-tours-list');
  }

  bindEvents() {
    // Mở Auth Modal
    this.btnHeaderLogin?.addEventListener('click', () => this.openAuthModal('login'));
    this.btnHeaderSignup?.addEventListener('click', () => this.openAuthModal('signup'));

    // Đóng Auth Modal
    this.btnCloseAuthModal?.addEventListener('click', () => this.closeAuthModal());
    this.authModal?.addEventListener('click', (e) => {
      if (e.target === this.authModal) this.closeAuthModal();
    });

    // Chuyển đổi tab Đăng nhập / Đăng ký
    this.tabLogin?.addEventListener('click', () => this.setAuthMode('login'));
    this.tabSignup?.addEventListener('click', () => this.setAuthMode('signup'));
    this.btnSwitchAuthMode?.addEventListener('click', () => {
      this.setAuthMode(this.authModalMode === 'login' ? 'signup' : 'login');
    });

    // Toggle Dropdown Menu
    this.userProfileChip?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.userDropdownMenu?.classList.toggle('active');
    });

    // Đóng dropdown khi click ra ngoài
    document.addEventListener('click', () => {
      this.userDropdownMenu?.classList.remove('active');
    });

    this.userDropdownMenu?.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    // Đăng xuất
    this.btnHeaderLogout?.addEventListener('click', async () => {
      try {
        await logoutUser();
        this.userDropdownMenu?.classList.remove('active');
        this.showToast('Đã đăng xuất thành công.');
      } catch (err) {
        console.error('Lỗi đăng xuất:', err);
      }
    });

    // Đăng nhập Google
    this.btnGoogleAuth?.addEventListener('click', () => this.handleGoogleLogin());

    // Toggle hiện / ẩn mật khẩu
    this.btnTogglePassword?.addEventListener('click', () => {
      const isPassword = this.authInputPassword?.type === 'password';
      if (this.authInputPassword) {
        this.authInputPassword.type = isPassword ? 'text' : 'password';
      }
      this.eyeOpenIcon?.classList.toggle('hidden', isPassword);
      this.eyeClosedIcon?.classList.toggle('hidden', !isPassword);
      this.btnTogglePassword?.setAttribute(
        'title',
        isPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'
      );
      this.btnTogglePassword?.setAttribute(
        'aria-label',
        isPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'
      );
    });

    // Checkbox Ghi nhớ mật khẩu: tự động xóa bộ nhớ nếu người dùng chủ động bỏ chọn
    this.authRememberMe?.addEventListener('change', () => {
      if (!this.authRememberMe.checked) {
        this.clearSavedCredentials();
      }
    });

    // Submit form Email/Password
    this.authForm?.addEventListener('submit', (e) => this.handleEmailFormSubmit(e));

    // Nút dùng thử nhanh Demo Mode
    this.btnQuickDemoLogin?.addEventListener('click', () => {
      loginWithDemoUser();
      this.closeAuthModal();
      this.showToast('Đã kích hoạt chế độ Trải nghiệm Khách (Demo).');
    });

    // Cấu hình Firebase Modal
    this.btnOpenFirebaseConfig?.addEventListener('click', () => {
      this.userDropdownMenu?.classList.remove('active');
      this.openConfigModal();
    });
    this.btnCloseConfigModal?.addEventListener('click', () => this.closeConfigModal());
    this.configModal?.addEventListener('click', (e) => {
      if (e.target === this.configModal) this.closeConfigModal();
    });


    // Modal Lịch trình đã lưu
    this.btnOpenSavedTours?.addEventListener('click', () => {
      this.userDropdownMenu?.classList.remove('active');
      this.openSavedToursModal();
    });
    this.btnCloseSavedToursModal?.addEventListener('click', () => this.closeSavedToursModal());
    this.savedToursModal?.addEventListener('click', (e) => {
      if (e.target === this.savedToursModal) this.closeSavedToursModal();
    });

    window.addEventListener('tour-saved', () => {
      if (this.savedToursModal?.classList.contains('active')) {
        this.renderSavedTours();
      }
    });
  }

  initAuthObserver() {
    onAuthChange((user) => {
      this.currentUser = user;
      this.updateHeaderUI(user);
    });
  }

  updateHeaderUI(user) {
    if (user) {
      // Đang đăng nhập
      this.btnHeaderLogin?.classList.add('hidden');
      this.btnHeaderSignup?.classList.add('hidden');
      this.userProfileChip?.classList.remove('hidden');

      const displayName = user.displayName || user.email?.split('@')[0] || 'Du Khách';
      const initial = displayName.charAt(0).toUpperCase();

      if (this.userNameLabel) {
        this.userNameLabel.textContent = displayName;
      }
      if (this.dropdownUserName) {
        this.dropdownUserName.textContent = displayName;
      }
      if (this.dropdownUserEmail) {
        this.dropdownUserEmail.textContent = user.email || 'user@example.com';
      }

      if (user.photoURL && this.userAvatarImg) {
        this.userAvatarImg.src = user.photoURL;
        this.userAvatarImg.classList.remove('hidden');
        this.userAvatarFallback?.classList.add('hidden');
      } else {
        if (this.userAvatarImg) this.userAvatarImg.classList.add('hidden');
        if (this.userAvatarFallback) {
          this.userAvatarFallback.textContent = initial;
          this.userAvatarFallback.classList.remove('hidden');
        }
      }

      // Check badge Google
      const isGoogle = user.providerData?.some(p => p.providerId === 'google.com');
      if (this.dropdownBadgeGoogle) {
        this.dropdownBadgeGoogle.classList.toggle('hidden', !isGoogle && !user.isDemo);
        if (user.isDemo) {
          this.dropdownBadgeGoogle.textContent = 'Bản Thử Nghiệm';
        } else {
          this.dropdownBadgeGoogle.textContent = 'Google Account';
        }
      }
    } else {
      // Chưa đăng nhập
      this.btnHeaderLogin?.classList.remove('hidden');
      this.btnHeaderSignup?.classList.remove('hidden');
      this.userProfileChip?.classList.add('hidden');
      this.userDropdownMenu?.classList.remove('active');
    }
  }

  openAuthModal(mode = 'login') {
    this.setAuthMode(mode);
    this.clearAuthError();
    if (mode === 'login') {
      this.loadSavedCredentials();
    }
    this.authModal?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  closeAuthModal() {
    this.authModal?.classList.remove('active');
    document.body.style.overflow = '';
    this.clearAuthError();
    this.resetPasswordVisibility();
  }

  resetPasswordVisibility() {
    if (this.authInputPassword) {
      this.authInputPassword.type = 'password';
    }
    this.eyeOpenIcon?.classList.remove('hidden');
    this.eyeClosedIcon?.classList.add('hidden');
    this.btnTogglePassword?.setAttribute('title', 'Hiện mật khẩu');
    this.btnTogglePassword?.setAttribute('aria-label', 'Hiện mật khẩu');
  }

  loadSavedCredentials(force = false) {
    try {
      // Dọn dẹp khóa cũ nếu có chứa dữ liệu nhạy cảm
      if (localStorage.getItem('hue_remembered_credentials')) {
        localStorage.removeItem('hue_remembered_credentials');
      }
      const rememberedEmail = localStorage.getItem('hue_remembered_email');
      if (rememberedEmail) {
        if (this.authRememberMe) {
          this.authRememberMe.checked = true;
        }
        if (this.authInputEmail && (!this.authInputEmail.value || force)) {
          this.authInputEmail.value = rememberedEmail;
        }
        // Tuyệt đối không nạp/lưu mật khẩu trong localStorage theo chuẩn an toàn OWASP;
        // Trình duyệt tự động điền mật khẩu qua thuộc tính autocomplete="current-password"
      }
    } catch (e) {
      console.warn('Không thể nạp thông tin email đã ghi nhớ:', e);
    }
  }

  saveSavedCredentials(email) {
    try {
      // Chỉ lưu địa chỉ Email đã ghi nhớ, không lưu mật khẩu trong bộ nhớ cục bộ
      if (email) {
        localStorage.setItem('hue_remembered_email', email);
      }
    } catch (e) {
      console.warn('Không thể ghi nhớ email:', e);
    }
  }

  clearSavedCredentials() {
    try {
      localStorage.removeItem('hue_remembered_email');
      localStorage.removeItem('hue_remembered_credentials');
    } catch (e) {
      console.warn('Không thể xóa email ghi nhớ:', e);
    }
  }

  setAuthMode(mode) {
    this.authModalMode = mode;
    this.clearAuthError();
    this.resetPasswordVisibility();

    if (mode === 'login') {
      this.tabLogin?.classList.add('active');
      this.tabSignup?.classList.remove('active');
      this.authNameGroup?.classList.add('hidden');
      this.authOptionsGroup?.classList.remove('hidden');
      if (this.authModalTitle) this.authModalTitle.textContent = 'Đăng nhập';
      if (this.authModalSubtitle) this.authModalSubtitle.textContent = 'Chào mừng bạn đến với Cố đô Huế Travel';
      if (this.btnAuthSubmit) this.btnAuthSubmit.textContent = 'Đăng nhập';
      if (this.authSwitchText) this.authSwitchText.textContent = 'Chưa có tài khoản?';
      if (this.btnSwitchAuthMode) this.btnSwitchAuthMode.textContent = 'Đăng ký ngay';
      this.loadSavedCredentials();
    } else {
      this.tabSignup?.classList.add('active');
      this.tabLogin?.classList.remove('active');
      this.authNameGroup?.classList.remove('hidden');
      this.authOptionsGroup?.classList.add('hidden');
      if (this.authModalTitle) this.authModalTitle.textContent = 'Tạo tài khoản';
      if (this.authModalSubtitle) this.authModalSubtitle.textContent = 'Đăng ký để lưu giữ lịch trình và cá nhân hóa trải nghiệm';
      if (this.btnAuthSubmit) this.btnAuthSubmit.textContent = 'Tạo tài khoản';
      if (this.authSwitchText) this.authSwitchText.textContent = 'Đã có tài khoản?';
      if (this.btnSwitchAuthMode) this.btnSwitchAuthMode.textContent = 'Đăng nhập ngay';
    }
  }

  showAuthError(message) {
    if (this.authErrorBanner) {
      this.authErrorBanner.textContent = message;
      this.authErrorBanner.classList.remove('hidden');
      this.authErrorBanner.style.display = 'block';
    }
  }

  clearAuthError() {
    if (this.authErrorBanner) {
      this.authErrorBanner.textContent = '';
      this.authErrorBanner.classList.add('hidden');
      this.authErrorBanner.style.display = 'none';
    }
  }

  async handleGoogleLogin() {
    this.clearAuthError();
    if (!isFirebaseConfigured()) {
      // Nếu chưa có config Firebase thật, gợi ý người dùng
      this.showAuthError(
        '⚠️ Chưa tìm thấy cấu hình Firebase API của bạn. Bạn có thể nhấn nút "Trải nghiệm nhanh (Demo Mode)" bên dưới để dùng ngay, hoặc mở "Cài đặt kết nối Firebase" để nhập API Key.'
      );
      return;
    }

    try {
      this.btnGoogleAuth?.setAttribute('disabled', 'true');
      this.btnGoogleAuth.style.opacity = '0.6';
      await loginWithGoogle();
      this.closeAuthModal();
      this.showToast('Đăng nhập thành công bằng tài khoản Google!');
    } catch (err) {
      this.showAuthError(err.message || 'Không thể đăng nhập bằng Google.');
    } finally {
      this.btnGoogleAuth?.removeAttribute('disabled');
      this.btnGoogleAuth.style.opacity = '1';
    }
  }

  async handleEmailFormSubmit(e) {
    e.preventDefault();
    this.clearAuthError();

    const email = this.authInputEmail?.value?.trim();
    const password = this.authInputPassword?.value;
    const name = this.authInputName?.value?.trim();

    if (!email || !password) {
      this.showAuthError('Vui lòng điền đầy đủ Email và Mật khẩu.');
      return;
    }

    if (!isFirebaseConfigured()) {
      this.showAuthError(
        '⚠️ Ứng dụng chưa được nạp khóa Firebase API. Bạn có thể dùng nút "Trải nghiệm nhanh (Demo Mode)" ngay bên dưới để thử nghiệm đầy đủ tính năng.'
      );
      return;
    }

    try {
      this.btnAuthSubmit?.setAttribute('disabled', 'true');
      this.btnAuthSubmit.textContent = 'Đang xử lý...';

      if (this.authModalMode === 'login') {
        await loginWithEmail(email, password);
        if (this.authRememberMe?.checked) {
          this.saveSavedCredentials(email);
        } else {
          this.clearSavedCredentials();
        }
        this.closeAuthModal();
        this.showToast(`Chào mừng ${email} đã quay trở lại!`);
      } else {
        await registerWithEmail(email, password, name);
        this.closeAuthModal();
        this.showToast(`Chúc mừng ${name || email} đã đăng ký tài khoản thành công!`);
      }
    } catch (err) {
      this.showAuthError(err.message || 'Lỗi thao tác tài khoản.');
    } finally {
      this.btnAuthSubmit?.removeAttribute('disabled');
      this.btnAuthSubmit.textContent = this.authModalMode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản';
    }
  }

  // Modal Cài đặt ứng dụng & Cấu hình Firebase
  openConfigModal() {
    // Luôn đưa về Tab 1 (Trải nghiệm chung) thân thiện người dùng khi mở modal
    const defaultTab = document.getElementById('tab-settings-general');
    if (defaultTab) {
      defaultTab.click();
    }
    this.configModal?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  closeConfigModal() {
    this.configModal?.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Modal Lịch trình đã lưu
  async openSavedToursModal() {
    if (!this.currentUser) {
      this.openAuthModal('login');
      return;
    }

    this.savedToursModal?.classList.add('active');
    document.body.style.overflow = 'hidden';
    await this.renderSavedTours();
  }

  closeSavedToursModal() {
    this.savedToursModal?.classList.remove('active');
    document.body.style.overflow = '';
  }

  async renderSavedTours() {
    if (!this.savedToursList) return;
    this.savedToursList.innerHTML = '<div class="saved-tours-loading">Đang tải các lịch trình đã lưu từ Cloud...</div>';

    const items = await getUserItineraries(this.currentUser.uid);
    if (!items || items.length === 0) {
      this.savedToursList.innerHTML = `
        <div class="saved-tours-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#A1A1AA" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <h4>Chưa có lịch trình nào được lưu</h4>
          <p>Khi trợ lý AI tạo cho bạn một kế hoạch du lịch Huế, hãy bấm nút "Lưu vào tài khoản" để xem lại bất kỳ lúc nào.</p>
        </div>
      `;
      return;
    }

    this.savedToursList.innerHTML = '';
    items.forEach(tour => {
      const card = document.createElement('div');
      card.className = 'saved-tour-card';
      
      const dateStr = tour.savedAt ? new Date(tour.savedAt).toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
      }) : 'Gần đây';

      card.innerHTML = `
        <div class="saved-tour-header">
          <div class="saved-tour-title-group">
            <span class="saved-tour-tag">${tour.days} Ngày</span>
            <h4 class="saved-tour-title">${tour.title}</h4>
          </div>
          <button type="button" class="btn-delete-saved-tour" title="Xóa lịch trình này" data-id="${tour.id}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
        <div class="saved-tour-meta">
          <span>👥 Đối tượng: ${tour.tripType}</span>
          <span>📍 Xuất phát: ${tour.userLocationName}</span>
          <span>🏛️ Số điểm: ${tour.stopsCount || tour.items?.length || 0} điểm</span>
          <span>⏱️ Lưu ngày: ${dateStr}</span>
        </div>
        <div class="saved-tour-actions">
          <button type="button" class="btn-load-saved-tour" data-id="${tour.id}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            <span>Mở lại trên Bản đồ & Chat</span>
          </button>
          <button type="button" class="btn-budget-saved-tour" data-id="${tour.id}" title="Dự toán ngân sách cho lịch trình này">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"></rect>
              <line x1="2" y1="10" x2="22" y2="10"></line>
            </svg>
            <span>Dự toán chi phí</span>
          </button>
        </div>
      `;

      // Nút xóa
      card.querySelector('.btn-delete-saved-tour')?.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (confirm(`Bạn có chắc muốn xóa lịch trình "${tour.title}"?`)) {
          await deleteItinerary(this.currentUser.uid, tour.id);
          this.renderSavedTours();
          this.showToast('Đã xóa lịch trình.');
        }
      });

      // Nút tải lại tour
      card.querySelector('.btn-load-saved-tour')?.addEventListener('click', () => {
        this.closeSavedToursModal();
        window.dispatchEvent(new CustomEvent('load-saved-tour', { detail: tour }));
        this.showToast(`Đã tải lại lịch trình "${tour.title}" lên bản đồ!`);
      });

      // Nút dự toán chi phí tour đã lưu
      card.querySelector('.btn-budget-saved-tour')?.addEventListener('click', () => {
        if (window.budgetEstimator) {
          const rawPlan = tour.rawResult?.itinerary_data || tour.rawResult || { days: tour.days, items: tour.items };
          window.budgetEstimator.openModal(rawPlan, tour.title);
        }
      });

      this.savedToursList.appendChild(card);
    });
  }

  showToast(message) {
    let toast = document.getElementById('auth-toast-notification');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'auth-toast-notification';
      toast.className = 'auth-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('visible');
    setTimeout(() => {
      toast.classList.remove('visible');
    }, 3500);
  }
}
