// 🔧 Gestionnaire de sessions pour Vercel
// Gère les problèmes de sessionStorage/localStorage sur Vercel

class SessionManager {
  constructor() {
    this.isVercel = process.env.NODE_ENV === 'production' && window.location.hostname.includes('vercel');
    this.fallbackStorage = {};
  }

  // Récupère une valeur du storage avec fallback
  getItem(key) {
    try {
      if (this.isVercel) {
        // Sur Vercel, utiliser localStorage comme fallback
        return localStorage.getItem(key) || this.fallbackStorage[key] || null;
      }
      return sessionStorage.getItem(key) || localStorage.getItem(key) || this.fallbackStorage[key] || null;
    } catch (error) {
      console.warn('⚠️ [SESSION] Erreur getItem, utilisation du fallback:', error);
      return this.fallbackStorage[key] || null;
    }
  }

  // Sauvegarde une valeur dans le storage avec fallback
  setItem(key, value) {
    try {
      if (this.isVercel) {
        // Sur Vercel, sauvegarder dans localStorage
        localStorage.setItem(key, value);
      } else {
        sessionStorage.setItem(key, value);
      }
      // Toujours sauvegarder dans le fallback
      this.fallbackStorage[key] = value;
    } catch (error) {
      console.warn('⚠️ [SESSION] Erreur setItem, utilisation du fallback:', error);
      this.fallbackStorage[key] = value;
    }
  }

  // Supprime une valeur du storage
  removeItem(key) {
    try {
      if (this.isVercel) {
        localStorage.removeItem(key);
      } else {
        sessionStorage.removeItem(key);
      }
      delete this.fallbackStorage[key];
    } catch (error) {
      console.warn('⚠️ [SESSION] Erreur removeItem:', error);
      delete this.fallbackStorage[key];
    }
  }

  // Nettoie toutes les sessions
  clearSessions() {
    try {
      // Nettoyer sessionStorage
      if (!this.isVercel) {
        sessionStorage.clear();
      }
      
      // Nettoyer localStorage des sessions
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('auth_session_') || key === 'current_session_id') {
          localStorage.removeItem(key);
        }
      });
      
      // Nettoyer le fallback
      this.fallbackStorage = {};
    } catch (error) {
      console.warn('⚠️ [SESSION] Erreur clearSessions:', error);
      this.fallbackStorage = {};
    }
  }

  // Récupère l'ID de session actuel
  getCurrentSessionId() {
    return this.getItem('current_session_id');
  }

  // Définit l'ID de session actuel
  setCurrentSessionId(sessionId) {
    this.setItem('current_session_id', sessionId);
  }

  // Récupère les données de session
  getSessionData(sessionId) {
    const sessionKey = `auth_session_${sessionId}`;
    const sessionData = this.getItem(sessionKey);
    
    if (!sessionData) {
      return null;
    }

    try {
      return JSON.parse(sessionData);
    } catch (error) {
      console.error('❌ [SESSION] Erreur parsing sessionData:', error);
      return null;
    }
  }

  // Sauvegarde les données de session
  saveSessionData(sessionId, sessionData) {
    const sessionKey = `auth_session_${sessionId}`;
    this.setItem(sessionKey, JSON.stringify(sessionData));
  }
}

// Instance singleton
const sessionManager = new SessionManager();

export default sessionManager;
