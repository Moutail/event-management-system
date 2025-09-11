import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  useTheme,
  useMediaQuery,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4,
  Brightness7,
  Event as EventIcon,
  Info as InfoIcon,
  ContactSupport as ContactIcon,
  Login as LoginIcon,
  PersonAdd as PersonAddIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toggleDarkMode } from '../../store/slices/uiSlice';

const PublicHeader = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { darkMode } = useSelector((state) => state.ui);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  const handleThemeToggle = () => {
    dispatch(toggleDarkMode());
  };

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar />
      <Divider />
      <List>
        <ListItem button onClick={() => handleNavigation('/')}>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Accueil" />
        </ListItem>
        
        <ListItem button onClick={() => handleNavigation('/about')}>
          <ListItemIcon>
            <InfoIcon />
          </ListItemIcon>
          <ListItemText primary="À propos" />
        </ListItem>
        
        <ListItem button onClick={() => handleNavigation('/contact')}>
          <ListItemIcon>
            <ContactIcon />
          </ListItemIcon>
          <ListItemText primary="Contact" />
        </ListItem>
        
        <ListItem button onClick={() => handleNavigation('/login')}>
          <ListItemIcon>
            <LoginIcon />
          </ListItemIcon>
          <ListItemText primary="Connexion" />
        </ListItem>
        
        <ListItem button onClick={() => handleNavigation('/register')}>
          <ListItemIcon>
            <PersonAddIcon />
          </ListItemIcon>
          <ListItemText primary="Inscription" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <>
      <AppBar 
        position="fixed" 
        sx={{ 
          background: 'linear-gradient(135deg, #6C63FF 0%, #22D3EE 100%)',
          boxShadow: '0 4px 20px rgba(108, 99, 255, 0.3)',
        }}
      >
        <Toolbar>
          {/* Logo et titre */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <EventIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 700,
                fontSize: '1.5rem',
                background: 'linear-gradient(45deg, #ffffff 30%, #f0f0f0 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              EventManager
            </Typography>
          </Box>

          {/* Navigation desktop */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 1 }}>
            <IconButton
              color="inherit"
              onClick={handleThemeToggle}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              {darkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>

            <Button 
              color="inherit" 
              onClick={() => handleNavigation('/')}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease-in-out',
                fontWeight: 600,
              }}
            >
              Accueil
            </Button>

            <Button
              color="inherit"
              startIcon={<InfoIcon />}
              onClick={() => handleNavigation('/about')}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease-in-out',
                fontWeight: 500,
              }}
            >
              À propos
            </Button>

            <Button
              color="inherit"
              startIcon={<ContactIcon />}
              onClick={() => handleNavigation('/contact')}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease-in-out',
                fontWeight: 500,
              }}
            >
              Contact
            </Button>

            <Button
              color="inherit"
              startIcon={<LoginIcon />}
              onClick={() => handleNavigation('/login')}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease-in-out',
                fontWeight: 500,
              }}
            >
              Connexion
            </Button>

            <Button
              variant="outlined"
              color="inherit"
              startIcon={<PersonAddIcon />}
              onClick={() => handleNavigation('/register')}
              sx={{
                borderColor: 'rgba(255,255,255,0.5)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: 'white',
                  transform: 'translateY(-1px)',
                },
                transition: 'all 0.2s ease-in-out',
                fontWeight: 600,
                ml: 1,
              }}
            >
              Inscription
            </Button>
          </Box>

          {/* Menu mobile */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ display: { xs: 'block', md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Drawer mobile */}
      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default PublicHeader;
