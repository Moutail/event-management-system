import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Snackbar,
  CircularProgress,
  Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Event as EventIcon,
  AttachMoney as MoneyIcon,
  Settings as SettingsIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingIcon,
  Refresh as RefreshIcon,
  Category as CategoryIcon,
  LocalOffer as TagIcon
} from '@mui/icons-material';
import api from '../services/api';

// Import des composants
import SuperAdminRefundManagement from '../components/SuperAdminRefundManagement';
import PlatformAnalytics from '../components/PlatformAnalytics';
import EventModeration from '../components/EventModeration';
import CategoryTagManagement from '../components/CategoryTagManagement';
import SystemHealth from '../components/SystemHealth';
import UserCreationModal from '../components/UserCreationModal';
import EventDetailModal from '../components/EventDetailModal';
import DebugAuth from '../components/DebugAuth';
import UserManagement from '../components/UserManagement';
import EventManagement from '../components/EventManagement';

// Composant pour les statistiques
const StatsCard = ({ title, value, subtitle, icon, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="h4" component="div" color={color}>
            {value}
          </Typography>
          <Typography variant="h6" color="textSecondary">
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="textSecondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box color={color}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

// Composant principal du dashboard
const SuperAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [userCreationModal, setUserCreationModal] = useState(false);
  const [eventDetailModal, setEventDetailModal] = useState({ open: false, eventId: null });

  useEffect(() => {
    loadDashboardData();
    
    // Écouteur pour ouvrir le modal de création d'utilisateur
    const handleOpenUserCreation = () => setUserCreationModal(true);
    window.addEventListener('openUserCreation', handleOpenUserCreation);
    
    return () => {
      window.removeEventListener('openUserCreation', handleOpenUserCreation);
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Utiliser les vraies APIs
      try {
        // Charger les statistiques
        const statsResponse = await api.get('/admin/global_stats/');
        const statsData = statsResponse.data;
        
        // Formater les statistiques pour l'affichage
        const formattedStats = {
          total_users: statsData.general_stats.total_users,
          total_events: statsData.general_stats.total_events,
          total_registrations: statsData.general_stats.total_registrations,
          total_revenue: statsData.general_stats.total_revenue,
          active_users: statsData.general_stats.active_users,
          pending_approvals: statsData.general_stats.pending_events,
          pending_refunds: 0 // À implémenter si nécessaire
        };
        
        setStats(formattedStats);
        
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
        showSnackbar('Erreur lors du chargement des données', 'error');
        
        // En cas d'erreur, utiliser des données par défaut
        setStats({
          total_users: 0,
          total_events: 0,
          total_registrations: 0,
          total_revenue: 0,
          active_users: 0,
          pending_approvals: 0,
          pending_refunds: 0
        });
      }
      
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      showSnackbar('Erreur lors du chargement des données', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleViewEventDetails = (event) => {
    console.log('🔍 handleViewEventDetails appelé avec:', event);
    setEventDetailModal({ open: true, eventId: event.id });
  };

  const handleUserCreated = (newUser) => {
    // Mettre à jour les statistiques
    setStats(prev => ({
      ...prev,
      total_users: (prev.total_users || 0) + 1,
      active_users: (prev.active_users || 0) + 1
    }));
    
    showSnackbar('Utilisateur créé avec succès', 'success');
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Dashboard Super Admin
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gestion complète de la plateforme d'événements
        </Typography>
      </Box>

      {/* Statistiques globales */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Utilisateurs"
              value={stats.total_users || 0}
              subtitle={`${stats.active_users || 0} actifs`}
              icon={<PeopleIcon />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Événements"
              value={stats.total_events || 0}
              subtitle={`${stats.pending_approvals || 0} en attente`}
              icon={<EventIcon />}
              color="secondary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Inscriptions"
              value={stats.total_registrations || 0}
              subtitle="Total des inscriptions"
              icon={<PeopleIcon />}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Revenus"
              value={`$${stats.total_revenue || 0}`}
              subtitle="Total des ventes"
              icon={<MoneyIcon />}
              color="warning"
            />
          </Grid>
        </Grid>
      )}

      {/* Tabs de navigation */}
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <DashboardIcon />
              Gestion de la plateforme
            </Box>
          }
          action={
            <Button
              startIcon={<RefreshIcon />}
              onClick={loadDashboardData}
              variant="outlined"
            >
              Actualiser
            </Button>
          }
        />
        <CardContent>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
          >
            <Tab label="Utilisateurs" icon={<PeopleIcon />} />
            <Tab label="Événements" icon={<EventIcon />} />
            <Tab label="Modération" icon={<WarningIcon />} />
            <Tab label="Remboursements" icon={<MoneyIcon />} />
            <Tab label="Analytics" icon={<TrendingIcon />} />
            <Tab label="Catégories & Tags" icon={<CategoryIcon />} />
            <Tab label="Système" icon={<SettingsIcon />} />
            <Tab label="Debug Auth" icon={<SettingsIcon />} />
          </Tabs>

          {/* Contenu des tabs */}
          {activeTab === 0 && (
            <UserManagement />
          )}

          {activeTab === 1 && (
            <EventManagement />
          )}

          {activeTab === 2 && (
            <EventModeration />
          )}

          {activeTab === 3 && (
            <SuperAdminRefundManagement />
          )}

          {activeTab === 4 && (
            <PlatformAnalytics />
          )}

          {activeTab === 5 && (
            <CategoryTagManagement />
          )}

          {activeTab === 6 && (
            <SystemHealth />
          )}

          {activeTab === 7 && (
            <DebugAuth />
          )}
        </CardContent>
      </Card>

      {/* Snackbar pour les notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Box>
          <Typography variant="body2">
            {snackbar.message}
          </Typography>
        </Box>
      </Snackbar>

      {/* Modal de création d'utilisateur */}
      <UserCreationModal
        open={userCreationModal}
        onClose={() => setUserCreationModal(false)}
        onUserCreated={handleUserCreated}
      />

      {/* Modal de détails de l'événement */}
      <EventDetailModal
        open={eventDetailModal.open}
        onClose={() => setEventDetailModal({ open: false, eventId: null })}
        eventId={eventDetailModal.eventId}
        onEventAction={(action, eventId) => {
          console.log('🔍 Action sur événement:', action, eventId);
          setEventDetailModal({ open: false, eventId: null });
          loadDashboardData(); // Recharger les données
        }}
      />
    </Container>
  );
};

export default SuperAdminDashboard;
