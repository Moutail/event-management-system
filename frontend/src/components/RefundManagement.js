import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  IconButton,
  Tooltip,
  Box,
  Alert,
  CircularProgress,
  TextField,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  AccessTime as PendingIcon,
  Euro as EuroIcon,
  Person as PersonIcon,
  Event as EventIcon
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { showSnackbar } from '../store/slices/uiSlice';
import { fetchEventStatistics } from '../store/slices/eventSlice';
import { eventAPI } from '../services/api';
import { formatPrice, formatDateTime } from '../utils/formatters';

const RefundManagement = ({ open, onClose, event }) => {
  const dispatch = useDispatch();
  const [refundRequests, setRefundRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});
  const [processingDialog, setProcessingDialog] = useState({ open: false, request: null, action: null });

  useEffect(() => {
    if (open && event?.id) {
      loadRefundRequests();
    }
  }, [open, event?.id]);

  const loadRefundRequests = async () => {
    try {
      setLoading(true);
      const response = await eventAPI.getRefundRequests(event.id);
      setRefundRequests(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des demandes de remboursement:', error);
      dispatch(showSnackbar({ 
        message: 'Erreur lors du chargement des demandes de remboursement', 
        severity: 'error' 
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleProcessRefund = async (requestId, action) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: action }));
      
      await eventAPI.processRefund(requestId, action);
      
      dispatch(showSnackbar({ 
        message: action === 'approve' ? 'Remboursement approuvé avec succès' : 'Demande rejetée',
        severity: 'success' 
      }));
      
      // Recharger les données
      loadRefundRequests();
      // Recharger les statistiques du tableau de bord si un remboursement a été approuvé
      if (action === 'approve') {
        dispatch(fetchEventStatistics());
      }
      setProcessingDialog({ open: false, request: null, action: null });
      
    } catch (error) {
      console.error(`Erreur lors du ${action}:`, error);
      dispatch(showSnackbar({ 
        message: `Erreur lors du ${action === 'approve' ? 'remboursement' : 'rejet'}`, 
        severity: 'error' 
      }));
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: false }));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'info';
      case 'processed': return 'success';
      case 'rejected': return 'error';
      case 'expired': return 'default';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending': return 'En attente';
      case 'approved': return 'Approuvé';
      case 'processed': return 'Traité';
      case 'rejected': return 'Rejeté';
      case 'expired': return 'Expiré';
      default: return status;
    }
  };

  const calculateRefundAmount = (request) => {
    return (request.amount_paid * request.refund_percentage) / 100;
  };

  if (loading) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <EuroIcon color="primary" />
            <Typography variant="h6">
              Gestion des Remboursements - {event?.title}
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {refundRequests.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              Aucune demande de remboursement pour cet événement.
            </Alert>
          ) : (
            <>
              {/* Statistiques rapides */}
              <Box display="flex" gap={2} mb={3}>
                <Card sx={{ flex: 1 }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="warning.main">
                      {refundRequests.filter(r => r.status === 'pending').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      En attente
                    </Typography>
                  </CardContent>
                </Card>
                
                <Card sx={{ flex: 1 }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main">
                      {refundRequests.filter(r => r.status === 'processed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Traités
                    </Typography>
                  </CardContent>
                </Card>
                
                <Card sx={{ flex: 1 }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary.main">
                      {formatPrice(refundRequests
                        .filter(r => r.status === 'processed')
                        .reduce((sum, r) => sum + calculateRefundAmount(r), 0)
                      )}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Montant remboursé
                    </Typography>
                  </CardContent>
                </Card>
              </Box>

              <Divider sx={{ mb: 2 }} />

              {/* Table des demandes */}
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Participant</TableCell>
                      <TableCell>Montant payé</TableCell>
                      <TableCell>% Remboursement</TableCell>
                      <TableCell>Montant à rembourser</TableCell>
                      <TableCell>Statut</TableCell>
                      <TableCell>Date demande</TableCell>
                      <TableCell>Raison</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {refundRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <PersonIcon fontSize="small" color="action" />
                            <div>
                              <Typography variant="body2" fontWeight="medium">
                                {request.registration?.user?.first_name} {request.registration?.user?.last_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {request.registration?.user?.email}
                              </Typography>
                            </div>
                          </Box>
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {formatPrice(request.amount_paid)}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Chip 
                            label={`${request.refund_percentage}%`} 
                            size="small" 
                            color="primary" 
                            variant="outlined" 
                          />
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {formatPrice(calculateRefundAmount(request))}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Chip 
                            label={getStatusLabel(request.status)}
                            color={getStatusColor(request.status)}
                            size="small"
                          />
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="body2">
                            {formatDateTime(request.created_at)}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}
                          >
                            {request.reason || 'Aucune raison fournie'}
                          </Typography>
                        </TableCell>
                        
                        <TableCell align="center">
                          {request.status === 'pending' && (
                            <Box display="flex" gap={1}>
                              <Tooltip title="Approuver le remboursement">
                                <IconButton
                                  color="success"
                                  onClick={() => setProcessingDialog({ 
                                    open: true, 
                                    request, 
                                    action: 'approve' 
                                  })}
                                  disabled={actionLoading[request.id]}
                                >
                                  {actionLoading[request.id] === 'approve' ? (
                                    <CircularProgress size={20} />
                                  ) : (
                                    <ApproveIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                              
                              <Tooltip title="Rejeter la demande">
                                <IconButton
                                  color="error"
                                  onClick={() => setProcessingDialog({ 
                                    open: true, 
                                    request, 
                                    action: 'reject' 
                                  })}
                                  disabled={actionLoading[request.id]}
                                >
                                  {actionLoading[request.id] === 'reject' ? (
                                    <CircularProgress size={20} />
                                  ) : (
                                    <RejectIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            </Box>
                          )}
                          
                          {request.status !== 'pending' && (
                            <Tooltip title={`Traité le ${formatDateTime(request.processed_at)}`}>
                              <PendingIcon color="disabled" />
                            </Tooltip>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose}>Fermer</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de confirmation */}
      <Dialog
        open={processingDialog.open}
        onClose={() => setProcessingDialog({ open: false, request: null, action: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {processingDialog.action === 'approve' ? 'Confirmer le remboursement' : 'Confirmer le rejet'}
        </DialogTitle>
        
        <DialogContent>
          {processingDialog.request && (
            <Box>
              <Typography variant="body1" gutterBottom>
                {processingDialog.action === 'approve' 
                  ? `Êtes-vous sûr de vouloir approuver le remboursement de ${formatPrice(calculateRefundAmount(processingDialog.request))} pour ${processingDialog.request.registration?.user?.first_name} ${processingDialog.request.registration?.user?.last_name} ?`
                  : `Êtes-vous sûr de vouloir rejeter cette demande de remboursement ?`
                }
              </Typography>
              
              {processingDialog.request.reason && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <strong>Raison :</strong> {processingDialog.request.reason}
                </Alert>
              )}
              
              {processingDialog.action === 'approve' && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Le remboursement sera traité automatiquement via Stripe et l'utilisateur recevra un email de confirmation.
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button 
            onClick={() => setProcessingDialog({ open: false, request: null, action: null })}
          >
            Annuler
          </Button>
          <Button 
            variant="contained"
            color={processingDialog.action === 'approve' ? 'success' : 'error'}
            onClick={() => handleProcessRefund(processingDialog.request?.id, processingDialog.action)}
            disabled={actionLoading[processingDialog.request?.id]}
          >
            {processingDialog.action === 'approve' ? 'Approuver' : 'Rejeter'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RefundManagement;
