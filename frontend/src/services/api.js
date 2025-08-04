import axios from 'axios';

// Configuration de base d'Axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs et le refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Éviter les boucles infinies
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Ne pas essayer de rafraîchir le token si c'est déjà une requête de refresh
      if (originalRequest.url.includes('/token/refresh/')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken,
          });
          
          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.log('Refresh token failed, redirecting to login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Éviter la redirection en boucle
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

// Service d'authentification
export const authAPI = {
  login: (credentials) => api.post('/token/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  refreshToken: (refresh) => api.post('/token/refresh/', { refresh }),
  getCurrentUser: () => api.get('/auth/user/'),
  logout: () => api.post('/auth/logout/'),
};

// Service des événements
export const eventAPI = {
  // Récupération des événements
  getEvents: (params = {}) => api.get('/events/', { params }),
  getEventById: (id) => api.get(`/events/${id}/`),
  getFeaturedEvents: () => api.get('/events/featured/'),
  getUpcomingEvents: () => api.get('/events/upcoming/'),
  getOngoingEvents: () => api.get('/events/ongoing/'),
  getMyEvents: () => api.get('/events/my_events/'),
  getEventStatistics: () => api.get('/events/statistics/'),
  
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
      } else if (key === 'tags' && Array.isArray(eventData[key])) {
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
  getUpcomingRegistrations: () => api.get('/registrations/upcoming/'),
  
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
export const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatPrice = (price) => {
  if (price === 0 || price === null || price === undefined) return 'Gratuit';
  // Convertir en nombre si c'est une chaîne
  const numericPrice = typeof price === 'string' ? parseFloat(price) : price;
  if (isNaN(numericPrice)) return 'Gratuit';
  return `${numericPrice.toFixed(2)} €`;
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
  
  // Sinon, construire l'URL avec l'API
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  return `${API_BASE_URL}${imagePath}`;
};

export default api; 