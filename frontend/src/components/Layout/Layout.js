import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header />
      <Sidebar />
      <Box
        component="main"
        className="fade-in"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8, // Pour compenser la hauteur du header
          ml: { xs: 0, sm: '240px' }, // Marge à gauche pour la sidebar sur desktop
          backgroundColor: 'background.default',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout; 