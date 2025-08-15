import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Avatar,
  Typography,
} from '@mui/material';
import {
  Home as HomeIcon,
  Event as EventIcon,
  Add as AddIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Bookmark as BookmarkIcon,
  QrCodeScanner as QrCodeScannerIcon,
  AdminPanelSettings as SuperAdminIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { setSidebarOpen } from '../../store/slices/uiSlice';

const drawerWidth = 240;

const baseMenuItems = [
  { text: 'Accueil', icon: <HomeIcon />, path: '/' },
  { text: 'Événements', icon: <EventIcon />, path: '/events' },
  { text: 'Créer un événement', icon: <AddIcon />, path: '/create-event' },
  { text: 'Mes événements', icon: <EventIcon />, path: '/my-events' },
  { text: 'Mes inscriptions', icon: <BookmarkIcon />, path: '/my-registrations' },
  { text: 'Tableau de bord', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Mon profil', icon: <PersonIcon />, path: '/profile' },
];

const Sidebar = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen } = useSelector((state) => state.ui);
  const { user } = useSelector((state) => state.auth);

  const handleNavigation = (path) => {
    navigate(path);
    dispatch(setSidebarOpen(false));
  };

  const drawer = (
    <Box>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar src={user?.profile_picture} sx={{ width: 40, height: 40 }} />
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            {user?.username || 'Utilisateur'}
          </Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            {user?.email || 'Bienvenue'}
          </Typography>
        </Box>
      </Box>
      <Divider />
      <List>
        {(() => {
          let menuItems = [...baseMenuItems];
          
          // Ajouter Scanner billets pour staff
          if (user && user.is_staff) {
            menuItems.splice(6, 0, { text: 'Scanner billets', icon: <QrCodeScannerIcon />, path: '/scan' });
          }
          
          // Ajouter Super Admin Dashboard pour super admins
          if (user && (
            user.is_staff || 
            user.is_superuser || 
            (user.profile && user.profile.role === 'super_admin')
          )) {
            menuItems.splice(6, 0, { text: '🎛️ Super Admin', icon: <SuperAdminIcon />, path: '/super-admin' });
          }
          
          return menuItems;
        })().map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      {/* Sidebar mobile (temporaire) */}
      <Drawer
        variant="temporary"
        open={sidebarOpen}
        onClose={() => dispatch(setSidebarOpen(false))}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundImage: (theme) => theme.palette.gradients?.sidebar,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Sidebar desktop (permanente) */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundImage: (theme) => theme.palette.gradients?.sidebar,
          },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Sidebar; 