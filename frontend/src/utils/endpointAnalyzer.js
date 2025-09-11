/**
 * Analyseur d'endpoints pour le frontend
 * Compare les URLs appelées par le frontend avec celles disponibles sur le backend
 */

// URLs appelées par le frontend (extrait de api.js)
export const FRONTEND_ENDPOINTS = {
  // Authentification
  auth: {
    login: 'POST /auth/token/',
    register: 'POST /auth/register/',
    refreshToken: 'POST /auth/token/refresh/',
    getCurrentUser: 'GET /auth/user/',
    logout: 'POST /auth/logout/',
    changePassword: 'POST /auth/change_password/',
    updateProfile: 'POST /auth/update_profile/',
  },

  // Événements
  events: {
    getEvents: 'GET /events/',
    getEventById: 'GET /events/{id}/',
    getEventParticipants: 'GET /events/{id}/participants/',
    getFeaturedEvents: 'GET /events/featured/',
    getUpcomingEvents: 'GET /events/upcoming/',
    getOngoingEvents: 'GET /events/ongoing/',
    getMyEvents: 'GET /events/my_events/',
    getEventStatistics: 'GET /events/statistics/',
    getTicketTypes: 'GET /events/{id}/ticket_types/',
    createTicketType: 'POST /events/{id}/ticket_types/',
    getSessionTypes: 'GET /events/{id}/session_types/',
    createSessionType: 'POST /events/{id}/session_types/',
    exportRegistrationsCSV: 'GET /events/{id}/export_registrations_csv/',
    exportRegistrationsExcel: 'GET /events/{id}/export_registrations_excel/',
    exportRegistrationsPDF: 'GET /events/{id}/export_registrations_pdf/',
    createEvent: 'POST /events/',
    updateEvent: 'PATCH /events/{id}/',
    deleteEvent: 'DELETE /events/{id}/',
    duplicateEvent: 'POST /events/{id}/duplicate/',
    publishEvent: 'POST /events/{id}/publish/',
    cancelEvent: 'POST /events/{id}/cancel/',
  },

  // Catégories et tags
  categories: {
    getCategories: 'GET /categories/',
    getTags: 'GET /tags/',
  },

  // Inscriptions
  registrations: {
    registerForEvent: 'POST /registrations/',
    getMyRegistrations: 'GET /registrations/',
    cancelRegistration: 'POST /registrations/{id}/cancel/',
    cancelPayment: 'POST /registrations/{id}/cancel_payment/',
    confirmRegistration: 'POST /registrations/{id}/confirm/',
    getRegistrationQr: 'GET /registrations/{id}/qr/',
    getUpcomingRegistrations: 'GET /registrations/upcoming/',
  },

  // Listes d'attente
  waitlist: {
    getWaitlistedRegistrations: 'GET /events/{id}/waitlisted_registrations/',
    approveWaitlist: 'POST /registrations/{id}/approve_waitlist/',
    rejectWaitlist: 'POST /registrations/{id}/reject_waitlist/',
  },

  // Remboursements
  refunds: {
    requestRefund: 'POST /registrations/{id}/request_refund/',
    processRefund: 'POST /refund/{id}/process/',
    getRefundRequests: 'GET /events/{id}/refund_requests/',
  },

  // Historique
  history: {
    getEventHistory: 'GET /history/',
  },

  // Administration
  admin: {
    getAllEvents: 'GET /admin/all_events/',
    getAllUsers: 'GET /admin/all_users/',
    bulkModerateEvents: 'POST /admin/bulk_moderate_events/',
    getGlobalStats: 'GET /admin/global_stats/',
    manageUser: 'POST /admin/manage_user/',
    moderateEvent: 'POST /admin/moderate_event/',
    getEventHistory: 'GET /admin/{id}/event_history/',
    getAnalytics: 'GET /admin/analytics/',
    getModeration: 'GET /admin/moderation/',
    getEventDetail: 'GET /admin/events/{id}/detail/',
    rejectEvent: 'POST /admin/events/{id}/reject/',
    deleteEvent: 'POST /admin/events/{id}/delete/',
    getRefunds: 'GET /admin/refunds/',
    processRefund: 'POST /admin/process_refund/',
    bulkProcessRefunds: 'POST /admin/bulk_process_refunds/',
    getPendingRegistrations: 'GET /admin/pending_registrations/',
    confirmRegistration: 'POST /admin/confirm_registration/',
    rejectRegistration: 'POST /admin/reject_registration/',
    bulkConfirmRegistrations: 'POST /admin/bulk_confirm_registrations/',
    getSystemHealth: 'GET /admin/system_health/',
    getPredictiveAnalytics: 'GET /admin/predictive_analytics/',
    trainMLModels: 'POST /admin/train_ml_models/',
    predictFillRate: 'POST /admin/predict_fill_rate/',
    optimizePricing: 'POST /admin/optimize_pricing/',
    getEmergingTrends: 'GET /admin/emerging_trends/',
    getMarketAnalysis: 'GET /admin/market_analysis/',
    getPredictiveInsights: 'GET /admin/predictive_insights/',
    generateContent: 'POST /admin/generate_content/',
    getPendingOrganizerApprovals: 'GET /admin/pending_organizer_approvals/',
    approveOrganizerAccount: 'POST /admin/approve_organizer_account/',
    rejectOrganizerAccount: 'POST /admin/reject_organizer_account/',
  },

  // Organisateur
  organizer: {
    getRefunds: 'GET /organizer/refunds/',
    processRefundRequest: 'POST /organizer/refunds/{id}/process/',
    bulkProcessRefunds: 'POST /organizer/bulk_process_refunds/',
  },

  // Événements virtuels
  virtualEvents: {
    getVirtualEvents: 'GET /virtual-events/',
    getVirtualEventById: 'GET /virtual-events/{id}/',
    getVirtualInteractions: 'GET /virtual-interactions/',
    getVirtualInteractionById: 'GET /virtual-interactions/{id}/',
  },

  // Rappels personnalisés
  customReminders: {
    getCustomReminders: 'GET /custom-reminders/',
    getCustomReminderById: 'GET /custom-reminders/{id}/',
  },

  // Streaming
  streaming: {
    createStream: 'POST /streaming/{id}/create/',
    getStreamStatus: 'GET /streaming/{id}/status/',
    updateStream: 'PUT /streaming/{id}/update/',
    deleteStream: 'DELETE /streaming/{id}/delete/',
    getStreamingInstructions: 'GET /streaming/{id}/instructions/',
    configureStream: 'POST /streaming/{id}/configure/',
    startStream: 'POST /streaming/{id}/start/',
    pauseStream: 'POST /streaming/{id}/pause/',
    stopStream: 'POST /streaming/{id}/stop/',
    joinStream: 'POST /streaming/{id}/join/',
    listPlatforms: 'GET /streaming/platforms/',
    testPlatformConnection: 'GET /streaming/platforms/{platform}/test/',
  },

  // IA
  ai: {
    chat: 'POST /ai/chat/',
    suggestions: 'GET /ai/suggestions/',
    helpEvent: 'GET /ai/help/event/{id}/',
    info: 'GET /ai/info/',
    feedback: 'POST /ai/feedback/',
  },

  // Fichiers
  files: {
    uploadFile: 'POST /upload/',
  },

  // Cron
  cron: {
    notifications: 'GET /cron/notifications/',
    test: 'GET /cron/test/',
  },

  // Health
  health: {
    healthCheck: 'GET /health/',
  },
};

/**
 * Analyse les endpoints du frontend et génère un rapport
 */
export class EndpointAnalyzer {
  constructor() {
    this.frontendEndpoints = this.extractAllEndpoints();
    this.analysis = {
      total: 0,
      byMethod: {},
      byCategory: {},
      missingBackend: [],
      extraBackend: [],
      inconsistencies: []
    };
  }

  /**
   * Extrait tous les endpoints du frontend
   */
  extractAllEndpoints() {
    const endpoints = [];
    
    Object.keys(FRONTEND_ENDPOINTS).forEach(category => {
      Object.keys(FRONTEND_ENDPOINTS[category]).forEach(endpointName => {
        const endpoint = FRONTEND_ENDPOINTS[category][endpointName];
        const [method, path] = endpoint.split(' ');
        
        endpoints.push({
          category,
          name: endpointName,
          method: method,
          path: path,
          fullEndpoint: endpoint
        });
      });
    });
    
    return endpoints;
  }

  /**
   * Analyse les endpoints et génère des statistiques
   */
  analyze() {
    this.analysis.total = this.frontendEndpoints.length;
    
    // Analyser par méthode HTTP
    this.frontendEndpoints.forEach(endpoint => {
      const method = endpoint.method;
      if (!this.analysis.byMethod[method]) {
        this.analysis.byMethod[method] = 0;
      }
      this.analysis.byMethod[method]++;
    });
    
    // Analyser par catégorie
    this.frontendEndpoints.forEach(endpoint => {
      const category = endpoint.category;
      if (!this.analysis.byCategory[category]) {
        this.analysis.byCategory[category] = 0;
      }
      this.analysis.byCategory[category]++;
    });
    
    return this.analysis;
  }

  /**
   * Compare avec les endpoints du backend
   */
  compareWithBackend(backendEndpoints) {
    const frontendPaths = this.frontendEndpoints.map(e => e.path);
    const backendPaths = backendEndpoints.map(e => e.pattern);
    
    // Endpoints du frontend manquants dans le backend
    this.analysis.missingBackend = frontendPaths.filter(path => 
      !backendPaths.some(backendPath => this.pathsMatch(path, backendPath))
    );
    
    // Endpoints du backend non utilisés par le frontend
    this.analysis.extraBackend = backendPaths.filter(backendPath => 
      !frontendPaths.some(path => this.pathsMatch(path, backendPath))
    );
    
    return this.analysis;
  }

  /**
   * Vérifie si deux chemins correspondent (en tenant compte des paramètres)
   */
  pathsMatch(frontendPath, backendPath) {
    // Normaliser les chemins
    const normalizePath = (path) => {
      return path
        .replace(/^\/api\//, '')
        .replace(/\{([^}]+)\}/g, '<\\w+:[^>]+>')
        .replace(/\{id\}/g, '<int:pk>')
        .replace(/\{event_id\}/g, '<int:event_id>')
        .replace(/\{registration_id\}/g, '<int:registration_id>')
        .replace(/\{refund_id\}/g, '<int:refund_id>')
        .replace(/\{refund_request_id\}/g, '<int:refund_request_id>')
        .replace(/\{platform\}/g, '<str:platform>')
        .replace(/\{format\}/g, '<str:format>');
    };
    
    const normalizedFrontend = normalizePath(frontendPath);
    const normalizedBackend = normalizePath(backendPath);
    
    return normalizedFrontend === normalizedBackend;
  }

  /**
   * Génère un rapport détaillé
   */
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalEndpoints: this.analysis.total,
        byMethod: this.analysis.byMethod,
        byCategory: this.analysis.byCategory,
        missingInBackend: this.analysis.missingBackend.length,
        extraInBackend: this.analysis.extraBackend.length
      },
      details: {
        missingInBackend: this.analysis.missingBackend,
        extraInBackend: this.analysis.extraBackend,
        inconsistencies: this.analysis.inconsistencies
      },
      recommendations: this.generateRecommendations()
    };
    
    return report;
  }

  /**
   * Génère des recommandations basées sur l'analyse
   */
  generateRecommendations() {
    const recommendations = [];
    
    if (this.analysis.missingBackend.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `${this.analysis.missingBackend.length} endpoints du frontend manquants dans le backend`,
        action: 'Vérifier que ces endpoints sont bien implémentés côté backend'
      });
    }
    
    if (this.analysis.extraBackend.length > 0) {
      recommendations.push({
        type: 'info',
        message: `${this.analysis.extraBackend.length} endpoints du backend non utilisés par le frontend`,
        action: 'Considérer la suppression ou l\'ajout de ces endpoints au frontend'
      });
    }
    
    // Vérifier les méthodes HTTP les plus utilisées
    const mostUsedMethod = Object.keys(this.analysis.byMethod).reduce((a, b) => 
      this.analysis.byMethod[a] > this.analysis.byMethod[b] ? a : b
    );
    
    if (mostUsedMethod === 'GET' && this.analysis.byMethod.GET > this.analysis.total * 0.6) {
      recommendations.push({
        type: 'info',
        message: 'Le frontend utilise principalement des requêtes GET',
        action: 'Vérifier que le cache est bien configuré pour optimiser les performances'
      });
    }
    
    return recommendations;
  }

  /**
   * Exporte les endpoints au format JSON
   */
  exportToJSON() {
    return JSON.stringify(this.generateReport(), null, 2);
  }

  /**
   * Exporte les endpoints au format CSV
   */
  exportToCSV() {
    const headers = ['Category', 'Name', 'Method', 'Path', 'Full Endpoint'];
    const rows = [headers.join(',')];
    
    this.frontendEndpoints.forEach(endpoint => {
      const row = [
        endpoint.category,
        endpoint.name,
        endpoint.method,
        endpoint.path,
        endpoint.fullEndpoint
      ].map(field => `"${field}"`).join(',');
      rows.push(row);
    });
    
    return rows.join('\n');
  }
}

/**
 * Fonction utilitaire pour analyser les endpoints
 */
export function analyzeEndpoints() {
  const analyzer = new EndpointAnalyzer();
  analyzer.analyze();
  return analyzer.generateReport();
}

/**
 * Fonction utilitaire pour tester un endpoint spécifique
 */
export async function testEndpoint(endpoint, baseURL = process.env.REACT_APP_API_URL) {
  const [method, path] = endpoint.split(' ');
  const url = `${baseURL}${path}`;
  
  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return {
      endpoint,
      url,
      status: response.status,
      success: response.ok,
      responseTime: Date.now() - performance.now()
    };
  } catch (error) {
    return {
      endpoint,
      url,
      status: 0,
      success: false,
      error: error.message
    };
  }
}

export default EndpointAnalyzer;
