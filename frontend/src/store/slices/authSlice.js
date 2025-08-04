import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';

// Actions asynchrones
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      
      // Stocker seulement les données nécessaires (sérialisables)
      const { access, refresh } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Retourner seulement les données nécessaires
      return {
        access,
        refresh,
        user: response.data.user || null
      };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.response?.data || 'Erreur de connexion';
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Erreur de connexion');
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
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.response?.data || 'Erreur d\'inscription';
      return rejectWithValue(typeof errorMessage === 'string' ? errorMessage : 'Erreur d\'inscription');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return null;
    } catch (error) {
      return rejectWithValue('Erreur de déconnexion');
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (!refresh) {
        throw new Error('Aucun token de rafraîchissement');
      }
      
      const response = await authAPI.refreshToken(refresh);
      localStorage.setItem('access_token', response.access);
      return response;
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return rejectWithValue('Token expiré');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue, getState }) => {
    try {
      // Vérifier si on a déjà un utilisateur
      const state = getState();
      if (state.auth.user) {
        return state.auth.user;
      }

      const response = await authAPI.getCurrentUser();
      return response.data;
    } catch (error) {
      // Ne pas supprimer les tokens ici, laissez l'intercepteur Axios s'en charger
      console.log('getCurrentUser failed:', error.response?.status);
      return rejectWithValue('Erreur de récupération du profil');
    }
  }
);

// Vérifier si on a un token valide au démarrage
const hasValidToken = () => {
  const token = localStorage.getItem('access_token');
  return !!token;
};

const initialState = {
  user: null,
  token: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: hasValidToken(),
  loading: false,
  error: null,
  initialized: false, // Nouveau flag pour éviter les boucles
};

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
        state.error = null;
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
        // Ne pas changer isAuthenticated ici, laissez l'intercepteur Axios s'en charger
        state.user = null;
        state.initialized = true;
      });
  },
});

export const { clearError, setLoading, setInitialized } = authSlice.actions;
export default authSlice.reducer; 