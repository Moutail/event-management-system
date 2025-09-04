import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Paper,
  AppBar,
  Toolbar,
  useTheme,
  useMediaQuery,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Badge,
} from '@mui/material';
import {
  Event as EventIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  People as PeopleIcon,
  Login as LoginIcon,
  PersonAdd as PersonAddIcon,
  AccountCircle as AccountIcon,
  Home as HomeIcon,
  Bookmark as BookmarkIcon,
  Logout as LogoutIcon,
  Brightness4 as ThemeIcon,
  Brightness7 as Brightness7Icon,
  Notifications as NotificationsIcon,
  Info as InfoIcon,
  ContactSupport as ContactIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import api from '../services/api';
import { toggleDarkMode } from '../store/slices/uiSlice';

const PublicHomePage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const { darkMode } = useSelector((state) => state.ui);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // État pour le menu utilisateur
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = () => {
    // TODO: Implémenter la déconnexion
    handleMenuClose();
    navigate('/login');
  };

  // Fonctions pour les nouvelles icônes
  const handleThemeToggle = () => {
    dispatch(toggleDarkMode());
  };

  const handleNotifications = () => {
    // TODO: Implémenter la gestion des notifications
    console.log('Notifications');
  };

  const handleEvents = () => {
    // 🎯 NOUVELLE LOGIQUE : Permettre aux visiteurs de voir tous les événements
    if (isAuthenticated) {
      navigate('/dashboard/events');
    } else {
      navigate('/public/events'); // Route publique pour tous les événements
    }
  };

  const handleAbout = () => {
    navigate('/about');
  };

  const handleContact = () => {
    navigate('/contact');
  };

  useEffect(() => {
    fetchPublicEvents();
  }, []);

  const fetchPublicEvents = async () => {
    try {
      setLoading(true);
      // Récupérer tous les événements avec tous les détails
      const response = await api.get('/events/', {
        params: {
          page_size: 100, // Récupérer plus d'événements
        }
      });
      
      // Debug: afficher les données reçues
      console.log('🔍 [PUBLIC_HOME] Données reçues de l\'API:', response.data);
      if (response.data.results) {
        console.log('🔍 [PUBLIC_HOME] Premier événement:', response.data.results[0]);
        console.log('🔍 [PUBLIC_HOME] current_registrations du premier événement:', response.data.results[0]?.current_registrations);
      }
      
      setEvents(response.data.results || response.data || []);
    } catch (error) {
      console.error('Erreur lors du chargement des événements:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEventClick = (eventId) => {
    // 🎯 NOUVELLE LOGIQUE : Permettre aux visiteurs de voir les événements
    // Plus besoin de rediriger vers /login - on va directement aux détails
    if (isAuthenticated) {
      navigate(`/dashboard/events/${eventId}`);
    } else {
      navigate(`/public/events/${eventId}`);
    }
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Header public */}
      <AppBar 
        position="static" 
        sx={{ 
          background: 'linear-gradient(135deg, rgba(108,99,255,0.95) 0%, rgba(34,211,238,0.95) 100%)',
          boxShadow: '0 2px 20px rgba(108,99,255,0.3)',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Logo et titre */}
          <Typography 
            variant="h5" 
            component="h1" 
            sx={{ 
              fontWeight: 700, 
              color: 'white',
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          >
            🎉 Gestion d'Événements
          </Typography>
          
          {/* Navigation droite avec icônes et liens */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Icône thème */}
            <IconButton
              onClick={handleThemeToggle}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                },
              }}
            >
              {darkMode ? <Brightness7Icon /> : <ThemeIcon />}
            </IconButton>

            {/* Icône notifications avec badge */}
            <IconButton
              onClick={handleNotifications}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                },
              }}
            >
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>

            {/* Icône événements */}
            <IconButton
              onClick={handleEvents}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                },
              }}
            >
              <EventIcon />
            </IconButton>

            {/* Lien À propos */}
            <Button
              startIcon={<InfoIcon />}
              onClick={handleAbout}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                },
                fontWeight: 500,
              }}
            >
              À propos
            </Button>

            {/* Lien Contact */}
            <Button
              startIcon={<ContactIcon />}
              onClick={handleContact}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                },
                fontWeight: 500,
              }}
            >
              Contact
            </Button>
            
            {/* Boutons de connexion/inscription ou profil utilisateur */}
            <Box sx={{ display: 'flex', gap: 2, ml: 2 }}>
              {!isAuthenticated ? (
                // Boutons pour visiteurs non connectés
                <>
                  <Button
                    variant="outlined"
                    startIcon={<LoginIcon />}
                    onClick={handleLogin}
                    sx={{
                      borderColor: 'rgba(255,255,255,0.7)',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.15)',
                        borderColor: 'white',
                      },
                      fontWeight: 600,
                    }}
                  >
                    Se connecter
                  </Button>
                  
                  <Button
                    variant="contained"
                    startIcon={<PersonAddIcon />}
                    onClick={handleRegister}
                    sx={{
                      backgroundColor: 'rgba(255,255,255,0.9)',
                      color: 'primary.main',
                      fontWeight: 600,
                      '&:hover': {
                        backgroundColor: 'white',
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    S'inscrire
                  </Button>
                </>
              ) : (
                // Icône profil pour utilisateurs connectés
                <>
                  <IconButton
                    onClick={handleMenuOpen}
                    sx={{
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.15)',
                      },
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 40,
                        height: 40,
                        bgcolor: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        fontWeight: 600,
                      }}
                    >
                      {user?.username?.charAt(0)?.toUpperCase() || 'U'}
                    </Avatar>
                  </IconButton>
                  
                  {/* Menu déroulant utilisateur */}
                  <Menu
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleMenuClose}
                    PaperProps={{
                      sx: {
                        mt: 1,
                        minWidth: 200,
                        boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                        borderRadius: 2,
                      },
                    }}
                  >
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
                      <AccountIcon sx={{ mr: 2, color: 'primary.main' }} />
                      Mon Profil
                    </MenuItem>
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/'); }}>
                      <HomeIcon sx={{ mr: 2, color: 'primary.main' }} />
                      Accueil
                    </MenuItem>
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/dashboard/events'); }}>
                      <EventIcon sx={{ mr: 2, color: 'primary.main' }} />
                      Événements
                    </MenuItem>
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/my-registrations'); }}>
                      <BookmarkIcon sx={{ mr: 2, color: 'primary.main' }} />
                      Mes Inscriptions
                    </MenuItem>
                    <MenuItem onClick={handleLogout}>
                      <LogoutIcon sx={{ mr: 2, color: 'error.main' }} />
                      Déconnexion
                    </MenuItem>
                  </Menu>
                </>
              )}
            </Box>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Contenu principal */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
        {/* Section héro */}
        <Paper 
          elevation={0}
          sx={{
            p: { xs: 4, md: 6 },
            mb: 6,
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            borderRadius: 3,
            textAlign: 'center',
            border: '1px solid rgba(108,99,255,0.1)',
          }}
        >
          <Typography 
            variant="h2" 
            component="h1" 
            sx={{ 
              fontWeight: 800, 
              mb: 3,
              background: 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            Découvrez des événements incroyables
          </Typography>
          
          <Typography 
            variant="h6" 
            color="text.secondary" 
            sx={{ 
              mb: 4, 
              maxWidth: 600, 
              mx: 'auto',
              lineHeight: 1.6,
            }}
          >
            Explorez notre sélection d'événements et inscrivez-vous à ceux qui vous intéressent. 
            Créez un compte pour suivre vos inscriptions et accéder à plus de fonctionnalités !
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PersonAddIcon />}
              onClick={handleRegister}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(108,99,255,0.3)',
                },
              }}
            >
              Commencer maintenant
            </Button>
            
            <Button
              variant="outlined"
              size="large"
              startIcon={<EventIcon />}
              onClick={() => document.getElementById('events-section').scrollIntoView({ behavior: 'smooth' })}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              Voir les événements
            </Button>
          </Box>
        </Paper>

        {/* Section événements */}
        <Box id="events-section">
          <Typography 
            variant="h4" 
            component="h2" 
            sx={{ 
              fontWeight: 700, 
              mb: 4, 
              textAlign: 'center',
              color: 'text.primary',
            }}
          >
            Événements disponibles
          </Typography>

          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Chargement des événements...
              </Typography>
            </Box>
          ) : events.length > 0 ? (
            <>
              <Typography 
                variant="h6" 
                sx={{ 
                  textAlign: 'center', 
                  mb: 4, 
                  color: 'text.secondary',
                  fontWeight: 500,
                }}
              >
                {events.length} événement(s) trouvé(s)
              </Typography>
              
              <Grid container spacing={3}>
                {events.map((event) => (
                  <Grid item xs={12} sm={6} md={4} key={event.id}>
                    <Card 
                      elevation={2}
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: '0 8px 25px rgba(108,99,255,0.2)',
                        },
                      }}
                      onClick={() => handleEventClick(event.id)}
                    >
                      {/* Image de l'événement */}
                      <Box
                        sx={{
                          height: 200,
                          backgroundImage: event.poster 
                            ? `url(${event.poster})`
                            : 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          backgroundRepeat: 'no-repeat',
                          position: 'relative',
                          borderRadius: '8px 8px 0 0',
                        }}
                      >
                        {/* Identifiant de l'événement */}
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 8,
                            left: 8,
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            color: 'white',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 1,
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}
                        >
                          {event.id}
                        </Box>
                        
                        {/* Statut de l'événement */}
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            backgroundColor: 'success.main',
                            color: 'white',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 1,
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}
                        >
                          Publié
                        </Box>
                      </Box>

                      <CardContent sx={{ flexGrow: 1, p: 2 }}>
                        {/* Titre de l'événement */}
                        <Typography 
                          variant="h6" 
                          component="h3" 
                          sx={{ 
                            fontWeight: 600, 
                            mb: 1,
                            color: 'text.primary',
                            lineHeight: 1.3,
                          }}
                        >
                          {event.title}
                        </Typography>
                        
                        {/* Sous-titre ou description courte */}
                        {event.description && (
                          <Typography 
                            variant="body2" 
                            color="text.secondary" 
                            sx={{ 
                              mb: 2,
                              lineHeight: 1.4,
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {event.description}
                          </Typography>
                        )}
                        
                        {/* Détails de l'événement */}
                        <Box sx={{ mb: 2 }}>
                          {/* Date et heure */}
                          <Typography 
                            variant="body2" 
                            color="text.secondary" 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: 1, 
                              mb: 1,
                              fontSize: '0.875rem',
                            }}
                          >
                            <CalendarIcon fontSize="small" />
                            {format(new Date(event.start_date), 'dd MMM yyyy à HH:mm', { locale: fr })}
                          </Typography>
                          
                          {/* Lieu */}
                          {event.location && (
                            <Typography 
                              variant="body2" 
                              color="text.secondary" 
                              sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1, 
                                mb: 1,
                                fontSize: '0.875rem',
                              }}
                            >
                              <LocationIcon fontSize="small" />
                              {event.location}
                            </Typography>
                          )}
                          
                          {/* Prix */}
                          {event.price && (
                            <Typography 
                              variant="body2" 
                              color="primary.main" 
                              sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1, 
                                mb: 1,
                                fontSize: '0.875rem',
                                fontWeight: 600,
                              }}
                            >
                              💰 $ {parseFloat(event.price).toFixed(2)} $US
                            </Typography>
                          )}
                          
                          {/* Participants */}
                          {event.max_capacity && (
                            <Typography 
                              variant="body2" 
                              color="text.secondary" 
                              sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1,
                                fontSize: '0.875rem',
                              }}
                            >
                              <PeopleIcon fontSize="small" />
                              {event.current_registrations || 0} inscrits
                            </Typography>
                          )}
                        </Box>
                        
                        {/* Catégorie */}
                        {event.category && (
                          <Chip
                            label={event.category.name}
                            size="small"
                            sx={{ 
                              mb: 2,
                              backgroundColor: 'primary.main',
                              color: 'white',
                              fontWeight: 500,
                              fontSize: '0.75rem',
                            }}
                          />
                        )}
                      </CardContent>
                      
                      <CardActions sx={{ p: 2, pt: 0 }}>
                        <Button
                          variant="outlined"
                          fullWidth
                          startIcon={<EventIcon />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEventClick(event.id);
                          }}
                          sx={{
                            fontWeight: 600,
                            borderColor: 'primary.main',
                            color: 'primary.main',
                            '&:hover': {
                              backgroundColor: 'primary.main',
                              color: 'white',
                            },
                          }}
                        >
                          Voir les détails
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          ) : (
            <Paper 
              elevation={0}
              sx={{
                p: 6,
                textAlign: 'center',
                background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                borderRadius: 3,
                border: '2px dashed rgba(108,99,255,0.2)',
              }}
            >
              <EventIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                Aucun événement disponible pour le moment
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Revenez bientôt pour découvrir de nouveaux événements !
              </Typography>
            </Paper>
          )}
        </Box>

                 {/* Section CTA - Différente selon l'état de connexion */}
         {events.length > 0 && (
           <Paper 
             elevation={0}
             sx={{
               p: { xs: 4, md: 6 },
               mt: 6,
               background: 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
               borderRadius: 3,
               textAlign: 'center',
               color: 'white',
             }}
           >
             {!isAuthenticated ? (
               // CTA pour visiteurs non connectés
               <>
                 <Typography 
                   variant="h4" 
                   component="h2" 
                   sx={{ 
                     fontWeight: 700, 
                     mb: 3,
                     color: 'white',
                   }}
                 >
                   Prêt à participer ?
                 </Typography>
                 
                 <Typography 
                   variant="h6" 
                   sx={{ 
                     mb: 4, 
                     maxWidth: 600, 
                     mx: 'auto',
                     opacity: 0.9,
                     lineHeight: 1.6,
                   }}
                 >
                   Créez votre compte gratuitement pour vous inscrire aux événements, 
                   suivre vos participations et accéder à plus de fonctionnalités !
                 </Typography>
                 
                 <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                   <Button
                     variant="contained"
                     size="large"
                     startIcon={<PersonAddIcon />}
                     onClick={handleRegister}
                     sx={{
                       px: 4,
                       py: 1.5,
                       fontSize: '1.1rem',
                       fontWeight: 600,
                       backgroundColor: 'white',
                       color: 'primary.main',
                       '&:hover': {
                         backgroundColor: 'rgba(255,255,255,0.9)',
                         transform: 'translateY(-2px)',
                       },
                     }}
                   >
                     Créer mon compte
                   </Button>
                   
                   <Button
                     variant="outlined"
                     size="large"
                     startIcon={<LoginIcon />}
                     onClick={handleLogin}
                     sx={{
                       px: 4,
                       py: 1.5,
                       fontSize: '1.1rem',
                       fontWeight: 600,
                       borderColor: 'white',
                       color: 'white',
                       '&:hover': {
                         backgroundColor: 'rgba(255,255,255,0.15)',
                         borderColor: 'white',
                         transform: 'translateY(-2px)',
                       },
                     }}
                   >
                     Me connecter
                   </Button>
                 </Box>
               </>
             ) : (
               // CTA pour utilisateurs connectés
               <>
                 <Typography 
                   variant="h4" 
                   component="h2" 
                   sx={{ 
                     fontWeight: 700, 
                     mb: 3,
                     color: 'white',
                   }}
                 >
                   Bienvenue, {user?.username || 'Utilisateur'} ! 🎉
                 </Typography>
                 
                 <Typography 
                   variant="h6" 
                   sx={{ 
                     mb: 4, 
                     maxWidth: 600, 
                     mx: 'auto',
                     opacity: 0.9,
                     lineHeight: 1.6,
                   }}
                 >
                   Explorez les événements disponibles et inscrivez-vous à ceux qui vous intéressent ! 
                   Utilisez le menu en haut à droite pour accéder à votre profil et vos inscriptions.
                 </Typography>
                 
                 <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                   <Button
                     variant="contained"
                     size="large"
                     startIcon={<EventIcon />}
                     onClick={() => navigate('/dashboard/events')}
                     sx={{
                       px: 4,
                       py: 1.5,
                       fontSize: '1.1rem',
                       fontWeight: 600,
                       backgroundColor: 'white',
                       color: 'primary.main',
                       '&:hover': {
                         backgroundColor: 'rgba(255,255,255,0.9)',
                         transform: 'translateY(-2px)',
                       },
                     }}
                   >
                     Voir tous les événements
                   </Button>
                   
                   <Button
                     variant="outlined"
                     size="large"
                     startIcon={<BookmarkIcon />}
                     onClick={() => navigate('/my-registrations')}
                     sx={{
                       px: 4,
                       py: 1.5,
                       fontSize: '1.1rem',
                       fontWeight: 600,
                       borderColor: 'white',
                       color: 'white',
                       '&:hover': {
                         backgroundColor: 'rgba(255,255,255,0.15)',
                         borderColor: 'white',
                         transform: 'translateY(-2px)',
                       },
                     }}
                   >
                     Mes inscriptions
                   </Button>
                 </Box>
               </>
             )}
           </Paper>
         )}
      </Container>
    </Box>
  );
};

export default PublicHomePage;
