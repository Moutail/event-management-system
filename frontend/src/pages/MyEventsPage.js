import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  Chip,
  Box,
  CircularProgress,
  Alert,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { fetchMyEvents, deleteEvent, publishEvent, cancelEvent } from '../store/slices/eventSlice';
import { getImageUrl } from '../services/api';

const MyEventsPage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { myEvents, loading, error } = useSelector((state) => state.events);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState(null);

  useEffect(() => {
    dispatch(fetchMyEvents());
  }, [dispatch]);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleSearch = () => {
    // Implémenter la recherche côté client ou côté serveur
    console.log('Recherche:', searchTerm);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
  };

  const handleDeleteClick = (event) => {
    setEventToDelete(event);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (eventToDelete) {
      try {
        await dispatch(deleteEvent(eventToDelete.id)).unwrap();
        dispatch(fetchMyEvents()); // Recharger la liste
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
    setDeleteDialogOpen(false);
    setEventToDelete(null);
  };

  const handlePublishEvent = async (eventId) => {
    try {
      await dispatch(publishEvent(eventId)).unwrap();
      dispatch(fetchMyEvents()); // Recharger la liste
    } catch (error) {
      console.error('Erreur lors de la publication:', error);
    }
  };

  const handleCancelEvent = async (eventId) => {
    try {
      await dispatch(cancelEvent(eventId)).unwrap();
      dispatch(fetchMyEvents()); // Recharger la liste
    } catch (error) {
      console.error('Erreur lors de l\'annulation:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'published':
        return 'success';
      case 'cancelled':
        return 'error';
      case 'completed':
        return 'info';
      case 'postponed':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'draft':
        return 'Brouillon';
      case 'published':
        return 'Publié';
      case 'cancelled':
        return 'Annulé';
      case 'completed':
        return 'Terminé';
      case 'postponed':
        return 'Reporté';
      default:
        return status;
    }
  };

  const filteredEvents = myEvents.filter((event) => {
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || event.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const eventsPerPage = 6;
  const totalPages = Math.ceil(filteredEvents.length / eventsPerPage);
  const paginatedEvents = filteredEvents.slice(
    (page - 1) * eventsPerPage,
    page * eventsPerPage
  );

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Mes événements
        </Typography>
        <Fab
          color="primary"
          aria-label="ajouter"
          onClick={() => navigate('/events/create')}
        >
          <AddIcon />
        </Fab>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {typeof error === 'string' ? error : error.detail || error.message || 'Une erreur est survenue'}
        </Alert>
      )}

      {/* Filtres */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
          <TextField
            placeholder="Rechercher un événement..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            sx={{ minWidth: 300 }}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
          />
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filtres
          </Button>
          {(searchTerm || statusFilter) && (
            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={handleClearFilters}
            >
              Effacer
            </Button>
          )}
        </Box>

        {showFilters && (
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Statut</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Statut"
              >
                <MenuItem value="">Tous les statuts</MenuItem>
                <MenuItem value="draft">Brouillon</MenuItem>
                <MenuItem value="published">Publié</MenuItem>
                <MenuItem value="cancelled">Annulé</MenuItem>
                <MenuItem value="completed">Terminé</MenuItem>
                <MenuItem value="postponed">Reporté</MenuItem>
              </Select>
            </FormControl>
          </Box>
        )}
      </Box>

      {/* Liste des événements */}
      {paginatedEvents.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Aucun événement trouvé
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm || statusFilter 
              ? 'Aucun événement ne correspond à vos critères de recherche.'
              : 'Vous n\'avez pas encore créé d\'événements.'
            }
          </Typography>
          {!searchTerm && !statusFilter && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/events/create')}
              sx={{ mt: 2 }}
            >
              Créer votre premier événement
            </Button>
          )}
        </Box>
      ) : (
        <>
          <Grid container spacing={3}>
            {Array.isArray(paginatedEvents) && paginatedEvents.map((event) => (
              <Grid item xs={12} md={6} lg={4} key={event.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {event.poster && (
                    <CardMedia
                      component="img"
                      height="200"
                      image={getImageUrl(event.poster)}
                      alt={event.title}
                      sx={{ objectFit: 'cover' }}
                    />
                  )}
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="h6" component="h2" sx={{ flex: 1, mr: 1 }}>
                        {event.title}
                      </Typography>
                      <Chip
                        label={getStatusLabel(event.status)}
                        color={getStatusColor(event.status)}
                        size="small"
                      />
                    </Box>
                    
                    {event.short_description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {event.short_description}
                      </Typography>
                    )}

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        📅 {format(new Date(event.start_date), 'dd MMM yyyy à HH:mm', { locale: fr })}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        📍 {event.location}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {event.is_free ? '🆓 Gratuit' : `💰 ${event.price}€`}
                      </Typography>
                      {event.place_type === 'limited' && (
                        <Typography variant="body2" color="text.secondary">
                          👥 {event.current_registrations}/{event.max_capacity} inscrits
                        </Typography>
                      )}
                    </Box>

                    {event.tags && event.tags.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                        {event.tags.slice(0, 3).map((tag) => (
                          <Chip
                            key={tag.id}
                            label={tag.name}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                        {event.tags.length > 3 && (
                          <Chip
                            label={`+${event.tags.length - 3}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    )}
                  </CardContent>
                  
                  <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
                    <Box>
                      <Tooltip title="Voir l'événement">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/events/${event.id}`)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Modifier">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/events/${event.id}/edit`)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Supprimer">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteClick(event)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    <Box>
                      {event.status === 'draft' && (
                        <Button
                          size="small"
                          variant="outlined"
                          color="success"
                          onClick={() => handlePublishEvent(event.id)}
                        >
                          Publier
                        </Button>
                      )}
                      {event.status === 'published' && (
                        <Button
                          size="small"
                          variant="outlined"
                          color="warning"
                          onClick={() => handleCancelEvent(event.id)}
                        >
                          Annuler
                        </Button>
                      )}
                    </Box>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* Dialog de confirmation de suppression */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer l'événement "{eventToDelete?.title}" ?
            Cette action est irréversible.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Annuler
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MyEventsPage; 