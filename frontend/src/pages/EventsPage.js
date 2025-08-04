import React, { useEffect, useState } from 'react';
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchEvents, setFilters } from '../store/slices/eventSlice';
import { formatDate, formatPrice, getImageUrl } from '../services/api';

const EventsPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { events, loading, filters, pagination } = useSelector((state) => state.events);
  const { categories } = useSelector((state) => state.events);

  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    dispatch(fetchEvents(filters));
  }, [dispatch, filters]);

  const handleEventClick = (eventId) => {
    navigate(`/events/${eventId}`);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    dispatch(setFilters({ search: e.target.value }));
  };

  const handleCategoryChange = (e) => {
    dispatch(setFilters({ category: e.target.value }));
  };

  const handleStatusChange = (e) => {
    dispatch(setFilters({ status: e.target.value }));
  };

  const handlePageChange = (event, page) => {
    dispatch(setFilters({ page }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Tous les événements
        </Typography>
        
        {/* Filtres */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Rechercher..."
                value={searchTerm}
                onChange={handleSearchChange}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={handleCategoryChange}
                >
                  <MenuItem value="">Toutes</MenuItem>
                  {Array.isArray(categories) && categories.map((category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Statut</InputLabel>
                <Select
                  value={filters.status}
                  label="Statut"
                  onChange={handleStatusChange}
                >
                  <MenuItem value="">Tous</MenuItem>
                  <MenuItem value="published">Publié</MenuItem>
                  <MenuItem value="draft">Brouillon</MenuItem>
                  <MenuItem value="cancelled">Annulé</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                onClick={() => navigate('/create-event')}
              >
                Créer
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Box>

      {/* Liste des événements */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Chargement...</Typography>
        </Box>
      ) : (
        <>
          <Grid container spacing={3}>
            {Array.isArray(events) && events.map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.id}>
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
                      image={getImageUrl(event.poster)}
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
                    <Typography variant="body2" color="text.secondary" paragraph>
                      📍 {event.location}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                      {event.tags.slice(0, 3).map((tag) => (
                        <Chip
                          key={tag.id}
                          label={tag.name}
                          size="small"
                          sx={{ backgroundColor: tag.color, color: 'white' }}
                        />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip
                        label={event.status}
                        size="small"
                        color={event.status === 'published' ? 'success' : 'default'}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {event.registration_count} inscrits
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={pagination.totalPages}
                page={pagination.currentPage}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default EventsPage; 