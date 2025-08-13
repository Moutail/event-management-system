import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { eventAPI } from '../../services/api';

// Fonction utilitaire pour extraire le message d'erreur
const extractErrorMessage = (error, defaultMessage) => {
  console.log('DEBUG: extractErrorMessage - Error object:', error);
  console.log('DEBUG: extractErrorMessage - Error response:', error.response);
  console.log('DEBUG: extractErrorMessage - Error response data:', error.response?.data);
  
  let errorMessage = defaultMessage;
  
  if (error.response?.data) {
    if (typeof error.response.data === 'string') {
      errorMessage = error.response.data;
    } else if (error.response.data.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response.data.message) {
      errorMessage = error.response.data.message;
    } else if (error.response.data.error) {
      errorMessage = error.response.data.error;
    } else {
      // Si c'est un objet avec des erreurs de validation
      const validationErrors = Object.entries(error.response.data)
        .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
        .join('; ');
      errorMessage = validationErrors || JSON.stringify(error.response.data);
    }
  } else if (error.message) {
    errorMessage = error.message;
  }
  
  console.log('DEBUG: extractErrorMessage - Final error message:', errorMessage);
  return errorMessage;
};

// Actions asynchrones
export const fetchEvents = createAsyncThunk(
  'events/fetchEvents',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getEvents(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des événements'));
    }
  }
);

export const fetchEventById = createAsyncThunk(
  'events/fetchEventById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getEventById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération de l\'événement'));
    }
  }
);

export const createEvent = createAsyncThunk(
  'events/createEvent',
  async (eventData, { rejectWithValue }) => {
    try {
      console.log('DEBUG: createEvent thunk - Données reçues:', eventData);
      const response = await eventAPI.createEvent(eventData);
      console.log('DEBUG: createEvent thunk - Réponse reçue:', response);
      return response.data;
    } catch (error) {
      console.error('DEBUG: createEvent thunk - Erreur:', error);
      console.error('DEBUG: createEvent thunk - Error response:', error.response);
      console.error('DEBUG: createEvent thunk - Error message:', error.message);
      return rejectWithValue(extractErrorMessage(error, 'Erreur de création de l\'événement'));
    }
  }
);

export const updateEvent = createAsyncThunk(
  'events/updateEvent',
  async ({ id, eventData }, { rejectWithValue }) => {
    try {
      const response = await eventAPI.updateEvent(id, eventData);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de mise à jour de l\'événement'));
    }
  }
);

export const deleteEvent = createAsyncThunk(
  'events/deleteEvent',
  async (id, { rejectWithValue }) => {
    try {
      await eventAPI.deleteEvent(id);
      return id;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de suppression de l\'événement'));
    }
  }
);

export const duplicateEvent = createAsyncThunk(
  'events/duplicateEvent',
  async (id, { rejectWithValue }) => {
    try {
      const response = await eventAPI.duplicateEvent(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de duplication de l\'événement'));
    }
  }
);

export const publishEvent = createAsyncThunk(
  'events/publishEvent',
  async (id, { rejectWithValue }) => {
    try {
      const response = await eventAPI.publishEvent(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de publication de l\'événement'));
    }
  }
);

export const cancelEvent = createAsyncThunk(
  'events/cancelEvent',
  async (id, { rejectWithValue }) => {
    try {
      const response = await eventAPI.cancelEvent(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur d\'annulation de l\'événement'));
    }
  }
);

export const fetchFeaturedEvents = createAsyncThunk(
  'events/fetchFeaturedEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getFeaturedEvents();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des événements en vedette'));
    }
  }
);

export const fetchUpcomingEvents = createAsyncThunk(
  'events/fetchUpcomingEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getUpcomingEvents();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des événements à venir'));
    }
  }
);

export const fetchOngoingEvents = createAsyncThunk(
  'events/fetchOngoingEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getOngoingEvents();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des événements en cours'));
    }
  }
);

export const fetchMyEvents = createAsyncThunk(
  'events/fetchMyEvents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getMyEvents();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération de vos événements'));
    }
  }
);

export const fetchEventStatistics = createAsyncThunk(
  'events/fetchEventStatistics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getEventStatistics();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des statistiques'));
    }
  }
);

// Actions pour les inscriptions aux événements
export const registerForEvent = createAsyncThunk(
  'events/registerForEvent',
  async (registrationData, { rejectWithValue }) => {
    try {
      const response = await eventAPI.registerForEvent(registrationData.event, registrationData);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur d\'inscription à l\'événement'));
    }
  }
);

export const fetchMyRegistrations = createAsyncThunk(
  'events/fetchMyRegistrations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getMyRegistrations();
      // Normaliser les réponses paginées DRF
      return response.data.results || response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération de vos inscriptions'));
    }
  }
);

export const cancelRegistration = createAsyncThunk(
  'events/cancelRegistration',
  async (registrationId, { rejectWithValue }) => {
    try {
      const response = await eventAPI.cancelRegistration(registrationId);
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur d\'annulation de l\'inscription'));
    }
  }
);

export const fetchUpcomingRegistrations = createAsyncThunk(
  'events/fetchUpcomingRegistrations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getUpcomingRegistrations();
      return response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des inscriptions à venir'));
    }
  }
);

// Actions pour les catégories et tags
export const fetchCategories = createAsyncThunk(
  'events/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getCategories();
      // Extraire le tableau results de la réponse paginée
      return response.data.results || response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des catégories'));
    }
  }
);

export const fetchTags = createAsyncThunk(
  'events/fetchTags',
  async (_, { rejectWithValue }) => {
    try {
      const response = await eventAPI.getTags();
      // Extraire le tableau results de la réponse paginée
      return response.data.results || response.data;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error, 'Erreur de récupération des tags'));
    }
  }
);

const initialState = {
  events: [],
  currentEvent: null,
  featuredEvents: [],
  upcomingEvents: [],
  ongoingEvents: [],
  myEvents: [],
  categories: [],
  tags: [],
  statistics: null,
  // États pour les inscriptions
  myRegistrations: [],
  upcomingRegistrations: [],
  registrationLoading: false,
  registrationError: null,
  loading: false,
  error: null,
  filters: {
    search: '',
    status: '',
    category: '',
    tags: [],
    dateFilter: '',
    minPrice: '',
    maxPrice: '',
    location: '',
    organizer: '',
  },
  pagination: {
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
    pageSize: 10,
  },
};

const eventSlice = createSlice({
  name: 'events',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentEvent: (state, action) => {
      state.currentEvent = action.payload;
    },
    clearCurrentEvent: (state) => {
      state.currentEvent = null;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Events
      .addCase(fetchEvents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEvents.fulfilled, (state, action) => {
        state.loading = false;
        state.events = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination.totalCount = action.payload.count;
          state.pagination.totalPages = Math.ceil(action.payload.count / state.pagination.pageSize);
        }
      })
      .addCase(fetchEvents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Fetch Event by ID
      .addCase(fetchEventById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEventById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentEvent = action.payload;
      })
      .addCase(fetchEventById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Create Event
      .addCase(createEvent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createEvent.fulfilled, (state, action) => {
        state.loading = false;
        state.events.unshift(action.payload);
      })
      .addCase(createEvent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Update Event
      .addCase(updateEvent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateEvent.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.events.findIndex(event => event.id === action.payload.id);
        if (index !== -1) {
          state.events[index] = action.payload;
        }
        if (state.currentEvent && state.currentEvent.id === action.payload.id) {
          state.currentEvent = action.payload;
        }
        // Mettre à jour les autres listes en mémoire
        const updateListItem = (list) => {
          const idx = list.findIndex(e => e.id === action.payload.id);
          if (idx !== -1) list[idx] = action.payload;
        };
        updateListItem(state.myEvents);
        updateListItem(state.featuredEvents);
        updateListItem(state.upcomingEvents);
        updateListItem(state.ongoingEvents);
      })
      .addCase(updateEvent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Delete Event
      .addCase(deleteEvent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteEvent.fulfilled, (state, action) => {
        state.loading = false;
        state.events = state.events.filter(event => event.id !== action.payload);
        if (state.currentEvent && state.currentEvent.id === action.payload) {
          state.currentEvent = null;
        }
      })
      .addCase(deleteEvent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Duplicate Event
      .addCase(duplicateEvent.fulfilled, (state, action) => {
        state.events.unshift(action.payload);
      })
      
      // Publish Event
      .addCase(publishEvent.fulfilled, (state, action) => {
        const index = state.events.findIndex(event => event.id === action.payload.id);
        if (index !== -1) {
          state.events[index] = action.payload;
        }
        if (state.currentEvent && state.currentEvent.id === action.payload.id) {
          state.currentEvent = action.payload;
        }
      })
      
      // Cancel Event
      .addCase(cancelEvent.fulfilled, (state, action) => {
        const index = state.events.findIndex(event => event.id === action.payload.id);
        if (index !== -1) {
          state.events[index] = action.payload;
        }
        if (state.currentEvent && state.currentEvent.id === action.payload.id) {
          state.currentEvent = action.payload;
        }
      })
      
      // Featured Events
      .addCase(fetchFeaturedEvents.fulfilled, (state, action) => {
        state.featuredEvents = action.payload;
      })
      
      // Upcoming Events
      .addCase(fetchUpcomingEvents.fulfilled, (state, action) => {
        state.upcomingEvents = action.payload;
      })
      
      // Ongoing Events
      .addCase(fetchOngoingEvents.fulfilled, (state, action) => {
        state.ongoingEvents = action.payload;
      })
      
      // My Events
      .addCase(fetchMyEvents.fulfilled, (state, action) => {
        state.myEvents = action.payload;
      })
      
      // Event Statistics
      .addCase(fetchEventStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      })
      
      // Categories
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })
      
      // Tags
      .addCase(fetchTags.fulfilled, (state, action) => {
        state.tags = action.payload;
      })
      
      // Register for Event
      .addCase(registerForEvent.pending, (state) => {
        state.registrationLoading = true;
        state.registrationError = null;
      })
      .addCase(registerForEvent.fulfilled, (state, action) => {
        state.registrationLoading = false;
        // Mettre à jour l'événement courant si c'est le même
        if (state.currentEvent && state.currentEvent.id === action.payload.event) {
          state.currentEvent = {
            ...state.currentEvent,
            current_registrations: state.currentEvent.current_registrations + 1
          };
        }
      })
      .addCase(registerForEvent.rejected, (state, action) => {
        state.registrationLoading = false;
        state.registrationError = action.payload;
      })
      
      // Fetch My Registrations
      .addCase(fetchMyRegistrations.pending, (state) => {
        state.registrationLoading = true;
        state.registrationError = null;
      })
      .addCase(fetchMyRegistrations.fulfilled, (state, action) => {
        state.registrationLoading = false;
        state.myRegistrations = action.payload;
      })
      .addCase(fetchMyRegistrations.rejected, (state, action) => {
        state.registrationLoading = false;
        state.registrationError = action.payload;
      })
      
      // Cancel Registration
      .addCase(cancelRegistration.pending, (state) => {
        state.registrationLoading = true;
        state.registrationError = null;
      })
      .addCase(cancelRegistration.fulfilled, (state, action) => {
        state.registrationLoading = false;
        // Mettre à jour la liste des inscriptions
        state.myRegistrations = state.myRegistrations.map(reg => 
          reg.id === action.payload.id ? action.payload : reg
        );
        // Mettre à jour l'événement courant si c'est le même
        if (state.currentEvent && state.currentEvent.id === action.payload.event) {
          state.currentEvent = {
            ...state.currentEvent,
            current_registrations: Math.max(0, state.currentEvent.current_registrations - 1)
          };
        }
      })
      .addCase(cancelRegistration.rejected, (state, action) => {
        state.registrationLoading = false;
        state.registrationError = action.payload;
      })
      
      // Fetch Upcoming Registrations
      .addCase(fetchUpcomingRegistrations.pending, (state) => {
        state.registrationLoading = true;
        state.registrationError = null;
      })
      .addCase(fetchUpcomingRegistrations.fulfilled, (state, action) => {
        state.registrationLoading = false;
        state.upcomingRegistrations = action.payload;
      })
      .addCase(fetchUpcomingRegistrations.rejected, (state, action) => {
        state.registrationLoading = false;
        state.registrationError = action.payload;
      });
  },
});

export const { 
  clearError, 
  setCurrentEvent, 
  clearCurrentEvent, 
  setFilters, 
  clearFilters, 
  setPagination 
} = eventSlice.actions;

export default eventSlice.reducer; 