import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';
import sessionManager from '../../utils/sessionManager';

// Actions asynchrones
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    console.log('🔐 [AUTH_SLICE] LOGIN démarré pour:', credentials.username);
    try {
      const response = await authAPI.login(credentials);
      console.log('✅ [AUTH_SLICE] Réponse API login reçue:', {
        user: response.data.user?.username,
        role: response.data.user?.profile?.role
      });

      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      console.log('🆔 [AUTH_SLICE] Nouveau sessionId généré:', sessionId);
      
      const { access, refresh } = response.data;
      const userSession = {
        sessionId,
        access,
        refresh,
        user: response.data.user || null,
        timestamp: Date.now()
      };

      console.log('💾 [AUTH_SLICE] Sauvegarde session dans localStorage:', {
        key: `auth_session_${sessionId}`,
        user: userSession.user?.username
      });

      sessionManager.saveSessionData(sessionId, userSession);
      sessionManager.setCurrentSessionId(sessionId);

      console.log('✅ [AUTH_SLICE] Session sauvegardée avec succès');
      console.log('🔍 [AUTH_SLICE] localStorage après sauvegarde:', {
        current_session_id: localStorage.getItem('current_session_id'),
        session_keys: Object.keys(localStorage).filter(key => key.startsWith('auth_session_'))
      });

      return {
        sessionId,
        access,
        refresh,
        user: response.data.user || null
      };
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur login:', error);
      return rejectWithValue(error.response?.data?.message || 'Erreur de connexion');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(userData);
      return response;
    } catch (error) {
      console.log('🔍 [AUTH_SLICE] Erreur register détaillée:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      // Priorité des messages d'erreur du backend
      let errorMessage = 'Erreur d\'inscription';
      
      if (error.response?.data) {
        // Si c'est un objet avec une propriété 'error'
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        }
        // Si c'est un objet avec une propriété 'detail'
        else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
        // Si c'est un objet avec une propriété 'message'
        else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        // Si c'est directement une string
        else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      }
      
      console.log('🔍 [AUTH_SLICE] Message d\'erreur final:', errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue, getState }) => {
    console.log('🚪 [AUTH_SLICE] LOGOUT démarré');
    try {
      const state = getState();
      const sessionId = state.auth.sessionId;
      console.log('🔍 [AUTH_SLICE] SessionId pour logout:', sessionId);

      if (sessionId) {
        console.log('🗑️ [AUTH_SLICE] Suppression session:', sessionId);
        localStorage.removeItem(`auth_session_${sessionId}`);
        
        // Ne supprimer current_session_id que si c'est la session actuelle
        const currentSessionId = sessionStorage.getItem('current_session_id');
        if (currentSessionId === sessionId) {
          sessionStorage.removeItem('current_session_id');
        }
        
        console.log('✅ [AUTH_SLICE] Session supprimée');
        console.log('🔍 [AUTH_SLICE] localStorage après suppression:', {
          current_session_id: localStorage.getItem('current_session_id'),
          session_keys: Object.keys(localStorage).filter(key => key.startsWith('auth_session_'))
        });
      } else {
        console.log('⚠️ [AUTH_SLICE] Aucun sessionId trouvé pour logout');
      }
      return null;
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur logout:', error);
      return rejectWithValue('Erreur de déconnexion');
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue, getState }) => {
    console.log('🔄 [AUTH_SLICE] REFRESH_TOKEN démarré');
    try {
      const state = getState();
      const sessionId = state.auth.sessionId;
      console.log('🔍 [AUTH_SLICE] SessionId pour refresh:', sessionId);

      if (!sessionId) {
        console.log('❌ [AUTH_SLICE] Aucun sessionId pour refresh');
        throw new Error('Aucune session trouvée');
      }
      
      const sessionData = localStorage.getItem(`auth_session_${sessionId}`);
      console.log('🔍 [AUTH_SLICE] SessionData récupérée:', sessionData ? 'OUI' : 'NON');
      
      if (!sessionData) {
        console.log('❌ [AUTH_SLICE] Session expirée pour refresh');
        throw new Error('Session expirée');
      }
      
      const parsedSession = JSON.parse(sessionData);
      const refresh = parsedSession.refresh;
      console.log('🔍 [AUTH_SLICE] Refresh token récupéré:', refresh ? 'OUI' : 'NON');

      if (!refresh) {
        console.log('❌ [AUTH_SLICE] Aucun refresh token');
        throw new Error('Aucun token de rafraîchissement');
      }

      console.log('🔄 [AUTH_SLICE] Appel API refreshToken');
      const response = await authAPI.refreshToken(refresh);
      console.log('✅ [AUTH_SLICE] Nouveau access token reçu');
      
      parsedSession.access = response.access;
      localStorage.setItem(`auth_session_${sessionId}`, JSON.stringify(parsedSession));
      console.log('💾 [AUTH_SLICE] Session mise à jour avec nouveau token');

      return response;
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur refreshToken:', error);
      const state = getState();
      const sessionId = state.auth.sessionId;
      if (sessionId) {
        console.log('🗑️ [AUTH_SLICE] Suppression session après erreur refresh');
        localStorage.removeItem(`auth_session_${sessionId}`);
        const currentSessionId = sessionStorage.getItem('current_session_id');
        if (currentSessionId === sessionId) {
          sessionStorage.removeItem('current_session_id');
        }
      }
      return rejectWithValue('Token expiré');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue, getState }) => {
    console.log('👤 [AUTH_SLICE] GET_CURRENT_USER démarré');
    try {
      const state = getState();
      if (state.auth.user) {
        console.log('✅ [AUTH_SLICE] User déjà dans le state, retour direct');
        return state.auth.user;
      }

      console.log('🔄 [AUTH_SLICE] Appel API getCurrentUser');
      const response = await authAPI.getCurrentUser();
      console.log('✅ [AUTH_SLICE] User récupéré de l\'API:', response.data?.username);

      const sessionId = state.auth.sessionId;
      console.log('🔍 [AUTH_SLICE] SessionId pour mise à jour:', sessionId);
      
      if (!sessionId) {
        console.log('❌ [AUTH_SLICE] Aucun sessionId pour mise à jour');
        throw new Error('Aucune session trouvée');
      }
      
      const sessionData = localStorage.getItem(`auth_session_${sessionId}`);
      console.log('🔍 [AUTH_SLICE] SessionData pour mise à jour:', sessionData ? 'OUI' : 'NON');
      
      if (!sessionData) {
        console.log('❌ [AUTH_SLICE] Session expirée pour mise à jour');
        throw new Error('Session expirée');
      }

      const parsedSession = JSON.parse(sessionData);
      parsedSession.user = response.data;
      localStorage.setItem(`auth_session_${sessionId}`, JSON.stringify(parsedSession));
      console.log('💾 [AUTH_SLICE] Session mise à jour avec user data');

      return response.data;
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur getCurrentUser:', error);
      const state = getState();
      const sessionId = state.auth.sessionId;
      if (sessionId) {
        console.log('🗑️ [AUTH_SLICE] Suppression session après erreur getCurrentUser');
        localStorage.removeItem(`auth_session_${sessionId}`);
        const currentSessionId = sessionStorage.getItem('current_session_id');
        if (currentSessionId === sessionId) {
          sessionStorage.removeItem('current_session_id');
        }
      }
      console.log('getCurrentUser failed:', error.response?.status || error.message);
      return rejectWithValue('Erreur de récupération du profil');
    }
  }
);

// Action pour charger une session spécifique
export const loadSession = createAsyncThunk(
  'auth/loadSession',
  async (sessionId, { rejectWithValue }) => {
    console.log('📂 [AUTH_SLICE] LOAD_SESSION démarré pour:', sessionId);
    try {
      const sessionData = localStorage.getItem(`auth_session_${sessionId}`);
      console.log('🔍 [AUTH_SLICE] SessionData récupérée:', sessionData ? 'OUI' : 'NON');
      
      if (!sessionData) {
        console.log('❌ [AUTH_SLICE] Session non trouvée:', sessionId);
        throw new Error('Session non trouvée');
      }

      const parsedSession = JSON.parse(sessionData);
      console.log('✅ [AUTH_SLICE] Session parsée:', {
        user: parsedSession.user?.username,
        role: parsedSession.user?.profile?.role
      });

      // Mettre à jour current_session_id (par onglet)
      sessionStorage.setItem('current_session_id', sessionId);
      
      return {
        sessionId: parsedSession.sessionId,
        access: parsedSession.access,
        refresh: parsedSession.refresh,
        user: parsedSession.user
      };
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur loadSession:', error);
      return rejectWithValue('Session non trouvée');
    }
  }
);

// Action pour lister toutes les sessions disponibles
export const listSessions = createAsyncThunk(
  'auth/listSessions',
  async (_, { rejectWithValue }) => {
    console.log('📋 [AUTH_SLICE] LIST_SESSIONS démarré');
    try {
      const sessions = [];
      const currentSessionId = sessionStorage.getItem('current_session_id');
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('auth_session_')) {
          try {
            const sessionData = JSON.parse(localStorage.getItem(key));
            sessions.push({
              sessionId: sessionData.sessionId,
              user: sessionData.user?.username,
              role: sessionData.user?.profile?.role,
              timestamp: sessionData.timestamp,
              isCurrent: sessionData.sessionId === currentSessionId
            });
          } catch (e) {
            console.warn('⚠️ [AUTH_SLICE] Session corrompue ignorée:', key);
          }
        }
      }
      
      console.log('✅ [AUTH_SLICE] Sessions trouvées:', sessions.length);
      return sessions;
    } catch (error) {
      console.error('❌ [AUTH_SLICE] Erreur listSessions:', error);
      return rejectWithValue('Erreur lors de la récupération des sessions');
    }
  }
);

// Récupérer la session actuelle au démarrage
const getCurrentSessionData = () => {
  console.log('🔍 [AUTH_SLICE] getCurrentSessionData() appelé');
  const currentSessionId = sessionStorage.getItem('current_session_id');
  console.log('🔍 [AUTH_SLICE] current_session_id récupéré:', currentSessionId);
  
  if (!currentSessionId) {
    console.log('❌ [AUTH_SLICE] Aucun current_session_id trouvé');
    return null;
  }
  
  const sessionData = localStorage.getItem(`auth_session_${currentSessionId}`);
  console.log('🔍 [AUTH_SLICE] sessionData récupéré:', sessionData ? 'OUI' : 'NON');
  
  if (!sessionData) {
    console.log('❌ [AUTH_SLICE] Aucune sessionData trouvée pour:', currentSessionId);
    return null;
  }
  
  try {
    const parsed = JSON.parse(sessionData);
    console.log('✅ [AUTH_SLICE] Session parsée avec succès:', {
      sessionId: parsed.sessionId,
      user: parsed.user?.username,
      role: parsed.user?.profile?.role
    });
    return parsed;
  } catch (error) {
    console.error('❌ [AUTH_SLICE] Erreur parsing session:', error);
    return null;
  }
};

const sessionData = getCurrentSessionData();

console.log('🚀 [AUTH_SLICE] Initialisation avec sessionData:', sessionData ? {
  sessionId: sessionData.sessionId,
  user: sessionData.user?.username,
  role: sessionData.user?.profile?.role
} : 'AUCUNE');

const initialState = {
  user: sessionData?.user || null,
  token: sessionData?.access || null,
  refreshToken: sessionData?.refresh || null,
  sessionId: sessionData?.sessionId || null,
  isAuthenticated: !!sessionData,
  loading: false,
  error: null,
  initialized: false,
  availableSessions: [], // Nouveau: liste des sessions disponibles
};

console.log('🚀 [AUTH_SLICE] État initial créé:', {
  isAuthenticated: initialState.isAuthenticated,
  sessionId: initialState.sessionId,
  user: initialState.user?.username
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setInitialized: (state) => {
      state.initialized = true;
    },
    // Nouveau: action pour changer de session
    switchSession: (state, action) => {
      const { sessionId, access, refresh, user } = action.payload;
      state.sessionId = sessionId;
      state.token = access;
      state.refreshToken = refresh;
      state.user = user;
      state.isAuthenticated = !!user;
      state.initialized = true;
    },
    // 🎯 NOUVEAU: Action pour mettre à jour l'utilisateur
    updateUser: (state, action) => {
      console.log('🔍 [AUTH_SLICE] UPDATE_USER action appelée');
      console.log('🔍 [AUTH_SLICE] Payload reçu:', action.payload);
      console.log('🔍 [AUTH_SLICE] User avant mise à jour:', state.user);
      
      state.user = action.payload;
      
      console.log('🔍 [AUTH_SLICE] User après mise à jour:', state.user);
      
      // Mettre à jour la session dans localStorage
      if (state.sessionId) {
        const sessionData = localStorage.getItem(`auth_session_${state.sessionId}`);
        if (sessionData) {
          const parsedSession = JSON.parse(sessionData);
          parsedSession.user = action.payload;
          localStorage.setItem(`auth_session_${state.sessionId}`, JSON.stringify(parsedSession));
          console.log('🔍 [AUTH_SLICE] Session mise à jour dans localStorage');
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.sessionId = action.payload.sessionId;
        state.user = action.payload.user || null;
        state.initialized = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
        state.user = null;
      })
      
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        state.error = null;
        state.initialized = true;
      })
      
      // Refresh Token
      .addCase(refreshToken.pending, (state) => {
        state.loading = true;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access;
        state.isAuthenticated = true;
        state.initialized = true;
      })
      .addCase(refreshToken.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        state.initialized = true;
      })
      
      // Get Current User
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.initialized = true;
      })
      .addCase(getCurrentUser.rejected, (state) => {
        state.loading = false;
        // EN CAS D'ERREUR, FORCER LA DÉCONNEXION COMPLÈTE
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        state.initialized = true;
      })
      
      // Load Session
      .addCase(loadSession.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadSession.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.sessionId = action.payload.sessionId;
        state.user = action.payload.user || null;
        state.initialized = true;
        state.error = null;
      })
      .addCase(loadSession.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.sessionId = null;
      })
      
      // List Sessions
      .addCase(listSessions.fulfilled, (state, action) => {
        state.availableSessions = action.payload;
      });
  },
});

export const { clearError, setLoading, setInitialized, switchSession } = authSlice.actions;
export default authSlice.reducer; 