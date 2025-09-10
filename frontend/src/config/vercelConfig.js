// 🔧 Configuration spécifique pour Vercel
// Gère les problèmes de déploiement et d'environnement

export const VERCEL_CONFIG = {
  // Détection de l'environnement Vercel
  isVercel: process.env.NODE_ENV === 'production' && 
            (window.location.hostname.includes('vercel') || 
             window.location.hostname.includes('vercel.app')),
  
  // Configuration des URLs
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  baseUrl: process.env.REACT_APP_BASE_URL || 'http://localhost:8000',
  
  // Configuration des sessions
  useLocalStorage: process.env.NODE_ENV === 'production',
  
  // Configuration du debug
  debugMode: process.env.REACT_APP_DEBUG_MODE === 'true',
  
  // Configuration Stripe
  stripePk: process.env.REACT_APP_STRIPE_PK,
  
  // Configuration de l'authentification sociale
  socialAuth: {
    enabled: process.env.REACT_APP_SOCIAL_AUTH_ENABLED === 'true',
    googleClientId: process.env.REACT_APP_GOOGLE_CLIENT_ID,
    facebookAppId: process.env.REACT_APP_FACEBOOK_APP_ID,
    successUrl: process.env.REACT_APP_SOCIAL_AUTH_SUCCESS_URL || '/dashboard',
    failureUrl: process.env.REACT_APP_SOCIAL_AUTH_FAILURE_URL || '/login?error=social_auth_failed'
  }
};

// Fonction pour vérifier la configuration
export const validateConfig = () => {
  const errors = [];
  
  if (!VERCEL_CONFIG.apiUrl) {
    errors.push('REACT_APP_API_URL manquante');
  }
  
  if (!VERCEL_CONFIG.baseUrl) {
    errors.push('REACT_APP_BASE_URL manquante');
  }
  
  if (VERCEL_CONFIG.socialAuth.enabled && !VERCEL_CONFIG.socialAuth.googleClientId) {
    errors.push('REACT_APP_GOOGLE_CLIENT_ID manquante pour l\'authentification sociale');
  }
  
  if (VERCEL_CONFIG.socialAuth.enabled && !VERCEL_CONFIG.socialAuth.facebookAppId) {
    errors.push('REACT_APP_FACEBOOK_APP_ID manquante pour l\'authentification sociale');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Fonction pour logger la configuration (en mode debug)
export const logConfig = () => {
  if (VERCEL_CONFIG.debugMode) {
    console.log('🔧 [VERCEL_CONFIG] Configuration chargée:', {
      isVercel: VERCEL_CONFIG.isVercel,
      apiUrl: VERCEL_CONFIG.apiUrl,
      baseUrl: VERCEL_CONFIG.baseUrl,
      useLocalStorage: VERCEL_CONFIG.useLocalStorage,
      debugMode: VERCEL_CONFIG.debugMode,
      stripeConfigured: !!VERCEL_CONFIG.stripePk,
      socialAuthEnabled: VERCEL_CONFIG.socialAuth.enabled
    });
  }
};

export default VERCEL_CONFIG;
