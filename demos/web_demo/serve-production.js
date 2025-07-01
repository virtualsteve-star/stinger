#!/usr/bin/env node

const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the React build
const buildPath = path.join(__dirname, 'frontend', 'build');
app.use(express.static(buildPath));

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
  target: 'https://localhost:8000',
  changeOrigin: true,
  secure: false, // Accept self-signed certificates
  logLevel: 'warn'
}));

// Handle React routing - serve index.html for all non-API routes
app.get('*', (req, res) => {
  res.sendFile(path.join(buildPath, 'index.html'));
});

// Check if SSL certificates exist
const certPath = path.join(__dirname, 'backend', 'cert.pem');
const keyPath = path.join(__dirname, 'backend', 'key.pem');

if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  // Use HTTPS with existing certificates
  const httpsOptions = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
  };

  https.createServer(httpsOptions, app).listen(PORT, () => {
    console.log(`✅ Production server running on https://localhost:${PORT}`);
    console.log(`📋 Backend API expected at https://localhost:8000`);
    console.log(`\n🌐 Open https://localhost:${PORT} in your browser`);
  });
} else {
  // Fallback to HTTP if no certificates
  app.listen(PORT, () => {
    console.log(`✅ Production server running on http://localhost:${PORT}`);
    console.log(`⚠️  Warning: Running without HTTPS. Generate SSL certificates for secure operation.`);
    console.log(`📋 Backend API expected at https://localhost:8000`);
    console.log(`\n🌐 Open http://localhost:${PORT} in your browser`);
  });
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\nShutting down server...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nShutting down server...');
  process.exit(0);
});