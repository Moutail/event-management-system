import React, { useState, useEffect } from 'react';
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
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { showSnackbar } from '../store/slices/uiSlice';
import { registerForEvent, cancelPayment, fetchEventById } from '../store/slices/eventSlice';
import api, { eventAPI, formatPrice } from '../services/api';
import { CardElement, useElements, useStripe } from '@stripe/react-stripe-js';

const RegistrationModal = ({ open, onClose, event }) => {
  const dispatch = useDispatch();
  // Important: ne pas appeler useStripe()/useElements ici pour éviter l'erreur sans <Elements>
  const { registrationLoading, registrationError } = useSelector((state) => state.events);
  const { locale } = useSelector((state) => state.ui);
  
  const [formData, setFormData] = useState({
    notes: '',
    special_requirements: '',
    ticket_type_id: '',
  });
  const [ticketTypes, setTicketTypes] = useState([]);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState('');
  const [pendingReg, setPendingReg] = useState(null);

  useEffect(() => {
    const loadTickets = async () => {
      if (event?.id) {
        try {
          const res = await eventAPI.getTicketTypes(event.id);
          setTicketTypes(res.data || []);
        } catch (_) {}
      }
    };
    if (open) loadTickets();
  }, [open, event]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPaymentError('');

    try {
      // Si événement gratuit, créer l'inscription directement
      if (!isPaid) {
        const payload = { event: event.id, notes: formData.notes, special_requirements: formData.special_requirements };
        if (formData.ticket_type_id !== '' && formData.ticket_type_id !== undefined && formData.ticket_type_id !== null) {
          payload.ticket_type_id = Number(formData.ticket_type_id);
        }
        await dispatch(registerForEvent(payload)).unwrap();

        // Reset and close
        setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
        // Rafraîchir les données de l'événement pour mettre à jour le compteur
        if (event?.id) {
          dispatch(fetchEventById(event.id));
        }
        dispatch(showSnackbar({ message: "Inscription confirmée. Consultez votre email pour votre QR.", severity: 'success', persist: true }));
        onClose();
      } else {
        // Si événement payant, afficher directement la section de paiement SANS créer d'inscription
        setPendingReg({ 
          event: event.id, 
          notes: formData.notes, 
          special_requirements: formData.special_requirements,
          ticket_type_id: formData.ticket_type_id !== '' ? Number(formData.ticket_type_id) : null
        });
        dispatch(showSnackbar({ message: "Procédez au paiement pour confirmer votre inscription.", severity: 'info', persist: true }));
      }
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
    setPaymentError('');
    setPendingReg(null);
    onClose();
  };

  const handleCancelPayment = () => {
    // Maintenant c'est simple : on annule juste le processus de paiement
    // Aucune inscription n'a été créée, donc rien à supprimer côté serveur
    setPendingReg(null);
    dispatch(showSnackbar({ message: "Processus d'inscription annulé. Vous pouvez recommencer si vous le souhaitez.", severity: 'info' }));
  };

  if (!event) return null;

  const selectedTicket = ticketTypes.find(t => String(t.id) === String(formData.ticket_type_id));
  const selectedPrice = selectedTicket ? (Number(selectedTicket.effective_price ?? selectedTicket.price) || 0) : (Number(event.price) || 0);
  const selectedHasDiscount = selectedTicket ? !!selectedTicket.has_discount : false;
  const isPaid = selectedPrice > 0;
  const stripeEnabled = Boolean(process.env.REACT_APP_STRIPE_PK);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        S'inscrire à "{event.title}"
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Box sx={{
            mb: 3,
            p: 2.5,
            borderRadius: 2,
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider'
          }}>
            <Typography variant="h6" sx={{ mb: 1 }}>{event.title}</Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', color: 'text.secondary' }}>
              <Typography variant="body2">📅 {new Date(event.start_date).toLocaleDateString(locale || 'fr-FR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</Typography>
              <Typography variant="body2">📍 {event.location}</Typography>
              <Typography variant="body2">{event.is_free ? '🆓 Gratuit' : `💰 ${formatPrice(event.price)}`}</Typography>
            </Box>
          </Box>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="ticket-type-label">Type de billet</InputLabel>
            <Select
              labelId="ticket-type-label"
              name="ticket_type_id"
              label="Type de billet"
              value={formData.ticket_type_id}
              onChange={handleInputChange}
            >
              <MenuItem value="">Par défaut {Number(event.price) > 0 ? `(${formatPrice(event.price)})` : '(Gratuit)'}</MenuItem>
              {ticketTypes.map(tt => {
                const remaining = tt.available_quantity;
                const isSoldOut = remaining === 0;
                return (
                <MenuItem key={tt.id} value={tt.id} disabled={isSoldOut}>
                   {tt.name} — {Number(tt.effective_price) > 0 ? (
                    tt.has_discount ? (
                      <>
                        <span style={{ textDecoration: 'line-through', marginRight: 6 }}>{formatPrice(Number(tt.price))}</span>
                        <strong>{formatPrice(Number(tt.effective_price))}</strong>
                      </>
                    ) : (
                      <>{formatPrice(Number(tt.effective_price))}</>
                    )
                  ) : 'Gratuit'}
                  {remaining !== null && remaining !== undefined ? ` (restant: ${remaining})` : ''}
                  {isSoldOut ? ' — Épuisé' : ''}
                </MenuItem>
              )})}
            </Select>
          </FormControl>

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

          {pendingReg && isPaid && stripeEnabled && (
            <PaymentSection
              registrationData={pendingReg}
              setPaymentError={setPaymentError}
              setPaymentLoading={setPaymentLoading}
              onPaid={async () => {
                setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
                setPendingReg(null);
                // Rafraîchir les données de l'événement pour mettre à jour le compteur
                if (event?.id) {
                  dispatch(fetchEventById(event.id));
                }
                dispatch(showSnackbar({ message: "Paiement confirmé. Votre billet (QR) a été envoyé à votre email.", severity: 'success', persist: true }));
                onClose();
              }}
              onCancel={handleCancelPayment}
            />
          )}
          {pendingReg && isPaid && !stripeEnabled && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Paiement requis mais la clé publique Stripe n'est pas configurée (REACT_APP_STRIPE_PK).
            </Alert>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={registrationLoading || paymentLoading}>
            Fermer
          </Button>
          {pendingReg && isPaid && (
            <Button 
              onClick={handleCancelPayment} 
              disabled={registrationLoading || paymentLoading}
              color="error"
            >
              Annuler l'inscription
            </Button>
          )}
          <Button
            type="submit"
            variant="contained"
            disabled={registrationLoading || paymentLoading || (pendingReg && isPaid)}
            startIcon={(registrationLoading || paymentLoading) ? <CircularProgress size={20} /> : null}
          >
            {(registrationLoading || paymentLoading) ? 'Traitement...' : (pendingReg && isPaid ? 'Procéder au paiement ci-dessous' : (isPaid ? 'Procéder au paiement' : 'Confirmer l\'inscription'))}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RegistrationModal; 

// Section de paiement isolée qui nécessite le contexte <Elements>
const PaymentSection = ({ registrationData, setPaymentError, setPaymentLoading, onPaid, onCancel }) => {
  const stripe = useStripe();
  const elements = useElements();
  const dispatch = useDispatch();

  const handlePay = async () => {
    setPaymentError('');
    if (!stripe || !elements) {
      setPaymentError("Stripe n'est pas prêt");
      return;
    }
    try {
      setPaymentLoading(true);
      
      // 1. Créer l'inscription d'abord
      const payload = { 
        event: registrationData.event, 
        notes: registrationData.notes, 
        special_requirements: registrationData.special_requirements 
      };
      if (registrationData.ticket_type_id) {
        payload.ticket_type_id = registrationData.ticket_type_id;
      }
      const registration = await dispatch(registerForEvent(payload)).unwrap();

      // 2. Créer le payment intent
      const intent = await api.post(`/registrations/${registration.id}/create_payment_intent/`).then(r => r.data);
      
      // 3. Effectuer le paiement
      const card = elements.getElement(CardElement);
      const { error, paymentIntent } = await stripe.confirmCardPayment(intent.client_secret, { payment_method: { card } });
      if (error) {
        // Si le paiement échoue, annuler l'inscription qui vient d'être créée
        try {
          await dispatch(cancelPayment(registration.id));
        } catch (e) {
          console.error('Erreur lors de l\'annulation après échec de paiement:', e);
        }
        setPaymentError(error.message || 'Paiement échoué');
        setPaymentLoading(false);
        return;
      }
      
      // 4. Confirmer le paiement côté serveur et récupérer le statut final
      let finalRegistration = registration;
      try {
        const confirmResponse = await api.post(`/registrations/${registration.id}/confirm_payment/`, { payment_intent_id: paymentIntent?.id || intent.payment_intent_id });
        finalRegistration = confirmResponse.data;
      } catch (e) {
        console.error('Erreur de confirmation serveur:', e);
      }
      
      setPaymentLoading(false);
      
      // Afficher le message approprié selon le statut final
      if (finalRegistration.status === 'waitlisted') {
        dispatch(showSnackbar({ 
          message: "Paiement confirmé. Votre inscription est en attente de validation par l'organisateur.", 
          severity: 'warning', 
          persist: true 
        }));
      } else if (finalRegistration.status === 'confirmed') {
        dispatch(showSnackbar({ 
          message: "Paiement confirmé. Votre billet (QR) a été envoyé à votre email.", 
          severity: 'success', 
          persist: true 
        }));
      } else {
        dispatch(showSnackbar({ 
          message: "Paiement confirmé. Votre inscription est en cours de traitement.", 
          severity: 'info', 
          persist: true 
        }));
      }
      
      onPaid?.();
    } catch (e) {
      setPaymentLoading(false);
      setPaymentError('Erreur lors de l\'inscription ou du paiement');
      console.error('Erreur complète:', e);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>Informations de paiement</Typography>
      <Box sx={{ p: 1.5, border: '1px solid #ddd', borderRadius: 1 }}>
        <CardElement options={{ hidePostalCode: true }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button variant="outlined" color="error" onClick={onCancel}>
          Annuler l'inscription
        </Button>
        <Button variant="contained" onClick={handlePay}>Payer</Button>
      </Box>
    </Box>
  );
};