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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Badge,
  Avatar,
  LinearProgress
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Event as EventIcon,
  AttachMoney as MoneyIcon,
  Settings as SettingsIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Block as BlockIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Category as CategoryIcon,
  LocalOffer as TagIcon,
  PersonAdd as PersonAddIcon
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
import TestAuth from '../components/TestAuth';
import SimpleAuthTest from '../components/SimpleAuthTest';

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

// Composant pour la gestion des utilisateurs
const UsersManagement = ({ users, onUserAction, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [actionData, setActionData] = useState({});

  const handleAction = (user, action) => {
    setSelectedUser(user);
    setActionType(action);
    setActionDialog(true);
    
    if (action === 'change_role') {
      setActionData({ new_role: user.role });
    } else {
      setActionData({});
    }
  };

  const confirmAction = async () => {
    try {
      await onUserAction(selectedUser.id, actionType, actionData);
      setActionDialog(false);
      setSelectedUser(null);
      setActionType('');
      setActionData({});
    } catch (error) {
      console.error('Erreur lors de l\'action:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = !roleFilter || user.role === roleFilter;
    const matchesStatus = !statusFilter || 
                         (statusFilter === 'active' && user.is_active) ||
                         (statusFilter === 'inactive' && !user.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

    return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            label="Rechercher"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon />
            }}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Rôle</InputLabel>
            <Select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              label="Rôle"
            >
              <MenuItem value="">Tous</MenuItem>
              <MenuItem value="super_admin">Super Admin</MenuItem>
              <MenuItem value="organizer">Organisateur</MenuItem>
              <MenuItem value="participant">Participant</MenuItem>
              <MenuItem value="guest">Invité</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Statut</InputLabel>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              label="Statut"
            >
              <MenuItem value="">Tous</MenuItem>
              <MenuItem value="active">Actif</MenuItem>
              <MenuItem value="inactive">Inactif</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Button
          variant="contained"
          startIcon={<PersonAddIcon />}
          onClick={() => window.dispatchEvent(new CustomEvent('openUserCreation'))}
          sx={{ ml: 2 }}
        >
          Créer un Utilisateur
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Utilisateur</TableCell>
              <TableCell>Rôle</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Statut</TableCell>
              <TableCell>Événements</TableCell>
              <TableCell>Inscriptions</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredUsers.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Avatar>{user.username[0].toUpperCase()}</Avatar>
                    <Box>
                      <Typography variant="subtitle2">{user.username}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {user.first_name} {user.last_name}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.role}
                    color={
                      user.role === 'super_admin' ? 'error' :
                      user.role === 'organizer' ? 'primary' :
                      user.role === 'participant' ? 'success' : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip
                    label={user.is_active ? 'Actif' : 'Inactif'}
                    color={user.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{user.event_count || 0}</TableCell>
                <TableCell>{user.registration_count || 0}</TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Voir le profil">
                      <IconButton size="small" color="primary">
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Changer le rôle">
                      <IconButton 
                        size="small" 
                        color="secondary"
                        onClick={() => handleAction(user, 'change_role')}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    {user.is_active ? (
                      <Tooltip title="Suspendre">
                        <IconButton 
                          size="small" 
                          color="warning"
                          onClick={() => handleAction(user, 'suspend')}
                        >
                          <BlockIcon />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      <Tooltip title="Réactiver">
                        <IconButton 
                          size="small" 
                          color="success"
                          onClick={() => handleAction(user, 'activate')}
                        >
                          <CheckIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Supprimer">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleAction(user, 'delete')}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog pour les actions */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)}>
        <DialogTitle>
          {actionType === 'suspend' && 'Suspendre l\'utilisateur'}
          {actionType === 'activate' && 'Réactiver l\'utilisateur'}
          {actionType === 'change_role' && 'Changer le rôle'}
          {actionType === 'delete' && 'Supprimer l\'utilisateur'}
        </DialogTitle>
        <DialogContent>
          {actionType === 'change_role' && (
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Nouveau rôle</InputLabel>
              <Select
                value={actionData.new_role || ''}
                onChange={(e) => setActionData({ ...actionData, new_role: e.target.value })}
                label="Nouveau rôle"
              >
                <MenuItem value="super_admin">Super Admin</MenuItem>
                <MenuItem value="organizer">Organisateur</MenuItem>
                <MenuItem value="participant">Participant</MenuItem>
                <MenuItem value="guest">Invité</MenuItem>
              </Select>
            </FormControl>
          )}
          
          {actionType === 'delete' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Cette action est irréversible. L'utilisateur sera définitivement supprimé.
            </Alert>
          )}
          
          <Typography variant="body2" sx={{ mt: 2 }}>
            Utilisateur: <strong>{selectedUser?.username}</strong>
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Annuler</Button>
          <Button 
            onClick={confirmAction} 
            color={actionType === 'delete' ? 'error' : 'primary'}
            variant="contained"
          >
            Confirmer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Composant pour la gestion des événements
const EventsManagement = ({ events, onEventAction, onViewEventDetails, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');

  const handleAction = (event, action) => {
    setSelectedEvent(event);
    setActionType(action);
    setActionDialog(true);
  };

  const confirmAction = async () => {
    try {
      await onEventAction(selectedEvent.id, actionType);
      setActionDialog(false);
      setSelectedEvent(null);
      setActionType('');
    } catch (error) {
      console.error('Erreur lors de l\'action:', error);
    }
  };

  const filteredEvents = events.filter(event => {
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || event.status === statusFilter;
    const matchesCategory = !categoryFilter || event.category === categoryFilter;
    
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'success';
      case 'draft': return 'default';
      case 'cancelled': return 'error';
      case 'completed': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box mb={3} display="flex" gap={2} alignItems="center">
        <TextField
          label="Rechercher"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon />
          }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Statut</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            label="Statut"
          >
            <MenuItem value="">Tous</MenuItem>
            <MenuItem value="published">Publié</MenuItem>
            <MenuItem value="draft">Brouillon</MenuItem>
            <MenuItem value="cancelled">Annulé</MenuItem>
            <MenuItem value="completed">Terminé</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Événement</TableCell>
              <TableCell>Organisateur</TableCell>
              <TableCell>Statut</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Participants</TableCell>
              <TableCell>Revenus</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEvents.map((event) => (
              <TableRow key={event.id}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2">{event.title}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {event.location}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2">{event.organizer.username}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {event.organizer.email}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={event.status}
                    color={getStatusColor(event.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2">
                      {new Date(event.start_date).toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {new Date(event.start_date).toLocaleTimeString()}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  {event.current_participants} / {event.max_participants}
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="success.main">
                    ${event.revenue}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Voir l'événement">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => onViewEventDetails(event)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    {event.status === 'draft' && (
                      <Tooltip title="Approuver">
                        <IconButton 
                          size="small" 
                          color="success"
                          onClick={() => handleAction(event, 'approve')}
                        >
                          <CheckIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {event.status === 'published' && (
                      <Tooltip title="Suspendre">
                        <IconButton 
                          size="small" 
                          color="warning"
                          onClick={() => handleAction(event, 'suspend')}
                        >
                          <BlockIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Supprimer">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleAction(event, 'delete')}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog pour les actions */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)}>
        <DialogTitle>
          {actionType === 'approve' && 'Approuver l\'événement'}
          {actionType === 'suspend' && 'Suspendre l\'événement'}
          {actionType === 'delete' && 'Supprimer l\'événement'}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Événement: <strong>{selectedEvent?.title}</strong>
          </Typography>
          
          {actionType === 'delete' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Cette action est irréversible. L'événement sera définitivement supprimé.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Annuler</Button>
          <Button 
            onClick={confirmAction} 
            color={actionType === 'delete' ? 'error' : 'primary'}
            variant="contained"
          >
            Confirmer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Composant principal du dashboard
const SuperAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [events, setEvents] = useState([]);
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
        
        // Charger les utilisateurs
        const usersResponse = await api.get('/admin/all_users/');
        setUsers(usersResponse.data.results || []);
        
        // Charger les événements (utiliser l'API existante)
        const eventsResponse = await api.get('/admin/all_events/');
        setEvents(eventsResponse.data.results || []);
        
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
        setUsers([]);
        setEvents([]);
      }
      
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      showSnackbar('Erreur lors du chargement des données', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (userId, action, data = {}) => {
    try {
      // Utiliser l'API réelle
      await api.post('/admin/manage_user/', {
        user_id: userId,
        action: action,
        ...data
      });
      
      showSnackbar('Action effectuée avec succès', 'success');
      loadDashboardData(); // Recharger les données
    } catch (error) {
      console.error('Erreur lors de l\'action utilisateur:', error);
      showSnackbar('Erreur lors de l\'action', 'error');
    }
  };

  const handleEventAction = async (eventId, action) => {
    try {
      // Utiliser l'API réelle
      await api.post('/admin/moderate_event/', {
        event_id: eventId,
        action: action
      });
      
      showSnackbar('Action effectuée avec succès', 'success');
      loadDashboardData(); // Recharger les données
    } catch (error) {
      console.error('Erreur lors de l\'action événement:', error);
      showSnackbar('Erreur lors de l\'action', 'error');
    }
  };

  const handleViewEventDetails = (event) => {
    console.log('🔍 handleViewEventDetails appelé avec:', event);
    setEventDetailModal({ open: true, eventId: event.id });
  };

  const handleUserCreated = (newUser) => {
    // Ajouter le nouvel utilisateur à la liste
    setUsers(prev => [newUser, ...prev]);
    
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
            <Tab label="Test Auth" icon={<PersonAddIcon />} />
            <Tab label="Test Simple" icon={<SettingsIcon />} />
          </Tabs>

          {/* Contenu des tabs */}
          {activeTab === 0 && (
            <UsersManagement
              users={users}
              onUserAction={handleUserAction}
              loading={loading}
            />
          )}

          {activeTab === 1 && (
            <EventsManagement
              events={events}
              onEventAction={handleEventAction}
              onViewEventDetails={handleViewEventDetails}
              loading={loading}
            />
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
            <TestAuth />
          )}

          {activeTab === 8 && (
            <SimpleAuthTest />
          )}
        </CardContent>
      </Card>

      {/* Snackbar pour les notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
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
