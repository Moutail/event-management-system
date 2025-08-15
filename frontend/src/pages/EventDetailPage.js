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
  Avatar,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Skeleton,
  useTheme,
  useMediaQuery,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  Category as CategoryIcon,
  Tag as TagIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Language as WebsiteIcon,
  Share as ShareIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  ExpandMore as ExpandMoreIcon,
  AccessTime as TimeIcon,
  EventSeat as SeatIcon,
  Description as DescriptionIcon,
  Image as ImageIcon,
  VideoLibrary as VideoIcon,
  Map as MapIcon,
  Directions as DirectionsIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  fetchEventById, 
  cancelRegistration,
  fetchMyRegistrations
} from '../store/slices/eventSlice';
import { showSnackbar } from '../store/slices/uiSlice';
import { getImageUrl } from '../services/api';
import { useLocale } from '../hooks/useLocale';
import RegistrationModal from '../components/RegistrationModal';
import WaitlistManagement from '../components/WaitlistManagement';
import RefundManagement from '../components/RefundManagement';
import { eventAPI } from '../services/api';

const EventDetailPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { id } = useParams();
  const { formatDate, formatPrice } = useLocale();
  const { 
    currentEvent, 
    loading, 
    myRegistrations, 
    registrationLoading, 
    registrationError 
  } = useSelector((state) => state.events);
  const { user } = useSelector((state) => state.auth);

  // Vérifier si l'utilisateur est inscrit à cet événement
  const userRegistration = Array.isArray(myRegistrations)
    ? myRegistrations.find(reg => (Number(reg.event) === Number(id) || Number(reg.event?.id) === Number(id)))
    : null;
  const canCancel = !!(userRegistration && ['pending', 'confirmed', 'waitlisted', 'attended'].includes(userRegistration.status));
  const isConfirmed = !!(userRegistration && ['confirmed', 'attended'].includes(userRegistration.status));
  const isPending = !!(userRegistration && userRegistration.status === 'pending');
  const isWaitlisted = !!(userRegistration && userRegistration.status === 'waitlisted');
  const isCancelled = !!(userRegistration && userRegistration.status === 'cancelled');
  
  // État pour le modal d'inscription
  const [registrationModalOpen, setRegistrationModalOpen] = useState(false);
  const [waitlistModalOpen, setWaitlistModalOpen] = useState(false);
  const [refundModalOpen, setRefundModalOpen] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [loadingParticipants, setLoadingParticipants] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLiked, setIsLiked] = useState(false);

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

  // Charger la liste des participants si l'utilisateur est l'organisateur
  useEffect(() => {
    const loadParticipants = async () => {
      if (!currentEvent || !user) return;
      if (currentEvent.organizer?.id !== user.id && !user.is_staff) return;
      setLoadingParticipants(true);
      try {
        const res = await eventAPI.getEventParticipants(currentEvent.id);
        setParticipants(res.data || []);
      } catch (_) {}
      setLoadingParticipants(false);
    };
    loadParticipants();
  }, [currentEvent, user]);

  const handleExport = async (type) => {
    if (!currentEvent) return;
    try {
      const res = await eventAPI.exportEventData(currentEvent.id, type);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${currentEvent.title}_${type}.${type === 'csv' ? 'csv' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      dispatch(showSnackbar({ message: `Export ${type.toUpperCase()} réussi`, severity: 'success' }));
    } catch (error) {
      dispatch(showSnackbar({ message: 'Erreur lors de l\'export', severity: 'error' }));
    }
  };

  const handleCancelRegistration = async () => {
    if (!userRegistration) return;
    try {
      await dispatch(cancelRegistration(userRegistration.id)).unwrap();
      dispatch(showSnackbar({ message: 'Inscription annulée avec succès', severity: 'success' }));
      // Recharger les données
      dispatch(fetchEventById(id));
      dispatch(fetchMyRegistrations());
    } catch (error) {
      dispatch(showSnackbar({ message: 'Erreur lors de l\'annulation', severity: 'error' }));
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: currentEvent.title,
        text: currentEvent.short_description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      dispatch(showSnackbar({ message: 'Lien copié dans le presse-papiers', severity: 'success' }));
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 3, mb: 3 }} />
            <Skeleton variant="text" height={48} sx={{ mb: 2 }} />
            <Skeleton variant="text" height={24} sx={{ mb: 1 }} />
            <Skeleton variant="text" height={24} sx={{ mb: 3 }} />
            <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 3 }} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (!currentEvent) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <Typography variant="h4" color="text.secondary">
          Événement non trouvé
        </Typography>
      </Container>
    );
  }

  const renderEventInfo = () => (
    <Paper elevation={1} sx={{ 
      p: 3, 
      mb: 3,
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      border: '1px solid rgba(148,163,184,0.2)',
      borderRadius: 2,
    }}>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CalendarIcon sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(currentEvent.start_date)}
            </Typography>
          </Box>
          {currentEvent.end_date && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TimeIcon sx={{ color: 'primary.main', mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Fin: {formatDate(currentEvent.end_date)}
              </Typography>
            </Box>
          )}
        </Grid>

        <Grid item xs={12} sm={6}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LocationIcon sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentEvent.location}
              </Typography>
              </Box>
          {currentEvent.venue && (
            <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
              {currentEvent.venue}
              </Typography>
          )}
        </Grid>

        <Grid item xs={12} sm={6}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <MoneyIcon sx={{ color: 'success.main', mr: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 500, color: 'success.main' }}>
              {currentEvent.is_free ? 'Gratuit' : formatPrice(currentEvent.price)}
                </Typography>
          </Box>
          {currentEvent.capacity && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SeatIcon sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                {currentEvent.registration_count || 0} / {currentEvent.capacity} places
                </Typography>
              </Box>
          )}
        </Grid>

        <Grid item xs={12} sm={6}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PeopleIcon sx={{ color: 'info.main', mr: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentEvent.registration_count || 0} inscrits
            </Typography>
          </Box>
          {currentEvent.category && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CategoryIcon sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                {currentEvent.category.name}
                  </Typography>
                </Box>
              )}
        </Grid>
      </Grid>
    </Paper>
  );

  const renderOrganizerInfo = () => (
    <Paper elevation={1} sx={{ 
      p: 3, 
      mb: 3,
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      border: '1px solid rgba(148,163,184,0.2)',
      borderRadius: 2,
    }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Organisateur
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar 
          src={currentEvent.organizer?.avatar} 
          sx={{ width: 56, height: 56, mr: 2 }}
        >
          {currentEvent.organizer?.first_name?.[0]}{currentEvent.organizer?.last_name?.[0]}
        </Avatar>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {currentEvent.organizer?.first_name} {currentEvent.organizer?.last_name}
                    </Typography>
          {currentEvent.organizer?.email && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
              <EmailIcon sx={{ fontSize: 16, color: 'text.secondary', mr: 0.5 }} />
              <Typography variant="body2" color="text.secondary">
                {currentEvent.organizer.email}
                    </Typography>
            </Box>
                  )}
                </Box>
      </Box>
      
      {currentEvent.organizer?.bio && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {currentEvent.organizer.bio}
                </Typography>
              )}

      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {currentEvent.organizer?.website && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<WebsiteIcon />}
            href={currentEvent.organizer.website}
            target="_blank"
            rel="noopener noreferrer"
            sx={{ borderRadius: 1.5 }}
          >
            Site web
          </Button>
        )}
        {currentEvent.organizer?.phone && (
                <Button
                  variant="outlined"
            size="small"
            startIcon={<PhoneIcon />}
            href={`tel:${currentEvent.organizer.phone}`}
            sx={{ borderRadius: 1.5 }}
          >
            Téléphone
                </Button>
              )}
      </Box>
    </Paper>
  );

  const renderTags = () => (
    currentEvent.tags && currentEvent.tags.length > 0 && (
      <Paper elevation={1} sx={{ 
        p: 3, 
        mb: 3,
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        border: '1px solid rgba(148,163,184,0.2)',
        borderRadius: 2,
      }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Tags
              </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {currentEvent.tags.map((tag) => (
            <Chip
              key={tag.id}
              icon={<TagIcon />}
              label={tag.name}
              variant="outlined"
              sx={{ 
                borderColor: 'rgba(79,70,229,0.3)',
                color: 'primary.main',
                fontWeight: 500,
              }}
            />
          ))}
        </Box>
      </Paper>
    )
  );

  const renderParticipants = () => (
    <Paper elevation={1} sx={{ 
      p: 3, 
      mb: 3,
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      border: '1px solid rgba(148,163,184,0.2)',
      borderRadius: 2,
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Participants ({participants.length})
                </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={() => handleExport('csv')}
            sx={{ borderRadius: 1.5 }}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            size="small"
            onClick={() => handleExport('excel')}
            sx={{ borderRadius: 1.5 }}
          >
            Export Excel
          </Button>
        </Box>
                </Box>
      
                {loadingParticipants ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Chargement des participants...</Typography>
                      </Box>
      ) : participants.length > 0 ? (
        <List>
          {participants.map((participant, index) => (
            <React.Fragment key={participant.id}>
              <ListItem>
                <ListItemIcon>
                  <Avatar src={participant.user?.avatar}>
                    {participant.user?.first_name?.[0]}{participant.user?.last_name?.[0]}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={`${participant.user?.first_name} ${participant.user?.last_name}`}
                  secondary={`${participant.user?.email} • ${participant.ticket_type_name || 'Par défaut'} • ${formatPrice(participant.price_paid || 0)}`}
                />
                <Chip
                  label={participant.status}
                  size="small"
                  color={participant.status === 'confirmed' ? 'success' : 'default'}
                />
              </ListItem>
              {index < participants.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      ) : (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">
            Aucun participant inscrit pour le moment
          </Typography>
                  </Box>
                )}
    </Paper>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* En-tête de l'événement */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h3" component="h1" sx={{ 
            fontWeight: 700,
            color: 'text.primary',
            fontSize: { xs: '2rem', md: '2.5rem' }
          }}>
            {currentEvent.title}
              </Typography>
              
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={handleShare} sx={{ color: 'primary.main' }}>
              <ShareIcon />
            </IconButton>
            <IconButton onClick={() => setIsBookmarked(!isBookmarked)} sx={{ color: 'primary.main' }}>
              {isBookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
            </IconButton>
            <IconButton onClick={() => setIsLiked(!isLiked)} sx={{ color: 'error.main' }}>
              {isLiked ? <FavoriteIcon /> : <FavoriteBorderIcon />}
            </IconButton>
          </Box>
              </Box>

        {currentEvent.short_description && (
          <Typography variant="h6" color="text.secondary" sx={{ mb: 3, lineHeight: 1.6, fontWeight: 400 }}>
            {currentEvent.short_description}
                  </Typography>
        )}

        {/* Statut de l'événement */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Chip
            label={currentEvent.status}
            color={currentEvent.status === 'published' ? 'success' : 'default'}
            sx={{ fontWeight: 500 }}
          />
          {currentEvent.is_free && (
            <Chip
              label="Gratuit"
              color="success"
              variant="outlined"
              sx={{ fontWeight: 500 }}
            />
          )}
        </Box>
      </Box>

      <Grid container spacing={4}>
        {/* Colonne principale */}
        <Grid item xs={12} md={8}>
          {/* Image principale */}
          {currentEvent.poster ? (
            <CardMedia
              component="img"
              height="400"
              image={getImageUrl(currentEvent.poster)}
              alt={currentEvent.title}
              sx={{ 
                borderRadius: 2, 
                mb: 3,
                objectFit: 'cover',
                width: '100%'
              }}
            />
          ) : (
            <Box
              sx={{
                height: 400,
                background: 'linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%)',
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                mb: 3,
              }}
            >
              <ImageIcon sx={{ fontSize: 56, opacity: 0.8 }} />
                </Box>
              )}

          {/* Informations de base */}
          {renderEventInfo()}

          {/* Description détaillée */}
          {currentEvent.description && (
            <Paper elevation={1} sx={{ 
              p: 3, 
              mb: 3,
              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
              border: '1px solid rgba(148,163,184,0.2)',
              borderRadius: 2,
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <DescriptionIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Description
                  </Typography>
                </Box>
              <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                {currentEvent.description}
              </Typography>
            </Paper>
          )}

          {/* Tags */}
          {renderTags()}

          {/* Informations sur l'organisateur */}
          {renderOrganizerInfo()}

          {/* Participants (si organisateur) */}
          {(currentEvent.organizer?.id === user?.id || user?.is_staff) && renderParticipants()}
        </Grid>

        {/* Colonne latérale */}
        <Grid item xs={12} md={4}>
          {/* Carte d'inscription */}
          <Paper elevation={2} sx={{ 
            p: 3, 
            mb: 3,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid rgba(148,163,184,0.2)',
            borderRadius: 2,
            position: 'sticky',
            top: 24,
          }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, textAlign: 'center' }}>
              {currentEvent.is_free ? 'Inscription gratuite' : `Prix: ${formatPrice(currentEvent.price)}`}
            </Typography>

            {userRegistration ? (
              <Box sx={{ textAlign: 'center' }}>
                <Alert 
                  severity={
                    isConfirmed ? 'success' : 
                    isPending ? 'info' : 
                    isCancelled ? 'error' : 
                    'warning'
                  } 
                  sx={{ mb: 2 }}
                >
                  {isConfirmed ? 'Inscription confirmée !' : 
                   isPending ? 'Inscription en attente de confirmation' : 
                   isWaitlisted ? 'Vous êtes sur liste d\'attente' : 
                   isCancelled ? 'Votre inscription est annulée' :
                   'Inscription en cours de traitement'}
                </Alert>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Statut: {userRegistration.status}
              </Typography>
              
                {canCancel && (
                  <Button
                    variant="outlined"
                    color="error"
                    fullWidth
                    onClick={handleCancelRegistration}
                    sx={{ mb: 2 }}
                  >
                    Annuler l'inscription
                  </Button>
                )}

                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/my-registrations')}
                >
                  Voir mes inscriptions
                </Button>

                {/* Boutons de gestion pour l'organisateur (même inscrit) */}
                {user && user.id === currentEvent.organizer?.id && (
                  <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      onClick={() => setWaitlistModalOpen(true)}
                      sx={{
                        py: 1.5,
                        fontSize: '1rem',
                        fontWeight: 600,
                        borderColor: 'warning.main',
                        color: 'warning.main',
                        '&:hover': {
                          borderColor: 'warning.dark',
                          backgroundColor: 'warning.light',
                          color: 'warning.dark',
                        },
                      }}
                    >
                      Gérer les listes d'attente
                    </Button>
                    
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      onClick={() => setRefundModalOpen(true)}
                      sx={{
                        py: 1.5,
                        fontSize: '1rem',
                        fontWeight: 600,
                        borderColor: 'error.main',
                        color: 'error.main',
                        '&:hover': {
                          borderColor: 'error.dark',
                          backgroundColor: 'error.light',
                          color: 'error.dark',
                        },
                      }}
                    >
                      💰 Gérer les remboursements
                    </Button>
                  </Box>
                )}
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {currentEvent.capacity ? 
                    `${currentEvent.capacity - (currentEvent.registration_count || 0)} places disponibles` : 
                    'Places illimitées'
                  }
                  </Typography>

                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={handleRegisterClick}
                  disabled={currentEvent.status !== 'published'}
                  sx={{
                    background: 'linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%)',
                    fontWeight: 600,
                    py: 1.5,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #4338CA 0%, #0891B2 100%)',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease-in-out',
                  }}
                >
                  {currentEvent.status === 'published' ? 'S\'inscrire' : 'Inscriptions fermées'}
                </Button>

                {/* Boutons de gestion pour l'organisateur (quand pas inscrit) */}
                {user && user.id === currentEvent.organizer?.id && (
                  <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      onClick={() => setWaitlistModalOpen(true)}
                      sx={{
                        py: 1.5,
                        fontSize: '1rem',
                        fontWeight: 600,
                        borderColor: 'warning.main',
                        color: 'warning.main',
                        '&:hover': {
                          borderColor: 'warning.dark',
                          backgroundColor: 'warning.light',
                          color: 'warning.dark',
                        },
                      }}
                    >
                      Gérer les listes d'attente
                    </Button>
                    
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      onClick={() => setRefundModalOpen(true)}
                      sx={{
                        py: 1.5,
                        fontSize: '1rem',
                        fontWeight: 600,
                        borderColor: 'error.main',
                        color: 'error.main',
                        '&:hover': {
                          borderColor: 'error.dark',
                          backgroundColor: 'error.light',
                          color: 'error.dark',
                        },
                      }}
                    >
                      💰 Gérer les remboursements
                    </Button>
                  </Box>
                )}

                {currentEvent.status !== 'published' && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Cet événement n'est pas encore ouvert aux inscriptions
                  </Typography>
                )}
                </Box>
            )}
          </Paper>

          {/* Carte de localisation */}
          <Paper elevation={1} sx={{ 
            p: 3,
            background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            border: '1px solid rgba(148,163,184,0.2)',
            borderRadius: 2,
          }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Localisation
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {currentEvent.location}
                </Typography>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<DirectionsIcon />}
              href={`https://maps.google.com/?q=${encodeURIComponent(currentEvent.location)}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Voir sur la carte
            </Button>
          </Paper>
          </Grid>
      </Grid>

      {/* Modal d'inscription */}
      <RegistrationModal
        open={registrationModalOpen}
        onClose={handleRegistrationModalClose}
        event={currentEvent}
      />

      {/* Modal de gestion des listes d'attente */}
      <WaitlistManagement
        open={waitlistModalOpen}
        onClose={() => setWaitlistModalOpen(false)}
        event={currentEvent}
      />

      {/* Modal de gestion des remboursements */}
      <RefundManagement
        open={refundModalOpen}
        onClose={() => setRefundModalOpen(false)}
        event={currentEvent}
      />
    </Container>
  );
};

export default EventDetailPage; 