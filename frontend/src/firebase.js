// =============================================================================
// HUẾ SMART TOURISM — FIREBASE AUTHENTICATION & FIRESTORE DATABASE SERVICE
// Hỗ trợ đăng nhập bằng Gmail (Google Sign-In), Email/Password & Lưu trữ Firestore
// =============================================================================

import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  updateProfile,
  signOut,
  onAuthStateChanged
} from 'firebase/auth';
import {
  getFirestore,
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  deleteDoc,
  serverTimestamp,
  query,
  orderBy
} from 'firebase/firestore';

const STORAGE_KEY = 'hue_smart_tourism_firebase_config';
const DEMO_USER_KEY = 'hue_smart_tourism_demo_user';
const LOCAL_ITINERARIES_KEY = 'hue_smart_tourism_local_itineraries';

// Đọc cấu hình từ localStorage hoặc biến môi trường Vite (.env)
export function getFirebaseConfig() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (err) {
    console.warn('Không thể đọc cấu hình Firebase từ localStorage:', err);
  }

  // Fallback sang biến môi trường nếu có
  if (import.meta.env.VITE_FIREBASE_API_KEY && import.meta.env.VITE_FIREBASE_PROJECT_ID) {
    return {
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || `${import.meta.env.VITE_FIREBASE_PROJECT_ID}.firebaseapp.com`,
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
      storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || `${import.meta.env.VITE_FIREBASE_PROJECT_ID}.appspot.com`,
      messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
      appId: import.meta.env.VITE_FIREBASE_APP_ID || ''
    };
  }

  return null;
}

export function saveFirebaseConfig(config) {
  if (!config || !config.apiKey || !config.projectId) {
    throw new Error('Cấu hình Firebase phải bao gồm tối thiểu apiKey và projectId.');
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  // Tải lại trang để khởi tạo lại Firebase với cấu hình mới
  window.location.reload();
}

export function clearFirebaseConfig() {
  localStorage.removeItem(STORAGE_KEY);
  window.location.reload();
}

export function isFirebaseConfigured() {
  const cfg = getFirebaseConfig();
  return Boolean(cfg && cfg.apiKey && cfg.projectId && cfg.apiKey !== 'YOUR_API_KEY');
}

// Khởi tạo Firebase App nếu có cấu hình hợp lệ
let firebaseApp = null;
let firebaseAuth = null;
let firestoreDb = null;

try {
  const config = getFirebaseConfig();
  if (config && config.apiKey && config.projectId) {
    if (getApps().length === 0) {
      firebaseApp = initializeApp(config);
    } else {
      firebaseApp = getApp();
    }
    firebaseAuth = getAuth(firebaseApp);
    firestoreDb = getFirestore(firebaseApp);
    console.log('🔥 Firebase đã được khởi tạo thành công với project:', config.projectId);
  }
} catch (err) {
  console.warn('Chưa khởi tạo Firebase SDK (chờ cấu hình của người dùng):', err);
}

// Danh sách lắng nghe thay đổi trạng thái đăng nhập
const authListeners = [];

function notifyAuthListeners(user) {
  authListeners.forEach(cb => {
    try {
      cb(user);
    } catch (e) {
      console.error('Lỗi trong Auth listener callback:', e);
    }
  });
}

// Đăng ký observer trạng thái đăng nhập
export function onAuthChange(callback) {
  authListeners.push(callback);

  if (firebaseAuth) {
    onAuthStateChanged(firebaseAuth, async (user) => {
      if (user) {
        // Đồng bộ/tạo profile trên Firestore
        try {
          if (firestoreDb) {
            const userRef = doc(firestoreDb, 'users', user.uid);
            await setDoc(userRef, {
              uid: user.uid,
              displayName: user.displayName || user.email.split('@')[0],
              email: user.email,
              photoURL: user.photoURL || '',
              lastLoginAt: serverTimestamp()
            }, { merge: true });
          }
        } catch (e) {
          console.warn('Lỗi cập nhật profile người dùng lên Firestore:', e);
        }
        callback(user);
      } else {
        // Kiểm tra xem có người dùng Demo không
        const demoUser = getDemoUser();
        callback(demoUser);
      }
    });
  } else {
    // Không có Firebase Auth SDK, dùng Demo User nếu có
    const demoUser = getDemoUser();
    callback(demoUser);
  }
}

// =============================================================================
// CÁC HÀM XÁC THỰC (AUTHENTICATION API)
// =============================================================================

/**
 * Đăng nhập bằng Google Account (Gmail) qua Popup
 */
export async function loginWithGoogle() {
  if (!firebaseAuth) {
    throw new Error('NO_CONFIG');
  }

  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  
  try {
    const result = await signInWithPopup(firebaseAuth, provider);
    const user = result.user;
    notifyAuthListeners(user);
    return user;
  } catch (error) {
    console.error('Lỗi đăng nhập Google Popup:', error);
    if (error.code === 'auth/unauthorized-domain') {
      throw new Error(
        'Tên miền hiện tại chưa được cấp phép trong Firebase Console. ' +
        'Vui lòng vào Firebase Console > Authentication > Settings > Authorized Domains và thêm tên miền này (ví dụ: localhost).'
      );
    } else if (error.code === 'auth/popup-closed-by-user') {
      throw new Error('Cửa sổ đăng nhập đã bị đóng trước khi hoàn tất.');
    } else if (error.code === 'auth/network-request-failed') {
      throw new Error('Lỗi kết nối mạng khi liên lạc với máy chủ Google.');
    }
    throw error;
  }
}

/**
 * Đăng nhập bằng Email & Mật khẩu
 */
export async function loginWithEmail(email, password) {
  if (!firebaseAuth) {
    throw new Error('NO_CONFIG');
  }

  try {
    const userCred = await signInWithEmailAndPassword(firebaseAuth, email, password);
    notifyAuthListeners(userCred.user);
    return userCred.user;
  } catch (error) {
    console.error('Lỗi đăng nhập Email/Password:', error);
    if (error.code === 'auth/invalid-credential' || error.code === 'auth/wrong-password' || error.code === 'auth/user-not-found') {
      throw new Error('Email hoặc mật khẩu không chính xác.');
    } else if (error.code === 'auth/invalid-email') {
      throw new Error('Định dạng email không hợp lệ.');
    }
    throw error;
  }
}

/**
 * Đăng ký tài khoản mới bằng Email & Mật khẩu
 */
export async function registerWithEmail(email, password, displayName) {
  if (!firebaseAuth) {
    throw new Error('NO_CONFIG');
  }

  try {
    const userCred = await createUserWithEmailAndPassword(firebaseAuth, email, password);
    const user = userCred.user;
    if (displayName) {
      await updateProfile(user, { displayName });
    }
    notifyAuthListeners(user);
    return user;
  } catch (error) {
    console.error('Lỗi đăng ký tài khoản:', error);
    if (error.code === 'auth/email-already-in-use') {
      throw new Error('Email này đã được sử dụng bởi một tài khoản khác.');
    } else if (error.code === 'auth/weak-password') {
      throw new Error('Mật khẩu quá yếu (cần tối thiểu 6 ký tự).');
    }
    throw error;
  }
}

/**
 * Đăng xuất người dùng
 */
export async function logoutUser() {
  // Xóa demo user nếu đang dùng
  localStorage.removeItem(DEMO_USER_KEY);

  if (firebaseAuth) {
    await signOut(firebaseAuth);
  }
  notifyAuthListeners(null);
}

// =============================================================================
// CHẾ ĐỘ DEMO USER (DÀNH CHO KIỂM THỬ TRƯỚC KHI CẤU HÌNH FIREBASE)
// =============================================================================

export function loginWithDemoUser(email = 'dukhach.hue@gmail.com', name = 'Du Khách Cố Đô') {
  const demoUser = {
    uid: 'demo_user_hue_2026',
    email: email,
    displayName: name,
    photoURL: '',
    isDemo: true
  };
  localStorage.setItem(DEMO_USER_KEY, JSON.stringify(demoUser));
  notifyAuthListeners(demoUser);
  return demoUser;
}

export function getDemoUser() {
  try {
    const raw = localStorage.getItem(DEMO_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

// =============================================================================
// QUẢN LÝ LỊCH TRÌNH NGƯỜI DÙNG (FIRESTORE & LOCAL FALLBACK)
// =============================================================================

/**
 * Lưu một tour/lịch trình đã tạo vào tài khoản của người dùng
 */
export async function saveItinerary(userId, itineraryData) {
  if (!userId) {
    throw new Error('Bạn cần đăng nhập để lưu lịch trình.');
  }

  const payload = {
    title: itineraryData.title || `Lịch trình Huế ${itineraryData.days || 1} ngày`,
    days: itineraryData.days || 1,
    tripType: itineraryData.tripType || 'Gia đình',
    userLocationName: itineraryData.userLocationName || 'Thành phố Huế',
    items: itineraryData.items || [],
    stopsCount: itineraryData.stopsCount || 0,
    totalKm: itineraryData.totalKm || 0,
    savedAt: new Date().toISOString()
  };

  // Nếu có Firestore
  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      const docRef = doc(collection(firestoreDb, 'users', userId, 'itineraries'));
      await setDoc(docRef, {
        ...payload,
        createdAt: serverTimestamp()
      });
      return { id: docRef.id, ...payload };
    } catch (e) {
      console.warn('Không thể ghi Firestore, lưu fallback vào LocalStorage:', e);
    }
  }

  // Fallback lưu LocalStorage
  const list = getLocalItineraries(userId);
  const newItem = { id: 'itinerary_' + Date.now(), ...payload };
  list.unshift(newItem);
  localStorage.setItem(`${LOCAL_ITINERARIES_KEY}_${userId}`, JSON.stringify(list));
  return newItem;
}

/**
 * Lấy danh sách lịch trình đã lưu của người dùng
 */
export async function getUserItineraries(userId) {
  if (!userId) return [];

  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      const q = query(
        collection(firestoreDb, 'users', userId, 'itineraries'),
        orderBy('createdAt', 'desc')
      );
      const snapshot = await getDocs(q);
      const results = [];
      snapshot.forEach(docSnap => {
        results.push({ id: docSnap.id, ...docSnap.data() });
      });
      return results;
    } catch (e) {
      console.warn('Lỗi đọc Firestore, lấy từ LocalStorage:', e);
    }
  }

  return getLocalItineraries(userId);
}

/**
 * Xóa một lịch trình đã lưu
 */
export async function deleteItinerary(userId, itineraryId) {
  if (!userId || !itineraryId) return;

  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      const docRef = doc(firestoreDb, 'users', userId, 'itineraries', itineraryId);
      await deleteDoc(docRef);
    } catch (e) {
      console.warn('Lỗi xóa trên Firestore:', e);
    }
  }

  // Xóa cả trong LocalStorage
  const list = getLocalItineraries(userId).filter(item => item.id !== itineraryId);
  localStorage.setItem(`${LOCAL_ITINERARIES_KEY}_${userId}`, JSON.stringify(list));
}

function getLocalItineraries(userId) {
  try {
    const raw = localStorage.getItem(`${LOCAL_ITINERARIES_KEY}_${userId}`);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
