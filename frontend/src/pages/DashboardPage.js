import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  Event as EventIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  AttachMoney as MoneyIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { fetchEventStatistics, fetchMyEvents, fetchUpcomingEvents } from '../store/slices/eventSlice';

const DashboardPage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { statistics, myEvents, upcomingEvents, loading, error } = useSelector((state) => state.events);

  useEffect(() => {
    dispatch(fetchEventStatistics());
    dispatch(fetchMyEvents());
    dispatch(fetchUpcomingEvents());
  }, [dispatch]);

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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'draft':
        return <WarningIcon />;
      case 'published':
        return <CheckCircleIcon />;
      case 'cancelled':
        return <ErrorIcon />;
      case 'completed':
        return <CheckCircleIcon />;
      case 'postponed':
        return <WarningIcon />;
      default:
        return <EventIcon />;
    }
  };

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
      <Typography variant="h4" component="h1" gutterBottom>
        Tableau de bord
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {typeof error === 'string' ? error : error.detail || error.message || 'Une erreur est survenue'}
        </Alert>
      )}

      {/* Statistiques générales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <EventIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {statistics?.total_events || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total événements
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <PeopleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {statistics?.total_registrations || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total inscriptions
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {statistics?.upcoming_events || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Événements à venir
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <MoneyIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {statistics?.total_revenue || 0}€
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Revenus totaux
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Mes événements récents */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2">
                Mes événements récents
              </Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => navigate('/events/create')}
              >
                Créer
              </Button>
            </Box>

            {myEvents && myEvents.length > 0 ? (
              <List>
                {Array.isArray(myEvents) && myEvents.slice(0, 5).map((event, index) => (
                  <React.Fragment key={event.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(event.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={event.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {format(new Date(event.start_date), 'dd MMM yyyy à HH:mm', { locale: fr })}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <Chip
                                label={getStatusLabel(event.status)}
                                color={getStatusColor(event.status)}
                                size="small"
                              />
                              {event.place_type === 'limited' && (
                                <Chip
                                  label={`${event.current_registrations}/${event.max_capacity}`}
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </Box>
                        }
                      />
                      <Box>
                        <Button
                          size="small"
                          startIcon={<ViewIcon />}
                          onClick={() => navigate(`/events/${event.id}`)}
                        >
                          Voir
                        </Button>
                      </Box>
                    </ListItem>
                    {index < Math.min(5, myEvents.length) - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <EventIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  Aucun événement créé
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/events/create')}
                >
                  Créer votre premier événement
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Événements à venir */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Événements à venir
            </Typography>

            {upcomingEvents && upcomingEvents.length > 0 ? (
              <List>
                {Array.isArray(upcomingEvents) && upcomingEvents.slice(0, 5).map((event, index) => (
                  <React.Fragment key={event.id}>
                    <ListItem>
                      <ListItemIcon>
                        <CalendarIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={event.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {format(new Date(event.start_date), 'dd MMM yyyy à HH:mm', { locale: fr })}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              📍 {event.location}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {event.is_free ? '🆓 Gratuit' : `💰 ${event.price}€`}
                            </Typography>
                          </Box>
                        }
                      />
                      <Box>
                        <Button
                          size="small"
                          startIcon={<ViewIcon />}
                          onClick={() => navigate(`/events/${event.id}`)}
                        >
                          Voir
                        </Button>
                      </Box>
                    </ListItem>
                    {index < Math.min(5, upcomingEvents.length) - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <CalendarIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Aucun événement à venir
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Statistiques détaillées */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Statistiques détaillées
            </Typography>

            <Grid container spacing={3}>
              {/* Répartition par statut */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Répartition par statut
                </Typography>
                {statistics?.status_distribution && Object.entries(statistics.status_distribution).map(([status, count]) => (
                  <Box key={status} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        {getStatusLabel(status)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {count}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(count / statistics.total_events) * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}
              </Grid>

              {/* Répartition par catégorie */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Répartition par catégorie
                </Typography>
                {statistics?.category_distribution && Object.entries(statistics.category_distribution).map(([category, count]) => (
                  <Box key={category} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        {category || 'Sans catégorie'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {count}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(count / statistics.total_events) * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Actions rapides */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Actions rapides
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/events/create')}
                >
                  Créer un événement
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<EventIcon />}
                  onClick={() => navigate('/my-events')}
                >
                  Mes événements
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<CalendarIcon />}
                  onClick={() => navigate('/events')}
                >
                  Tous les événements
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage; 