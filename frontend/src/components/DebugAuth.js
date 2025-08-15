import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, TextField } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { login, getCurrentUser } from '../store/slices/authSlice';
import api from '../services/api';

const DebugAuth = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading } = useSelector((state) => state.auth);
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [testResult, setTestResult] = useState('');

  const handleLogin = async () => {
    try {
      setTestResult('Tentative de connexion...');
      const result = await dispatch(login(credentials));
      if (login.fulfilled.match(result)) {
        setTestResult('✅ Connexion réussie !');
      } else {
        setTestResult(`❌ Erreur: ${result.payload}`);
      }
    } catch (error) {
      setTestResult(`❌ Erreur: ${error.message}`);
    }
  };

  const testAPI = async () => {
    try {
      setTestResult('Test de l\'API...');
      const response = await api.get('/auth/user/');
      setTestResult(`✅ API OK: ${JSON.stringify(response.data, null, 2)}`);
    } catch (error) {
      setTestResult(`❌ API Error: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
    }
  };

  const testToken = () => {
    const token = localStorage.getItem('access_token');
    const refresh = localStorage.getItem('refresh_token');
    setTestResult(`Token: ${token ? '✅ Présent' : '❌ Absent'}\nRefresh: ${refresh ? '✅ Présent' : '❌ Absent'}`);
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setTestResult('Tokens supprimés');
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          🔧 Debug Authentification
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">État actuel:</Typography>
          <Typography>Authentifié: {isAuthenticated ? '✅ Oui' : '❌ Non'}</Typography>
          <Typography>Utilisateur: {user ? user.username : 'Aucun'}</Typography>
          <Typography>Chargement: {loading ? '🔄 Oui' : '⏸️ Non'}</Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">Connexion:</Typography>
          <TextField
            fullWidth
            label="Nom d'utilisateur"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Mot de passe"
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handleLogin} sx={{ mr: 1 }}>
            Se connecter
          </Button>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">Tests:</Typography>
          <Button variant="outlined" onClick={testAPI} sx={{ mr: 1, mb: 1 }}>
            Test API
          </Button>
          <Button variant="outlined" onClick={testToken} sx={{ mr: 1, mb: 1 }}>
            Vérifier Tokens
          </Button>
          <Button variant="outlined" onClick={clearTokens} sx={{ mr: 1, mb: 1 }}>
            Nettoyer Tokens
          </Button>
        </Box>

        <Box>
          <Typography variant="h6">Résultat:</Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.100', fontFamily: 'monospace', fontSize: '0.875rem' }}>
            {testResult || 'Aucun test effectué'}
          </Paper>
        </Box>
      </Paper>
    </Box>
  );
};

export default DebugAuth;
