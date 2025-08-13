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
import { registerForEvent } from '../store/slices/eventSlice';
import api, { eventAPI } from '../services/api';
import { CardElement, useElements, useStripe } from '@stripe/react-stripe-js';

const RegistrationModal = ({ open, onClose, event }) => {
  const dispatch = useDispatch();
  // Important: ne pas appeler useStripe()/useElements ici pour éviter l'erreur sans <Elements>
  const { registrationLoading, registrationError } = useSelector((state) => state.events);
  
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
      // 1) Créer l'inscription (peut être waitlisted)
      const payload = { event: event.id, notes: formData.notes, special_requirements: formData.special_requirements };
      if (formData.ticket_type_id !== '' && formData.ticket_type_id !== undefined && formData.ticket_type_id !== null) {
        payload.ticket_type_id = Number(formData.ticket_type_id);
      }
      const reg = await dispatch(registerForEvent(payload)).unwrap();

      // 2) Si paiement requis, afficher la section de paiement (gérée par Stripe Elements)
      if (Number(reg.price_paid) > 0 || isPaid) {
        setPendingReg(reg);
        dispatch(showSnackbar({ message: "Inscription créée. Procédez au paiement pour finaliser et recevoir votre QR par email.", severity: 'info', persist: true }));
        return; // Laisser l'utilisateur payer via la section dédiée
      }

      // Reset and close
      setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
      dispatch(showSnackbar({ message: "Inscription confirmée. Consultez votre email pour votre QR.", severity: 'success', persist: true }));
      onClose();
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
    setPaymentError('');
    onClose();
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
              <Typography variant="body2">📅 {new Date(event.start_date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</Typography>
              <Typography variant="body2">📍 {event.location}</Typography>
              <Typography variant="body2">{event.is_free ? '🆓 Gratuit' : `💰 ${event.price} €`}</Typography>
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
              <MenuItem value="">Par défaut {Number(event.price) > 0 ? `(${event.price} €)` : '(Gratuit)'}</MenuItem>
              {ticketTypes.map(tt => (
                <MenuItem key={tt.id} value={tt.id}>
                  {tt.name} — {tt.effective_price > 0 ? (
                    tt.has_discount ? (
                      <>
                        <span style={{ textDecoration: 'line-through', marginRight: 6 }}>{Number(tt.price).toFixed(2)} €</span>
                        <strong>{Number(tt.effective_price).toFixed(2)} €</strong>
                      </>
                    ) : (
                      <>{Number(tt.effective_price).toFixed(2)} €</>
                    )
                  ) : 'Gratuit'}
                  {tt.available_quantity !== null ? ` (restant: ${tt.available_quantity})` : ''}
                </MenuItem>
              ))}
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
              registrationId={pendingReg.id}
              setPaymentError={setPaymentError}
              setPaymentLoading={setPaymentLoading}
              onPaid={async () => {
                setFormData({ notes: '', special_requirements: '', ticket_type_id: '' });
                setPendingReg(null);
                dispatch(showSnackbar({ message: "Paiement confirmé. Votre billet (QR) a été envoyé à votre email.", severity: 'success', persist: true }));
                onClose();
              }}
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
            Annuler
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={registrationLoading || paymentLoading}
            startIcon={(registrationLoading || paymentLoading) ? <CircularProgress size={20} /> : null}
          >
            {(registrationLoading || paymentLoading) ? 'Traitement...' : (pendingReg && isPaid ? 'Inscription créée - procéder au paiement ci-dessous' : 'Confirmer l\'inscription')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RegistrationModal; 

// Section de paiement isolée qui nécessite le contexte <Elements>
const PaymentSection = ({ registrationId, setPaymentError, setPaymentLoading, onPaid }) => {
  const stripe = useStripe();
  const elements = useElements();

  const handlePay = async () => {
    setPaymentError('');
    if (!stripe || !elements) {
      setPaymentError("Stripe n'est pas prêt");
      return;
    }
    try {
      setPaymentLoading(true);
      const intent = await api.post(`/registrations/${registrationId}/create_payment_intent/`).then(r => r.data);
      const card = elements.getElement(CardElement);
      const { error, paymentIntent } = await stripe.confirmCardPayment(intent.client_secret, { payment_method: { card } });
      if (error) {
        setPaymentError(error.message || 'Paiement échoué');
        setPaymentLoading(false);
        return;
      }
      try {
        await api.post(`/registrations/${registrationId}/confirm_payment/`, { payment_intent_id: paymentIntent?.id || intent.payment_intent_id });
      } catch (e) {
        console.error('Erreur de confirmation serveur:', e);
      }
      setPaymentLoading(false);
      onPaid?.();
    } catch (e) {
      setPaymentLoading(false);
      setPaymentError('Erreur de paiement');
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>Informations de paiement</Typography>
      <Box sx={{ p: 1.5, border: '1px solid #ddd', borderRadius: 1 }}>
        <CardElement options={{ hidePostalCode: true }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button variant="contained" onClick={handlePay}>Payer</Button>
      </Box>
    </Box>
  );
};