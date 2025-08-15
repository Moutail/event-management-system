import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material';
import api from '../services/api';

const TestAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [credentials, setCredentials] = useState({
    username: 'frontend_test_admin',
    password: 'testpass123'
  });
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await api.post('/token/', credentials);
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      setToken(access);
      
      setSuccess('Connexion réussie!');
    } catch (err) {
      setError(`Erreur de connexion: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testGlobalStats = async () => {
    if (!token) {
      setError('Veuillez d\'abord vous connecter');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await api.get('/admin/global_stats/');
      setSuccess(`global_stats fonctionne! Utilisateurs: ${response.data.general_stats.total_users}`);
    } catch (err) {
      setError(`Erreur global_stats: ${err.response?.status} - ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setSuccess('Tokens supprimés');
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🧪 Test d'Authentification Admin
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            État de l'authentification
          </Typography>
          
          {token ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              ✅ Connecté avec token: {token.substring(0, 20)}...
            </Alert>
          ) : (
            <Alert severity="warning" sx={{ mb: 2 }}>
              ⚠️ Non connecté
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button 
              variant="contained" 
              onClick={handleLogin}
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> : 'Se connecter'}
            </Button>
            
            <Button 
              variant="outlined" 
              onClick={testGlobalStats}
              disabled={!token || loading}
            >
              Tester global_stats
            </Button>
            
            <Button 
              variant="outlined" 
              color="secondary"
              onClick={clearTokens}
            >
              Effacer tokens
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Informations de connexion
          </Typography>
          
          <TextField
            label="Username"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
            fullWidth
            sx={{ mb: 2 }}
          />
          
          <TextField
            label="Password"
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
            fullWidth
            sx={{ mb: 2 }}
          />
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          ❌ {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          ✅ {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Debug Info
          </Typography>
          
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            Base URL: {process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}
          </Typography>
          
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            Token présent: {token ? 'Oui' : 'Non'}
          </Typography>
          
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            LocalStorage: {localStorage.getItem('access_token') ? 'Token trouvé' : 'Aucun token'}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TestAuth;
