import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.primary.main,
        color: 'white',
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" align="center">
          © {new Date().getFullYear()} DynamixAI. All rights reserved. | <Link href="https://dynamix-ai.com" target="_blank" rel="noopener" sx={{ color: 'white', textDecoration: 'underline', '&:hover': { opacity: 0.8 } }}>dynamix-ai.com</Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 