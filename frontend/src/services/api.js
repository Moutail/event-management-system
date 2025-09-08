import axios from 'axios';

// Configuration de base d'Axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fonction pour récupérer le token de la session actuelle
const getCurrentSessionToken = () => {
  console.log('🔍 [API] getCurrentSessionToken() appelé');
  const currentSessionId = sessionStorage.getItem('current_session_id');
  console.log('🔍 [API] current_session_id récupéré:', currentSessionId);
  
  if (!currentSessionId) {
    console.log('❌ [API] Aucun current_session_id trouvé');
    return null;
  }
  
  const sessionData = localStorage.getItem(`auth_session_${currentSessionId}`);
  console.log('🔍 [API] sessionData récupéré:', sessionData ? 'OUI' : 'NON');
  
  if (!sessionData) {
    console.log('❌ [API] Aucune sessionData trouvée pour:', currentSessionId);
    return null;
  }
  
  try {
    const parsed = JSON.parse(sessionData);
    console.log('✅ [API] Token récupéré pour session:', {
      sessionId: currentSessionId,
      user: parsed.user?.username,
      hasAccessToken: !!parsed.access
    });
    return parsed.access;
  } catch (error) {
    console.error('❌ [API] Erreur parsing sessionData:', error);
    return null;
  }
};

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    console.log('📤 [API] Requête envoyée vers:', config.url);
    const token = getCurrentSessionToken();
    if (token) {
      console.log('🔑 [API] Token ajouté au header pour:', config.url);
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('⚠️ [API] Aucun token trouvé pour:', config.url);
    }
    return config;
  },
  (error) => {
    console.error('❌ [API] Erreur interceptor request:', error);
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs et le refresh token
api.interceptors.response.use(
  (response) => {
    console.log('✅ [API] Réponse reçue de:', response.config.url, 'Status:', response.status);
    return response;
  },
  async (error) => {
    console.log('❌ [API] Erreur réponse de:', error.config?.url, 'Status:', error.response?.status);
    
    const originalRequest = error.config;
    
    // Éviter les boucles infinies - version simplifiée
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('🔄 [API] Tentative de refresh token pour:', originalRequest.url);
      originalRequest._retry = true;
      
      // Si c'est une erreur 401 sur /auth/user/, nettoyer la session actuelle
      if (originalRequest.url.includes('/auth/user/')) {
        console.log('🔄 [API] Refresh token pour /auth/user/');
        try {
          const currentSessionId = sessionStorage.getItem('current_session_id');
          console.log('🔍 [API] SessionId pour refresh:', currentSessionId);
          
          if (currentSessionId) {
            const sessionData = localStorage.getItem(`auth_session_${currentSessionId}`);
            console.log('🔍 [API] SessionData pour refresh:', sessionData ? 'OUI' : 'NON');
            
            if (sessionData) {
              const parsedSession = JSON.parse(sessionData);
              const refresh = parsedSession.refresh;
              console.log('🔍 [API] Refresh token trouvé:', refresh ? 'OUI' : 'NON');
              
              if (refresh) {
                console.log('🔄 [API] Appel API refreshToken');
                const refreshResponse = await api.post('/auth/refresh/', { refresh });
                console.log('✅ [API] Nouveau access token reçu');
                
                parsedSession.access = refreshResponse.data.access;
                localStorage.setItem(`auth_session_${currentSessionId}`, JSON.stringify(parsedSession));
                console.log('💾 [API] Session mise à jour avec nouveau token');
                
                originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access}`;
                console.log('🔄 [API] Retry de la requête originale avec nouveau token');
                return api(originalRequest);
              }
            }
          }
        } catch (refreshError) {
          console.error('❌ [API] Erreur refresh token:', refreshError);
        }
      }
      
      // Pour les autres endpoints, rediriger vers login
      if (!originalRequest.url.includes('/auth/token/')) {
        console.log('🗑️ [API] Suppression session après échec refresh');
        const currentSessionId = sessionStorage.getItem('current_session_id');
        if (currentSessionId) {
          localStorage.removeItem(`auth_session_${currentSessionId}`);
          sessionStorage.removeItem('current_session_id');
          console.log('✅ [API] Session supprimée');
        }
        
        // Éviter la redirection en boucle et les appels répétés
        if (window.location.pathname !== '/login') {
          // Utiliser replace pour éviter l'historique de navigation
          window.location.replace('/login');
        }
      }
      
      // Retourner une erreur pour arrêter la chaîne de promesses
      return Promise.reject(new Error('Authentication failed'));
    }

    return Promise.reject(error);
  }
);

// Service d'authentification
export const authAPI = {
  login: (credentials) => api.post('/auth/token/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
  getCurrentUser: () => api.get('/auth/user/'),
  logout: () => api.post('/auth/logout/'),
  changePassword: (oldPassword, newPassword) =>
    api.post('/auth/change_password/', { old_password: oldPassword, new_password: newPassword }),
};

// Service des événements
export const eventAPI = {
  // Récupération des événements
  getEvents: (params = {}) => api.get('/events/', { params }),
  getEventById: (id) => api.get(`/events/${id}/`),
  getEventParticipants: (id) => api.get(`/events/${id}/participants/`),
  getFeaturedEvents: () => api.get('/events/featured/'),
  getUpcomingEvents: () => api.get('/events/upcoming/'),
  getOngoingEvents: () => api.get('/events/ongoing/'),
  getMyEvents: () => api.get('/events/my_events/'),
  getEventStatistics: () => api.get('/events/statistics/'),
  getTicketTypes: (eventId) => api.get(`/events/${eventId}/ticket_types/`),
  createTicketType: (eventId, data) => api.post(`/events/${eventId}/ticket_types/`, data),
  getSessionTypes: (eventId) => api.get(`/events/${eventId}/session_types/`),
  createSessionType: (eventId, data) => api.post(`/events/${eventId}/session_types/`, data),
  exportRegistrationsCSV: (eventId) => api.get(`/events/${eventId}/export_registrations_csv/`, { responseType: 'blob' }),
  exportRegistrationsExcel: (eventId) => api.get(`/events/${eventId}/export_registrations_excel/`, { responseType: 'blob' }),
  exportRegistrationsPDF: (eventId) => api.get(`/events/${eventId}/export_registrations_pdf/`, { responseType: 'blob' }),
  
  // CRUD des événements
  createEvent: (eventData) => {
    console.log('DEBUG: createEvent - Données reçues:', eventData);
    console.log('DEBUG: createEvent - Type de données:', typeof eventData);
    console.log('DEBUG: createEvent - Instance de FormData:', eventData instanceof FormData);
    
    // Si c'est déjà un FormData, l'utiliser directement
    if (eventData instanceof FormData) {
      console.log('DEBUG: createEvent - Utilisation du FormData existant');
      console.log('DEBUG: createEvent - FormData contenu:');
      for (let [key, value] of eventData.entries()) {
        console.log(`  ${key}: ${value} (type: ${typeof value})`);
        if (value instanceof File) {
          console.log(`    - Nom du fichier: ${value.name}`);
          console.log(`    - Type du fichier: ${value.type}`);
          console.log(`    - Taille du fichier: ${value.size}`);
        }
      }
      
      return api.post('/events/', eventData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }
    
    // Sinon, créer un nouveau FormData
    const formData = new FormData();
    console.log('DEBUG: createEvent - Création d\'un nouveau FormData');
    
    // Ajouter les champs de base
    Object.keys(eventData).forEach(key => {
      if (key === 'poster' || key === 'banner') {
        if (eventData[key]) {
          formData.append(key, eventData[key]);
        }
      } else if (key === 'tag_ids' && Array.isArray(eventData[key])) {
        eventData[key].forEach(tagId => {
          formData.append('tag_ids', tagId);
        });
      } else if (eventData[key] !== null && eventData[key] !== undefined) {
        formData.append(key, eventData[key]);
      }
    });
    
    console.log('DEBUG: createEvent - FormData contenu:');
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}: ${value}`);
    }
    
    return api.post('/events/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  updateEvent: (id, eventData) => {
    console.log('DEBUG: updateEvent - Données reçues:', eventData);
    console.log('DEBUG: updateEvent - Type de données:', typeof eventData);
    
    // Accepter un FormData déjà construit
    if (eventData instanceof FormData) {
      console.log('DEBUG: updateEvent - Utilisation du FormData existant');
      return api.patch(`/events/${id}/`, eventData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    }

    // Vérifier que eventData n'est pas null ou undefined
    if (!eventData || typeof eventData !== 'object') {
      console.error('DEBUG: updateEvent - eventData invalide:', eventData);
      return Promise.reject(new Error('Données d\'événement invalides'));
    }

    const formData = new FormData();
    
    // Ajouter les champs de base
    Object.keys(eventData).forEach(key => {
      if (key === 'poster' || key === 'banner') {
        if (eventData[key]) {
          formData.append(key, eventData[key]);
        }
      } else if ((key === 'tags' || key === 'tag_ids') && Array.isArray(eventData[key])) {
        eventData[key].forEach(tagId => {
          formData.append('tag_ids', tagId);
        });
      } else if (eventData[key] !== null && eventData[key] !== undefined) {
        formData.append(key, eventData[key]);
      }
    });
    
    console.log('DEBUG: updateEvent - FormData créé');
    return api.patch(`/events/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  deleteEvent: (id) => api.delete(`/events/${id}/`),
  duplicateEvent: (id) => api.post(`/events/${id}/duplicate/`),
  publishEvent: (id) => api.post(`/events/${id}/publish/`),
  cancelEvent: (id) => api.post(`/events/${id}/cancel/`),
  
  // Catégories et tags
  getCategories: () => api.get('/categories/'),
  getTags: () => api.get('/tags/'),
  
  // Inscriptions
  registerForEvent: (eventId, registrationData) => 
    api.post('/registrations/', { event: eventId, ...registrationData }),
  getMyRegistrations: () => api.get('/registrations/'),
  cancelRegistration: (registrationId) => 
    api.post(`/registrations/${registrationId}/cancel/`),
  cancelPayment: (registrationId) => 
    api.post(`/registrations/${registrationId}/cancel_payment/`),
  confirmRegistration: (registrationId) => 
    api.post(`/registrations/${registrationId}/confirm/`),
  getRegistrationQr: (registrationId) => 
    api.get(`/registrations/${registrationId}/qr/`),
  getUpcomingRegistrations: () => api.get('/registrations/upcoming/'),
  
  // Gestion des listes d'attente
  getWaitlistedRegistrations: (eventId) => api.get(`/events/${eventId}/waitlisted_registrations/`),
  approveWaitlist: (registrationId) => api.post(`/registrations/${registrationId}/approve_waitlist/`),
  rejectWaitlist: (registrationId, reason) => api.post(`/registrations/${registrationId}/reject_waitlist/`, { reason }),

  // Gestion des remboursements
  requestRefund: (registrationId, data) => api.post(`/registrations/${registrationId}/request_refund/`, data),
  processRefund: (registrationId, action) => api.post(`/refund/${registrationId}/process/`, { action }),
  getRefundRequests: (eventId) => api.get(`/events/${eventId}/refund_requests/`),
  
  // Historique
  getEventHistory: () => api.get('/history/'),
};

// Service des fichiers
export const fileAPI = {
  uploadFile: (file, type = 'image') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    return api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Utilitaires
export const formatDate = (dateString, customLocale = null) => {
  if (!dateString) return '';
  const locale = customLocale || (typeof window !== 'undefined' && window.__APP_LOCALE__) || 'fr-FR';
  return new Date(dateString).toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatPrice = (price, customLocale = null) => {
  if (price === 0 || price === null || price === undefined) return 'Gratuit';
  // Convertir en nombre si c'est une chaîne
  const numericPrice = typeof price === 'string' ? parseFloat(price) : price;
  if (isNaN(numericPrice)) return 'Gratuit';
  const locale = customLocale || (typeof window !== 'undefined' && window.__APP_LOCALE__) || 'en-US';
  const currencyByLocale = {
    'fr-FR': 'USD',
    'en-US': 'USD',
    'es-ES': 'USD',
  };
  const currency = currencyByLocale[locale] || 'USD';
  try {
    return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(numericPrice);
  } catch (_) {
    return `${numericPrice.toFixed(2)} ${currency}`;
  }
};

export const getEventStatusColor = (status) => {
  const statusColors = {
    draft: '#757575',
    published: '#2e7d32',
    cancelled: '#d32f2f',
    completed: '#1976d2',
    postponed: '#ed6c02',
  };
  return statusColors[status] || '#757575';
};

export const getEventStatusLabel = (status) => {
  const statusLabels = {
    draft: 'Brouillon',
    published: 'Publié',
    cancelled: 'Annulé',
    completed: 'Terminé',
    postponed: 'Reporté',
  };
  return statusLabels[status] || status;
};

// Fonction pour construire l'URL complète d'une image
export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  
  // Si c'est déjà une URL complète, la retourner
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Construire l'URL correcte pour les images (pas via l'API)
  const BASE_URL = process.env.REACT_APP_BASE_URL || 'http://localhost:8000';
  
  // Si le chemin commence par /media/, l'utiliser directement
  if (imagePath.startsWith('/media/')) {
    return `${BASE_URL}${imagePath}`;
  }
  
  // Sinon, ajouter /media/ si nécessaire
  if (!imagePath.startsWith('/')) {
    imagePath = `/${imagePath}`;
  }
  
  return `${BASE_URL}${imagePath}`;
};

export default api; 

// Helper POST for dynamic endpoints (used in modal)
export const post = (url, data = {}) => api.post(url, data);