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
      appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
      measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || ''
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

export function loginWithDemoUser(email = 'dukhach.hue@gmail.com', name = 'Du khách Cố đô') {
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

/**
 * Lấy đối tượng người dùng hiện tại đang đăng nhập
 */
export function getCurrentUser() {
  if (firebaseAuth && firebaseAuth.currentUser) {
    return firebaseAuth.currentUser;
  }
  return getDemoUser();
}

// =============================================================================
// QUẢN LÝ LỊCH TRÌNH NGƯỜI DÙNG (FIRESTORE & LOCAL FALLBACK)
// =============================================================================

/**
 * Lưu một tour/lịch trình đã tạo vào tài khoản của người dùng (Offline-First & Cloud-Synced)
 */
export async function saveItinerary(userId, itineraryData) {
  if (!userId) {
    throw new Error('Bạn cần đăng nhập để lưu lịch trình.');
  }

  const itineraryId = itineraryData.id || `itinerary_${Date.now()}`;
  const rawPayload = {
    id: itineraryId,
    title: itineraryData.title || `Lịch trình Huế ${itineraryData.days || 1} ngày`,
    days: itineraryData.days || 1,
    tripType: itineraryData.tripType || 'Gia đình',
    userLocationName: itineraryData.userLocationName || 'Thành phố Huế',
    items: itineraryData.items || [],
    stopsCount: itineraryData.stopsCount || 0,
    totalKm: itineraryData.totalKm || 0,
    rawResult: itineraryData.rawResult || null,
    savedAt: new Date().toISOString()
  };

  // Làm sạch dữ liệu JSON, loại bỏ hoàn toàn các trường undefined gây lỗi Firestore
  const cleanPayload = JSON.parse(JSON.stringify(rawPayload));

  // 1. LUÔN LƯU VÀO BỘ NHỚ LOCALSTORAGE TRƯỚC (Đảm bảo tức thì 100%, không bao giờ mất)
  const localList = getLocalItineraries(userId);
  const existingIdx = localList.findIndex(item => item.id === itineraryId);
  if (existingIdx >= 0) {
    localList[existingIdx] = cleanPayload;
  } else {
    localList.unshift(cleanPayload);
  }
  localStorage.setItem(`${LOCAL_ITINERARIES_KEY}_${userId}`, JSON.stringify(localList));
  localStorage.setItem(LOCAL_ITINERARIES_KEY, JSON.stringify(localList)); // Bản sao lưu chung

  // 2. ĐỒNG BỘ LÊN CLOUD FIRESTORE NẾU CÓ KẾT NỐI
  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      const docRef = doc(firestoreDb, 'users', userId, 'itineraries', itineraryId);
      await setDoc(docRef, {
        ...cleanPayload,
        createdAt: serverTimestamp()
      }, { merge: true });
    } catch (e) {
      console.warn('Không thể ghi Firestore (lưu an toàn trong LocalStorage):', e);
    }
  }

  // Phát tín hiệu toàn cục để các modal UI tự động cập nhật
  try {
    window.dispatchEvent(new CustomEvent('tour-saved', { detail: cleanPayload }));
  } catch {}

  return cleanPayload;
}

/**
 * Lấy danh sách lịch trình đã lưu của người dùng (Hợp nhất Cloud Firestore & Local Cache)
 */
export async function getUserItineraries(userId) {
  if (!userId) return [];

  // 1. Lấy dữ liệu từ LocalStorage
  let localItems = getLocalItineraries(userId);

  // Nếu local của user này đang trống, kiểm tra bản sao lưu hoặc demo
  if (localItems.length === 0) {
    const fallbackList = getLocalItineraries('demo_user_hue_2026');
    if (fallbackList.length > 0) {
      localItems = fallbackList;
    } else {
      try {
        const generic = localStorage.getItem(LOCAL_ITINERARIES_KEY);
        if (generic) localItems = JSON.parse(generic);
      } catch {}
    }
  }

  // 2. Lấy dữ liệu từ Cloud Firestore (nếu có tài khoản thật)
  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      // Truy vấn collection trực tiếp (không bắt buộc orderBy để tránh lỗi thiếu index hay thiếu createdAt)
      const colRef = collection(firestoreDb, 'users', userId, 'itineraries');
      const snapshot = await getDocs(colRef);
      const cloudResults = [];
      snapshot.forEach(docSnap => {
        cloudResults.push({ id: docSnap.id, ...docSnap.data() });
      });

      if (cloudResults.length > 0) {
        // Hợp nhất dữ liệu Cloud và Local để không bị sót bất kỳ tour nào
        const mergedMap = new Map();
        cloudResults.forEach(item => mergedMap.set(item.id || item.savedAt, item));
        localItems.forEach(item => {
          if (!mergedMap.has(item.id) && !mergedMap.has(item.savedAt)) {
            mergedMap.set(item.id, item);
          }
        });

        const mergedList = Array.from(mergedMap.values());
        mergedList.sort((a, b) => new Date(b.savedAt || 0) - new Date(a.savedAt || 0));

        // Cập nhật lại cache local
        localStorage.setItem(`${LOCAL_ITINERARIES_KEY}_${userId}`, JSON.stringify(mergedList));
        return mergedList;
      }
    } catch (e) {
      console.warn('Lỗi đọc Firestore, sử dụng bộ nhớ cục bộ LocalStorage:', e);
    }
  }

  // Sắp xếp tour theo thời gian mới nhất
  localItems.sort((a, b) => new Date(b.savedAt || 0) - new Date(a.savedAt || 0));
  return localItems;
}

/**
 * Xóa một lịch trình đã lưu
 */
export async function deleteItinerary(userId, itineraryId) {
  if (!userId || !itineraryId) return;

  // 1. Xóa trên Cloud Firestore
  if (firestoreDb && !userId.startsWith('demo_')) {
    try {
      const docRef = doc(firestoreDb, 'users', userId, 'itineraries', itineraryId);
      await deleteDoc(docRef);
    } catch (e) {
      console.warn('Lỗi xóa trên Firestore:', e);
    }
  }

  // 2. Xóa trong LocalStorage
  const list = getLocalItineraries(userId).filter(item => item.id !== itineraryId);
  localStorage.setItem(`${LOCAL_ITINERARIES_KEY}_${userId}`, JSON.stringify(list));
  localStorage.setItem(LOCAL_ITINERARIES_KEY, JSON.stringify(list));
}

function getLocalItineraries(userId) {
  try {
    const raw = localStorage.getItem(`${LOCAL_ITINERARIES_KEY}_${userId}`);
    if (raw) return JSON.parse(raw);
    const genericRaw = localStorage.getItem(LOCAL_ITINERARIES_KEY);
    if (genericRaw) return JSON.parse(genericRaw);
    return [];
  } catch {
    return [];
  }
}

// =============================================================================
// QUẢN LÝ PHIÊN TRÒ CHUYỆN & LỊCH SỬ CHAT (CHAT SESSIONS ON FIRESTORE)
// =============================================================================
const LOCAL_CHAT_SESSIONS_KEY = 'hue_smart_tourism_chat_sessions';

/**
 * Lưu hoặc cập nhật một phiên chat (bao gồm tin nhắn & thẻ tour)
 */
export async function saveChatSession(userId, sessionData) {
  if (!sessionData || !sessionData.id) return null;

  const effectiveUserId = userId || 'guest';
  const payload = {
    id: sessionData.id,
    title: sessionData.title || 'Cuộc trò chuyện mới',
    messages: sessionData.messages || [],
    createdAt: sessionData.createdAt || new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  // 1. Lưu lên Cloud Firestore nếu người dùng đã đăng nhập
  if (firestoreDb && effectiveUserId !== 'guest' && !effectiveUserId.startsWith('demo_')) {
    try {
      const docRef = doc(firestoreDb, 'users', effectiveUserId, 'chat_sessions', sessionData.id);
      await setDoc(docRef, {
        ...payload,
        updatedAt: serverTimestamp()
      }, { merge: true });
    } catch (e) {
      console.warn('Lỗi ghi Chat Session lên Firestore, lưu fallback vào LocalStorage:', e);
    }
  }

  // 2. Lưu bộ nhớ đệm LocalStorage (đảm bảo phản hồi nhanh & offline)
  const sessions = getLocalChatSessions(effectiveUserId);
  const existingIdx = sessions.findIndex(s => s.id === sessionData.id);
  if (existingIdx >= 0) {
    sessions[existingIdx] = { ...sessions[existingIdx], ...payload };
  } else {
    sessions.unshift(payload);
  }
  localStorage.setItem(`${LOCAL_CHAT_SESSIONS_KEY}_${effectiveUserId}`, JSON.stringify(sessions));

  return payload;
}

/**
 * Lấy toàn bộ danh sách các phiên chat của người dùng (sắp xếp theo thời gian mới nhất)
 */
export async function getUserChatSessions(userId) {
  const effectiveUserId = userId || 'guest';

  if (firestoreDb && effectiveUserId !== 'guest' && !effectiveUserId.startsWith('demo_')) {
    try {
      const q = query(
        collection(firestoreDb, 'users', effectiveUserId, 'chat_sessions'),
        orderBy('updatedAt', 'desc')
      );
      const snapshot = await getDocs(q);
      const cloudSessions = [];
      snapshot.forEach(docSnap => {
        const data = docSnap.data();
        let formattedUpdatedAt = new Date().toISOString();
        if (data.updatedAt) {
          if (typeof data.updatedAt.toDate === 'function') {
            formattedUpdatedAt = data.updatedAt.toDate().toISOString();
          } else if (data.updatedAt.seconds) {
            formattedUpdatedAt = new Date(data.updatedAt.seconds * 1000).toISOString();
          } else if (typeof data.updatedAt === 'string') {
            formattedUpdatedAt = data.updatedAt;
          }
        }
        cloudSessions.push({ 
          id: docSnap.id, 
          ...data,
          updatedAt: formattedUpdatedAt
        });
      });

      if (cloudSessions.length > 0) {
        // Cập nhật lại cache local
        localStorage.setItem(`${LOCAL_CHAT_SESSIONS_KEY}_${effectiveUserId}`, JSON.stringify(cloudSessions));
        return cloudSessions;
      }
    } catch (e) {
      console.warn('Lỗi đọc Chat Sessions từ Firestore, dùng cache LocalStorage:', e);
    }
  }

  return getLocalChatSessions(effectiveUserId);
}

/**
 * Xóa một phiên chat
 */
export async function deleteChatSession(userId, sessionId) {
  if (!sessionId) return;
  const effectiveUserId = userId || 'guest';

  if (firestoreDb && effectiveUserId !== 'guest' && !effectiveUserId.startsWith('demo_')) {
    try {
      const docRef = doc(firestoreDb, 'users', effectiveUserId, 'chat_sessions', sessionId);
      await deleteDoc(docRef);
    } catch (e) {
      console.warn('Lỗi xóa Chat Session trên Firestore:', e);
    }
  }

  // Xóa trong LocalStorage
  const list = getLocalChatSessions(effectiveUserId).filter(s => s.id !== sessionId);
  localStorage.setItem(`${LOCAL_CHAT_SESSIONS_KEY}_${effectiveUserId}`, JSON.stringify(list));
}

export function getLocalChatSessions(userId) {
  try {
    const raw = localStorage.getItem(`${LOCAL_CHAT_SESSIONS_KEY}_${userId || 'guest'}`);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

// =============================================================================
// THU THẬP PHẢN HỒI ĐÁNH GIÁ CỦA NGƯỜI DÙNG (AI MODEL FEEDBACK LOOP - RLHF)
// Lưu trữ trực tiếp lên Cloud Firestore collection: `ai_feedbacks`
// =============================================================================
const LOCAL_FEEDBACKS_KEY = 'hue_smart_tourism_ai_feedbacks';

/**
 * Gửi phản hồi Thích / Chưa hài lòng cho câu trả lời của AI
 * @param {Object} feedbackData - { messageId, sessionId, rating, reason, comment, prompt, responseExcerpt, isItinerary }
 */
export async function submitAiFeedback(feedbackData) {
  if (!feedbackData) return null;

  const currentUser = getCurrentUser();
  const feedbackId = feedbackData.id || `fb_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
  
  const payload = {
    id: feedbackId,
    messageId: feedbackData.messageId || `msg_${Date.now()}`,
    sessionId: feedbackData.sessionId || 'current_session',
    rating: feedbackData.rating || 'like', // 'like' | 'dislike'
    reason: feedbackData.reason || '',
    comment: feedbackData.comment || '',
    prompt: feedbackData.prompt || '',
    responseExcerpt: feedbackData.responseExcerpt || '',
    isItinerary: Boolean(feedbackData.isItinerary),
    userId: currentUser ? currentUser.uid : 'anonymous',
    userEmail: currentUser ? (currentUser.email || currentUser.displayName) : 'Khách vãng lai',
    userAgent: navigator.userAgent || '',
    createdAt: new Date().toISOString()
  };

  // 1. Lưu lên Cloud Firestore
  if (firestoreDb) {
    // 1.1 Lưu vào Subcollection 'users/{uid}/ai_feedbacks' (Nếu user đã đăng nhập - quyền luôn được ưu tiên)
    if (currentUser && currentUser.uid && !currentUser.uid.startsWith('demo_')) {
      try {
        const userDocRef = doc(firestoreDb, 'users', currentUser.uid, 'ai_feedbacks', feedbackId);
        await setDoc(userDocRef, {
          ...payload,
          createdAt: serverTimestamp()
        }, { merge: true });
        console.log(`✅ Đã lưu phản hồi AI vào subcollection "users/${currentUser.uid}/ai_feedbacks":`, feedbackId);
      } catch (e) {
        console.warn(`Lỗi ghi phản hồi vào users/${currentUser.uid}/ai_feedbacks:`, e);
      }
    }

    // 1.2 Lưu vào Root Collection 'ai_feedbacks' (Cho Admin tổng hợp)
    try {
      const rootDocRef = doc(firestoreDb, 'ai_feedbacks', feedbackId);
      await setDoc(rootDocRef, {
        ...payload,
        createdAt: serverTimestamp()
      }, { merge: true });
      console.log('✅ Đã lưu phản hồi AI vào root collection "ai_feedbacks":', feedbackId);
    } catch (e) {
      console.warn('Lỗi ghi phản hồi AI vào root collection "ai_feedbacks" (kiểm tra Rules):', e);
    }
  }

  // 2. Lưu bộ nhớ đệm LocalStorage
  try {
    const list = getLocalFeedbacks();
    const existingIndex = list.findIndex(item => item.id === feedbackId || item.messageId === payload.messageId);
    if (existingIndex >= 0) {
      list[existingIndex] = { ...list[existingIndex], ...payload };
    } else {
      list.unshift(payload);
    }
    localStorage.setItem(LOCAL_FEEDBACKS_KEY, JSON.stringify(list));
  } catch (err) {
    console.warn('Lỗi lưu feedback vào LocalStorage:', err);
  }

  return payload;
}

/**
 * Lấy danh sách phản hồi từ LocalStorage cache
 */
export function getLocalFeedbacks() {
  try {
    const raw = localStorage.getItem(LOCAL_FEEDBACKS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

