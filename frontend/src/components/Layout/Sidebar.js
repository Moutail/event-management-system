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
} from '@mui/material';
import {
  Home as HomeIcon,
  Event as EventIcon,
  Add as AddIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Bookmark as BookmarkIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { setSidebarOpen } from '../../store/slices/uiSlice';

const drawerWidth = 240;

const menuItems = [
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

  const handleNavigation = (path) => {
    navigate(path);
    dispatch(setSidebarOpen(false));
  };

  const drawer = (
    <Box>
      <Box sx={{ p: 2 }}>
        <h3>Menu</h3>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
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
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Paramètres" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Drawer
      variant="temporary"
      open={sidebarOpen}
      onClose={() => dispatch(setSidebarOpen(false))}
      ModalProps={{
        keepMounted: true, // Better open performance on mobile.
      }}
      sx={{
        display: { xs: 'block', sm: 'none' },
        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
      }}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar; 