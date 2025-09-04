import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { register } from '../store/slices/authSlice';
import NotificationDialog from '../components/NotificationDialog';

const RegisterPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error, isAuthenticated, user } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    phone: '',
    country: 'FR',
    role: 'participant',
  });

  const [errors, setErrors] = useState({});
  const [notification, setNotification] = useState({
    open: false,
    title: '',
    message: '',
    type: 'success'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    
    // Effacer l'erreur du champ modifié
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: '',
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'L\'email n\'est pas valide';
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Le mot de passe doit contenir au moins 8 caractères';
    }

    if (formData.password !== formData.password2) {
      newErrors.password2 = 'Les mots de passe ne correspondent pas';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Le prénom est requis';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Le nom est requis';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Le numéro de téléphone est requis';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      const result = await dispatch(register(formData));
      if (register.fulfilled.match(result)) {
        // Rediriger selon le rôle
        if (formData.role === 'organizer') {
          // Afficher un message d'attente d'approbation
          setNotification({
            open: true,
            title: 'Compte Organisateur Créé !',
            message: '🎉 Votre compte organisateur a été créé avec succès !\n\n⏳ Votre compte est maintenant en attente d\'approbation par un Super Administrateur.\n\n📧 Vous recevrez un email de confirmation une fois approuvé.\n\n🔒 En attendant, vous pouvez vous connecter et accéder aux fonctionnalités participant (voir événements, s\'inscrire).',
            type: 'warning'
          });
        } else {
          // Rediriger directement vers la connexion pour les participants
          setNotification({
            open: true,
            title: 'Compte Participant Créé !',
            message: '🎉 Votre compte participant a été créé avec succès !\n\n✅ Vous pouvez maintenant vous connecter et accéder à toutes les fonctionnalités participant.',
            type: 'success'
          });
        }
      }
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
    }
  };

  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
    // Rediriger vers la page de connexion après fermeture de la notification
    navigate('/login');
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h5">
            Inscription
          </Typography>

          {isAuthenticated && (
            <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
              Vous êtes déjà connecté en tant que <strong>{user?.username}</strong> ({user?.profile?.role === 'super_admin' ? 'Super Admin' : user?.profile?.role === 'organizer' ? 'Organisateur' : 'Participant'}). 
              <br />
              <Button 
                variant="text" 
                color="primary" 
                onClick={() => navigate('/dashboard')}
                sx={{ p: 0, minWidth: 'auto', textTransform: 'none' }}
              >
                Aller au dashboard
              </Button>
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {typeof error === 'string' ? error : error.detail || error.message || 'Une erreur est survenue'}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Nom d'utilisateur"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleChange}
              error={!!errors.username}
              helperText={errors.username}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Adresse email"
              name="email"
              autoComplete="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              error={!!errors.email}
              helperText={errors.email}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="first_name"
              label="Prénom"
              name="first_name"
              autoComplete="given-name"
              value={formData.first_name}
              onChange={handleChange}
              error={!!errors.first_name}
              helperText={errors.first_name}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="last_name"
              label="Nom"
              name="last_name"
              autoComplete="family-name"
              value={formData.last_name}
              onChange={handleChange}
              error={!!errors.last_name}
              helperText={errors.last_name}
            />
            
            <FormControl fullWidth margin="normal" required>
              <InputLabel id="country-label">Pays</InputLabel>
              <Select
                labelId="country-label"
                id="country"
                name="country"
                value={formData.country}
                label="Pays"
                onChange={handleChange}
                error={!!errors.country}
              >
                <MenuItem value="FR">🇫🇷 France (+33)</MenuItem>
                <MenuItem value="US">🇺🇸 États-Unis (+1)</MenuItem>
                <MenuItem value="CA">🇨🇦 Canada (+1)</MenuItem>
                <MenuItem value="BE">🇧🇪 Belgique (+32)</MenuItem>
                <MenuItem value="CH">🇨🇭 Suisse (+41)</MenuItem>
                <MenuItem value="LU">🇱🇺 Luxembourg (+352)</MenuItem>
                <MenuItem value="DE">🇩🇪 Allemagne (+49)</MenuItem>
                <MenuItem value="IT">🇮🇹 Italie (+39)</MenuItem>
                <MenuItem value="ES">🇪🇸 Espagne (+34)</MenuItem>
                <MenuItem value="GB">🇬🇧 Royaume-Uni (+44)</MenuItem>
                <MenuItem value="NL">🇳🇱 Pays-Bas (+31)</MenuItem>
                <MenuItem value="PT">🇵🇹 Portugal (+351)</MenuItem>
                <MenuItem value="IE">🇮🇪 Irlande (+353)</MenuItem>
                <MenuItem value="AT">🇦🇹 Autriche (+43)</MenuItem>
                <MenuItem value="SE">🇸🇪 Suède (+46)</MenuItem>
                <MenuItem value="NO">🇳🇴 Norvège (+47)</MenuItem>
                <MenuItem value="DK">🇩🇰 Danemark (+45)</MenuItem>
                <MenuItem value="FI">🇫🇮 Finlande (+358)</MenuItem>
                <MenuItem value="PL">🇵🇱 Pologne (+48)</MenuItem>
                <MenuItem value="CZ">🇨🇿 République tchèque (+420)</MenuItem>
                <MenuItem value="HU">🇭🇺 Hongrie (+36)</MenuItem>
                <MenuItem value="RO">🇷🇴 Roumanie (+40)</MenuItem>
                <MenuItem value="BG">🇧🇬 Bulgarie (+359)</MenuItem>
                <MenuItem value="HR">🇭🇷 Croatie (+385)</MenuItem>
                <MenuItem value="SI">🇸🇮 Slovénie (+386)</MenuItem>
                <MenuItem value="SK">🇸🇰 Slovaquie (+421)</MenuItem>
                <MenuItem value="LT">🇱🇹 Lituanie (+370)</MenuItem>
                <MenuItem value="LV">🇱🇻 Lettonie (+371)</MenuItem>
                <MenuItem value="EE">🇪🇪 Estonie (+372)</MenuItem>
                <MenuItem value="CY">🇨🇾 Chypre (+357)</MenuItem>
                <MenuItem value="MT">🇲🇹 Malte (+356)</MenuItem>
                <MenuItem value="GR">🇬🇷 Grèce (+30)</MenuItem>
                <MenuItem value="TG">🇹🇬 Togo (+228)</MenuItem>
                <MenuItem value="CI">🇨🇮 Côte d'Ivoire (+225)</MenuItem>
                <MenuItem value="SN">🇸🇳 Sénégal (+221)</MenuItem>
                <MenuItem value="ML">🇲🇱 Mali (+223)</MenuItem>
                <MenuItem value="BF">🇧🇫 Burkina Faso (+226)</MenuItem>
                <MenuItem value="NE">🇳🇪 Niger (+227)</MenuItem>
                <MenuItem value="TD">🇹🇩 Tchad (+235)</MenuItem>
                <MenuItem value="CM">🇨🇲 Cameroun (+237)</MenuItem>
                <MenuItem value="CF">🇨🇫 République centrafricaine (+236)</MenuItem>
                <MenuItem value="CG">🇨🇬 Congo (+242)</MenuItem>
                <MenuItem value="CD">🇨🇩 République démocratique du Congo (+243)</MenuItem>
                <MenuItem value="GA">🇬🇦 Gabon (+241)</MenuItem>
                <MenuItem value="GQ">🇬🇶 Guinée équatoriale (+240)</MenuItem>
                <MenuItem value="ST">🇸🇹 Sao Tomé-et-Principe (+239)</MenuItem>
                <MenuItem value="AO">🇦🇴 Angola (+244)</MenuItem>
                <MenuItem value="NA">🇳🇦 Namibie (+264)</MenuItem>
                <MenuItem value="ZA">🇿🇦 Afrique du Sud (+27)</MenuItem>
                <MenuItem value="BW">🇧🇼 Botswana (+267)</MenuItem>
                <MenuItem value="ZW">🇿🇼 Zimbabwe (+263)</MenuItem>
                <MenuItem value="ZM">🇿🇲 Zambie (+260)</MenuItem>
                <MenuItem value="MW">🇲🇼 Malawi (+265)</MenuItem>
                <MenuItem value="MZ">🇲🇿 Mozambique (+258)</MenuItem>
                <MenuItem value="MG">🇲🇬 Madagascar (+261)</MenuItem>
                <MenuItem value="MU">🇲🇺 Maurice (+230)</MenuItem>
                <MenuItem value="SC">🇸🇨 Seychelles (+248)</MenuItem>
                <MenuItem value="KM">🇰🇲 Comores (+269)</MenuItem>
                <MenuItem value="DJ">🇩🇯 Djibouti (+253)</MenuItem>
                <MenuItem value="SO">🇸🇴 Somalie (+252)</MenuItem>
                <MenuItem value="ET">🇪🇹 Éthiopie (+251)</MenuItem>
                <MenuItem value="ER">🇪🇷 Érythrée (+291)</MenuItem>
                <MenuItem value="SD">🇸🇩 Soudan (+249)</MenuItem>
                <MenuItem value="SS">🇸🇸 Soudan du Sud (+211)</MenuItem>
                <MenuItem value="EG">🇪🇬 Égypte (+20)</MenuItem>
                <MenuItem value="LY">🇱🇾 Libye (+218)</MenuItem>
                <MenuItem value="TN">🇹🇳 Tunisie (+216)</MenuItem>
                <MenuItem value="DZ">🇩🇿 Algérie (+213)</MenuItem>
                <MenuItem value="MA">🇲🇦 Maroc (+212)</MenuItem>
                <MenuItem value="EH">🇪🇭 Sahara occidental (+212)</MenuItem>
                <MenuItem value="MR">🇲🇷 Mauritanie (+222)</MenuItem>
                <MenuItem value="GM">🇬🇲 Gambie (+220)</MenuItem>
                <MenuItem value="GN">🇬🇳 Guinée (+224)</MenuItem>
                <MenuItem value="GW">🇬🇼 Guinée-Bissau (+245)</MenuItem>
                <MenuItem value="SL">🇸🇱 Sierra Leone (+232)</MenuItem>
                <MenuItem value="LR">🇱🇷 Liberia (+231)</MenuItem>
                <MenuItem value="GH">🇬🇭 Ghana (+233)</MenuItem>
                <MenuItem value="BJ">🇧🇯 Bénin (+229)</MenuItem>
                <MenuItem value="NG">🇳🇬 Nigeria (+234)</MenuItem>
                <MenuItem value="RW">🇷🇼 Rwanda (+250)</MenuItem>
                <MenuItem value="KE">🇰🇪 Kenya (+254)</MenuItem>
                <MenuItem value="TZ">🇹🇿 Tanzanie (+255)</MenuItem>
                <MenuItem value="UG">🇺🇬 Ouganda (+256)</MenuItem>
                <MenuItem value="BI">🇧🇮 Burundi (+257)</MenuItem>
                <MenuItem value="RE">🇷🇪 La Réunion (+262)</MenuItem>
                <MenuItem value="LS">🇱🇸 Lesotho (+266)</MenuItem>
                <MenuItem value="SZ">🇸🇿 Eswatini (+268)</MenuItem>
                <MenuItem value="YT">🇾🇹 Mayotte (+262)</MenuItem>
              </Select>
              {errors.country && <FormHelperText error>{errors.country}</FormHelperText>}
            </FormControl>
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="phone"
              label="Numéro de téléphone"
              name="phone"
              autoComplete="tel"
              value={formData.phone}
              onChange={handleChange}
              error={!!errors.phone}
              helperText={errors.phone}
            />
            
            <FormControl fullWidth margin="normal" required>
              <InputLabel id="role-label">Rôle</InputLabel>
              <Select
                labelId="role-label"
                id="role"
                name="role"
                value={formData.role}
                label="Rôle"
                onChange={handleChange}
              >
                <MenuItem value="participant">Participant</MenuItem>
                <MenuItem value="organizer">Organisateur</MenuItem>
              </Select>
              <FormHelperText>
                {formData.role === 'organizer' 
                  ? 'Les comptes organisateurs nécessitent une approbation administrative'
                  : 'Les comptes participants sont activés immédiatement'
                }
              </FormHelperText>
            </FormControl>
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Mot de passe"
              type="password"
              id="password"
              autoComplete="new-password"
              value={formData.password}
              onChange={handleChange}
              error={!!errors.password}
              helperText={errors.password}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password2"
              label="Confirmer le mot de passe"
              type="password"
              id="password2"
              autoComplete="new-password"
              value={formData.password2}
              onChange={handleChange}
              error={!!errors.password2}
              helperText={errors.password2}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Inscription...' : 'S\'inscrire'}
            </Button>
            
            <Box sx={{ textAlign: 'center' }}>
              <Link component={RouterLink} to="/login" variant="body2">
                {"Vous avez déjà un compte ? Connectez-vous"}
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
      
      {/* Dialog de notification */}
      <NotificationDialog
        open={notification.open}
        onClose={handleNotificationClose}
        title={notification.title}
        message={notification.message}
        type={notification.type}
        actionText="Continuer"
      />
    </Container>
  );
};

export default RegisterPage; 