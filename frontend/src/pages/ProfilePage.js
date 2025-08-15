import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Box,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr, enUS, es } from 'date-fns/locale';
import { setDarkMode, setLocale } from '../store/slices/uiSlice';
import api, { authAPI } from '../services/api';

const ProfilePage = () => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.auth);
  const { darkMode, locale } = useSelector((state) => state.ui);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: user?.address || '',
    bio: user?.bio || '',
  });

  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    language: 'fr',
    timezone: 'Europe/Paris',
  });

  // Charger les paramètres sauvegardés (hors mode sombre qui est géré globalement)
  useEffect(() => {
    try {
      const saved = localStorage.getItem('profile_settings');
      if (saved) {
        const parsed = JSON.parse(saved);
        setSettings(prev => ({ ...prev, ...parsed }));
      }
    } catch (_) {}
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSettingChange = (setting, value) => {
    setSettings(prev => {
      const next = { ...prev, [setting]: value };
      try { localStorage.setItem('profile_settings', JSON.stringify(next)); } catch (_) {}
      return next;
    });
  };

  const handleSave = async () => {
    try {
      // TODO: brancher à un endpoint backend si dispo
      try { localStorage.setItem('profile_form', JSON.stringify(formData)); } catch(_) {}
      setIsEditing(false);
    } catch (error) {
      console.error('Erreur lors de la mise à jour du profil:', error);
    }
  };

  const handleCancel = () => {
    setFormData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || '',
      bio: user?.bio || '',
    });
    setIsEditing(false);
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

  const dateFnsLocale = ({ 'fr-FR': fr, 'en-US': enUS, 'es-ES': es }[locale] || fr);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Mon profil
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {typeof error === 'string' ? error : error.detail || error.message || 'Une erreur est survenue'}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Informations personnelles */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" component="h2">
                Informations personnelles
              </Typography>
              <Button
                variant={isEditing ? "outlined" : "contained"}
                startIcon={isEditing ? <CancelIcon /> : <EditIcon />}
                onClick={isEditing ? handleCancel : () => setIsEditing(true)}
              >
                {isEditing ? 'Annuler' : 'Modifier'}
              </Button>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Prénom"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nom"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  disabled={!isEditing}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Téléphone"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Adresse"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  disabled={!isEditing}
                  InputProps={{
                    startAdornment: <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Bio"
                  multiline
                  rows={4}
                  value={formData.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  disabled={!isEditing}
                  placeholder="Parlez-nous un peu de vous..."
                />
              </Grid>
            </Grid>

            {isEditing && (
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={handleCancel}
                >
                  Annuler
                </Button>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                >
                  Sauvegarder
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Avatar et informations de base */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <Avatar
              sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
              src={user?.avatar}
            >
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </Avatar>
            
            <Typography variant="h6" gutterBottom>
              {user?.first_name} {user?.last_name}
            </Typography>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              @{user?.username}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CalendarIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Membre depuis"
                  secondary={user?.date_joined ? format(new Date(user.date_joined), 'dd MMM yyyy', { locale: dateFnsLocale }) : 'N/A'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <EmailIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Email"
                  secondary={user?.email}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Paramètres */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography variant="h5" component="h2" gutterBottom>
              Paramètres
            </Typography>

            <Grid container spacing={3}>
              {/* Notifications */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <NotificationsIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">
                        Notifications
                      </Typography>
                    </Box>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.emailNotifications}
                          onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                        />
                      }
                      label="Notifications par email"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.pushNotifications}
                          onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                        />
                      }
                      label="Notifications push"
                    />
                  </CardContent>
                </Card>
              </Grid>

              {/* Apparence */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PaletteIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">
                        Apparence
                      </Typography>
                    </Box>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={!!darkMode}
                          onChange={(e) => dispatch(setDarkMode(e.target.checked))}
                        />
                      }
                      label="Mode sombre"
                    />
                  </CardContent>
                </Card>
              </Grid>

              {/* Langue et fuseau horaire */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <LanguageIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">
                        Langue et région
                      </Typography>
                    </Box>
                    
                     <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Langue</InputLabel>
                      <Select
                         value={locale || 'fr-FR'}
                         onChange={(e) => {
                           const value = e.target.value;
                           console.log('ProfilePage - Changing locale to:', value);
                           dispatch(setLocale(value));
                           handleSettingChange('language', value.startsWith('fr') ? 'fr' : value.startsWith('en') ? 'en' : 'es');
                           // Plus besoin de recharger - la locale est maintenant réactive
                         }}
                        label="Langue"
                      >
                         <MenuItem value="fr-FR">Français</MenuItem>
                         <MenuItem value="en-US">English</MenuItem>
                         <MenuItem value="es-ES">Español</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <FormControl fullWidth>
                      <InputLabel>Fuseau horaire</InputLabel>
                      <Select
                        value={settings.timezone}
                        onChange={(e) => handleSettingChange('timezone', e.target.value)}
                        label="Fuseau horaire"
                      >
                        <MenuItem value="Europe/Paris">Europe/Paris</MenuItem>
                        <MenuItem value="Europe/London">Europe/London</MenuItem>
                        <MenuItem value="America/New_York">America/New_York</MenuItem>
                      </Select>
                    </FormControl>
                  </CardContent>
                </Card>
              </Grid>

              {/* Sécurité */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SecurityIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">
                        Sécurité
                      </Typography>
                    </Box>
                    
                    <Button
                      variant="outlined"
                      fullWidth
                      sx={{ mb: 1 }}
                      onClick={async () => {
                        const old_password = window.prompt('Ancien mot de passe');
                        if (old_password === null) return;
                        const new_password = window.prompt('Nouveau mot de passe');
                        if (new_password === null) return;
                        try {
                          await authAPI.changePassword(old_password, new_password);
                          alert('Mot de passe modifié avec succès. Veuillez vous reconnecter.');
                          // Forcer la reconnexion
                          localStorage.removeItem('access_token');
                          localStorage.removeItem('refresh_token');
                          window.location.href = '/login';
                        } catch (e) {
                          const msg = e?.response?.data?.error || 'Échec du changement de mot de passe';
                          const details = e?.response?.data?.details;
                          alert(Array.isArray(details) ? `${msg}:\n- ${details.join('\n- ')}` : msg);
                        }
                      }}
                    >
                      Changer le mot de passe
                    </Button>
                    
                    <Button
                      variant="outlined"
                      fullWidth
                      sx={{ mb: 1 }}
                    >
                      Authentification à deux facteurs
                    </Button>
                    
                    <Button
                      variant="outlined"
                      fullWidth
                      color="error"
                      onClick={async () => {
                        const ok = window.confirm("Voulez-vous vraiment supprimer votre compte ? Cette action est irréversible.");
                        if (!ok) return;
                        try {
                          // Appelle DELETE /auth/user/
                          await api.delete('/auth/user/');
                          // Nettoyage côté client
                          localStorage.removeItem('access_token');
                          localStorage.removeItem('refresh_token');
                          window.location.href = '/login';
                        } catch (e) {
                          console.error('Suppression de compte échouée', e);
                          alert("Suppression impossible pour le moment.");
                        }
                      }}
                    >
                      Supprimer le compte
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ProfilePage; 