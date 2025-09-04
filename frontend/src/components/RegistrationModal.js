import React, { useState, useEffect, useCallback } from 'react';
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
import { registerForEvent, fetchEventById, clearRegistrationError } from '../store/slices/eventSlice';
import api, { eventAPI, formatPrice } from '../services/api';
import PaymentSection from './PaymentSection';

const RegistrationModal = ({ open, onClose, event }) => {
  const dispatch = useDispatch();
  // Important: ne pas appeler useStripe()/useElements ici pour éviter l'erreur sans <Elements>
  const { registrationLoading, registrationError } = useSelector((state) => state.events);
  const { locale } = useSelector((state) => state.ui);
  const { user } = useSelector((state) => state.auth);
  
  // 🎯 NOUVEAUX ÉTATS POUR LES INVITÉS - DÉPLACÉS AVANT LE useEffect
  const [formData, setFormData] = useState({
    ticket_type_id: null,
    session_type_id: '',
  });
  
  const [isGuestRegistration, setIsGuestRegistration] = useState(false);
  const [guestData, setGuestData] = useState({
    guest_full_name: '',
    guest_email: '',
    guest_phone: '',
    guest_country: 'FR' // 🎯 NOUVEAU : Pays par défaut
  });
  const [ticketTypes, setTicketTypes] = useState([]);
  const [sessionTypes, setSessionTypes] = useState([]);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [pendingReg, setPendingReg] = useState(null);
  // 🎯 NOUVEAU ÉTAT : Empêcher la soumission après nettoyage d'erreur
  const [isClearingError, setIsClearingError] = useState(false);
  // 🎯 NOUVEAU ÉTAT : Forcer le re-rendu du Select
  const [forceRender, setForceRender] = useState(0);
  
  // 🎯 DEBUG : Tracer les changements de registrationError - DÉPLACÉ APRÈS LES ÉTATS
  useEffect(() => {
    console.log('🔍 [REGISTRATION_ERROR] État changé:', registrationError);
    console.log('🔍 [REGISTRATION_ERROR] Type de registrationError:', typeof registrationError);
    console.log('🔍 [REGISTRATION_ERROR] isClearingError:', isClearingError);
    
    // 🎯 NOUVEAU : Forcer la mise à jour de l'état quand l'erreur est nettoyée
    if (!registrationError && isClearingError) {
      console.log('🔍 [REGISTRATION_ERROR] Erreur nettoyée, réinitialisation de isClearingError');
      setIsClearingError(false);
    }
    
    // 🎯 NOUVEAU : Log détaillé pour le débogage
    if (registrationError) {
      console.log('🔍 [REGISTRATION_ERROR] Erreur détectée:', {
        error: registrationError,
        includesEmail: registrationError.includes && registrationError.includes('email'),
        includesDejaUtilise: registrationError.includes && registrationError.includes('déjà utilisé'),
        isString: typeof registrationError === 'string'
      });
    }
  }, [registrationError, isClearingError]);

  // 🎯 NOUVEAU : Forcer le re-rendu du Select quand ticket_type_id change
  useEffect(() => {
    console.log('🔍 [TICKET_CHANGE] ticket_type_id changé:', formData.ticket_type_id);
    console.log('🔍 [TICKET_CHANGE] Type:', typeof formData.ticket_type_id);
    if (formData.ticket_type_id === '') {
      console.log('🔍 [TICKET_CHANGE] 🎯 BILLET PAR DÉFAUT DÉTECTÉ, FORÇAGE DU RE-RENDU !');
      setForceRender(prev => prev + 1);
    }
  }, [formData.ticket_type_id]);
  
  console.log('🔍 [REGISTRATION_MODAL] Rendu avec registrationError:', registrationError);
  
  // 🎯 NOUVEAU : Log détaillé de l'état des champs d'invité
  useEffect(() => {
    console.log('🔍 [GUEST_FIELDS] État des champs d\'invité:', {
      isGuestRegistration,
      guestData: {
        fullName: guestData.guest_full_name,
        email: guestData.guest_email,
        phone: guestData.guest_phone
      },
      user: !!user,
      sessionTypes: sessionTypes.length,
      selectedSessionType: formData.session_type_id
    });
  }, [isGuestRegistration, guestData, user, sessionTypes.length, formData.session_type_id]);

  useEffect(() => {
    const loadData = async () => {
      if (event?.id) {
        try {
          // Charger les types de billets
          const ticketsRes = await eventAPI.getTicketTypes(event.id);
          console.log('🔍 [LOAD_DATA] Types de billets récupérés:', ticketsRes.data);
          console.log('🔍 [LOAD_DATA] Détail des types de billets:', ticketsRes.data?.map(t => ({ id: t.id, name: t.name, type: typeof t.id })));
          setTicketTypes(ticketsRes.data || []);
          
          // Charger les types de sessions
          const sessionsRes = await eventAPI.getSessionTypes(event.id);
          console.log('🔍 DEBUG: Sessions récupérées:', sessionsRes.data);
          console.log('🔍 DEBUG: Nombre de sessions:', sessionsRes.data?.length);
          setSessionTypes(sessionsRes.data || []);
        } catch (_) {}
      }
    };
    if (open) loadData();
  }, [open, event]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log('🔍 [INPUT_CHANGE] ===== DÉBUT handleInputChange =====');
    console.log('🔍 [INPUT_CHANGE] name:', name);
    console.log('🔍 [INPUT_CHANGE] value:', value, 'type:', typeof value);
    console.log('🔍 [INPUT_CHANGE] État formData AVANT:', formData);
    console.log('🔍 [INPUT_CHANGE] ticketTypes disponibles:', ticketTypes.map(t => ({ id: t.id, name: t.name, type: typeof t.id })));
    
    // 🎯 NOUVEAU : Log spécial pour le billet par défaut
    if (name === 'ticket_type_id' && (value === '' || value === null || value === undefined)) {
      console.log('🔍 [INPUT_CHANGE] 🎯 BILLET PAR DÉFAUT SÉLECTIONNÉ !');
      console.log('🔍 [INPUT_CHANGE] 🎯 Valeur reçue:', value);
      console.log('🔍 [INPUT_CHANGE] 🎯 Type de valeur:', typeof value);
    }
    
    setFormData(prev => {
      const newFormData = {
        ...prev,
        [name]: value
      };
      console.log('🔍 [INPUT_CHANGE] Nouveau formData:', newFormData);
      console.log('🔍 [INPUT_CHANGE] ===== FIN handleInputChange =====');
      
      // 🎯 NOUVEAU : Forcer le re-rendu du Select
      if (name === 'ticket_type_id') {
        console.log('🔍 [INPUT_CHANGE] 🔄 Forçage du re-rendu du Select');
        setForceRender(prev => prev + 1);
      }
      
      return newFormData;
    });
  };
  
  // 🎯 NOUVELLE FONCTION POUR LES DONNÉES D'INVITÉ
  const handleGuestDataChange = (e) => {
    const { name, value } = e.target;
    console.log('🔍 [GUEST_DATA] handleGuestDataChange appelé:', { name, value });
    
    setGuestData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 🎯 CORRECTION : Nettoyer l'erreur d'inscription quand l'utilisateur modifie l'email
    if (name === 'guest_email') {
      console.log('🔍 [GUEST_DATA] Email modifié, dispatch clearRegistrationError()');
      console.log('🔍 [GUEST_DATA] État actuel registrationError:', registrationError);
      console.log('🔍 [GUEST_DATA] Type de registrationError:', typeof registrationError);
      
      setIsClearingError(true);
      dispatch(clearRegistrationError());
      console.log('🔍 [GUEST_DATA] clearRegistrationError() dispatché');
      
      // 🎯 CORRECTION : Nettoyer aussi les autres erreurs liées à l'email
      if (registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))) {
        console.log('🔍 [GUEST_DATA] Nettoyage forcé de l\'erreur d\'email');
        console.log('🔍 [GUEST_DATA] Délai de 50ms pour nettoyage forcé');
        // Forcer la mise à jour de l'état local
        setTimeout(() => {
          console.log('🔍 [GUEST_DATA] Nettoyage forcé terminé, isClearingError = false');
          setIsClearingError(false);
        }, 50);
      } else {
        console.log('🔍 [GUEST_DATA] Nettoyage normal de l\'erreur');
        console.log('🔍 [GUEST_DATA] Délai de 100ms pour nettoyage normal');
        // Réinitialiser l'état après un délai normal
        setTimeout(() => {
          console.log('🔍 [GUEST_DATA] Nettoyage normal terminé, isClearingError = false');
          setIsClearingError(false);
        }, 100);
      }
    }
    
    // 🎯 NOUVELLE LOGIQUE : Nettoyer l'erreur aussi quand les autres champs changent
    if (name === 'guest_full_name' || name === 'guest_phone') {
      if (registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))) {
        console.log('🔍 [GUEST_DATA] Autre champ modifié, nettoyage de l\'erreur d\'email');
        dispatch(clearRegistrationError());
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🔍 [SUBMIT] handleSubmit appelé');
    console.log('🔍 [SUBMIT] État actuel registrationError:', registrationError);
    console.log('🔍 [SUBMIT] État isClearingError:', isClearingError);

    // 🎯 NOUVELLE LOGIQUE : Empêcher la soumission si on est en train de nettoyer l'erreur
    if (isClearingError) {
      console.log('🔍 [SUBMIT] En cours de nettoyage d\'erreur, soumission bloquée');
      return;
    }

    // 🎯 CORRECTION : Validation plus stricte pour l'erreur d'email
    if (registrationError && registrationError.includes && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))) {
      console.log('🔍 [SUBMIT] Erreur d\'email existante, soumission bloquée');
      dispatch(showSnackbar({ 
        message: "Veuillez modifier l'email avant de réessayer", 
        severity: 'warning' 
      }));
      return;
    }

    // Validation : si des sessions existent, le choix est obligatoire
    if (sessionTypes.length > 0 && !formData.session_type_id) {
      dispatch(showSnackbar({ message: "Veuillez sélectionner une session", severity: 'error' }));
      return;
    }
    
    // 🎯 NOUVELLE VALIDATION : Vérifier les champs d'invité si nécessaire
    if (isGuestRegistration) {
      if (!guestData.guest_full_name.trim()) {
        dispatch(showSnackbar({ message: "Veuillez saisir votre nom complet", severity: 'error' }));
        return;
      }
      if (!guestData.guest_email.trim()) {
        dispatch(showSnackbar({ message: "Veuillez saisir votre email", severity: 'error' }));
        return;
      }
      if (!guestData.guest_phone.trim()) {
        dispatch(showSnackbar({ message: "Veuillez saisir votre téléphone", severity: 'error' }));
        return;
      }
    }

    try {
      console.log('🔍 [SUBMIT] Tentative d\'inscription...');
      // Si événement gratuit, créer l'inscription directement
      if (!isPaid) {
        const payload = { event: event.id };
        // N'envoyer ticket_type_id que si un type spécifique est sélectionné
        if (formData.ticket_type_id && formData.ticket_type_id !== '') {
          payload.ticket_type_id = Number(formData.ticket_type_id);
        }
        // Ajouter le type de session si des sessions existent
        if (sessionTypes.length > 0 && formData.session_type_id) {
          payload.session_type_id = Number(formData.session_type_id);
        }
        
        // 🎯 NOUVELLE LOGIQUE : Ajouter les données d'invité si c'est une inscription d'invité
        if (isGuestRegistration) {
          console.log("🔍 FRONTEND DEBUG: Construction payload invité");
          console.log("🔍 FRONTEND DEBUG: guest_full_name:", guestData.guest_full_name);
          console.log("🔍 FRONTEND DEBUG: guest_email:", guestData.guest_email);
          console.log("🔍 FRONTEND DEBUG: guest_phone:", guestData.guest_phone);
          console.log("🔍 FRONTEND DEBUG: guest_country:", guestData.guest_country);
          
          payload.guest_full_name = guestData.guest_full_name;
          payload.guest_email = guestData.guest_email;
          payload.guest_phone = guestData.guest_phone;
          payload.guest_country = guestData.guest_country;
          
          console.log("🔍 FRONTEND DEBUG: Payload final:", payload);
        }
        
        console.log('🔍 [SUBMIT] Payload pour inscription gratuite:', payload);
        await dispatch(registerForEvent(payload)).unwrap();
        console.log('🔍 [SUBMIT] Inscription gratuite réussie');

            // Reset and close
            setFormData({ notes: '', special_requirements: '', ticket_type_id: null });
        // Rafraîchir les données de l'événement pour mettre à jour le compteur
        if (event?.id) {
          dispatch(fetchEventById(event.id));
        }
        dispatch(showSnackbar({ message: "Inscription confirmée. Consultez votre email pour votre QR.", severity: 'success', persist: true }));
        onClose();
      } else {
        // Si événement payant, afficher directement la section de paiement SANS créer d'inscription
        setPendingReg({ 
          event: event, // Passer l'objet event complet au lieu de event.id
          ticket_type_id: formData.ticket_type_id && formData.ticket_type_id !== '' ? Number(formData.ticket_type_id) : null,
          session_type_id: sessionTypes.length > 0 && formData.session_type_id ? Number(formData.session_type_id) : null,
          // 🎯 NOUVELLE LOGIQUE : Ajouter les données d'invité si c'est une inscription d'invité
          ...(isGuestRegistration && {
            guest_full_name: guestData.guest_full_name,
            guest_email: guestData.guest_email,
            guest_phone: guestData.guest_phone,
            guest_country: guestData.guest_country
          })
        });
        dispatch(showSnackbar({ message: "Procédez au paiement pour confirmer votre inscription.", severity: 'info', persist: true }));
      }
    } catch (error) {
      console.error('🔍 [SUBMIT] Erreur lors de l\'inscription:', error);
      console.log('🔍 [SUBMIT] État registrationError après erreur:', registrationError);
      
      // 🎯 CORRECTION : Réinitialiser les données d'invité en cas d'erreur
      if (error?.message?.includes('email') || error?.message?.includes('déjà utilisé')) {
        console.log('🔍 [SUBMIT] Erreur liée à l\'email, réinitialisation des données d\'invité');
        setGuestData({ guest_full_name: '', guest_email: '', guest_phone: '', guest_country: 'FR' });
        setIsGuestRegistration(false);
      }
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleClose = () => {
    console.log('🔍 [MODAL] handleClose appelé');
    console.log('🔍 [MODAL] État actuel registrationError:', registrationError);
    
    // 🎯 CORRECTION : Réinitialisation complète de tous les états
    setFormData({ ticket_type_id: null, session_type_id: '' });
    setGuestData({ guest_full_name: '', guest_email: '', guest_phone: '', guest_country: 'FR' });
    setIsGuestRegistration(false);
    setPendingReg(null);
    setIsClearingError(false);
    
    // 🎯 CORRECTION : Nettoyer l'erreur d'inscription AVANT de fermer
    console.log('🔍 [MODAL] Dispatch clearRegistrationError() avant fermeture');
    dispatch(clearRegistrationError());
    console.log('🔍 [MODAL] clearRegistrationError() dispatché');
    
    // 🎯 NOUVEAU : Attendre un peu que l'erreur soit nettoyée avant de fermer
    setTimeout(() => {
      onClose();
    }, 50);
  };

  const handleCancelPayment = () => {
    // Maintenant c'est simple : on annule juste le processus de paiement
    // Aucune inscription n'a été créée, donc rien à supprimer côté serveur
    setPendingReg(null);
    dispatch(showSnackbar({ message: "Processus d'inscription annulé. Vous pouvez recommencer si vous le souhaitez.", severity: 'info' }));
  };

  // 🎯 SYNC : Mettre à jour les données de paiement si l'utilisateur modifie l'email invité
  useEffect(() => {
    if (event && pendingReg && isGuestRegistration) {
      const selectedTicket = ticketTypes.find(t => String(t.id) === String(formData.ticket_type_id));
      const selectedPrice = selectedTicket ? (Number(selectedTicket.effective_price ?? selectedTicket.price) || 0) : (Number(event.price) || 0);
      const isPaid = selectedPrice > 0;
      
      if (isPaid) {
        const updated = {
          ...pendingReg,
          guest_full_name: guestData.guest_full_name,
          guest_email: guestData.guest_email,
          guest_phone: guestData.guest_phone,
        };
        const changed = pendingReg.guest_full_name !== updated.guest_full_name ||
          pendingReg.guest_email !== updated.guest_email ||
          pendingReg.guest_phone !== updated.guest_phone;
        if (changed) {
          console.log('🔄 [SYNC] Mise à jour pendingReg avec les nouvelles données invité:', updated);
          setPendingReg(updated);
        }
      }
    }
  }, [event, guestData, formData.ticket_type_id, ticketTypes, pendingReg, isGuestRegistration]);

  if (!event) return null;

  const selectedTicket = ticketTypes.find(t => String(t.id) === String(formData.ticket_type_id));
  const selectedPrice = selectedTicket ? (Number(selectedTicket.effective_price ?? selectedTicket.price) || 0) : (Number(event.price) || 0);
  const isPaid = selectedPrice > 0;
  // Permettre le paiement même sans Stripe configuré (le backend gère le mode test)
  const stripeEnabled = true;

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

          {/* 🎯 NOUVEAU : Masquer le champ Type de billet pour les événements gratuits */}
          {!event.is_free && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="ticket-type-label">Type de billet</InputLabel>
              <Select
                key={`ticket-select-${formData.ticket_type_id || 'default'}-${forceRender}`}
                labelId="ticket-type-label"
                name="ticket_type_id"
                label="Type de billet"
                value={formData.ticket_type_id || ''}
                onChange={handleInputChange}
                // 🎯 NOUVEAU : Forcer le re-rendu avec displayEmpty
                displayEmpty
              renderValue={(value) => {
                console.log('🔍 [RENDER_VALUE] ===== DÉBUT renderValue =====');
                console.log('🔍 [RENDER_VALUE] value reçu:', value, 'type:', typeof value);
                console.log('🔍 [RENDER_VALUE] formData.ticket_type_id:', formData.ticket_type_id);
                console.log('🔍 [RENDER_VALUE] ticketTypes disponibles:', ticketTypes.map(t => ({ id: t.id, name: t.name, type: typeof t.id })));
                
                // 🎯 NOUVEAU : Log spécial pour la valeur vide
                if (value === '' || value === null || value === undefined) {
                  console.log('🔍 [RENDER_VALUE] 🎯 VALEUR VIDE DÉTECTÉE !');
                  console.log('🔍 [RENDER_VALUE] 🎯 Aucun billet sélectionné');
                  console.log('🔍 [RENDER_VALUE] ===== FIN renderValue =====');
                  return (
                    <span style={{ color: '#999', fontStyle: 'italic', fontSize: '0.9em' }}>
                      CHOISIR UN TYPE DE BILLET
                    </span>
                  );
                }

                // 🎯 NOUVEAU : Gérer la valeur "default"
                if (value === 'default') {
                  console.log('🔍 [RENDER_VALUE] 🎯 BILLET PAR DÉFAUT SÉLECTIONNÉ !');
                  console.log('🔍 [RENDER_VALUE] ===== FIN renderValue =====');
                  return `Par défaut ${Number(event.price) > 0 ? `(${formatPrice(event.price)})` : '(Gratuit)'}`;
                }
                
                // 🎯 NOUVEAU : Log pour voir si renderValue est appelé après le changement
                console.log('🔍 [RENDER_VALUE] 🔄 renderValue appelé après changement de valeur');
                
                // 🎯 CORRECTION : Vérifier si c'est le billet par défaut
                if (!value) {
                  console.log('🔍 [RENDER_VALUE] Aucun billet sélectionné (valeur falsy)');
                  console.log('🔍 [RENDER_VALUE] ===== FIN renderValue =====');
                  return 'CHOISIR UN TYPE DE BILLET';
                }
                
                console.log('🔍 [RENDER_VALUE] Recherche du ticket personnalisé avec value:', value);
                const selectedTicket = ticketTypes.find(t => {
                  const ticketId = String(t.id);
                  const selectedValue = String(value);
                  const match = ticketId === selectedValue;
                  console.log('🔍 [RENDER_VALUE] Comparaison:', { ticketId, selectedValue, match, ticketName: t.name });
                  return match;
                });
                
                console.log('🔍 [RENDER_VALUE] Ticket trouvé:', selectedTicket);
                
                if (selectedTicket) {
                  const displayText = `${selectedTicket.name} — ${Number(selectedTicket.effective_price) > 0 ? formatPrice(Number(selectedTicket.effective_price)) : 'Gratuit'}`;
                  console.log('🔍 [RENDER_VALUE] Texte à afficher:', displayText);
                  console.log('🔍 [RENDER_VALUE] ===== FIN renderValue =====');
                  return displayText;
                }
                
                console.log('🔍 [RENDER_VALUE] Aucun ticket trouvé, affichage par défaut');
                console.log('🔍 [RENDER_VALUE] ===== FIN renderValue =====');
                return 'Sélectionner un type de billet';
              }}
            >
                          <MenuItem 
              value="default"
              onClick={() => {
                console.log('🔍 [MENU_ITEM] Clic sur "Par défaut"');
                console.log('🔍 [MENU_ITEM] État formData avant:', formData);
              }}
            >
              Par défaut {Number(event.price) > 0 ? `(${formatPrice(event.price)})` : '(Gratuit)'}
            </MenuItem>
              {ticketTypes.map(tt => {
                const remaining = tt.available_quantity;
                const isSoldOut = remaining === 0;
                console.log('🔍 [MENU_ITEM] Création MenuItem pour:', { id: tt.id, name: tt.name, value: tt.id, type: typeof tt.id });
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
          )}

          {/* Sélection du type de session si des sessions existent */}
          {sessionTypes.length > 0 && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="session-type-label">Type de session *</InputLabel>
              <Select
                labelId="session-type-label"
                name="session_type_id"
                label="Type de session *"
                value={formData.session_type_id}
                onChange={handleInputChange}
                required
                error={!formData.session_type_id}
                renderValue={(value) => {
                  if (!value) {
                    return 'Choisissez une session';
                  }
                  const selectedSession = sessionTypes.find(s => String(s.id) === String(value));
                  if (selectedSession) {
                    return `${selectedSession.name} `;
                  }
                  return 'Sélectionner une session';
                }}
              >
                {(() => {
                  console.log('🔍 DEBUG: Affichage des sessions - Total:', sessionTypes.length);
                  const activeSessions = sessionTypes.filter(session => session.is_active);
                  console.log('🔍 DEBUG: Sessions actives:', activeSessions.length);
                  const sortedSessions = activeSessions.sort((a, b) => a.display_order - b.display_order);
                  console.log('🔍 DEBUG: Sessions triées:', sortedSessions.map(s => s.name));
                  
                  return sortedSessions.map(session => {
                    return (
                      <MenuItem key={session.id} value={session.id} disabled={!session.is_active}>
                        {session.name}
                        {!session.is_active ? ' — INACTIVE' : ''}
                      </MenuItem>
                    );
                  });
                })()}
              </Select>
            </FormControl>
          )}

          {/* 🎯 NOUVELLE SECTION : Formulaire d'invité - VISIBLE UNIQUEMENT POUR LES INVITÉS */}
          {!user && (
            <Box sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                📝 Informations d'inscription
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Button
                  variant={isGuestRegistration ? "contained" : "outlined"}
                  onClick={() => setIsGuestRegistration(!isGuestRegistration)}
                  sx={{ mb: 2 }}
                >
                  {isGuestRegistration ? "✅ Inscription en tant qu'invité" : "👤 Inscription en tant qu'invité"}
                </Button>
                
                {!isGuestRegistration && (
                  <Typography variant="body2" color="text.secondary">
                    Vous êtes connecté en tant que <strong>{user?.username || 'utilisateur'}</strong>
                  </Typography>
                )}
              </Box>

              {isGuestRegistration && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField
                    fullWidth
                    label="Nom complet *"
                    name="guest_full_name"
                    value={guestData.guest_full_name}
                    onChange={handleGuestDataChange}
                    required
                    error={!guestData.guest_full_name.trim()}
                    helperText={!guestData.guest_full_name.trim() ? "Le nom complet est obligatoire" : ""}
                    placeholder="Votre nom complet"
                  />
                  
                  <TextField
                    fullWidth
                    label="Email *"
                    name="guest_email"
                    type="email"
                    value={guestData.guest_email}
                    onChange={handleGuestDataChange}
                    required
                    error={(() => {
                      // 🎯 NOUVEAU : Log détaillé de la validation du champ email
                      const hasError = !guestData.guest_email.trim() || (registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé')));
                      console.log('🔍 [EMAIL_FIELD] Validation du champ email:', {
                        email: guestData.guest_email,
                        emailEmpty: !guestData.guest_email.trim(),
                        registrationError,
                        errorType: typeof registrationError,
                        hasEmailError: registrationError && registrationError.includes('email'),
                        hasDejaUtiliseError: registrationError && registrationError.includes('déjà utilisé'),
                        hasError
                      });
                      return hasError;
                    })()}
                    helperText={
                      !guestData.guest_full_name.trim() 
                        ? "L'email est obligatoire" 
                        : (registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé')))
                          ? "Modifiez cet email pour résoudre le problème"
                          : ""
                    }
                    placeholder="votre.email@exemple.com"
                  />
                  
                  {registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé')) && (
                    <Alert severity="warning" sx={{ mt: 1, mb: 2 }}>
                      <Typography variant="body2">
                        <strong>Problème détecté :</strong> Cet email est déjà utilisé pour cet événement. 
                        Modifiez l'email ci-dessus pour continuer.
                      </Typography>
                    </Alert>
                  )}
                  
                  {/* 🎯 NOUVEAU : Log détaillé de l'affichage des erreurs */}
                  {(() => {
                    console.log('🔍 [ERROR_DISPLAY] État des erreurs:', {
                      registrationError,
                      errorType: typeof registrationError,
                      hasEmailError: registrationError && registrationError.includes('email'),
                      hasDejaUtiliseError: registrationError && registrationError.includes('déjà utilisé'),
                      shouldShowWarning: registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))
                    });
                    return null;
                  })()}
                  
                  {/* 🎯 NOUVEAU : Sélecteur de pays pour le téléphone */}
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel id="country-label">Pays *</InputLabel>
                    <Select
                      labelId="country-label"
                      name="guest_country"
                      label="Pays *"
                      value={guestData.guest_country || 'FR'}
                      onChange={handleGuestDataChange}
                      required
                      error={!guestData.guest_country}
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
                      <MenuItem value="RE">🇷🇪 Réunion (+262)</MenuItem>
                      <MenuItem value="LS">🇱🇸 Lesotho (+266)</MenuItem>
                      <MenuItem value="SZ">🇸🇿 Eswatini (+268)</MenuItem>
                      <MenuItem value="YT">🇾🇹 Mayotte (+262)</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    label="Numéro de téléphone *"
                    name="guest_phone"
                    type="tel"
                    value={guestData.guest_phone}
                    onChange={handleGuestDataChange}
                    required
                    error={(() => {
                      // 🎯 NOUVEAU : Log détaillé de la validation du champ téléphone
                      const hasError = !guestData.guest_phone.trim() || (registrationError && (registrationError.includes('téléphone') || registrationError.includes('numéro')));
                      console.log('🔍 [PHONE_FIELD] Validation du champ téléphone:', {
                        phone: guestData.guest_phone,
                        phoneEmpty: !guestData.guest_phone.trim(),
                        registrationError: registrationError,
                        hasError: hasError
                      });
                      return hasError;
                    })()}
                    helperText={(() => {
                      if (!guestData.guest_phone.trim()) {
                        return "Le numéro de téléphone est obligatoire pour recevoir la confirmation par SMS";
                      }
                      if (registrationError && (registrationError.includes('téléphone') || registrationError.includes('numéro'))) {
                        return registrationError;
                      }
                      return "Format: 0612345678 (sans espaces ni tirets)";
                    })()}
                    placeholder="0612345678"
                  />
                  
                  <Alert severity="info">
                    📧 Un email avec votre QR-code sera envoyé à cette adresse après confirmation de l'inscription.
                    📱 Un SMS de confirmation sera également envoyé à votre numéro de téléphone.
                  </Alert>
                </Box>
              )}
            </Box>
          )}

          {registrationError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {registrationError}
              {(() => {
                // 🎯 NOUVEAU : Log détaillé de l'affichage principal des erreurs
                console.log('🔍 [MAIN_ERROR_DISPLAY] Affichage de l\'erreur principale:', {
                  registrationError,
                  errorType: typeof registrationError,
                  hasEmailError: registrationError && registrationError.includes('email'),
                  hasDejaUtiliseError: registrationError && registrationError.includes('déjà utilisé'),
                  shouldShowSolution: registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))
                });
                return null;
              })()}
              {registrationError.includes('email') || registrationError.includes('déjà utilisé') ? (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="inherit">
                    💡 <strong>Solution :</strong> Modifiez l'email dans le formulaire ci-dessus pour résoudre ce problème.
                  </Typography>
                </Box>
              ) : null}
            </Alert>
          )}



          {pendingReg && isPaid && stripeEnabled && (
            <PaymentSection
              registrationData={pendingReg}
              setPaymentLoading={setPaymentLoading}
              onPaid={async () => {
                setFormData({ ticket_type_id: null, session_type_id: '' });
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
            <Alert severity="info" sx={{ mt: 2 }}>
              💡 Mode test activé : Le paiement sera simulé par le backend. Aucune configuration Stripe requise.
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
            disabled={
              (() => {
                // 🎯 NOUVEAU : Log détaillé de la validation du bouton
                const conditions = {
                  registrationLoading,
                  paymentLoading,
                  isClearingError,
                  pendingRegAndPaid: (pendingReg && isPaid),
                  ticketTypeRequired: (!event.is_free && !formData.ticket_type_id),
                  sessionTypeRequired: (sessionTypes.length > 0 && !formData.session_type_id),
                  guestFieldsRequired: (!user && (!guestData.guest_full_name.trim() || !guestData.guest_email.trim() || !guestData.guest_phone.trim() || !guestData.guest_country)),
                  emailError: (registrationError && registrationError.includes && (registrationError.includes('email') || registrationError.includes('déjà utilisé')))
                };
                
                const isDisabled = conditions.registrationLoading || 
                  conditions.paymentLoading || 
                  conditions.isClearingError ||
                  conditions.pendingRegAndPaid ||
                  conditions.ticketTypeRequired ||
                  conditions.sessionTypeRequired ||
                  conditions.guestFieldsRequired ||
                  conditions.emailError;
                
                // 🎯 NOUVEAU : Log détaillé de chaque condition
                console.log('🔍 [BUTTON_VALIDATION] Conditions détaillées:', {
                  registrationLoading: conditions.registrationLoading,
                  paymentLoading: conditions.paymentLoading,
                  isClearingError: conditions.isClearingError,
                  pendingRegAndPaid: conditions.pendingRegAndPaid,
                  ticketTypeRequired: conditions.ticketTypeRequired,
                  sessionTypeRequired: conditions.sessionTypeRequired,
                  guestFieldsRequired: conditions.guestFieldsRequired,
                  emailError: conditions.emailError,
                  // 🎯 NOUVEAU : Valeurs des champs d'invité
                  guestFields: {
                    fullName: guestData.guest_full_name.trim(),
                    email: guestData.guest_email.trim(),
                    phone: guestData.guest_phone.trim(),
                    hasUser: !!user
                  },
                  // 🎯 NOUVEAU : Valeurs des sessions
                  sessionData: {
                    totalSessions: sessionTypes.length,
                    selectedSession: formData.session_type_id
                  }
                });
                
                console.log('🔍 [BUTTON_VALIDATION] Bouton désactivé:', isDisabled);
                
                return isDisabled;
              })()
            }
            startIcon={(registrationLoading || paymentLoading) ? <CircularProgress size={20} /> : null}
            sx={{ mt: 2 }}
          >
            {(() => {
              if (registrationLoading || paymentLoading) return 'Traitement...';
              if (isClearingError) return 'Nettoyage...';
              if (pendingReg && isPaid) return 'Procéder au paiement ci-dessous';
              if (isPaid) return 'Procéder au paiement';
              if (!event.is_free && !formData.ticket_type_id) return 'Sélectionnez un type de billet';
              if (sessionTypes.length > 0 && !formData.session_type_id) return 'Sélectionnez une session';
              if (!user && (!guestData.guest_full_name.trim() || !guestData.guest_email.trim() || !guestData.guest_phone.trim() || !guestData.guest_country)) {
                return 'Remplissez le formulaire invité';
              }
              if (registrationError && (registrationError.includes('email') || registrationError.includes('déjà utilisé'))) {
                return 'Modifiez l\'email pour continuer';
              }
              return 'Confirmer l\'inscription';
            })()}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RegistrationModal;