import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Snackbar, Alert } from '@mui/material';

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

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, loading: authLoading, user } = useSelector((state) => state.auth);
  const { darkMode } = useSelector((state) => state.ui);
  const { snackbar } = useSelector((state) => state.ui);

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
      // Pas besoin de les charger globalement ici
    };

    initializeApp();
  }, [dispatch, isAuthenticated, user]);

  // Gérer la fermeture du snackbar
  const handleSnackbarClose = () => {
    dispatch(hideSnackbar());
  };

  // Choisir le thème selon le mode
  const currentTheme = darkMode ? darkTheme : theme;

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
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        
        {/* Route 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>

      {/* Snackbar global */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
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
    </ThemeProvider>
  );
}

export default App; 