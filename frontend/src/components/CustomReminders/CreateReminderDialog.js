import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Grid,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Autocomplete,
  Divider
} from '@mui/material';
import {
  Email as EmailIcon,
  Sms as SmsIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';
import { toast } from 'react-toastify';
import api from '../../services/api';

const CreateReminderDialog = ({ 
  open, 
  onClose, 
  eventId, 
  eventTitle, 
  reminder = null, 
  onSuccess 
}) => {
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    reminder_type: 'general',
    target_audience: 'all',
    send_email: true,
    send_sms: true,
    scheduled_at: null,
    custom_recipient_ids: [],
    event: eventId || null
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [registrations, setRegistrations] = useState([]);
  const [loadingRegistrations, setLoadingRegistrations] = useState(false);
  const [events, setEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(false);

  // Types de rappels
  const reminderTypes = [
    { value: 'general', label: 'Rappel général' },
    { value: 'reminder', label: 'Rappel d\'événement' },
    { value: 'update', label: 'Mise à jour' },
    { value: 'cancellation', label: 'Annulation' },
    { value: 'postponement', label: 'Report' },
    { value: 'custom', label: 'Message personnalisé' }
  ];

  // Types d'audience
  const audienceTypes = [
    { value: 'all', label: 'Tous les participants' },
    { value: 'confirmed', label: 'Participants confirmés uniquement' },
    { value: 'waitlisted', label: 'Liste d\'attente uniquement' },
    { value: 'attended', label: 'Participants présents uniquement' },
    { value: 'custom', label: 'Sélection personnalisée' }
  ];

  // Charger les inscriptions pour la sélection personnalisée
  // Charger les événements de l'utilisateur
  const loadEvents = async () => {
    try {
      setLoadingEvents(true);
      console.log('🔍 DEBUG: Chargement des événements...');
      const response = await api.get('/events/my_events/');
      console.log('🔍 DEBUG: Événements reçus:', response.data);
      setEvents(response.data.results || response.data);
    } catch (err) {
      console.error('🔍 DEBUG: Erreur lors du chargement des événements:', err);
      setError('Erreur lors du chargement des événements');
    } finally {
      setLoadingEvents(false);
    }
  };

  const loadRegistrations = async () => {
    if (!formData.event) return;
    
    try {
      setLoadingRegistrations(true);
      console.log('🔍 DEBUG: Chargement des inscriptions pour événement:', formData.event);
      const response = await api.get(`/registrations/?event=${formData.event}`);
      console.log('🔍 DEBUG: Inscriptions reçues:', response.data);
      setRegistrations(response.data.results || response.data);
    } catch (err) {
      console.error('🔍 DEBUG: Erreur lors du chargement des inscriptions:', err);
      toast.error('Erreur lors du chargement des inscriptions');
    } finally {
      setLoadingRegistrations(false);
    }
  };

  // Initialiser le formulaire
  useEffect(() => {
    if (open) {
      // Charger les événements
      loadEvents();
      
      if (reminder) {
        // Mode édition
        setFormData({
          title: reminder.title || '',
          message: reminder.message || '',
          reminder_type: reminder.reminder_type || 'general',
          target_audience: reminder.target_audience || 'all',
          send_email: reminder.send_email !== false,
          send_sms: reminder.send_sms !== false,
          scheduled_at: reminder.scheduled_at ? new Date(reminder.scheduled_at) : null,
          custom_recipient_ids: reminder.custom_recipients?.map(r => r.id) || [],
          event: reminder.event || eventId || null
        });
      } else {
        // Mode création
        setFormData({
          title: '',
          message: '',
          reminder_type: 'general',
          target_audience: 'all',
          send_email: true,
          send_sms: true,
          scheduled_at: null,
          custom_recipient_ids: [],
          event: eventId || null
        });
      }
      setError(null);
    }
  }, [open, reminder]);

  // Charger les inscriptions quand l'audience ou l'événement change
  useEffect(() => {
    if (formData.target_audience === 'custom' && formData.event) {
      loadRegistrations();
    }
  }, [formData.target_audience, formData.event]);

  // Gérer les changements de formulaire
  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Réinitialiser les destinataires personnalisés si on change d'audience
    if (field === 'target_audience' && value !== 'custom') {
      setFormData(prev => ({
        ...prev,
        custom_recipient_ids: []
      }));
    }
  };

  // Valider le formulaire
  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Le titre est requis');
      return false;
    }
    
    if (!formData.message.trim()) {
      setError('Le message est requis');
      return false;
    }
    
    if (!formData.event) {
      setError('Vous devez sélectionner un événement');
      return false;
    }
    
    if (!formData.send_email && !formData.send_sms) {
      setError('Vous devez sélectionner au moins un canal d\'envoi (email ou SMS)');
      return false;
    }
    
    if (formData.target_audience === 'custom' && formData.custom_recipient_ids.length === 0) {
      setError('Vous devez sélectionner au moins un destinataire pour la sélection personnalisée');
      return false;
    }
    
    if (formData.scheduled_at && formData.scheduled_at <= new Date()) {
      setError('La date d\'envoi programmée doit être dans le futur');
      return false;
    }
    
    return true;
  };

  // Soumettre le formulaire
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const payload = {
        event: formData.event,
        title: formData.title.trim(),
        message: formData.message.trim(),
        reminder_type: formData.reminder_type,
        target_audience: formData.target_audience,
        send_email: formData.send_email,
        send_sms: formData.send_sms,
        scheduled_at: formData.scheduled_at ? formData.scheduled_at.toISOString() : null
      };

      // Ajouter les destinataires personnalisés si nécessaire
      if (formData.target_audience === 'custom') {
        payload.custom_recipient_ids = formData.custom_recipient_ids;
      }

      if (reminder) {
        // Mode édition
        await api.put(`/custom-reminders/${reminder.id}/`, payload);
        toast.success('Rappel modifié avec succès!');
      } else {
        // Mode création
        await api.post('/custom-reminders/', payload);
        toast.success('Rappel créé avec succès!');
      }

      onSuccess();
    } catch (err) {
      console.error('Erreur lors de la sauvegarde:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Erreur lors de la sauvegarde du rappel';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Obtenir le nombre de destinataires
  const getRecipientsCount = () => {
    if (formData.target_audience === 'custom') {
      return formData.custom_recipient_ids.length;
    }
    // Pour les autres types, on ne peut pas calculer sans faire un appel API
    return 'Calculé automatiquement';
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
      <Dialog 
        open={open} 
        onClose={onClose} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { minHeight: '70vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6">
              {reminder ? 'Modifier le Rappel' : 'Créer un Nouveau Rappel'}
            </Typography>
            <Chip 
              label={eventTitle} 
              color="primary" 
              size="small" 
              variant="outlined"
            />
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Titre */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Titre du rappel"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Ex: Rappel important pour l'événement"
                required
              />
            </Grid>

            {/* Sélection d'événement */}
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Événement</InputLabel>
                <Select
                  value={formData.event || ''}
                  onChange={(e) => handleChange('event', e.target.value)}
                  label="Événement"
                  required
                  disabled={loadingEvents}
                >
                  {loadingEvents ? (
                    <MenuItem disabled>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Chargement des événements...
                    </MenuItem>
                  ) : (
                    events.map((event) => (
                      <MenuItem key={event.id} value={event.id}>
                        {event.title} - {new Date(event.start_date).toLocaleDateString('fr-FR')}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>

            {/* Type de rappel */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type de rappel</InputLabel>
                <Select
                  value={formData.reminder_type}
                  onChange={(e) => handleChange('reminder_type', e.target.value)}
                  label="Type de rappel"
                >
                  {reminderTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Audience cible */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Audience cible</InputLabel>
                <Select
                  value={formData.target_audience}
                  onChange={(e) => handleChange('target_audience', e.target.value)}
                  label="Audience cible"
                >
                  {audienceTypes.map((audience) => (
                    <MenuItem key={audience.value} value={audience.value}>
                      {audience.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Sélection personnalisée des destinataires */}
            {formData.target_audience === 'custom' && (
              <Grid item xs={12}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    <PeopleIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Sélectionner les destinataires
                  </Typography>
                  {loadingRegistrations ? (
                    <Box display="flex" justifyContent="center" p={2}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : (
                    <Autocomplete
                      multiple
                      options={registrations}
                      getOptionLabel={(option) => `${option.guest_name} (${option.guest_email})`}
                      value={registrations.filter(r => formData.custom_recipient_ids.includes(r.id))}
                      onChange={(event, newValue) => {
                        handleChange('custom_recipient_ids', newValue.map(r => r.id));
                      }}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={`${option.guest_name} (${option.status})`}
                            {...getTagProps({ index })}
                            key={option.id}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          placeholder="Sélectionner les participants..."
                          helperText={`${formData.custom_recipient_ids.length} destinataire(s) sélectionné(s)`}
                        />
                      )}
                    />
                  )}
                </Box>
              </Grid>
            )}

            {/* Message */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Message"
                value={formData.message}
                onChange={(e) => handleChange('message', e.target.value)}
                placeholder="Tapez votre message ici..."
                required
                helperText={`${formData.message.length} caractères`}
              />
            </Grid>

            <Divider sx={{ width: '100%', my: 2 }} />

            {/* Canaux d'envoi */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Canaux d'envoi
              </Typography>
              <Box display="flex" gap={3}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.send_email}
                      onChange={(e) => handleChange('send_email', e.target.checked)}
                      icon={<EmailIcon />}
                      checkedIcon={<EmailIcon />}
                    />
                  }
                  label="Email"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.send_sms}
                      onChange={(e) => handleChange('send_sms', e.target.checked)}
                      icon={<SmsIcon />}
                      checkedIcon={<SmsIcon />}
                    />
                  }
                  label="SMS"
                />
              </Box>
            </Grid>

            {/* Programmation */}
            <Grid item xs={12}>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  <ScheduleIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Programmation (optionnel)
                </Typography>
                <DateTimePicker
                  label="Date et heure d'envoi"
                  value={formData.scheduled_at}
                  onChange={(newValue) => handleChange('scheduled_at', newValue)}
                  minDateTime={new Date()}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                  Si aucune date n'est sélectionnée, le rappel sera créé en brouillon
                </Typography>
              </Box>
            </Grid>

            {/* Résumé */}
            <Grid item xs={12}>
              <Box 
                sx={{ 
                  p: 2, 
                  bgcolor: 'grey.50', 
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.200'
                }}
              >
                <Typography variant="subtitle2" gutterBottom>
                  Résumé du rappel
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Destinataires:</strong> {getRecipientsCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Canaux:</strong> {formData.send_email ? 'Email ' : ''}{formData.send_sms ? 'SMS' : ''}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Envoi:</strong> {formData.scheduled_at ? 'Programmé' : 'Immédiat'}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button onClick={onClose} disabled={loading}>
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Sauvegarde...' : (reminder ? 'Modifier' : 'Créer')}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default CreateReminderDialog;
