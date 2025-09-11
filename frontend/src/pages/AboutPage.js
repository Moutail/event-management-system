import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Avatar,
  useTheme,
} from '@mui/material';
import {
  Event as EventIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Support as SupportIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import PublicHeader from '../components/Layout/PublicHeader';

const AboutPage = () => {
  const theme = useTheme();

  const features = [
    {
      icon: <EventIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Gestion d\'Événements',
      description: 'Créez, organisez et gérez vos événements avec une interface intuitive et des outils puissants.',
    },
    {
      icon: <PeopleIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Gestion des Participants',
      description: 'Suivez les inscriptions, gérez les listes d\'attente et communiquez efficacement avec vos participants.',
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Sécurité et Fiabilité',
      description: 'Vos données sont protégées avec les dernières technologies de sécurité et de cryptage.',
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Performance Optimale',
      description: 'Une plateforme rapide et responsive qui s\'adapte à tous vos besoins, même les plus exigeants.',
    },
    {
      icon: <SupportIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Support 24/7',
      description: 'Notre équipe est disponible pour vous accompagner à chaque étape de votre projet.',
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: 'Analytics Avancés',
      description: 'Analysez les performances de vos événements avec des rapports détaillés et des insights précieux.',
    },
  ];

  const team = [
    {
      name: 'Équipe de Développement',
      role: 'Innovation & Technologie',
      description: 'Notre équipe de développeurs passionnés travaille sans relâche pour créer la meilleure expérience utilisateur possible.',
    },
    {
      name: 'Équipe Support',
      role: 'Assistance & Formation',
      description: 'Dédiée à votre réussite, notre équipe support vous accompagne dans l\'utilisation de la plateforme.',
    },
    {
      name: 'Équipe Produit',
      role: 'Conception & Amélioration',
      description: 'Nous analysons constamment vos besoins pour améliorer et enrichir nos fonctionnalités.',
    },
  ];

  return (
    <>
      <PublicHeader />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', pt: 8, pb: 6 }}>
        <Container maxWidth="lg">
        {/* En-tête de la page */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
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
              fontSize: { xs: '2.5rem', md: '3.5rem' },
            }}
          >
            À Propos de Notre Plateforme
          </Typography>
          <Typography
            variant="h5"
            color="text.secondary"
            sx={{
              maxWidth: 800,
              mx: 'auto',
              lineHeight: 1.6,
              mb: 4,
            }}
          >
            Découvrez l'histoire, la mission et les valeurs qui animent notre plateforme de gestion d'événements
          </Typography>
        </Box>

        {/* Section Notre Mission */}
        <Paper
          elevation={0}
          sx={{
            p: { xs: 4, md: 6 },
            mb: 6,
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            borderRadius: 3,
            border: '1px solid rgba(108,99,255,0.1)',
          }}
        >
          <Typography
            variant="h3"
            component="h2"
            sx={{
              fontWeight: 700,
              mb: 4,
              textAlign: 'center',
              color: 'text.primary',
            }}
          >
            Notre Mission
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              maxWidth: 900,
              mx: 'auto',
              lineHeight: 1.8,
              color: 'text.secondary',
            }}
          >
            Nous nous engageons à révolutionner la gestion d'événements en offrant une plateforme intuitive, 
            puissante et accessible à tous. Notre objectif est de simplifier l'organisation d'événements 
            tout en maximisant l'engagement des participants et la réussite des organisateurs.
          </Typography>
        </Paper>

        {/* Section Nos Valeurs */}
        <Box sx={{ mb: 6 }}>
          <Typography
            variant="h3"
            component="h2"
            sx={{
              fontWeight: 700,
              mb: 4,
              textAlign: 'center',
              color: 'text.primary',
            }}
          >
            Nos Valeurs
          </Typography>
          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 12px 30px rgba(108,99,255,0.2)',
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                    <Box sx={{ mb: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography
                      variant="h6"
                      component="h3"
                      sx={{
                        fontWeight: 600,
                        mb: 2,
                        color: 'text.primary',
                      }}
                    >
                      {feature.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ lineHeight: 1.6 }}
                    >
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Section Notre Histoire */}
        <Paper
          elevation={0}
          sx={{
            p: { xs: 4, md: 6 },
            mb: 6,
            background: 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
            borderRadius: 3,
            color: 'white',
          }}
        >
          <Typography
            variant="h3"
            component="h2"
            sx={{
              fontWeight: 700,
              mb: 4,
              textAlign: 'center',
              color: 'white',
            }}
          >
            Notre Histoire
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              maxWidth: 900,
              mx: 'auto',
              lineHeight: 1.8,
              opacity: 0.95,
            }}
          >
            Fondée en 2025, notre plateforme est née de la constatation que la gestion d'événements 
            traditionnelle était souvent complexe et chronophage. Nous avons développé une solution 
            moderne qui combine simplicité d'utilisation et fonctionnalités avancées, permettant aux 
            organisateurs de se concentrer sur ce qui compte vraiment : créer des expériences 
            mémorables pour leurs participants.
          </Typography>
        </Paper>

        {/* Section Notre Équipe */}
        <Box sx={{ mb: 6 }}>
          <Typography
            variant="h3"
            component="h2"
            sx={{
              fontWeight: 700,
              mb: 4,
              textAlign: 'center',
              color: 'text.primary',
            }}
          >
            Notre Équipe
          </Typography>
          <Grid container spacing={4}>
            {team.map((member, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(108,99,255,0.15)',
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 4 }}>
                    <Avatar
                      sx={{
                        width: 80,
                        height: 80,
                        mx: 'auto',
                        mb: 3,
                        bgcolor: 'primary.main',
                        fontSize: '2rem',
                      }}
                    >
                      {member.name.charAt(0)}
                    </Avatar>
                    <Typography
                      variant="h6"
                      component="h3"
                      sx={{
                        fontWeight: 600,
                        mb: 1,
                        color: 'text.primary',
                      }}
                    >
                      {member.name}
                    </Typography>
                    <Typography
                      variant="subtitle1"
                      sx={{
                        mb: 2,
                        color: 'primary.main',
                        fontWeight: 500,
                      }}
                    >
                      {member.role}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ lineHeight: 1.6 }}
                    >
                      {member.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Section CTA */}
        <Paper
          elevation={0}
          sx={{
            p: { xs: 4, md: 6 },
            textAlign: 'center',
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            borderRadius: 3,
            border: '2px dashed rgba(108,99,255,0.3)',
          }}
        >
          <Typography
            variant="h4"
            component="h2"
            sx={{
              fontWeight: 700,
              mb: 3,
              color: 'text.primary',
            }}
          >
            Prêt à Commencer ?
          </Typography>
          <Typography
            variant="h6"
            sx={{
              mb: 4,
              maxWidth: 600,
              mx: 'auto',
              lineHeight: 1.6,
              color: 'text.secondary',
            }}
          >
            Rejoignez des milliers d'organisateurs qui font confiance à notre plateforme 
            pour créer des événements exceptionnels.
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: 'primary.main',
              fontWeight: 600,
              fontSize: '1.1rem',
            }}
          >
            🚀 Commencez votre aventure dès aujourd'hui !
          </Typography>
        </Paper>
        </Container>
      </Box>
    </>
  );
};

export default AboutPage;
















