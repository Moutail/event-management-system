import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  Button,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Badge,
  Avatar,
  CardMedia,
  Snackbar
} from '@mui/material';
import EventDetailModal from './EventDetailModal';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  Event as EventIcon
} from '@mui/icons-material';
import api from '../services/api';

const EventModeration = () => {
  const [pendingEvents, setPendingEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [reason, setReason] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedEventForDetail, setSelectedEventForDetail] = useState(null);

  useEffect(() => {
    loadPendingEvents();
  }, []);

  const loadPendingEvents = async () => {
    try {
      setLoading(true);
      console.log('🔄 Chargement des événements en attente...');
      const response = await api.get('/admin/moderation/');
      console.log('📊 Réponse API:', response.data);
      
      const events = response.data.pending_events || [];
      console.log('📋 Événements chargés:', events);
      console.log('📊 Nombre d\'événements:', events.length);
      
      setPendingEvents(events);
    } catch (error) {
      console.error('❌ Erreur lors du chargement des événements en attente:', error);
      showSnackbar('Erreur lors du chargement des événements', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (event, action) => {
    setSelectedEvent(event);
    setActionType(action);
    setActionDialog(true);
    setReason('');
  };

  const handleViewDetails = (event) => {
    console.log('🔍 handleViewDetails appelé avec:', event);
    console.log('🔍 Type de event:', typeof event);
    console.log('🔍 Event ID:', event?.id);
    console.log('🔍 Event title:', event?.title);
    
    if (!event || !event.id) {
      console.error('❌ Événement invalide:', event);
      return;
    }
    
    setSelectedEventForDetail(event);
    setDetailModalOpen(true);
    console.log('🔍 Modal ouvert:', true);
    console.log('🔍 Événement sélectionné:', event);
  };

  const handleEventAction = (action, eventId) => {
    // Rafraîchir la liste après une action
    loadPendingEvents();
    showSnackbar(`Événement ${action === 'rejected' ? 'rejeté' : 'supprimé'} avec succès`, 'success');
  };

  const confirmAction = async () => {
    try {
      await api.post('/admin/moderate_event/', {
        event_id: selectedEvent.id,
        action: actionType,
        reason: reason
      });
      
      showSnackbar('Action effectuée avec succès', 'success');
      setActionDialog(false);
      loadPendingEvents();
    } catch (error) {
      console.error('Erreur lors de l\'action:', error);
      showSnackbar('Erreur lors de l\'action', 'error');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft': return 'warning';
      case 'published': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'draft': return 'Brouillon';
      case 'published': return 'Publié';
      case 'cancelled': return 'Annulé';
      default: return status;
    }
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
    <Box>
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <EventIcon />
              Modération des Événements
            </Box>
          }
          subheader={`${pendingEvents.length} événement(s) en attente de modération`}
          action={
            <Button
              startIcon={<RefreshIcon />}
              onClick={loadPendingEvents}
              variant="outlined"
              size="small"
            >
              Actualiser
            </Button>
          }
        />
        <CardContent>
          {pendingEvents.length === 0 ? (
            <Alert severity="info">
              Aucun événement en attente de modération
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {pendingEvents.map((event) => (
                <Grid item xs={12} md={6} key={event.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" gap={2}>
                        {event.poster && (
                          <CardMedia
                            component="img"
                            sx={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 1 }}
                            image={event.poster}
                            alt={event.title}
                          />
                        )}
                        <Box flex={1}>
                          <Typography variant="h6" gutterBottom>
                            {event.title}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Organisateur: {event.organizer}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Date: {new Date(event.start_date).toLocaleDateString('fr-FR')}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Prix: ${event.price}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Créé le: {new Date(event.created_at).toLocaleDateString('fr-FR')}
                          </Typography>
                          
                          <Box mt={2} display="flex" gap={1}>
                            <Tooltip title="Voir les détails">
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  console.log('🔍 Clic sur le bouton œil pour l\'événement:', event);
                                  handleViewDetails(event);
                                }}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Approuver">
                              <IconButton 
                                size="small" 
                                color="success"
                                onClick={() => handleAction(event, 'approve')}
                              >
                                <ApproveIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Rejeter">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleAction(event, 'reject')}
                              >
                                <RejectIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Demander des modifications">
                              <IconButton 
                                size="small" 
                                color="warning"
                                onClick={() => handleAction(event, 'suspend')}
                              >
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Dialog pour les actions */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actionType === 'approve' && 'Approuver l\'événement'}
          {actionType === 'reject' && 'Rejeter l\'événement'}
          {actionType === 'suspend' && 'Demander des modifications'}
        </DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <Typography variant="body2" gutterBottom>
              <strong>Événement:</strong> {selectedEvent?.title}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Organisateur:</strong> {selectedEvent?.organizer}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Date:</strong> {selectedEvent?.start_date && new Date(selectedEvent.start_date).toLocaleDateString('fr-FR')}
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Raison de la décision"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              sx={{ mt: 2 }}
              placeholder={
                actionType === 'approve' 
                  ? 'Commentaire d\'approbation (optionnel)'
                  : actionType === 'reject'
                  ? 'Raison du rejet (requis)'
                  : 'Détails des modifications demandées (requis)'
              }
              required={actionType !== 'approve'}
            />
            
            {actionType === 'reject' && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                L'événement sera marqué comme annulé et l'organisateur sera notifié.
              </Alert>
            )}
            
            {actionType === 'suspend' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                L'événement sera remis en brouillon pour permettre les modifications.
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(false)}>Annuler</Button>
          <Button 
            onClick={confirmAction} 
            color={
              actionType === 'approve' ? 'success' : 
              actionType === 'reject' ? 'error' : 'warning'
            }
            variant="contained"
            disabled={
              (actionType === 'reject' || actionType === 'suspend') && !reason.trim()
            }
          >
            {actionType === 'approve' ? 'Approuver' : 
             actionType === 'reject' ? 'Rejeter' : 'Suspendre'}
          </Button>
        </DialogActions>
      </Dialog>

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

      {/* Modal de détails de l'événement */}
      <EventDetailModal
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        eventId={selectedEventForDetail?.id}
        onEventAction={handleEventAction}
      />
    </Box>
  );
};

export default EventModeration;
