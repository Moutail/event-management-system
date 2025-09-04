import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom';
import { login } from '../store/slices/authSlice';
import SocialAuthButtons from '../components/Auth/SocialAuthButtons';

const LoginPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error, isAuthenticated, user } = useSelector((state) => state.auth);
  
  // Récupérer le message de la page d'accueil publique
  const messageFromHome = location.state?.message;

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  
  const [localLoading, setLocalLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalLoading(true);
    
    try {
      const result = await dispatch(login(formData));
      if (login.fulfilled.match(result)) {
        // Redirection intelligente selon le rôle
        const user = result.payload;
        
        if (user.profile?.role === 'super_admin') {
          // Super Admin va directement au dashboard Super Admin
          navigate('/dashboard/super-admin');
        } else if (user.profile?.role === 'organizer') {
          // Organisateur approuvé va au dashboard organisateur
          navigate('/dashboard/organizer');
        } else {
          // Participant va à la page d'accueil publique
          navigate('/');
        }
      }
    } catch (error) {
      console.error('❌ [LOGIN_PAGE] Erreur lors de la connexion:', error);
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h5">
            Connexion
          </Typography>

          {/* Message de la page d'accueil publique */}
          {messageFromHome && (
            <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
              {messageFromHome}
            </Alert>
          )}

          {isAuthenticated && (
            <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
              Vous êtes déjà connecté en tant que <strong>{user?.username}</strong> ({user?.profile?.role === 'super_admin' ? 'Super Admin' : user?.profile?.role === 'organizer' ? 'Organisateur' : 'Participant'}). 
              <br />
                              <Button 
                  variant="text" 
                  color="primary" 
                  onClick={() => {
                    if (user?.profile?.role === 'super_admin') {
                      navigate('/dashboard/super-admin');
                    } else if (user?.profile?.role === 'organizer') {
                      navigate('/dashboard/organizer');
                    } else {
                      navigate('/');
                    }
                  }}
                  sx={{ p: 0, minWidth: 'auto', textTransform: 'none' }}
                >
                  {user?.profile?.role === 'participant' ? 'Aller à l\'accueil' : 'Aller au dashboard'}
                </Button>
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {typeof error === 'string' ? error : error.detail || error.message || 'Une erreur est survenue'}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Nom d'utilisateur"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Mot de passe"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
            />
                      <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={localLoading}
          >
            {localLoading ? 'Connexion...' : 'Se connecter'}
          </Button>
          
          {/* 🔐 Boutons d'authentification sociale */}
          <SocialAuthButtons 
            onSuccess={(data) => {
              console.log('✅ [LOGIN_PAGE] Social auth success:', data);
              // Redirection intelligente selon le rôle
              if (data.user.profile?.role === 'super_admin') {
                navigate('/dashboard/super-admin');
              } else if (data.user.profile?.role === 'organizer') {
                navigate('/dashboard/organizer');
              } else {
                navigate('/');
              }
            }}
            onError={(error) => {
              console.error('❌ [LOGIN_PAGE] Social auth error:', error);
              // Gérer l'erreur (afficher un message, etc.)
            }}
            loading={localLoading}
            setLoading={setLocalLoading}
          />
            <Box sx={{ textAlign: 'center' }}>
              <Link component={RouterLink} to="/register" variant="body2">
                {"Vous n'avez pas de compte ? Inscrivez-vous"}
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage; 