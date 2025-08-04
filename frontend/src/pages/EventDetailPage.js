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
  Divider,
  Avatar,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  fetchEventById, 
  registerForEvent, 
  cancelRegistration,
  fetchMyRegistrations
} from '../store/slices/eventSlice';
import { formatDate, formatPrice, getImageUrl } from '../services/api';
import RegistrationModal from '../components/RegistrationModal';

const EventDetailPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { id } = useParams();
  const { 
    currentEvent, 
    loading, 
    myRegistrations, 
    registrationLoading, 
    registrationError 
  } = useSelector((state) => state.events);
  const { user } = useSelector((state) => state.auth);

  // Vérifier si l'utilisateur est inscrit à cet événement
  const userRegistration = Array.isArray(myRegistrations) ? myRegistrations.find(reg => reg.event === parseInt(id)) : null;
  
  // État pour le modal d'inscription
  const [registrationModalOpen, setRegistrationModalOpen] = useState(false);

  useEffect(() => {
    if (id) {
      dispatch(fetchEventById(id));
    }
  }, [dispatch, id]);

  // Charger les inscriptions de l'utilisateur si connecté
  useEffect(() => {
    if (user) {
      dispatch(fetchMyRegistrations());
    }
  }, [dispatch, user]);

  // Fonction pour ouvrir le modal d'inscription
  const handleRegisterClick = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setRegistrationModalOpen(true);
  };

  // Fonction pour fermer le modal d'inscription
  const handleRegistrationModalClose = () => {
    setRegistrationModalOpen(false);
    // Recharger l'événement et les inscriptions pour mettre à jour les informations
    dispatch(fetchEventById(id));
    if (user) {
      dispatch(fetchMyRegistrations());
    }
  };

  // Fonction pour annuler une inscription
  const handleCancelRegistration = async () => {
    if (!userRegistration) return;

    try {
      await dispatch(cancelRegistration(userRegistration.id)).unwrap();
      
      // Recharger l'événement pour mettre à jour les informations
      dispatch(fetchEventById(id));
    } catch (error) {
      console.error('Erreur lors de l\'annulation:', error);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Chargement...</Typography>
        </Box>
      </Container>
    );
  }

  if (!currentEvent) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Événement non trouvé</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Grid container spacing={4}>
        {/* Image principale */}
        <Grid item xs={12} md={8}>
          {currentEvent.poster && (
            <CardMedia
              component="img"
              height="400"
              image={getImageUrl(currentEvent.poster)}
              alt={currentEvent.title}
              sx={{ borderRadius: 2, mb: 2 }}
            />
          )}
        </Grid>

        {/* Informations principales */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h4" gutterBottom>
                {currentEvent.title}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={currentEvent.status}
                  color={currentEvent.status === 'published' ? 'success' : 'default'}
                  sx={{ mr: 1 }}
                />
                {currentEvent.is_featured && (
                  <Chip label="En vedette" color="primary" />
                )}
              </Box>

              <Typography variant="h5" color="primary" gutterBottom>
                {formatPrice(currentEvent.price)}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  📅 {formatDate(currentEvent.start_date)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  📍 {currentEvent.location}
                </Typography>
              </Box>

              {currentEvent.place_type === 'limited' && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Places disponibles: {currentEvent.available_places} / {currentEvent.max_capacity}
                  </Typography>
                </Box>
              )}

              {!user ? (
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  sx={{ mb: 2 }}
                  onClick={() => navigate('/login')}
                >
                  Se connecter pour s'inscrire
                </Button>
              ) : userRegistration ? (
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="outlined"
                    color="error"
                    fullWidth
                    size="large"
                    onClick={handleCancelRegistration}
                    disabled={registrationLoading}
                    sx={{ mb: 1 }}
                  >
                    {registrationLoading ? 'Annulation...' : 'Annuler l\'inscription'}
                  </Button>
                  <Typography variant="body2" color="success.main" textAlign="center">
                    ✓ Vous êtes inscrit à cet événement
                  </Typography>
                  {userRegistration.status && (
                    <Typography variant="body2" color="text.secondary" textAlign="center">
                      Statut: {userRegistration.status}
                    </Typography>
                  )}
                </Box>
              ) : (
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  sx={{ mb: 2 }}
                  onClick={handleRegisterClick}
                  disabled={currentEvent.is_full}
                >
                  {currentEvent.is_full ? 'Complet' : 'S\'inscrire'}
                </Button>
              )}

              {registrationError && (
                <Typography variant="body2" color="error" textAlign="center" sx={{ mb: 2 }}>
                  {registrationError}
                </Typography>
              )}

              {user && currentEvent.organizer.id === user.id && (
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate(`/edit-event/${currentEvent.id}`)}
                >
                  Modifier l'événement
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Description */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Description
              </Typography>
              <Typography variant="body1" paragraph>
                {currentEvent.description}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Informations détaillées */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Informations détaillées
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Date de début:</strong> {formatDate(currentEvent.start_date)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Date de fin:</strong> {formatDate(currentEvent.end_date)}
                </Typography>
              </Box>

              {currentEvent.address && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Adresse:</strong> {currentEvent.address}
                  </Typography>
                </Box>
              )}

              {currentEvent.contact_email && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Contact:</strong> {currentEvent.contact_email}
                  </Typography>
                </Box>
              )}

              {currentEvent.website && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Site web:</strong> {currentEvent.website}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Organisateur */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Organisateur
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ mr: 2 }}>
                  {currentEvent.organizer.first_name?.[0] || currentEvent.organizer.username[0]}
                </Avatar>
                <Box>
                  <Typography variant="body1">
                    {currentEvent.organizer.first_name} {currentEvent.organizer.last_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    @{currentEvent.organizer.username}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Tags */}
        {currentEvent.tags && Array.isArray(currentEvent.tags) && currentEvent.tags.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Tags
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {currentEvent.tags.map((tag) => (
                    <Chip
                      key={tag.id}
                      label={tag.name}
                      sx={{ backgroundColor: tag.color, color: 'white' }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Modal d'inscription */}
      <RegistrationModal
        open={registrationModalOpen}
        onClose={handleRegistrationModalClose}
        event={currentEvent}
      />
    </Container>
  );
};

export default EventDetailPage; 