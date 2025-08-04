import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { registerForEvent } from '../store/slices/eventSlice';

const RegistrationModal = ({ open, onClose, event }) => {
  const dispatch = useDispatch();
  const { registrationLoading, registrationError } = useSelector((state) => state.events);
  
  const [formData, setFormData] = useState({
    notes: '',
    special_requirements: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await dispatch(registerForEvent({
        event: event.id,
        ...formData
      })).unwrap();
      
      // Réinitialiser le formulaire
      setFormData({
        notes: '',
        special_requirements: '',
      });
      
      onClose();
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
    }
  };

  const handleClose = () => {
    // Réinitialiser le formulaire
    setFormData({
      notes: '',
      special_requirements: '',
    });
    onClose();
  };

  if (!event) return null;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        S'inscrire à "{event.title}"
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              📅 {new Date(event.start_date).toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              📍 {event.location}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              💰 {event.is_free ? 'Gratuit' : `${event.price} €`}
            </Typography>
          </Box>

          {registrationError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {registrationError}
            </Alert>
          )}

          <TextField
            name="notes"
            label="Notes (optionnel)"
            multiline
            rows={3}
            fullWidth
            value={formData.notes}
            onChange={handleInputChange}
            placeholder="Ajoutez des notes ou commentaires..."
            sx={{ mb: 2 }}
          />

          <TextField
            name="special_requirements"
            label="Besoins spéciaux (optionnel)"
            multiline
            rows={2}
            fullWidth
            value={formData.special_requirements}
            onChange={handleInputChange}
            placeholder="Accessibilité, régime alimentaire, etc."
            helperText="Informez l'organisateur de vos besoins particuliers"
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={registrationLoading}>
            Annuler
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={registrationLoading}
            startIcon={registrationLoading ? <CircularProgress size={20} /> : null}
          >
            {registrationLoading ? 'Inscription...' : 'Confirmer l\'inscription'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RegistrationModal; 