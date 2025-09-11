import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Alert,
  Button,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  AttachMoney as MoneyIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import RefundManagement from '../components/RefundManagement';
import api from '../services/api';

const RefundsPage = () => {
  const [refundModalOpen, setRefundModalOpen] = useState(false);
  const [refunds, setRefunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger les remboursements au montage de la page
  useEffect(() => {
    loadRefunds();
  }, []);

  const loadRefunds = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/organizer/refunds/', {
        params: { page: 1, page_size: 100 } // Charger plus de remboursements pour les stats
      });
      
      setRefunds(response.data.results || []);
    } catch (err) {
      console.error('Erreur lors du chargement des remboursements:', err);
      setError('Erreur lors du chargement des remboursements');
    } finally {
      setLoading(false);
    }
  };

  // Calculer les statistiques
  const getPendingCount = () => refunds.filter(r => r.status === 'pending').length;
  const getApprovedCount = () => refunds.filter(r => r.status === 'approved').length;
  const getProcessedCount = () => refunds.filter(r => r.status === 'processed').length;
  const getRejectedCount = () => refunds.filter(r => r.status === 'rejected').length;
  const getTotalCount = () => refunds.length;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* En-tête de la page */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
          💰 Gestion des Remboursements
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Gérez tous les remboursements de vos événements, y compris ceux créés automatiquement lors des annulations.
        </Typography>
        
        {/* Boutons d'action */}
        <Box display="flex" gap={2} sx={{ mb: 3 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<MoneyIcon />}
            onClick={() => setRefundModalOpen(true)}
          >
            Ouvrir la Gestion des Remboursements
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            startIcon={<RefreshIcon />}
            onClick={loadRefunds}
            disabled={loading}
          >
            Actualiser
          </Button>
        </Box>
      </Box>

      {/* Informations importantes */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="body2">
          <strong>💡 Information :</strong> Lorsqu'un événement est annulé, des demandes de remboursement sont créées automatiquement 
          pour tous les participants qui ont payé. Vous pouvez les gérer depuis cette page.
        </Typography>
      </Alert>

      {/* Statistiques rapides */}
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      ) : (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardHeader
                title="Total Remboursements"
                avatar={<MoneyIcon color="primary" />}
                titleTypographyProps={{ variant: 'h6' }}
              />
              <CardContent>
                <Typography variant="h4" color="primary.main" sx={{ fontWeight: 700 }}>
                  {getTotalCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tous statuts confondus
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardHeader
                title="En Attente"
                avatar={<ScheduleIcon color="warning" />}
                titleTypographyProps={{ variant: 'h6' }}
              />
              <CardContent>
                <Typography variant="h4" color="warning.main" sx={{ fontWeight: 700 }}>
                  {getPendingCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  En attente de traitement
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardHeader
                title="Approuvés"
                avatar={<CheckIcon color="success" />}
                titleTypographyProps={{ variant: 'h6' }}
              />
              <CardContent>
                <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                  {getApprovedCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Remboursements approuvés
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardHeader
                title="Traités"
                avatar={<InfoIcon color="info" />}
                titleTypographyProps={{ variant: 'h6' }}
              />
              <CardContent>
                <Typography variant="h4" color="info.main" sx={{ fontWeight: 700 }}>
                  {getProcessedCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Remboursements traités
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {/* Carte des rejetés en dessous */}
      {!loading && !error && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardHeader
                title="Rejetés"
                avatar={<CancelIcon color="error" />}
                titleTypographyProps={{ variant: 'h6' }}
              />
              <CardContent>
                <Typography variant="h4" color="error.main" sx={{ fontWeight: 700 }}>
                  {getRejectedCount()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Remboursements rejetés
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Guide d'utilisation */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
          📋 Guide d'utilisation
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
              <CheckIcon color="success" sx={{ mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Remboursements automatiques
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Créés automatiquement lors de l'annulation d'un événement payant
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
              <InfoIcon color="info" sx={{ mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Gestion centralisée
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tous vos remboursements dans une seule interface
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
              <WarningIcon color="warning" sx={{ mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Actions en lot
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Traitez plusieurs remboursements simultanément
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
              <MoneyIcon color="primary" sx={{ mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Suivi complet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Historique et statuts de tous vos remboursements
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Modal de gestion des remboursements */}
      <RefundManagement
        open={refundModalOpen}
        onClose={() => setRefundModalOpen(false)}
        event={null} // null pour afficher tous les remboursements
      />
    </Container>
  );
};

export default RefundsPage;
