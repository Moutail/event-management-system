import React, { useState } from 'react';
import { Box, Button, Typography, Alert } from '@mui/material';

const SimpleAuthTest = () => {
  const [testResult, setTestResult] = useState(null);

  const testAuth = async () => {
    try {
      // Test simple de l'endpoint global_stats
      const response = await fetch('http://localhost:8000/api/admin/global_stats/', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      setTestResult({
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Données reçues:', data);
      } else {
        const errorText = await response.text();
        console.log('❌ Erreur:', errorText);
      }

    } catch (error) {
      setTestResult({
        error: error.message,
        type: 'network_error'
      });
      console.error('❌ Erreur réseau:', error);
    }
  };

  const testWithToken = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setTestResult({
          error: 'Aucun token trouvé dans localStorage',
          type: 'no_token'
        });
        return;
      }

      const response = await fetch('http://localhost:8000/api/admin/global_stats/', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      setTestResult({
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url,
        hasToken: true
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Données reçues avec token:', data);
      } else {
        const errorText = await response.text();
        console.log('❌ Erreur avec token:', errorText);
      }

    } catch (error) {
      setTestResult({
        error: error.message,
        type: 'network_error',
        hasToken: true
      });
      console.error('❌ Erreur réseau avec token:', error);
    }
  };

  const clearResult = () => {
    setTestResult(null);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        🧪 Test d'Authentification Simple
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Button 
          variant="contained" 
          onClick={testAuth}
          sx={{ mr: 2 }}
        >
          Test sans token
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={testWithToken}
          sx={{ mr: 2 }}
        >
          Test avec token
        </Button>
        
        <Button 
          variant="text" 
          onClick={clearResult}
        >
          Effacer
        </Button>
      </Box>

      {testResult && (
        <Alert 
          severity={testResult.error ? 'error' : (testResult.status === 200 ? 'success' : 'warning')}
          sx={{ mb: 2 }}
        >
          <Typography variant="h6" gutterBottom>
            Résultat du test
          </Typography>
          
          {testResult.error ? (
            <Typography>
              ❌ Erreur: {testResult.error}
              {testResult.type === 'no_token' && ' - Utilisez le composant TestAuth pour vous connecter'}
            </Typography>
          ) : (
            <Box>
              <Typography>
                Status: {testResult.status} {testResult.statusText}
              </Typography>
              <Typography>
                URL: {testResult.url}
              </Typography>
              <Typography>
                Token utilisé: {testResult.hasToken ? 'Oui' : 'Non'}
              </Typography>
              {testResult.status === 200 && (
                <Typography color="success.main">
                  ✅ Endpoint fonctionne correctement!
                </Typography>
              )}
              {testResult.status === 401 && (
                <Typography color="warning.main">
                  ⚠️ Authentification requise (comportement normal)
                </Typography>
              )}
              {testResult.status === 500 && (
                <Typography color="error.main">
                  ❌ Erreur serveur 500 détectée!
                </Typography>
              )}
            </Box>
          )}
        </Alert>
      )}

      <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          💡 Instructions
        </Typography>
        <Typography variant="body2" paragraph>
          1. <strong>Test sans token</strong> : Devrait retourner 401 (authentification requise)
        </Typography>
        <Typography variant="body2" paragraph>
          2. <strong>Test avec token</strong> : Nécessite d'être connecté via TestAuth
        </Typography>
        <Typography variant="body2" paragraph>
          3. Si vous obtenez une erreur 500, le problème est côté serveur
        </Typography>
        <Typography variant="body2">
          4. Si vous obtenez 401, c'est le comportement normal pour un utilisateur non connecté
        </Typography>
      </Box>
    </Box>
  );
};

export default SimpleAuthTest;
