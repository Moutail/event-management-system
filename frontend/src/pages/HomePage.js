import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  Chip,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  fetchFeaturedEvents,
  fetchUpcomingEvents,
  fetchEventStatistics,
} from '../store/slices/eventSlice';
import { formatDate, formatPrice } from '../services/api';

const HomePage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { featuredEvents, upcomingEvents, statistics } = useSelector((state) => state.events);

  useEffect(() => {
    dispatch(fetchFeaturedEvents());
    dispatch(fetchUpcomingEvents());
    dispatch(fetchEventStatistics());
  }, [dispatch]);

  const handleEventClick = (eventId) => {
    navigate(`/events/${eventId}`);
  };

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Bienvenue sur le Système de Gestion d'Événements
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Découvrez, créez et gérez vos événements en toute simplicité
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/create-event')}
          sx={{ mr: 2 }}
        >
          Créer un événement
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/events')}
        >
          Voir tous les événements
        </Button>
      </Box>

      {/* Statistiques */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 6 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statistics.total_events}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Événements totaux
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {statistics.published_events}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Événements publiés
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {statistics.upcoming_events}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Événements à venir
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {statistics.ongoing_events}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Événements en cours
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Événements en vedette */}
      {featuredEvents.length > 0 && (
        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" gutterBottom>
            Événements en vedette
          </Typography>
          <Grid container spacing={3}>
            {Array.isArray(featuredEvents) && featuredEvents.slice(0, 3).map((event) => (
              <Grid item xs={12} md={4} key={event.id}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    '&:hover': { transform: 'translateY(-4px)', transition: 'transform 0.2s' }
                  }}
                  onClick={() => handleEventClick(event.id)}
                >
                  {event.poster && (
                    <CardMedia
                      component="img"
                      height="200"
                      image={event.poster}
                      alt={event.title}
                    />
                  )}
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {event.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {event.short_description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(event.start_date)}
                      </Typography>
                      <Typography variant="body2" color="primary" fontWeight="bold">
                        {formatPrice(event.price)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {event.tags.slice(0, 2).map((tag) => (
                        <Chip
                          key={tag.id}
                          label={tag.name}
                          size="small"
                          sx={{ backgroundColor: tag.color, color: 'white' }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Événements à venir */}
      {upcomingEvents.length > 0 && (
        <Box>
          <Typography variant="h4" gutterBottom>
            Événements à venir
          </Typography>
          <Grid container spacing={3}>
            {Array.isArray(upcomingEvents) && upcomingEvents.slice(0, 6).map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.id}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    '&:hover': { transform: 'translateY(-4px)', transition: 'transform 0.2s' }
                  }}
                  onClick={() => handleEventClick(event.id)}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {event.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {event.short_description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(event.start_date)}
                      </Typography>
                      <Typography variant="body2" color="primary" fontWeight="bold">
                        {formatPrice(event.price)}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      📍 {event.location}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default HomePage; 