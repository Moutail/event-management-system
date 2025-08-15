import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, CardHeader, Typography, Button, TextField, Alert
} from '@mui/material';
import api from '../services/api';

const DebugAuth = () => {
  const [authStatus, setAuthStatus] = useState({});
  const [testResult, setTestResult] = useState(null);
  const [eventId, setEventId] = useState('60');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    setAuthStatus({
      accessToken: accessToken ? `Présent (${accessToken.substring(0, 20)}...)` : 'Absent',
      refreshToken: refreshToken ? `Présent (${refreshToken.substring(0, 20)}...)` : 'Absent',
      hasTokens: !!(accessToken && refreshToken)
    });
  };

  const testEndpoint = async () => {
    setLoading(true);
    setTestResult(null);
    
    try {
      console.log('🔍 Test de l\'endpoint avec eventId:', eventId);
      console.log('🔍 Token présent:', !!localStorage.getItem('access_token'));
      
      const response = await api.get(`/admin/events/${eventId}/detail/`);
      
      console.log('✅ Succès:', response.status, response.data);
      setTestResult({
        success: true,
        status: response.status,
        data: response.data,
        message: 'Endpoint accessible avec succès!'
      });
    } catch (error) {
      console.error('❌ Erreur:', error);
      setTestResult({
        success: false,
        status: error.response?.status,
        error: error.message,
        responseData: error.response?.data,
        message: `Erreur ${error.response?.status}: ${error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    checkAuthStatus();
    setTestResult(null);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Card>
        <CardHeader 
          title="🔍 Debug - État d'Authentification" 
          subheader="Vérification de l'authentification et test des endpoints"
        />
        <CardContent>
          <Typography variant="h6" gutterBottom>État des Tokens</Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2">Access Token: {authStatus.accessToken}</Typography>
            <Typography variant="body2">Refresh Token: {authStatus.refreshToken}</Typography>
            <Typography variant="body2" color={authStatus.hasTokens ? 'success.main' : 'error.main'}>
              Statut: {authStatus.hasTokens ? 'Authentifié' : 'Non authentifié'}
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>Test de l'Endpoint</Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                label="Event ID"
                value={eventId}
                onChange={(e) => setEventId(e.target.value)}
                size="small"
                sx={{ width: 120 }}
              />
              <Button 
                variant="contained" 
                onClick={testEndpoint}
                disabled={loading}
              >
                {loading ? 'Test...' : 'Tester Endpoint'}
              </Button>
              <Button variant="outlined" onClick={clearTokens}>
                Effacer Tokens
              </Button>
            </Box>
          </Box>

          {testResult && (
            <Box sx={{ mt: 2 }}>
              <Alert severity={testResult.success ? 'success' : 'error'}>
                {testResult.message}
              </Alert>
              
              {testResult.success ? (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">Statut: {testResult.status}</Typography>
                  <Typography variant="body2">Données reçues: {JSON.stringify(testResult.data, null, 2)}</Typography>
                </Box>
              ) : (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">Statut: {testResult.status}</Typography>
                  <Typography variant="body2">Erreur: {testResult.error}</Typography>
                  {testResult.responseData && (
                    <Typography variant="body2">Réponse: {JSON.stringify(testResult.responseData, null, 2)}</Typography>
                  )}
                </Box>
              )}
            </Box>
          )}

          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>Instructions</Typography>
            <Typography variant="body2" paragraph>
              1. Vérifiez que vous êtes connecté en tant que Super Admin
            </Typography>
            <Typography variant="body2" paragraph>
              2. Cliquez sur "Tester Endpoint" pour vérifier l'API
            </Typography>
            <Typography variant="body2" paragraph>
              3. Si vous obtenez une erreur 401, reconnectez-vous
            </Typography>
            <Typography variant="body2" paragraph>
              4. Si vous obtenez une erreur 500, il y a un problème backend
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DebugAuth;
