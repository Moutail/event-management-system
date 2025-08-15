import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Snackbar, Alert } from '@mui/material';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr, enUS, es } from 'date-fns/locale';

// Redux actions
import { getCurrentUser } from './store/slices/authSlice';
import { hideSnackbar } from './store/slices/uiSlice';

// Thèmes
import { theme, darkTheme } from './theme';

// Composants
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Pages
import HomePage from './pages/HomePage';
import EventsPage from './pages/EventsPage';
import EventDetailPage from './pages/EventDetailPage';
import CreateEventPage from './pages/CreateEventPage';
import EditEventPage from './pages/EditEventPage';
import MyEventsPage from './pages/MyEventsPage';
import MyRegistrationsPage from './pages/MyRegistrationsPage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import NotFoundPage from './pages/NotFoundPage';
import QRCodeScannerPage from './pages/QRCodeScannerPage';
import SuperAdminDashboard from './pages/SuperAdminDashboard';
import DebugAuth from './components/DebugAuth';

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, loading: authLoading, user } = useSelector((state) => state.auth);
  const { darkMode, locale } = useSelector((state) => state.ui);
  const { snackbar } = useSelector((state) => state.ui);

  // Appliquer la locale globale côté navigateur (dates/nombres)
  useEffect(() => {
    try {
      if (locale) {
        console.log('App.js - Setting window.__APP_LOCALE__ to:', locale);
        // Stocker la locale pour l'utiliser dans helpers et composants
        window.__APP_LOCALE__ = locale;
        try { localStorage.setItem('locale', locale); } catch(_) {}
      }
    } catch (_) {}
  }, [locale]);

  // Charger les données initiales une seule fois au démarrage
  useEffect(() => {
    const initializeApp = async () => {
      // Si on a un token mais pas d'utilisateur, récupérer l'utilisateur
      if (isAuthenticated && !user) {
        try {
          await dispatch(getCurrentUser());
        } catch (error) {
          console.log('Failed to get current user:', error);
        }
      }
      // Les données seront chargées par chaque page selon les besoins
    };

    initializeApp();
  }, [dispatch, isAuthenticated, user]);

  // Gérer la fermeture du snackbar
  const handleSnackbarClose = () => {
    dispatch(hideSnackbar());
  };

  // Choisir le thème selon le mode
  const currentTheme = darkMode ? darkTheme : theme;

  // Locale pour date-fns (réactive)
  const dateFnsLocale = ({ 'fr-FR': fr, 'en-US': enUS, 'es-ES': es }[locale] || fr);

  if (authLoading) {
    return (
      <ThemeProvider theme={currentTheme}>
        <CssBaseline />
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}>
          Chargement...
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={dateFnsLocale}>
        <StripeWrapper>
          <AppRoutes />
        </StripeWrapper>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

function AppRoutes() {
  const { isAuthenticated, loading: authLoading, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const { snackbar } = useSelector((state) => state.ui);

  useEffect(() => {
    const init = async () => {
      if (isAuthenticated && !user) {
        try {
          await dispatch(getCurrentUser());
        } catch (_) {}
      }
    };
    init();
  }, [dispatch, isAuthenticated, user]);

  const handleSnackbarClose = () => {
    dispatch(hideSnackbar());
  };

  if (authLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Chargement...</div>
    );
  }

  return (
      <>
      <Routes>
        {/* Routes publiques */}
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        } />
        <Route path="/register" element={
          isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />
        } />
        
        {/* Routes protégées avec layout */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<HomePage />} />
          <Route path="events" element={<EventsPage />} />
          <Route path="events/:id" element={<EventDetailPage />} />
          <Route path="create-event" element={<CreateEventPage />} />
          <Route path="edit-event/:id" element={<EditEventPage />} />
          <Route path="my-events" element={<MyEventsPage />} />
          <Route path="my-registrations" element={<MyRegistrationsPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="super-admin" element={<SuperAdminDashboard />} />
          <Route path="scan" element={<QRCodeScannerPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        
        {/* Route de debug temporaire */}
        <Route path="/debug" element={<DebugAuth />} />
        
        {/* Route 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      {/* Snackbar global */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={snackbar.persist ? null : 6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
      </>
  );
}

// Mémoriser la promesse Stripe pour éviter les re-créations
const stripePublicKey = process.env.REACT_APP_STRIPE_PK || '';
const stripePromise = stripePublicKey ? loadStripe(stripePublicKey) : null;

// Composant wrapper pour Stripe pour éviter les changements de props
function StripeWrapper({ children }) {
  if (stripePromise) {
    return (
      <Elements stripe={stripePromise}>
        {children}
      </Elements>
    );
  }
  
  return children;
}

export default App; 